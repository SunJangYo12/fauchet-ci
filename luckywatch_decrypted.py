import requests
import json
import time
import sys
import os
import io
import base64
import zlib
import struct
import math
import unicodedata
from urllib.parse import urlencode
import ast

def api_captcha(q, s):
    base = "https://minority-era-routine-sounds.trycloudflare.com"

    params = {
        "queue_b64": q,
        "image_b64": s
    }
    url  = f"{base}/?"+urlencode(params)

    print("[+] using api captcha")
    res = requests.get(url)
    print(res.text)

    data = ast.literal_eval(res.text)
    return data


# ========  AUTO LOGIN ========
#from playwright.sync_api import sync_playwright
import json

URL = "https://luckywatch.pro/home"

def sudah_login(page):
    return "/home" in page.url

def ambil_cookie():
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            "./tg_profile",
            channel="chrome",                       # Chrome asli, bukan Chromium bawaan
            headless=False,
            viewport={"width": 740, "height": 540},
            ignore_default_args=["--enable-automation"],
            args=["--disable-blink-features=AutomationControlled"],
        )
        try:
            page = ctx.pages[0] if ctx.pages else ctx.new_page()
            page.goto("https://luckywatch.pro/home")
            page.wait_for_load_state("networkidle")  # tunggu redirect selesai

            if not sudah_login(page):
                print("Belum login, silakan login di jendela...")
                page.wait_for_url("**/home", timeout=300_000)  # tunggu sampai 5 menit
                print("Login berhasil, sesi tersimpan")
            else:
                print("Sudah login.")

                cookies = ctx.cookies("https://luckywatch.pro")      # hanya untuk situs tertentu

                hash_value = next((c["value"] for c in cookies if c["name"] == "hash"), None)
                #print(hash_value)
                return hash_value

                #with open("cookies.json", "w", encoding="utf-8") as f:
                #    json.dump(cookies, f, indent=2)

        finally:
            ctx.close()  # penting: tutup normal supaya sesi tertulis ke disk

# ========  AUTO LOGIN ========



if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    G = Fore.GREEN + Style.BRIGHT
    Y = Fore.RED + Style.BRIGHT
    R = Fore.RED + Style.BRIGHT
    C = Fore.GREEN + Style.BRIGHT
    M = Fore.GREEN + Style.BRIGHT
    W = Fore.GREEN + Style.BRIGHT
    D = Fore.RED + Style.BRIGHT
    RESET = Style.RESET_ALL
except ImportError:
    G = Y = R = C = M = W = D = RESET = ""

WIDTH = 42


def disp_len(s):
    return sum(2 if unicodedata.east_asian_width(ch) in ('W', 'F') else 1 for ch in s)


def _line(inner, width=WIDTH):
    return '│' + inner + ' ' * max(0, width - disp_len(inner)) + '│'


def _rule(char='─', width=WIDTH):
    return '╭' + char * width + '╮'


def _mid(char='─', width=WIDTH):
    return '├' + char * width + '┤'


def _end(char='─', width=WIDTH):
    return '╰' + char * width + '╯'


def display_banner(width=42):
    def center(text):
        pad = max(0, width - disp_len(text))
        left = pad // 2
        return '│' + ' ' * left + text + ' ' * (pad - left) + '│'
    print(W + '╭' + '─' * width + '╮' + RESET)
    print(W + center('LUCKYWATCH BOT') + RESET)
    print(W + '├' + '─' * width + '┤' + RESET)
    print(W + center('🌐 luckywatch.pro') + RESET)
    print(W + center('📱 t.me/chaipiyo') + RESET)
    print(W + '├' + '─' * width + '┤' + RESET)
    print(W + center('made by') + RESET)
    print(W + center('https://bypassallshortlinks.space') + RESET)
    print(W + center('no api for captcha solve') + RESET)
    print(W + '╰' + '─' * width + '╯' + RESET)
    print()


def box(text="", color=""):
    return color + _line(text) + RESET


def box_rule(color="", char='─'):
    return color + _rule(char) + RESET


def box_mid(color="", char='─'):
    return color + _mid(char) + RESET


