from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs


def solve_captcha_accurate(queue_b64, image_b64):
    """
    High-accuracy captcha solver for LuckyWatch:
    1. Extract the 3 individual queue icons in left-to-right order.
    2. Segment scene icons by background subtraction & morphological closing.
    3. Match each queue icon to the best scene blob using multi-angle (0-360 deg)
       and multi-scale Normalized Cross-Correlation template matching.
    """
    try:
        from PIL import Image
        import cv2
        import numpy as np
        import base64
        import io

        q_bytes = base64.b64decode(queue_b64.split(",")[-1])
        s_bytes = base64.b64decode(image_b64.split(",")[-1])

        q_img = Image.open(io.BytesIO(q_bytes))
        s_img = Image.open(io.BytesIO(s_bytes))

        print("[+] Process image...")

        scene = cv2.cvtColor(np.array(s_img.convert("RGB")), cv2.COLOR_RGB2BGR)
        sw, sh = s_img.width, s_img.height

        # Queue alpha extraction
        if "A" in q_img.mode:
            q_alpha = np.array(q_img.split()[-1])
        elif q_img.mode == "LA":
            q_alpha = np.array(q_img.split()[1])
        else:
            q_alpha = 255 - np.array(q_img.convert("L"))

        # Extract target icons from queue (sorted left to right)
        ret, q_thresh = cv2.threshold(q_alpha, 25, 255, cv2.THRESH_BINARY)
        q_cnts, _ = cv2.findContours(q_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        queue_icons = []
        for c in q_cnts:
            x, y, w, h = cv2.boundingRect(c)
            if w >= 5 and h >= 5:
                icon_patch = q_alpha[y:y+h, x:x+w]
                queue_icons.append({'x': x, 'y': y, 'w': w, 'h': h, 'patch': icon_patch, 'cnt': c})

        queue_icons.sort(key=lambda item: item['x'])

        # Fallback to 3 equal slices if contouring found < 3 icons
        if len(queue_icons) < 3:
            queue_icons = []
            qw3 = q_alpha.shape[1] // 3
            for i in range(3):
                slc = q_alpha[:, i*qw3:(i+1)*qw3]
                queue_icons.append({'patch': slc, 'cnt': None, 'x': i*qw3, 'w': qw3, 'h': q_alpha.shape[0]})

        # Segment scene blobs via background subtraction
        bg = cv2.medianBlur(scene, 31)
        diff = cv2.absdiff(scene, bg)
        diff_gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        ret, s_mask = cv2.threshold(diff_gray, 8, 255, cv2.THRESH_BINARY)

        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        closed_mask = cv2.morphologyEx(s_mask, cv2.MORPH_CLOSE, kernel)
        dilated_mask = cv2.dilate(closed_mask, kernel, iterations=1)

        s_cnts, _ = cv2.findContours(dilated_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        scene_blobs = []
        for c in s_cnts:
            x, y, w, h = cv2.boundingRect(c)
            area = cv2.contourArea(c)
            if area > 60 or (w >= 15 and h >= 15):
                M = cv2.moments(c)
                if M['m00'] > 0:
                    cx = int(M['m10'] / M['m00'])
                    cy = int(M['m01'] / M['m00'])
                else:
                    cx, cy = x + w // 2, y + h // 2
                pad = 4
                x0 = max(0, x - pad); y0 = max(0, y - pad)
                x1 = min(scene.shape[1], x + w + pad); y1 = min(scene.shape[0], y + h + pad)
                crop_mask = dilated_mask[y0:y1, x0:x1]
                scene_blobs.append({
                    'cx': cx, 'cy': cy, 'bbox': (x, y, w, h), 'area': area,
                    'mask': crop_mask, 'cnt': c
                })

        if not scene_blobs:
            # Fallback if no blobs detected
            return [
                {"x": sw // 4 - (sw // 4 % 2), "y": sh // 2 - (sh // 2 % 2)},
                {"x": sw // 2 - (sw // 2 % 2), "y": sh // 2 - (sh // 2 % 2)},
                {"x": 3 * sw // 4 - (3 * sw // 4 % 2), "y": sh // 2 - (sh // 2 % 2)}
            ]

        # Multi-angle template correlation
        used_blobs = set()
        matched_coords = []

        for qi_idx, qi in enumerate(queue_icons[:3]):
            q_patch = qi['patch']
            _, q_bin = cv2.threshold(q_patch, 25, 255, cv2.THRESH_BINARY)
            pad = 8
            q_padded = cv2.copyMakeBorder(q_bin, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=0)
            qw, qh = q_padded.shape[1], q_padded.shape[0]

            best_score = -999.0
            best_bi = -1

            for bi, sb in enumerate(scene_blobs):
                if bi in used_blobs and len(used_blobs) < len(scene_blobs):
                    continue
                sb_mask = sb['mask']

                blob_best = -999.0
                for scale in np.linspace(0.8, 2.2, 8):
                    new_w = max(5, int(qw * scale))
                    new_h = max(5, int(qh * scale))
                    resized_q = cv2.resize(q_padded, (new_w, new_h), interpolation=cv2.INTER_AREA)

                    center = (new_w // 2, new_h // 2)
                    for angle in range(0, 360, 15):
                        M = cv2.getRotationMatrix2D(center, angle, 1.0)
                        rot_q = cv2.warpAffine(resized_q, M, (new_w, new_h), flags=cv2.INTER_LINEAR)
                        _, rot_q = cv2.threshold(rot_q, 40, 255, cv2.THRESH_BINARY)

                        pad_blob = cv2.copyMakeBorder(sb_mask, new_h, new_h, new_w, new_w, cv2.BORDER_CONSTANT, value=0)
                        res = cv2.matchTemplate(pad_blob, rot_q, cv2.TM_CCOEFF_NORMED)
                        score = float(np.max(res))
                        if score > blob_best:
                            blob_best = score

                if blob_best > best_score:
                    best_score = blob_best
                    best_bi = bi

            if best_bi == -1:
                for bi in range(len(scene_blobs)):
                    if bi not in used_blobs:
                        best_bi = bi
                        break
                if best_bi == -1:
                    best_bi = 0

            used_blobs.add(best_bi)
            matched_coords.append((scene_blobs[best_bi]['cx'], scene_blobs[best_bi]['cy']))

        while len(matched_coords) < 3:
            matched_coords.append((sw // 2, sh // 2))

        clicks = []
        for cx, cy in matched_coords[:3]:
            fx = int(cx) - (int(cx) % 2)
            fy = int(cy) - (int(cy) % 2)
            fx = max(8, min(fx, sw - 8))
            fy = max(8, min(fy, sh - 8))
            clicks.append({"x": fx, "y": fy})

        print("[+] Done.")
        return clicks

    except ImportError:
        # Pure Python fallback
        try:
            qb = base64.b64decode(queue_b64.split(",")[-1])
            sb = base64.b64decode(image_b64.split(",")[-1])
            qw, qh, q_rgb, q_alpha = decode_png_pure(qb)
            sw, sh, s_rgb, s_alpha = decode_png_pure(sb)

            corner_pixels = []
            margin = 12
            for y in range(min(margin, sh)):
                for x in range(min(margin, sw)):
                    corner_pixels.append(s_rgb[y][x])
                    corner_pixels.append(s_rgb[y][sw - 1 - x])
                    corner_pixels.append(s_rgb[sh - 1 - y][x])
                    corner_pixels.append(s_rgb[sh - 1 - y][sw - 1 - x])

            bg_r = sum(p[0] for p in corner_pixels) / len(corner_pixels)
            bg_g = sum(p[1] for p in corner_pixels) / len(corner_pixels)
            bg_b = sum(p[2] for p in corner_pixels) / len(corner_pixels)

            fg_mask = []
            for y in range(sh):
                row = []
                for x in range(sw):
                    r, g, b = s_rgb[y][x]
                    diff = max(abs(r - bg_r), abs(g - bg_g), abs(b - bg_b))
                    row.append(1 if diff > 25 else 0)
                fg_mask.append(row)

            visited = [[False]*sw for _ in range(sh)]
            blobs = []
            for y in range(0, sh, 2):
                for x in range(0, sw, 2):
                    if fg_mask[y][x] and not visited[y][x]:
                        queue = [(x, y)]
                        visited[y][x] = True
                        pts = []
                        while queue:
                            cx, cy = queue.pop(0)
                            pts.append((cx, cy))
                            for dx, dy in [(-2,0),(2,0),(0,-2),(0,2),(-2,-2),(2,-2),(-2,2),(2,2)]:
                                nx, ny = cx + dx, cy + dy
                                if 0 <= nx < sw and 0 <= ny < sh and fg_mask[ny][nx] and not visited[ny][nx]:
                                    visited[ny][nx] = True
                                    queue.append((nx, ny))
                        if len(pts) >= 12:
                            avg_x = sum(p[0] for p in pts) / len(pts)
                            avg_y = sum(p[1] for p in pts) / len(pts)
                            blobs.append((len(pts), int(avg_x), int(avg_y)))

            blobs.sort(reverse=True)
            merged = []
            used = set()
            for i, (area, bx, by) in enumerate(blobs):
                if i in used:
                    continue
                group = [(area, bx, by)]
                used.add(i)
                for j, (area2, bx2, by2) in enumerate(blobs):
                    if j in used:
                        continue
                    if math.hypot(bx - bx2, by - by2) < 35:
                        group.append((area2, bx2, by2))
                        used.add(j)
                tot_a = sum(g[0] for g in group)
                wx = int(sum(g[0]*g[1] for g in group) / tot_a)
                wy = int(sum(g[0]*g[2] for g in group) / tot_a)
                merged.append((tot_a, wx, wy))

            merged.sort(reverse=True)
            coords = [(bx, by) for (_, bx, by) in merged[:3]]
            while len(coords) < 3:
                coords.append((sw // 2, sh // 2))

            clicks = []
            for (cx, cy) in coords[:3]:
                fx = cx - (cx % 2)
                fy = cy - (cy % 2)
                fx = max(10, min(fx, sw - 10))
                fy = max(10, min(fy, sh - 10))
                clicks.append({"x": fx, "y": fy})
            return clicks
        except Exception:
            return None
    except Exception as e:
        return None


class MyHandler(BaseHTTPRequestHandler):
    # curl "http://127.0.0.1:8080/?nama=Jin&umur=24"

    def do_GET(self):
        # Mendapatkan URL dan parameter GET
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)

        queue_b64 = params.get("queue_b64", ["Guest"])[0]
        image_b64 = params.get("image_b64", ["Guest"])[0]

        result = solve_captcha_accurate(queue_b64, image_b64)

        # Response text
        response = result

        # Mengirim response
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()

        self.wfile.write(response.encode("utf-8"))

server = HTTPServer(("0.0.0.0", 8080), MyHandler)

print("Server berjalan di port 8080...")
server.serve_forever()
