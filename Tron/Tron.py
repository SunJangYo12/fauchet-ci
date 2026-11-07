#!/usr/bin/env python3
"""
T R O N B L O W   ·   N E O N   C L A I M E R   v3.3
Futuristic Auto-Claim Client · Created by Jendela Semesta
"""

import requests, re, time, sys, os, json, random
from datetime import datetime, timedelta

BASE_URL     = "https://tronblow.site"
COOLDOWN     = 70
SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE  = os.path.join(SCRIPT_DIR, "tronblow_config.json")
TYPING_SPEED = 0.012


# ═════════════════════════════════════════════════════════════════════
#  NEON PALETTE  (v3.3: semua abu → putih)
# ═════════════════════════════════════════════════════════════════════
class N:
    RST   = "\033[0m"
    BOLD  = "\033[1m"
    DIM   = "\033[2m"
    ITAL  = "\033[3m"

    CYAN  = "\033[38;5;51m"
    AQUA  = "\033[38;5;45m"
    TEAL  = "\033[38;5;43m"
    MAG   = "\033[38;5;201m"
    PINK  = "\033[38;5;213m"
    LPINK = "\033[38;5;218m"
    PURP  = "\033[38;5;141m"
    LIME  = "\033[38;5;118m"
    GRN   = "\033[38;5;46m"
    YEL   = "\033[38;5;226m"
    ORG   = "\033[38;5;208m"
    RED   = "\033[38;5;196m"
    WHT   = "\033[38;5;231m"
    GRAY  = "\033[38;5;231m"
    DGRAY = "\033[38;5;231m"

    BG_PURP = "\033[48;5;54m"
    BG_BLUE = "\033[48;5;17m"

def c(t, *styles): return "".join(styles) + str(t) + N.RST


# ═════════════════════════════════════════════════════════════════════
#  UTIL
# ═════════════════════════════════════════════════════════════════════
def clear_line():
    sys.stdout.write("\r\033[K"); sys.stdout.flush()

def typewrite_rich(segments, delay=TYPING_SPEED, end="\n"):
    for seg in segments:
        if not seg: continue
        if len(seg) == 1:   text, col, extra = seg[0], None, ""
        elif len(seg) == 2: text, col = seg; extra = ""
        else:               text, col = seg[0], seg[1]; extra = "".join(str(s) for s in seg[2:] if s)
        for ch in text:
            sys.stdout.write((col + extra + ch + N.RST) if col else ch)
            sys.stdout.flush(); time.sleep(delay)
    if end: sys.stdout.write(end); sys.stdout.flush()

def divider():
    print(c("  " + "─" * 46, N.WHT))


def mask_email(email):
    """anbukaskus1@gmail.com  ->  an****@gmail.com"""
    if not email or "@" not in email:
        return "****"
    user, _, domain = email.partition("@")
    shown = user if len(user) <= 2 else user[:2]
    return f"{shown}****@{domain}"


# ═════════════════════════════════════════════════════════════════════
#  BANNER BLOW
# ═════════════════════════════════════════════════════════════════════
def banner_blow():
    text   = N.GRN + N.BOLD
    indent = " " * 6

    print()
    print(c(indent + "   ██████╗ ██╗      ██████╗ ██╗    ██╗", text))
    print(c(indent + "   ██╔══██╗██║     ██╔═══██╗██║    ██║", text))
    print(c(indent + "   ██████╔╝██║     ██║   ██║██║ █╗ ██║", text))
    print(c(indent + "   ██╔══██╗██║     ██║   ██║██║███╗██║", text))
    print(c(indent + "   ██████╔╝███████╗╚██████╔╝╚███╔███╔╝", text))
    print(c(indent + "   ╚═════╝ ╚══════╝ ╚═════╝  ╚══╝╚══╝ ", text))
    print()

    credit = "Created by Jendela Semesta"
    pleft  = (len(indent + "   ██████╗ ██╗      ██████╗ ██╗    ██╗") - len(credit)) // 2
    print(" " * max(pleft, 0) + c(credit, N.WHT, N.BOLD))
    print()


# ═════════════════════════════════════════════════════════════════════
#  SECTION + KV  (v3.3: garis 46 karakter)
# ═════════════════════════════════════════════════════════════════════
def section(title, col=N.CYAN):
    print()
    print("  " + c("▎", N.PURP) + " " + c(title, col, N.BOLD))
    print(c("  " + "─" * 46, N.WHT))

def kv(key, val, ck=N.WHT, cv=N.WHT, indent="  "):
    key_field = f" {key}".ljust(18)
    print(indent + c(key_field, ck) + c(": ", N.WHT) + c(val, cv))