def box_end(color="", char='─'):
    return color + _end(char) + RESET


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def decode_png_pure(png_bytes):
    idx = 8
    width = height = color_type = 0
    idat_data = bytearray()
    while idx < len(png_bytes):
        length = struct.unpack(">I", png_bytes[idx:idx+4])[0]
        chunk_type = png_bytes[idx+4:idx+8]
        chunk_data = png_bytes[idx+8:idx+8+length]
        idx += 8 + length + 4
        if chunk_type == b'IHDR':
            width, height, _, color_type = struct.unpack(">IIBB", chunk_data[:10])
        elif chunk_type == b'IDAT':
            idat_data.extend(chunk_data)
        elif chunk_type == b'IEND':
            break
    raw = zlib.decompress(idat_data)
    bpp = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}.get(color_type, 3)

    rows_rgb = []
    rows_alpha = []
    prev_row = bytearray(width * bpp)
    raw_idx = 0
    for y in range(height):
        filter_type = raw[raw_idx]; raw_idx += 1
        recon = bytearray(width * bpp)
        row = raw[raw_idx:raw_idx + width * bpp]; raw_idx += width * bpp
        for i in range(width * bpp):
            left = recon[i - bpp] if i >= bpp else 0
            up = prev_row[i]
            diag = prev_row[i - bpp] if i >= bpp else 0
            if filter_type == 0: val = row[i]
            elif filter_type == 1: val = (row[i] + left) & 0xFF
            elif filter_type == 2: val = (row[i] + up) & 0xFF
            elif filter_type == 3: val = (row[i] + ((left + up) >> 1)) & 0xFF
            elif filter_type == 4:
                p = left + up - diag
                pa, pb, pc = abs(p-left), abs(p-up), abs(p-diag)
                pr = left if (pa<=pb and pa<=pc) else (up if pb<=pc else diag)
                val = (row[i] + pr) & 0xFF
            recon[i] = val
        prev_row = recon

        row_rgb = []
        row_a = []
        for x in range(width):
            if bpp == 4:
                r, g, b, a = recon[x*4], recon[x*4+1], recon[x*4+2], recon[x*4+3]
                row_rgb.append((r, g, b))
                row_a.append(a)
            elif bpp == 3:
                r, g, b = recon[x*3], recon[x*3+1], recon[x*3+2]
                row_rgb.append((r, g, b))
                row_a.append(255)
            elif bpp == 2:
                lum, a = recon[x*2], recon[x*2+1]
                row_rgb.append((lum, lum, lum))
                row_a.append(a)
            else:
                lum = recon[x]
                row_rgb.append((lum, lum, lum))
                row_a.append(255)
        rows_rgb.append(row_rgb)
        rows_alpha.append(row_a)
    return width, height, rows_rgb, rows_alpha


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

        q_bytes = base64.b64decode(queue_b64.split(",")[-1])
        s_bytes = base64.b64decode(image_b64.split(",")[-1])


        q_img = Image.open(io.BytesIO(q_bytes))
        s_img = Image.open(io.BytesIO(s_bytes))

        q_img.save("/dev/shm/q.png")
        s_img.save("/dev/shm/s.png")

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