# ═════════════════════════════════════════════════════════════════════
#  TAGS
# ═════════════════════════════════════════════════════════════════════
def tag_ok(msg):   return c(" ● OK ",   N.BG_BLUE, N.CYAN, N.BOLD) + " " + c(msg, N.CYAN)
def tag_err(msg):  return c(" ● ERR ",  N.RED, N.WHT, N.BOLD)     + " " + c(msg, N.RED)
def tag_warn(msg): return c(" ● WARN ", N.ORG, N.WHT, N.BOLD)     + " " + c(msg, N.ORG)
def tag_info(msg): return c(" ● INFO ", N.PURP, N.WHT, N.BOLD)    + " " + c(msg, N.WHT)

def say_ok(m):   print("  " + tag_ok(m))
def say_err(m):  print("  " + tag_err(m))
def say_warn(m): print("  " + tag_warn(m))
def say_info(m): print("  " + tag_info(m))


# ═════════════════════════════════════════════════════════════════════
#  CONFIG
# ═════════════════════════════════════════════════════════════════════
def load_config():
    try:
        with open(CONFIG_FILE) as f: return json.load(f)
    except Exception: return {}

def save_config(d):
    try:
        with open(CONFIG_FILE, "w") as f: json.dump(d, f, indent=2)
        return True
    except Exception: return False


def confirm(prompt):
    try:
        a = input("  " + c("?", N.YEL, N.BOLD) + " "
                  + c(prompt, N.WHT) + " " + c("[y/N]", N.YEL) + " "
                  + c("›", N.CYAN, N.BOLD) + " ").strip().lower()
        return a in ("y", "ya", "yes")
    except (EOFError, KeyboardInterrupt):
        print(); return False


def ask_email():
    cfg = load_config()
    saved = cfg.get("email", "").strip()
    if saved:
        print()
        say_info("Email tersimpan ditemukan:")
        print("    " + c("◈ ", N.PURP) + c(mask_email(saved), N.CYAN, N.BOLD))
        if confirm("Gunakan email ini?"):
            say_ok(f"Email dimuat  ·  {mask_email(saved)}")
            return saved
    while True:
        try:
            val = input("  " + c("▶", N.MAG, N.BOLD) + " "
                        + c("Email FaucetPay", N.WHT, N.BOLD)
                        + " " + c("›", N.WHT) + " ").strip()
        except (EOFError, KeyboardInterrupt):
            print(); sys.exit(0)
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", val):
            say_err("Format email tidak valid."); continue
        say_ok(f"Email OK  ·  {mask_email(val)}")
        if confirm("Simpan untuk sesi berikutnya?"):
            if save_config({"email": val, "saved_at": datetime.now().isoformat()}):
                say_ok(f"Tersimpan  ·  {os.path.basename(CONFIG_FILE)}")
        return val


# ═════════════════════════════════════════════════════════════════════
#  CLIENT
# ═════════════════════════════════════════════════════════════════════
class TronBlowClient:
    def __init__(self, email):
        self.email = email
        self.session = requests.Session()
        self.session.headers.update({
            "host": "tronblow.site",
            "user-agent": ("Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 "
                           "(KHTML, like Gecko) Chrome/139.0.0.0 Mobile Safari/537.36"),
            "accept": ("text/html,application/xhtml+xml,application/xml;q=0.9,"
                       "image/avif,image/webp,image/apng,*/*;q=0.8"),
            "accept-language": "en-US,en;q=0.9,id-ID;q=0.8,id;q=0.7",
            "cache-control": "max-age=0",
            "sec-ch-ua": '"Chromium";v="139", "Not;A=Brand";v="99"',
            "sec-ch-ua-mobile": "?1",
            "sec-ch-ua-platform": '"Android"',
            "upgrade-insecure-requests": "1",
            "origin": BASE_URL,
            "referer": f"{BASE_URL}/",
            "sec-fetch-site": "same-origin",
            "sec-fetch-mode": "navigate",
            "sec-fetch-user": "?1",
            "sec-fetch-dest": "document",
            "content-type": "application/x-www-form-urlencoded",
        })
        self.csrf_token = None
        self.captcha_q = None
        self.captcha_a = None
        self.stats = {"attempts":0,"success":0,"fail":0,"total_sat":0,
                      "start":datetime.now(),"last_payout":"-"}

    def _parse_csrf(self, html):
        for p in [
            r'<input[^>]+name=["\']csrf_token["\'][^>]+value=["\']([^"\']+)["\']',
            r'csrf_token["\']?\s*[:=]\s*["\']([^"\']+)["\']',
        ]:
            m = re.search(p, html, re.IGNORECASE | re.DOTALL)
            if m: return m.group(1)
        return None

    def _parse_captcha(self, html):
        m = re.search(r"What is\s+(\d+)\s*([+\-])\s*(\d+)\s*=", html, re.IGNORECASE)
        if not m: return None, None
        a, op, b = int(m.group(1)), m.group(2), int(m.group(3))
        return f"{a} {op} {b}", (a + b if op == "+" else a - b)

    def _parse_wait(self, html):
        m = re.search(r"Please wait\s+(\d+)m\s+(\d+)s", html)
        if m: return int(m.group(1)) * 60 + int(m.group(2))
        return 0

    def _parse_cooldown_js(self, html):
        m = re.search(r"endAt\s*=\s*(\d+)\s*\*\s*1000", html)
        if not m: return 0
        try:
            left = int((int(m.group(1)) * 1000 - time.time() * 1000) / 1000)
            return max(0, left)
        except Exception: return 0

    def _parse_result(self, html):
        if "Success!" in html and "sent to your FaucetPay" in html:
            pm = re.search(r"Payout\s*#?(\d+)", html)
            am = re.search(r"(\d+)\s*Satoshi\s*TRX", html, re.IGNORECASE)
            return {"success": True,
                    "payout": pm.group(1) if pm else "?",
                    "reward": (am.group(1)+" sat") if am else "1000 sat",
                    "reward_num": int(am.group(1)) if am else 1000,
                    "server_wait": 0}
        m = re.search(r'class="alert alert-error"[^>]*>([^<]+)<', html)
        if m:
            return {"success": False, "reason": m.group(1).strip(),
                    "server_wait": self._parse_wait(html)}
        if "alert-banned" in html:
            return {"success": False, "reason": "BANNED / VPN detected",
                    "server_wait": 0}
        return {"success": False, "reason": "unknown", "server_wait": 0}

    def refresh(self):
        try:
            r = self.session.get(f"{BASE_URL}/", timeout=30)
            #print(r.status_code, r.headers.get("content-encoding"), r.headers.get("server"))
            #with open("debug.html", "w", encoding="utf-8") as f:
            #    f.write(r.text)
            #print(r.text[:500])

            low = r.text.lower()
            if "just a moment" in low or "challenge-platform" in low:
                return False, "cf_challenge"
            self.csrf_token = self._parse_csrf(r.text)
            if not self.csrf_token: return False, "no_csrf"
            self.captcha_q, self.captcha_a = self._parse_captcha(r.text)
            if self.captcha_a is None: return False, "no_captcha"
            return True, "ok"
        except Exception as e:
            return False, f"network:{e}"

    def claim(self):
        self.stats["attempts"] += 1
        data = {"action":"claim","csrf_token":self.csrf_token,
                "website":"","email":self.email,"math_answer":str(self.captcha_a)}
        try:
            r = self.session.post(f"{BASE_URL}/", data=data, timeout=30)
        except Exception:
            self.stats["fail"] += 1
            return {"success":False,"reason":"network","server_wait":0}
        result = self._parse_result(r.text)
        if result["success"]:
            self.stats["success"] += 1
            self.stats["total_sat"] += result.get("reward_num", 0)
            self.stats["last_payout"] = f"#{result.get('payout','?')}"
        else:
            self.stats["fail"] += 1
        self.csrf_token = self._parse_csrf(r.text) or self.csrf_token
        q, a = self._parse_captcha(r.text)
        if a is not None: self.captcha_q, self.captcha_a = q, a
        result["cooldown"] = self._parse_cooldown_js(r.text) or COOLDOWN
        return result


# ═════════════════════════════════════════════════════════════════════
#  RENDER · CLAIM
# ═════════════════════════════════════════════════════════════════════
def render_claim(idx, data):
    divider()
    rail = c("  ▎ ", N.PURP)
    if data.get("success"):
        segments = [
            (rail,),
            ("✅ ", None),
            (f"#{idx:>03}  ", N.WHT),
            (" ▸ CLAIMED ", N.BG_BLUE, N.CYAN, N.BOLD),
            ("   ",),
            (f"+{data.get('reward','?')}", N.LIME, N.BOLD),
            ("   ",),
            ("Sukses!", N.LIME, N.BOLD),
        ]
    else:
        reason = str(data.get("reason","unknown"))
        mapping = {"cf_challenge":"Cloudflare challenge",
                   "no_csrf":"CSRF token missing",
                   "no_captcha":"Captcha missing",
                   "network":"Network failure"}
        msg = mapping.get(reason, reason[:52])
        segments = [
            (rail,),
            ("❌ ", None),
            (f"#{idx:>03}  ", N.WHT),
            (" ▸ FAILED  ", N.RED, N.WHT, N.BOLD),
            ("   ",),
            (msg, N.YEL),
        ]
    typewrite_rich(segments, delay=0.004)