class LuckyWatchBot:
    BASE_URL = "https://luckywatch.pro"
    TASKS_API = f"{BASE_URL}/api/user/tasks/"
    CLAIM_API = f"{BASE_URL}/api/user/captcha/check/"
    USER_API = f"{BASE_URL}/api/user/"
    AUTH_API = f"{BASE_URL}/api/auth/"

    def __init__(self):
        self.session = requests.Session()
        self.email = ""
        self.password = ""
        self.bypass_api_key = ""
        self.session_hash = ""
        self.user_agent = "Mozilla/5.0 (Linux; Android 14; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.6613.127 Mobile Safari/537.36"
        self.balance = 0.0
        self.coins = 0
        self.cur_day = 0
        self.cur_hour = 0
        self.daily_limit = 560
        self.hourly_limit = 65
        self.completed_today = 0
        self.total_earned = 0.0

    def print_banner(self):
        clear_screen()
        display_banner()

    def _parse_and_set_cookies(self, raw_input):
        raw_input = raw_input.strip()
        parsed_cookies = {}
        # Check if user pasted full Cookie header: e.g. "signed=1; hash=085a2...; PHPSESSID=..."
        if "=" in raw_input:
            for item in raw_input.split(";"):
                item = item.strip()
                if "=" in item:
                    k, v = item.split("=", 1)
                    k = k.strip()
                    v = v.strip().replace('"', '').replace("'", "")
                    if k and v:
                        parsed_cookies[k] = v
                        self.session.cookies.set(k, v, domain="luckywatch.pro")

        # Ensure hash is found
        h = parsed_cookies.get("hash") or raw_input.replace('"', '').replace("'", "").strip()
        if h:
            self.session_hash = h
            self.session.cookies.set("hash", h, domain="luckywatch.pro")
            if "signed" not in parsed_cookies:
                self.session.cookies.set("signed", "1", domain="luckywatch.pro")
        return self.session_hash

    def load_config(self):
        self.print_banner()
        cfg_file = "config.json"
        config = {}
        if os.path.exists(cfg_file):
            try:
                with open(cfg_file, "r", encoding="utf-8") as f:
                    config = json.load(f)
            except Exception as e:
                print(f"{R}Config error: {e}{RESET}")

        self.session_hash = config.get("session_hash") or config.get("hash") or ""
        self.user_agent = config.get("user_agent") or self.user_agent
        self.balance = float(config.get("last_balance") or 0.0)

        self.session.headers.update({
            "User-Agent": self.user_agent,
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": self.BASE_URL,
            "Referer": f"{self.BASE_URL}/watch",
            "Sec-Ch-Ua": '"Chromium";v="128", "Not;A=Brand";v="24", "Android WebView";v="128"',
            "Sec-Ch-Ua-Mobile": "?1",
            "Sec-Ch-Ua-Platform": '"Android"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "X-Requested-With": "XMLHttpRequest"
        })

        if not self.session_hash:
            print(box_rule())
            print(box(f"{W}        SETUP"))
            print(box_end() + RESET + "\n")

            while not self.session_hash:
                raw_in = input(f"{G}  → cookie / hash: ").strip()
                #raw_in = ambil_cookie()
                self._parse_and_set_cookies(raw_in)
                if not self.session_hash:
                    print(f"    {R}Cookies cannot be empty!{RESET}")
        else:
            self._parse_and_set_cookies(self.session_hash)

        config["session_hash"] = self.session_hash
        config["hash"] = self.session_hash
        config["user_agent"] = self.user_agent

        with open(cfg_file, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4)

        return True

    def save_session_hash(self, new_hash):
        self._parse_and_set_cookies(new_hash)
        try:
            cfg_file = "config.json"
            config = {}
            if os.path.exists(cfg_file):
                with open(cfg_file, "r", encoding="utf-8") as f:
                    config = json.load(f)
            config["session_hash"] = self.session_hash
            config["hash"] = self.session_hash
            with open(cfg_file, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4)
        except Exception:
            pass

    def _handle_security_check(self, lim_data):
        try:
            udata = lim_data.get("ucheckerData")
            urls = lim_data.get("ucheckerUrls", [])
            if udata and urls:
                for u in urls:
                    try:
                        self.session.post(u, data={"data": udata}, timeout=5)
                    except Exception:
                        pass
        except Exception:
            pass

    def login(self):
        print(f"{G}Checking login...{RESET}")
        try:
            # 1. Initialize IP verification handshake
            self.session.post(self.TASKS_API, data={"method": "checkIp"}, timeout=10)

            # 2. Check limits - this reliably validates login state
            r_lim = self.session.post(self.TASKS_API, data={"method": "getLimits"}, timeout=10)
            try:
                lim_json = r_lim.json()
            except Exception:
                lim_json = {}

            if lim_json.get("status") == "ok":
                lim_data = lim_json.get("data", {})
                self.daily_limit = int(lim_data.get("limDay", 560))
                self.hourly_limit = int(lim_data.get("limHour", 65))
                self._handle_security_check(lim_data)

                # Try to fetch balance info if available
                try:
                    r_u = self.session.post(self.USER_API, data={"method": "getCurrentUser"}, timeout=10)
                    u_info = r_u.json().get("data", {})
                    if u_info.get("balance"):
                        self.balance = float(u_info.get("balance", 0.0))
                    self.coins = int(u_info.get("clover", 0) or 0)
                except Exception:
                    pass

                print(f"{G}Logged in. Limits: {self.hourly_limit}/h, {self.daily_limit}/d{RESET}")
                return True
            else:
                msg = lim_json.get("message")
                print(f"{R}Login failed ({msg or 'noAuth'}). Cookie expired.{RESET}")
        except Exception as e:
            print(f"{R}Check failed: {e}{RESET}")

        # If invalid, prompt user to re-enter
        print(f"\n{R}Enter new cookie / hash:{RESET}")
        self.session_hash = ""
        while not self.session_hash:
            raw_in = input(f"{G}  → cookie / hash: ").strip()
            self._parse_and_set_cookies(raw_in)
        self.save_session_hash(self.session_hash)
        return self.login()

    def fetch_limits(self):
        try:
            r = self.session.post(self.TASKS_API, data={"method": "getLimits"}, timeout=10)
            data = r.json()
            if data.get("status") == "ok":
                lim = data.get("data", {})
                self.daily_limit = int(lim.get("limDay", 560))
                self.hourly_limit = int(lim.get("limHour", 65))
                self._handle_security_check(lim)
        except Exception:
            pass

    def solve_pattern_captcha(self, queue_b64, image_b64):
        return solve_captcha_accurate(queue_b64, image_b64)

    def skip_current_task(self, task_id=None):
        try:
            self.session.post(self.CLAIM_API, data={"refreshTask": "1"}, timeout=10)
        except Exception:
            pass

    def _cooldown(self, seconds=180):
        for rem in range(seconds, 0, -1):
            mins, secs = divmod(rem, 60)
            sys.stdout.write(f"\r  {Y}Wait {W}{mins:02d}m {secs:02d}s...{RESET}  ")
            sys.stdout.flush()
            time.sleep(1)
        print()

    def run(self):
        if not self.load_config():
            return
        if not self.login():
            return

        self.fetch_limits()

        print(box_rule())
        print(box(f"{W} STATUS"))
        print(box_mid())
        bal_str = f"${self.balance:.7f}" if self.balance > 0 else f"${self.balance:.7f} (sync)"
        print(box(f"{W} → Balance : {bal_str}"))
        print(box(f"{W} → Hourly  : {self.hourly_limit}/h"))
        print(box(f"{W} → Daily   : {self.daily_limit}/d"))
        print(box_end() + RESET)

        while True:
            if self.cur_hour >= self.hourly_limit:
                print(f"\n{Y}Hourly limit. Wait 3m...{RESET}")
                self._cooldown(180)
                self.cur_hour = 0
                continue

            if self.cur_day >= self.daily_limit:
                print(f"\n{G}Daily limit done!{RESET}")
                break

            print(f"\n{M}Getting task...{RESET}")
            try:
                self.session.post(self.TASKS_API, data={"method": "checkIp"}, timeout=10)
                r_task = self.session.post(self.TASKS_API, data={"method": "get", "mac": 1}, timeout=15)
                task_resp = r_task.json()
            except Exception as e:
                print(f"{R}Task error: {e}{RESET}")
                time.sleep(5)
                continue

            if task_resp.get("status") != "ok" or not task_resp.get("data"):
                msg = task_resp.get("message") or task_resp.get("error") or "No videos available"
                print(f"{Y}Msg: {W}{msg}{RESET}")
                if any(k in msg.lower() for k in ["limit", "hour", "break"]):
                    print(f"\n{Y}Limit hit. Wait 30m...{RESET}")
                    self._cooldown(1800)
                else:
                    time.sleep(5)
                continue

            task_data = task_resp.get("data", {})
            task_id = task_data.get("id") or task_data.get("TaskId")
            if task_data.get("balance"):
                self.balance = float(task_data.get("balance"))
                self.save_session_hash(self.session_hash)
            raw_duration = int(task_data.get("duration", 15))
            watch_duration = max(16, raw_duration + 3)
            yt_url = task_data.get("href") or task_data.get("link") or "https://www.youtube.com"

            self.cur_day = int(task_data.get("curDay", self.cur_day + 1))
            self.cur_hour += 1

            print(box_rule())
            print(box(f"{W} TASK #{task_id}"))
            print(box_mid())
            print(box(f"{W} → Source : YouTube"))
            print(box(f"{W} → Time   : {watch_duration}s | +$0.00025"))
            sys.stdout.write(box(f"{W} → Watching : {watch_duration:02d}s..."))
            sys.stdout.flush()

            if yt_url.startswith("http"):
                try:
                    self.session.get(yt_url, timeout=10)
                except Exception:
                    pass

            for rem in range(watch_duration, -1, -1):
                sys.stdout.write("\r" + box(f"{W} → Watching : {rem:02d}s..."))
                sys.stdout.flush()
                if rem > 0:
                    time.sleep(1)
            print()
            print(box_end() + RESET)

            time.sleep(1)

            try:
                r_claim = self.session.post(self.CLAIM_API, data={}, timeout=15)
                claim_data = r_claim.json()

                round_num = 1
                print(f"  {G}Solving captcha...{RESET}")
                while claim_data.get("status") == "data" and round_num <= 5:

                    data_obj = claim_data.get("data", {})
                    q_b64 = data_obj.get("queue")
                    img_b64 = data_obj.get("image")

                    if not q_b64 or not img_b64:
                        break

                    #coor = self.solve_pattern_captcha(q_b64, img_b64)
                    coor = api_captcha(q_b64, img_b64)

                    if not coor:
                        break

                    form_data = {
                        "coor[0][x]": str(coor[0]["x"]), "coor[0][y]": str(coor[0]["y"]),
                        "coor[1][x]": str(coor[1]["x"]), "coor[1][y]": str(coor[1]["y"]),
                        "coor[2][x]": str(coor[2]["x"]), "coor[2][y]": str(coor[2]["y"]),
                    }

                    print("COOR:", coor)
                    print("FORM DATA:", form_data)
                    print(json.dumps(form_data, indent=4))

                    time.sleep(0.5)
                    r_sub = self.session.post(self.CLAIM_API, data=form_data, timeout=25)
                    claim_data = r_sub.json()
                    round_num += 1

                status = claim_data.get("status")
                msg = claim_data.get("message", "")

                if status == "ok" or "reward" in claim_data.get("data", {}):
                    earned = float(
                        claim_data.get("reward") or
                        claim_data.get("data", {}).get("reward") or 0.00025
                    )
                    self.completed_today += 1
                    self.total_earned += earned
                    self.balance += earned
                    self.save_session_hash(self.session_hash)

                    print(f"  {G}Counted! {W}(+${earned:.5f} USD){RESET}")
                    print(f"  {G}Balance: {W}${self.balance:.7f} "
                          f"{D}[H:{self.cur_hour}/{self.hourly_limit}] "
                          f"[D:{self.cur_day}/{self.daily_limit}]{RESET}")
                    time.sleep(1)

                elif msg == "limitIsOver" or "limit" in msg.lower():
                    print(f"\n{Y}Limit reached. Wait 3m...{RESET}")
                    self._cooldown(180)

                else:
                    print(f"  {Y}Reply: {W}{msg or status}{RESET}")
                    time.sleep(2)

            except Exception as e:
                print(f"  {R}Error: {e}{RESET}")
                time.sleep(2)

        print(box_rule())
        print(box(f"{W}         DONE"))
        print(box_mid())
        print(box(f"{W}  Videos : {self.completed_today}"))
        print(box(f"{W}  Earned : +${self.total_earned:.5f} USD"))
        print(box(f"{W}  Balance: ${self.balance:.7f} USD"))
        print(box_end() + RESET + "\n")


if __name__ == "__main__":
    try:
        bot = LuckyWatchBot()
        bot.run()
    except KeyboardInterrupt:
        print(f"\n\n{Y}Stopped. Bye!{RESET}\n")