def render_progress(wait):
    bar_len = 36
    for i in range(wait):
        rem = wait - i
        filled = int(bar_len * (i + 1) / wait)
        clear_line()
        sys.stdout.write(
            "  " + c("▎ ", N.PURP) + c("◷ ", N.CYAN, N.BOLD)
            + c("cooldown ", N.WHT)
            + c("▰"*filled, N.CYAN) + c("▱"*(bar_len-filled), N.WHT)
            + "  " + c(f"{rem:>3}s", N.MAG, N.BOLD))
        sys.stdout.flush(); time.sleep(1)
    clear_line()


# ═════════════════════════════════════════════════════════════════════
#  RENDER · STATS
# ═════════════════════════════════════════════════════════════════════
def render_stats(st):
    dur = str(timedelta(seconds=int((datetime.now()-st["start"]).total_seconds())))
    total = st["success"] + st["fail"]
    rate = (st["success"]/total*100) if total else 0

    section("◈  SESSION REPORT  ◈", N.MAG)
    kv("Runtime",      dur,                      N.WHT, N.CYAN)
    kv("Attempts",     str(total),               N.WHT, N.WHT)
    kv("Success",      str(st["success"]),       N.WHT, N.LIME + N.BOLD)
    kv("Failed",       str(st["fail"]),          N.WHT, N.RED)
    kv("Success Rate", f"{rate:>5.1f}%",         N.WHT, N.CYAN + N.BOLD)
    kv("Total Earned", f"{st['total_sat']} sat", N.WHT, N.YEL + N.BOLD)
    kv("Last Payout",  st["last_payout"],        N.WHT, N.PURP)
    print()


# ═════════════════════════════════════════════════════════════════════
#  RENDER · INFO SECTIONS
# ═════════════════════════════════════════════════════════════════════
def show_system_check():
    section("SYSTEM CHECK", N.CYAN)
    kv("Python",   sys.version.split()[0],           N.WHT, N.CYAN)
    kv("Server",   BASE_URL.replace("https://",""),  N.WHT, N.WHT)
    kv("Cooldown", f"~{COOLDOWN}s",                  N.WHT, N.YEL)
    kv("Engine",   "Email + auto math-captcha",      N.WHT, N.PURP)
    kv("Theme",    "Neon Futuristic v3.3",           N.WHT, N.MAG)


def show_auth(email, csrf, captcha_q, captcha_a):
    section("AUTHENTICATION", N.MAG)
    kv("Email",   mask_email(email),           N.WHT, N.CYAN + N.BOLD)
    kv("CSRF",    csrf[:36] + "…",             N.WHT, N.PURP)
    kv("Captcha", f"{captcha_q} = {captcha_a}", N.WHT, N.LIME)


# ═════════════════════════════════════════════════════════════════════
#  MAIN
# ═════════════════════════════════════════════════════════════════════
def main():
    banner_blow()
    show_system_check()

    email = ask_email()

    client = TronBlowClient(email)

    section("HANDSHAKE", N.CYAN)
    print("  " + c("◐ ", N.YEL, N.BOLD) + c("Menghubungi server...", N.WHT),
          end=" ", flush=True)

    ok, reason = client.refresh()
    if not ok:
        print(c("FAILED", N.RED, N.BOLD)); say_err(f"Alasan: {reason}"); return
    print(c("OK sukses terhubung", N.LIME, N.BOLD))

    show_auth(email, client.csrf_token, client.captcha_q, client.captcha_a)

    section("AUTO-CLAIM STREAM", N.CYAN)
    print()

    idx = 0
    try:
        while True:
            idx += 1
            ok, reason = client.refresh()
            if not ok:
                render_claim(idx, {"success": False, "reason": reason})
                say_warn("Refresh gagal · tunggu 15s")
                time.sleep(15); continue
            t0 = time.time()
            data = client.claim()
            elapsed = time.time() - t0
            render_claim(idx, data)
            wait = (COOLDOWN + 3) if data.get("success") else max(data.get("server_wait", 0) + 3, 5)
            render_progress(wait)
    except KeyboardInterrupt:
        pass
    render_stats(client.stats)
    print(c("  ◈  Sesi selesai. Sampai jumpa!", N.MAG, N.BOLD))
    print()


# ═════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(c("\n\n  ◈  Dibatalkan.\n", N.MAG, N.BOLD))
