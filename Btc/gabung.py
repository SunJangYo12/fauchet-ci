#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════╗
║  BTC FAUCET AUTO FARM — NEON Edition v5                      ║
║  Host: btc.zrbtdoma.com | Adexium + GigaPub + Auto Captcha   ║
║  Blacklist provider yang fail 2x, sisa lanjut                ║
╚══════════════════════════════════════════════════════════════╝
"""

import requests, json, time, sys, os, random, re
from urllib.parse import parse_qs, parse_qsl, urlparse, quote

# ═══════════════════ NEON COLORS ═══════════════════
def _c(n): return f"\033[38;5;{n}m"
RED     = _c(196)
GREEN   = _c(118)
YELLOW  = _c(226)
BLUE    = _c(39)
CYAN    = _c(51)
MAGENTA = _c(201)
ORANGE  = _c(208)
PINK    = _c(205)
PURPLE  = _c(129)
WHITE   = _c(231)
GRAY    = _c(245)
AQUA    = _c(87)
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"

# ═══════════════════ HOST CONFIG ═══════════════════
DEFAULT_HOST = "https://btc.zrbtdoma.com"
HOST_CANDIDATES = ["https://btc.zrbtdoma.com"]

GIGA_URL = "https://ad.gigapub.tech/v1/ad"
GIGA_PROJ = "5736"
GIGA_TOKEN = "CEEUHXgZVL184wyaDp6laEchjHQ7RNN3"
UA_TG = ("Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) "
         "Chrome/151.0.7922.199 Mobile Safari/537.36 "
         "Telegram-Android/12.9.1 (Xiaomi M2006C3LG; Android 10; SDK 29; AVERAGE)")
CONFIG_FILE = "btcFaucet.json"
SPINNER_FRAMES = ['⣾', '⣽', '⣻', '⢿', '⡿', '⣟', '⣯', '⣷']

INIT_DATA = ""
BASE_URL = DEFAULT_HOST
REAUTH_PROMPTED = False

# ── Provider blacklist ──
# Setelah fail MAX_FAILS kali dalam 1 sesi farm, provider di-blacklist.
# Gak bakal dicoba lagi sampe farm restart.
FAIL_COUNT = {}       # {provider: jumlah_fail_sesi_ini}
BLACKLISTED = set()   # provider yang udah di-blacklist
MAX_FAILS = 2         # batas fail sebelum blacklist


# ═══════════════════ UTILS ═══════════════════
def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


def timer(seconds, prefix="[!] please wait"):
    wait_time = int(seconds)
    if wait_time < 1:
        return
    frame_delay = 0.1
    current_frame = 0

    try:
        while wait_time > 0:
            start_time = time.time()
            while (time.time() - start_time) < 1:
                h = wait_time // 3600
                m = (wait_time % 3600) // 60
                s = wait_time % 60
                fmt_t = f"{h:02d}:{m:02d}:{s:02d}"
                spinner = SPINNER_FRAMES[current_frame]
                sys.stdout.write(f"\r{WHITE}{prefix}{GREEN} {fmt_t} {CYAN}{spinner}{RESET}   ")
                sys.stdout.flush()
                time.sleep(frame_delay)
                current_frame = (current_frame + 1) % len(SPINNER_FRAMES)
                if (time.time() - start_time) >= 1:
                    break
            wait_time -= 1
    except KeyboardInterrupt:
        sys.stdout.write("\r" + " " * 60 + "\r")
        sys.stdout.flush()
        raise
    sys.stdout.write("\r" + " " * 60 + "\r")
    sys.stdout.flush()


def fmt(n):
    try:
        s = f"{float(n):.8f}".rstrip('0').rstrip('.')
        return s if s else "0"
    except Exception:
        return str(n)


def get_init_user_id(init_data):
    try:
        kv = dict(parse_qsl(init_data, keep_blank_values=True))
        u = json.loads(kv.get('user', '{}'))
        return u.get('id')
    except Exception:
        return None


def reset_fail_tracker():
    global FAIL_COUNT, BLACKLISTED
    FAIL_COUNT = {}
    BLACKLISTED = set()


def mark_fail(prov):
    """Naikin fail count, blacklist kalau udah >= MAX_FAILS."""
    if prov in BLACKLISTED:
        return False
    FAIL_COUNT[prov] = FAIL_COUNT.get(prov, 0) + 1
    if FAIL_COUNT[prov] >= MAX_FAILS:
        BLACKLISTED.add(prov)
        return True  # baru di-blacklist
    return False


def mark_ok(prov):
    """Reset fail count kalau ada yang sukses."""
    if prov in BLACKLISTED:
        return
    FAIL_COUNT[prov] = 0


# ═══════════════════ TELEGRAM WEB INITDATA ═══════════════════
# Samakan BOT/PEER_ID/NAMA_CHAT dengan bot dan chat Mini App milik Anda.
TG_BOT = "fbtc0bot"          # username bot tanpa @
TG_APP = ""                  # short name Mini App; kosong = buka dari tombol chat
TG_START = ""                # startapp opsional
TG_TIMEOUT = 60
TG_PEER_ID = "8735295509"
TG_CHAT_NAME = "BTC Faucet Free Bitcoin"
TG_PROFILE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tg_profile")

TG_WEB_PATCH = r"""
(() => {
  if (location.hash.includes('tgWebAppPlatform=')) {
    const h = location.hash.replace(/tgWebAppPlatform=[^&]*/, 'tgWebAppPlatform=android');
    history.replaceState(null, '', location.pathname + location.search + h);
  }
})();
"""


def cari_init_data(ctx, verbose=False):
    """Ambil initData dari URL/frame atau Telegram WebApp runtime."""
    for pg in ctx.pages:
        for fr in pg.frames:
            if verbose:
                print(f"{GRAY}[TG] frame: {fr.url[:120]}{RESET}")
            try:
                if "tgWebAppData" in fr.url:
                    val = parse_qs(urlparse(fr.url).fragment).get("tgWebAppData")
                    if val and val[0]:
                        return val[0]
            except Exception:
                pass
            try:
                val = fr.evaluate("window.Telegram?.WebApp?.initData")
                if val:
                    return val
            except Exception:
                pass
            try:
                raw = fr.evaluate("sessionStorage.getItem('__telegram__initParams')")
                if raw:
                    val = json.loads(raw).get("tgWebAppData")
                    if val:
                        return val
            except Exception:
                pass
    return None


def masuk_chat_telegram(page):
    try:
        page.wait_for_selector("a.chatlist-chat", timeout=30000)
    except Exception:
        pass
    kandidat = [
        page.locator(f'a.chatlist-chat[data-peer-id="{TG_PEER_ID}"] .peer-title'),
        page.locator("a.chatlist-chat", has_text=TG_CHAT_NAME).locator(".peer-title"),
    ]
    for loc in kandidat:
        try:
            loc.first.click(timeout=5000)
            return True
        except Exception:
            pass
    try:
        search = page.locator(".input-search-input").first
        search.click(timeout=5000)
        search.fill(TG_BOT)
        page.wait_for_timeout(1500)
        page.locator(f'a[data-peer-id="{TG_PEER_ID}"]').first.click(timeout=5000)
        return True
    except Exception:
        return False


def buka_mini_app_telegram(page):
    if TG_APP:
        addr = f"tg://resolve?domain={TG_BOT}&appname={TG_APP}"
        if TG_START:
            addr += f"&startapp={TG_START}"
        page.goto("https://web.telegram.org/k/#?tgaddr=" + quote(addr, safe=""))
    else:
        if not masuk_chat_telegram(page):
            print(f"{YELLOW}[TG] Chat belum terbuka otomatis; silakan buka chat bot di jendela Telegram Web.{RESET}")
        try:
            page.wait_for_selector(
                ".new-message-bot-commands.is-view, button.reply-markup-button.is-web-view",
                timeout=20000,
            )
        except Exception:
            pass
        kandidat = [
            page.locator(".new-message-bot-commands.is-view"),
            page.locator("button.reply-markup-button.is-web-view").last,
            page.locator("button.peer-profile-open-app-button"),
        ]
        for loc in kandidat:
            try:
                loc.first.click(timeout=5000)
                break
            except Exception:
                continue
    try:
        page.get_by_role("button", name=re.compile(r"^(launch|open|confirm)", re.I)).first.click(timeout=4000)
    except Exception:
        pass


def get_initdata_auto():
    """Buka Telegram Web dengan profil persisten dan kembalikan initData di memori."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print(f"{RED}[TG] Playwright belum terpasang. Jalankan: pip install playwright{RESET}")
        print(f"{GRAY}Lalu pasang browser: playwright install chromium{RESET}")
        return None

    ctx = None
    try:
        print(f"{WHITE}[TG] Membuka Telegram Web (profil: {TG_PROFILE_DIR})...{RESET}")
        with sync_playwright() as pw:
            device = pw.devices.get("Pixel 7", {})
            launch_args = ["--window-size=460,800", "--window-position=0,0"]
            kwargs = {
                "user_data_dir": TG_PROFILE_DIR,
                "headless": False,
                "no_viewport": True,
                "args": launch_args,
            }
            if device.get("user_agent"):
                kwargs["user_agent"] = device["user_agent"]
            ctx = pw.chromium.launch_persistent_context(**kwargs)
            ctx.add_init_script(TG_WEB_PATCH)
            page = ctx.pages[0] if ctx.pages else ctx.new_page()
            page.goto("https://web.telegram.org/k/", wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(4000)
            if page.locator("canvas, .qr-container, input[type=tel]").count() > 0:
                print(f"{YELLOW}[TG] Telegram Web belum login. Login di jendela browser yang terbuka; menunggu...{RESET}")
                deadline = time.time() + TG_TIMEOUT
                while time.time() < deadline:
                    try:
                        if page.locator("a.chatlist-chat").count() > 0:
                            break
                    except Exception:
                        pass
                    page.wait_for_timeout(1000)
            buka_mini_app_telegram(page)
            deadline = time.time() + TG_TIMEOUT
            while time.time() < deadline:
                value = cari_init_data(ctx)
                if value:
                    return value
                page.wait_for_timeout(1500)
            print(f"{RED}[TG] initData tidak ditemukan dalam {TG_TIMEOUT} detik.{RESET}")
            cari_init_data(ctx, verbose=True)
            return None
    except Exception as exc:
        print(f"{RED}[TG] Gagal mengambil initData: {type(exc).__name__}: {exc}{RESET}")
        return None
    finally:
        if ctx is not None:
            try:
                ctx.close()
            except Exception:
                pass


# ═══════════════════ CONFIG I/O ═══════════════════
def get_config():
    if not os.path.exists(CONFIG_FILE):
        cfg = {"initData": "", "base_url": DEFAULT_HOST}
        try:
            with open(CONFIG_FILE, "w") as f:
                json.dump(cfg, f, indent=2)
        except Exception as e:
            print(f"{RED}gagal membuat config: {e}{RESET}")
        return cfg
    try:
        with open(CONFIG_FILE) as f:
            cfg = json.load(f)
        return cfg if isinstance(cfg, dict) else {"initData": "", "base_url": DEFAULT_HOST}
    except Exception:
        return {"initData": "", "base_url": DEFAULT_HOST}


def save_config(data):
    try:
        cfg = {}
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE) as f:
                cfg = json.load(f)
        cfg.update(data)
        with open(CONFIG_FILE, "w") as f:
            json.dump(cfg, f, indent=2)
        try:
            if os.name == "posix":
                os.chmod(CONFIG_FILE, 0o600)
        except Exception:
            pass
        return True
    except Exception:
        return False


def save_base_url(url):
    save_config({"base_url": url})


# ═══════════════════ HTTP ═══════════════════
def http_json(url, payload, headers, timeout=20):
    try:
        r = requests.post(url, json=payload, headers=headers, timeout=timeout)
        try:
            j = r.json()
            return j, None, r.text[:500]
        except Exception:
            return None, f"invalid_json_http{r.status_code}", r.text[:500]
    except requests.exceptions.Timeout:
        return None, "timeout", ""
    except requests.exceptions.ConnectionError:
        return None, "connection_failed", ""
    except requests.exceptions.SSLError:
        return None, "ssl_error", ""
    except Exception as e:
        return None, f"net_{type(e).__name__}", ""


def tg_headers(extra=None):
    h = {
        'user-agent': UA_TG,
        'content-type': 'application/json',
        'x-requested-with': 'org.telegram.messenger.web',
        'origin': BASE_URL or DEFAULT_HOST,
        'referer': (BASE_URL or DEFAULT_HOST) + '/',
        'sec-ch-ua': '"Not=A?Brand";v="99", "Android WebView";v="151", "Chromium";v="151"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'accept-language': 'en,id-ID;q=0.9,id;q=0.8'
    }
    if extra:
        h.update(extra)
    return h


# ═══════════════════ HOST DETECT ═══════════════════
def probe_host(url, timeout=8):
    try:
        requests.post(
            url.rstrip('/') + "/api/init",
            json={"initData": INIT_DATA},
            headers={
                'user-agent': UA_TG,
                'content-type': 'application/json',
                'x-requested-with': 'org.telegram.messenger.web',
                'origin': url,
                'referer': url + '/',
            },
            timeout=timeout,
        )
        return True
    except Exception:
        return False


def detect_base_url():
    global BASE_URL
    env_url = os.environ.get("BTC_BASE_URL", "").strip().rstrip('/')
    if env_url:
        print(f"{WHITE}[HOST] test env: {CYAN}{env_url}{RESET}")
        if probe_host(env_url):
            print(f"{WHITE}[HOST] {GREEN}✓ live{RESET}")
            BASE_URL = env_url
            save_base_url(env_url)
            return True
        print(f"{WHITE}[HOST] {RED}✖ unreachable{RESET}")
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE) as f:
                cfg = json.load(f)
            cfg_url = (cfg.get("base_url", "") or "").strip().rstrip('/')
            if cfg_url:
                print(f"{WHITE}[HOST] test cached: {CYAN}{cfg_url}{RESET}")
                if probe_host(cfg_url):
                    print(f"{WHITE}[HOST] {GREEN}✓ live{RESET}")
                    BASE_URL = cfg_url
                    return True
                print(f"{WHITE}[HOST] {RED}✖ unreachable{RESET}")
    except Exception:
        pass
    for url in HOST_CANDIDATES:
        url = url.rstrip('/')
        print(f"{WHITE}[HOST] probe {CYAN}{url}{RESET}...")
        if probe_host(url):
            print(f"{WHITE}[HOST] {GREEN}✓ live{RESET}")
            BASE_URL = url
            save_base_url(url)
            return True
        print(f"{WHITE}[HOST] {RED}✖ unreachable{RESET}")
    return False


# ═══════════════════ AUTH DETECTION ═══════════════════
def classify_response(j, raw):
    if not isinstance(j, dict):
        return "other"
    msg = (str(j.get('detail', '')) + ' ' +
           str(j.get('message', '')) + ' ' +
           str(j.get('error', ''))).lower()
    if 'initdata' in msg or 'session expired' in msg or 'unauthorized' in msg or 'invalid init' in msg:
        return "auth"
    if 'captcha' in msg:
        return "captcha"
    if 'user' in j:
        return "ok"
    if j.get('success') or j.get('status') == 'success':
        return "ok"
    if j.get('status') == 'ad_required':
        return "ok"
    return "other"


def build_init_payload(init_data):
    return {
        "initData": init_data,
        "start_param": None,
        "fingerprint": "aabbccddeeff00112233445566778899",
        "ua": UA_TG,
        "screen": "412x915",
        "lang": "id",
        "tz": "Asia/Jakarta",
        "platform": "Linux armv81",
        "tg_platform": "android",
        "viewport_width": 412,
        "viewport_height": 891,
        "max_touch_points": 5,
        "device_pixel_ratio": 2.625
    }


def validate_initdata(init_data):
    j, err, raw = http_json(BASE_URL + "/api/init", build_init_payload(init_data), tg_headers())
    if err:
        print(f"{RED}[AUTH] validasi gagal: {err}{RESET}")
        return None
    if isinstance(j, dict) and isinstance(j.get("user"), dict):
        return j
    detail = j.get("detail") or j.get("message") or j.get("error") or "respons tidak valid" if isinstance(j, dict) else "respons tidak valid"
    print(f"{RED}[AUTH] initData baru ditolak server: {detail}{RESET}")
    return None


def refresh_initdata(reason="", force=False):
    global INIT_DATA, REAUTH_PROMPTED
    if REAUTH_PROMPTED and not force:
        print(f"{WHITE}[AUTH] refresh sudah dicoba; pilih menu [3] untuk mencoba lagi{RESET}")
        return False
    old_uid = get_init_user_id(INIT_DATA)
    print()
    if reason:
        print(f"{YELLOW}[AUTH] alasan: {reason}{RESET}")
    if old_uid:
        print(f"{WHITE}[AUTH] akun saat ini: user_id={CYAN}{old_uid}{RESET}")
    REAUTH_PROMPTED = True
    new = get_initdata_auto()
    if not new:
        print(f"{RED}[AUTH] tidak memperoleh initData dari Telegram Web.{RESET}")
        return False
    new_uid = get_init_user_id(new)
    if not new_uid:
        print(f"{RED}[AUTH] initData tidak berisi user_id; dibatalkan.{RESET}")
        return False
    if old_uid and new_uid and old_uid != new_uid:
        print(f"{RED}[AUTH] akun berbeda! lama={old_uid}, baru={new_uid}. Token tidak disimpan.{RESET}")
        return False

    print(f"{WHITE}[AUTH] memvalidasi initData baru...{RESET}")
    checked = validate_initdata(new)
    if not checked:
        return False
    if not save_config({"initData": new}):
        print(f"{RED}[AUTH] gagal menyimpan {CONFIG_FILE}; token tidak diaktifkan.{RESET}")
        return False
    INIT_DATA = new
    REAUTH_PROMPTED = False
    user = checked.get("user", {})
    print(f"{GREEN}[AUTH] ✓ initData berhasil diperbarui untuk user_id={new_uid}; balance {fmt(user.get('balance', 0))} sat{RESET}")
    return True


# ═══════════════════ API ═══════════════════
def api(path, extra=None, allow_reauth=True):
    global INIT_DATA, BASE_URL
    r = None
    last_err = None
    for attempt in range(2):
        payload = {"initData": INIT_DATA}
        if extra:
            payload.update(extra)
        j, err, raw = http_json(BASE_URL + path, payload, tg_headers())
        if err:
            last_err = err
            if err == "connection_failed" and attempt == 0:
                print(f"{WHITE}[NET] {YELLOW}koneksi gagal — re-probe host...{RESET}")
                if detect_base_url():
                    continue
            return {"status": "error", "detail": err}
        kind = classify_response(j, raw)
        if kind == "auth":
            if allow_reauth and attempt == 0:
                reason = j.get('detail') or j.get('message') or "auth error"
                print(f"{WHITE}[AUTH] {YELLOW}server bilang: {reason}{RESET}")
                if refresh_initdata(reason=reason):
                    continue
            return {"status": "error", "detail": "initData expired"}
        return j
    return r if r else {"status": "error", "detail": last_err or "unknown"}


def giga_call(body):
    extra = {
        'authorization': 'Bearer ' + GIGA_TOKEN,
        'project-id': GIGA_PROJ
    }
    j, err, _ = http_json(GIGA_URL, body, tg_headers(extra))
    if err:
        return {"status": "error", "detail": err}
    return j


def giga_user():
    global INIT_DATA
    try:
        p = parse_qs(INIT_DATA)
        u = json.loads(p.get('user', ['{}'])[0])
    except Exception:
        u = {}
    return {'user': u, 'platform': 'android', 'version': '9.6', 'start_param': None}


# ═══════════════════ GETTERS ═══════════════════
def get_state():
    r = api("/api/tasks/ads/state", allow_reauth=True)
    if isinstance(r, dict):
        return r.get('tasks', []) or []
    return []


def get_init(allow_reauth=True):
    global INIT_DATA
    payload = build_init_payload(INIT_DATA)
    for attempt in range(2):
        # Refresh dapat mengganti INIT_DATA di tengah loop; retry harus memakai token baru.
        payload["initData"] = INIT_DATA
        j, err, raw = http_json(BASE_URL + "/api/init", payload, tg_headers())
        if err:
            return {"status": "error", "detail": err}
        kind = classify_response(j, raw)
        if kind == "auth":
            if allow_reauth and attempt == 0:
                reason = j.get('detail') or j.get('message') or "auth error"
                print(f"{WHITE}[AUTH] {YELLOW}server bilang: {reason}{RESET}")
                if refresh_initdata(reason=reason):
                    continue
            return {"status": "error", "detail": "initData expired"}
        return j
    return j


# ═══════════════════ CAPTCHA ═══════════════════
def captcha_answer(ch):
    prompt_raw = str(ch.get('prompt', ''))
    prompt = re.sub(r'[^a-zA-Z ]', '', prompt_raw).lower().strip()
    m = re.search(r'the (\w+)', prompt)
    if m:
        want = m.group(1)
    else:
        want = prompt.replace('tap ', '').strip()
    options = ch.get('options', []) or []
    for o in options:
        oid = str(o.get('id', '')).lower()
        olabel = str(o.get('label', '')).lower()
        if oid == want or olabel == want:
            return o.get('id', '')
    return ''


def detect_and_solve_captcha():
    j = get_init(allow_reauth=True)
    if not isinstance(j, dict):
        return False
    if j.get('detail') == 'initData expired':
        print(f"{WHITE}[AUTH] {RED}initData expired — pilih menu [3] buat refresh{RESET}")
        return False
    u = j.get('user', {}) or {}
    required = bool(u.get('captcha_required', False))
    ch = u.get('captcha_challenge')
    if not required and not ch:
        return True
    if ch:
        prompt = ch.get('prompt', '?')
        ans = captcha_answer(ch)
        if ans == '':
            print(f"{WHITE}[CAPTCHA] {RED}jawaban gak ketemu utk '{prompt}'{RESET}")
            return False
        print(f"{WHITE}[CAPTCHA] {YELLOW}solve '{prompt}' -> {ans}...{RESET}")
        r = api("/api/captcha/verify", {
            "challenge_id": ch.get('challenge_id', ''),
            "answer": ans,
        })
        if isinstance(r, dict) and r.get('status') == 'success':
            print(f"{WHITE}[CAPTCHA] {GREEN}✔ solved{RESET}")
            return True
        msg = 'gagal'
        if isinstance(r, dict):
            msg = r.get('detail') or r.get('message') or 'gagal'
        print(f"{WHITE}[CAPTCHA] {RED}{msg}{RESET}")
        return False
    if required and not ch:
        return False
    return True


# ═══════════════════ TASK HANDLERS ═══════════════════
def handle_gigapub(sid, st):
    tg = giga_user()
    giga_call({'method': 'init', 'args': {'user': tg}, 'version': 'v85', 'seconds': 9.9})

    uniq = f"{random.randint(100000000, 999999999)}.{random.randint(100000, 999999)}"
    any_data = {
        'showDone': True,
        'fallPriorityList': ['rich', 'rD', 't', 'd', 'monetag', 'm1', 'o1', 'rB'],
        'fallRotationType': 'priority',
        'showCounter': 0,
        'showTryCounter': 0,
        'uniqShowId': uniq,
        'readyNetsCount': 4,
        'showTag': None
    }
    base = {'user': tg, 'placementId': 'main', 'transactionId': None, 'version': 'v85'}

    r1 = giga_call({'method': 'adShowTryStart', 'args': {
        **base, 'network': 't', 'rotationType': 'priority',
        'showCounter': 0, 'anyData': any_data}})
    if isinstance(r1, dict) and r1.get('status') == 'error':
        return False, f"giga_try1: {r1.get('detail', 'fail')}"

    time.sleep(4)

    any2 = dict(any_data); any2['showDone'] = False; any2['showTryCounter'] = 1
    r2 = giga_call({'method': 'adShowed', 'args': {
        **base, 'network': 't', 'rotationType': 'priority',
        'showCounter': 0, 'seconds': 18.7, 'anyData': any2}})
    if isinstance(r2, dict) and r2.get('status') == 'error':
        return False, f"giga_showed: {r2.get('detail', 'fail')}"

    any3 = dict(any_data); any3['showCounter'] = 1; any3['showTryCounter'] = 2
    r3 = giga_call({'method': 'adShowTryStart', 'args': {
        **base, 'network': 'd', 'rotationType': 'priority',
        'showCounter': 1, 'anyData': any3}})
    if isinstance(r3, dict) and r3.get('status') == 'error':
        return False, f"giga_try2: {r3.get('detail', 'fail')}"

    time.sleep(4)

    any4 = dict(any3); any4['showDone'] = True
    r4 = giga_call({'method': 'adShowedX', 'args': {
        **base, 'network': 'd', 'rotationType': 'priority',
        'showCounter': 2, 'seconds': 32.8, 'anyData': any4}})
    if isinstance(r4, dict) and r4.get('status') == 'error':
        return False, f"giga_showedX: {r4.get('detail', 'fail')}"

    return True, None


def handle_adexium(sid, st):
    time.sleep(2)
    return True, None


def confirm_with_retry(sid, prov, max_retry=3):
    cf = None
    for i in range(max_retry):
        cf = api("/api/tasks/ads/confirm", {"session_uid": sid})
        if not isinstance(cf, dict):
            return None

        status = cf.get('status', '')

        if status in ('success', 'already_confirmed'):
            return cf

        if status in ('ad_required', 'pending_postback'):
            if i < max_retry - 1:
                wait = 3 + i * 2
                print(f"{WHITE}[{CYAN}{prov}{WHITE}] {YELLOW}{status} — retry confirm {i+1}/{max_retry} dalam {wait}s{RESET}")
                time.sleep(wait)
                continue
            return cf

        return cf

    return cf


# ═══════════════════ FARM ═══════════════════
def do_farm():
    notified_limit = {}
    captcha_retries = 0
    state_retry = 0

    # Reset fail tracker tiap kali farm baru dimulai
    reset_fail_tracker()

    while True:
        tasks = get_state()

        if not tasks:
            state_retry += 1
            if captcha_retries < 3:
                print(f"{WHITE}[STATE] {YELLOW}kosong — cek captcha...{RESET}")
                if detect_and_solve_captcha():
                    tasks = get_state()
                    if tasks:
                        captcha_retries = 0
                        state_retry = 0
                    else:
                        timer(10, "  retry...")
                        continue
                else:
                    captcha_retries += 1
                    if captcha_retries >= 3:
                        print(f"{WHITE}[STATE] {RED}captcha gagal 3x — mundur 60s{RESET}")
                        captcha_retries = 0
                        timer(60, "  retry...")
                        continue
                    timer(5, "  retry...")
                    continue
            else:
                timer(30, "  retry...")
                continue
        else:
            captcha_retries = 0
            state_retry = 0

        busy = 0
        tried_any = False
        claimed = False
        all_providers_dead = True  # track kalau semua provider udah blacklist/limit

        for t in tasks:
            prov = t.get('provider', '')
            if prov not in ('adexium', 'gigapubs'):
                continue

            # ── BLACKLIST check ──
            if prov in BLACKLISTED:
                continue

            rem = int(t.get('remaining_today', 0))
            cdl = int(t.get('cooldown_left', 0))
            cds = int(t.get('cooldown_seconds', 300))

            if rem <= 0:
                if not notified_limit.get(prov):
                    print(f"{WHITE}[{CYAN}{prov}{WHITE}] {YELLOW}limit habis, skip{RESET}")
                    notified_limit[prov] = True
                continue

            if cdl > 0:
                busy = max(busy, cdl)
                all_providers_dead = False  # masih ada harapan, cuma cooldown
                continue

            tried_any = True
            all_providers_dead = False

            # ── 1. Start ──
            st = api("/api/tasks/ads/start", {"provider": prov, "interaction": None},
                     allow_reauth=True)

            if isinstance(st, dict):
                msg = str(st.get('detail', '')) + ' ' + str(st.get('message', ''))
                if 'captcha' in msg.lower():
                    print(f"{WHITE}[{CYAN}{prov}{WHITE}] {YELLOW}server minta captcha...{RESET}")
                    if detect_and_solve_captcha():
                        st = api("/api/tasks/ads/start", {"provider": prov, "interaction": None})

            sid = st.get('session_uid', '') if isinstance(st, dict) else ''
            if not sid:
                msg = 'start gagal'
                if isinstance(st, dict):
                    msg = st.get('detail') or st.get('message') or 'start gagal'
                print(f"{WHITE}[{CYAN}{prov}{WHITE}] {RED}{msg} — skip lanjut{RESET}")
                new_blacklist = mark_fail(prov)
                if new_blacklist:
                    print(f"{WHITE}[{CYAN}{prov}{WHITE}] {ORANGE}{BOLD}✖ BLACKLISTED (fail {MAX_FAILS}x) — stop provider ini{RESET}")
                continue

            # ── 2. Handle per-provider ──
            if prov == 'gigapubs':
                ok, err = handle_gigapub(sid, st)
            elif prov == 'adexium':
                ok, err = handle_adexium(sid, st)
            else:
                ok, err = True, None

            if not ok:
                print(f"{WHITE}[{CYAN}{prov}{WHITE}] {RED}bypass fail: {err} — skip lanjut{RESET}")
                new_blacklist = mark_fail(prov)
                if new_blacklist:
                    print(f"{WHITE}[{CYAN}{prov}{WHITE}] {ORANGE}{BOLD}✖ BLACKLISTED (fail {MAX_FAILS}x) — stop provider ini{RESET}")
                continue

            # ── 3. Confirm dengan retry ──
            cf = confirm_with_retry(sid, prov, max_retry=3)
            status = cf.get('status', '') if isinstance(cf, dict) else ''

            if status in ('success', 'already_confirmed'):
                amt = cf.get('reward_sats', 0.2)
                nb = cf.get('new_balance', '?')
                used = int(cf.get('used_today', 0))
                remaining = int(cf.get('remaining_today', rem))
                c = int(cf.get('cooldown', cds))
                print(f"{WHITE}[{MAGENTA}{prov}{WHITE}] "
                      f"+{GREEN}{BOLD}{fmt(amt)}{RESET}{WHITE} sat - "
                      f"{CYAN}{used}/{used + remaining}{WHITE} - balance "
                      f"{AQUA}{fmt(nb)}{WHITE} sat{RESET}")
                busy = max(busy, c)
                claimed = True
                mark_ok(prov)  # reset counter
                timer(random.randint(8, 10), "  wait...")

            elif status in ('ad_required', 'pending_postback'):
                # Bukan fatal, cuma belum siap. Skip aja, tapi jangan blacklist.
                print(f"{WHITE}[{MAGENTA}{prov}{WHITE}] {YELLOW}{status} — skip lanjut{RESET}")

            else:
                msg = 'gagal'
                if isinstance(cf, dict):
                    msg = cf.get('detail') or cf.get('message') or status or 'gagal'
                print(f"{WHITE}[{MAGENTA}{prov}{WHITE}] {RED}{msg} — skip lanjut{RESET}")
                new_blacklist = mark_fail(prov)
                if new_blacklist:
                    print(f"{WHITE}[{MAGENTA}{prov}{WHITE}] {ORANGE}{BOLD}✖ BLACKLISTED (fail {MAX_FAILS}x) — stop provider ini{RESET}")

        # ── End for loop ──

        # Kalau semua provider udah blacklist / limit → STOP
        active_providers = [p for p in ('adexium', 'gigapubs')
                            if p not in BLACKLISTED]

        # Cek apakah masih ada provider yang aktif DAN punya sisa
        has_alive = False
        for t in tasks:
            prov = t.get('provider', '')
            if prov not in ('adexium', 'gigapubs'):
                continue
            if prov in BLACKLISTED:
                continue
            rem = int(t.get('remaining_today', 0))
            if rem > 0:
                has_alive = True
                break

        if not has_alive:
            if BLACKLISTED:
                bl_list = ', '.join(BLACKLISTED)
                print(f"{WHITE}{ORANGE}semua provider sisa habis / blacklisted [{bl_list}] — bot stop{RESET}")
            else:
                print(f"{WHITE}semua limit hari ini, exit...{RESET}")
            return

        if busy > 0:
            timer(busy, "  next...")
            continue
        if not tried_any:
            # Semua provider aktif tapi lagi cooldown / sedang gak bisa
            print(f"{WHITE}semua provider cooldown — tunggu 30s{RESET}")
            timer(30, "  retry...")
            continue
        if claimed:
            timer(5, "  wait...")
            continue
        timer(20, "  retry...")


# ═══════════════════ MENU ═══════════════════
def show_account_info():
    detect_and_solve_captcha()
    ib = get_init()

    if isinstance(ib, dict) and 'user' in ib:
        u = ib['user']
        acc = ib.get('access', {}) or {}
        print(f"{WHITE}balance    : {AQUA}{BOLD}{fmt(u.get('balance', 0))}{RESET}{WHITE} sat{RESET}")
        print(f"{WHITE}cooldown   : {CYAN}{u.get('cooldown', 0)}s{RESET}")
        cap_stat = f"{YELLOW}required{RESET}" if u.get('captcha_required') else f"{GREEN}ok{RESET}"
        print(f"{WHITE}captcha    : {cap_stat}{RESET}")
        if acc.get('mobile_only_blocked'):
            print(f"{WHITE}status     : {RED}{BOLD}MOBILE ONLY BLOCKED{RESET}")
        elif u.get('is_blocked'):
            print(f"{WHITE}status     : {RED}BLOCKED ({u.get('ban_reason', '?')}){RESET}")
        else:
            print(f"{WHITE}status     : {GREEN}clean{WHITE} "
                  f"(risk {YELLOW}{u.get('risk_level', '?')}{WHITE} "
                  f"{CYAN}{u.get('risk_score', '?')}{WHITE}){RESET}")
    else:
        detail = '?'
        if isinstance(ib, dict):
            detail = ib.get('detail') or ib.get('message') or '?'
        print(f"{WHITE}balance    : {RED}gagal fetch ({detail}){RESET}")

    tasks = get_state()
    if tasks:
        print(f"{PURPLE}{BOLD}-- tasks --{RESET}")
        for t in tasks:
            prov = t.get('provider', '')
            if prov not in ('adexium', 'gigapubs'):
                continue
            used = int(t.get('daily_cap', 0)) - int(t.get('remaining_today', 0))
            cap = t.get('daily_cap', '?')
            rew = t.get('reward_sats', '?')
            cdl = t.get('cooldown_left', '?')
            bl_tag = f" {RED}[BLACKLISTED]{RESET}" if prov in BLACKLISTED else ""
            fail_tag = ""
            if prov in FAIL_COUNT and FAIL_COUNT[prov] > 0 and prov not in BLACKLISTED:
                fail_tag = f" {ORANGE}[fail {FAIL_COUNT[prov]}/{MAX_FAILS}]{RESET}"
            print(f"{MAGENTA}{prov:<10}{WHITE}: {CYAN}{used}/{cap}{WHITE} | "
                  f"reward {GREEN}{rew}{WHITE} sat | cooldown {YELLOW}{cdl}s{RESET}{bl_tag}{fail_tag}")
    else:
        print(f"{WHITE}tasks      : {RED}gagal fetch state{RESET}")


def manual_refresh_init():
    """Menu [3]: jalankan pengambilan initData otomatis dari Telegram Web."""
    return refresh_initdata(reason="refresh manual dari menu [3]", force=True)


# ═══════════════════ BANNER ═══════════════════
def print_banner():
    print(f"{CYAN}╔═══════════════════════════════════════════════════╗{RESET}")
    print(f"{CYAN}║{RESET}  {MAGENTA}{BOLD}⚡ BTC FAUCET AUTO FARM{RESET} {WHITE}|{RESET} {YELLOW}Bypass ADS{RESET}          {CYAN}║{RESET}")
    print(f"{CYAN}╚═══════════════════════════════════════════════════╝{RESET}")
    print(f"{PINK} ✦ ScriptMaker : {GREEN}{BOLD}MoneyMaker_w{RESET}")
    print(f"{PINK} ✦ Join Grup   : {AQUA}https://t.me/+f3QBLkR5D8k4YzNl{RESET}")
    print(f"{PINK} ✦ {YELLOW}Bypass Ad And Captcha{RESET}")
    print(f"{CYAN}═════════════════════════════════════════════════════{RESET}")


# ═══════════════════ MAIN ═══════════════════
def main():
    global INIT_DATA, BASE_URL, REAUTH_PROMPTED
    clear()
    config = get_config()
    INIT_DATA = (config.get('initData', '') or '').strip()
    cfg_url = (config.get('base_url', '') or '').strip().rstrip('/')
    BASE_URL = cfg_url if cfg_url else DEFAULT_HOST

    if not INIT_DATA:
        print(f"{YELLOW}[INIT] initData kosong; mengambil otomatis dari Telegram Web...{RESET}")
        if not refresh_initdata(reason="initData belum tersedia", force=True):
            print(f"{RED}Tidak bisa melanjutkan tanpa initData valid.{RESET}")
            return

    cur_uid = get_init_user_id(INIT_DATA)
    print(f"{WHITE}[INIT] host: {GREEN}{BASE_URL}{RESET}")
    print(f"{WHITE}[INIT] user_id: {CYAN}{cur_uid or '?'}{RESET}")
    time.sleep(0.7)

    while True:
        REAUTH_PROMPTED = False
        clear()
        print_banner()
        print(f"{WHITE}host           : {GREEN}{BASE_URL}{RESET}")
        print(f"{WHITE}user_id        : {CYAN}{get_init_user_id(INIT_DATA) or '?'}{RESET}")

        try:
            tasks = get_state()
        except Exception:
            tasks = []

        if tasks:
            total_used = 0
            total_cap = 0
            for t in tasks:
                prov = t.get('provider', '')
                if prov not in ('adexium', 'gigapubs'):
                    continue
                total_cap += int(t.get('daily_cap', 0))
                total_used += int(t.get('daily_cap', 0)) - int(t.get('remaining_today', 0))
            print(f"{WHITE}task progress  : {CYAN}{total_used}{WHITE}/{CYAN}{total_cap}{RESET}")
        else:
            print(f"{WHITE}task progress  : {RED}offline{RESET}")
            print(f"{GRAY}  → kalau sering offline, cek menu [3] refresh initData{RESET}")

        print()
        print(f"  {GREEN}[1]{RESET} {CYAN}{BOLD}Start Farm{RESET}   {DIM}(Adexium + GigaPubs){RESET}")
        print(f"  {GREEN}[2]{RESET} {CYAN}{BOLD}Cek Akun{RESET}     {DIM}(balance + tasks){RESET}")
        print(f"  {GREEN}[3]{RESET} {CYAN}{BOLD}Auto-refresh initData (Telegram Web){RESET}")
        print(f"  {GREEN}[4]{RESET} {CYAN}{BOLD}Re-probe Host{RESET}")
        print(f"  {RED}[0]{RESET} {RED}{BOLD}Exit{RESET}")
        print()

        # langsung cli
        do_farm()
        exit()


        print(f"{MAGENTA}❯{RESET} {YELLOW}pilih:{RESET} ", end="")

        try:
            opt = input().strip()
        except EOFError:
            opt = '0'

        if opt == '1':
            do_farm()
            print(f"\n{WHITE}enter untuk kembali...{RESET}", end="")
            try: input()
            except EOFError: pass

        elif opt == '2':
            print()
            show_account_info()
            print(f"\n{WHITE}enter untuk kembali...{RESET}", end="")
            try: input()
            except EOFError: pass

        elif opt == '3':
            print()
            manual_refresh_init()
            print(f"\n{WHITE}enter untuk kembali...{RESET}", end="")
            try: input()
            except EOFError: pass

        elif opt == '4':
            print()
            print(f"{WHITE}re-probe host...{RESET}")
            if detect_base_url():
                print(f"{GREEN}✓ host aktif: {BASE_URL}{RESET}")
            else:
                print(f"{RED}✖ gak ada host yang hidup{RESET}")
            print(f"\n{WHITE}enter untuk kembali...{RESET}", end="")
            try: input()
            except EOFError: pass

        elif opt == '0':
            clear()
            print(f"{GREEN}✦ Bye bro.{RESET}\n")
            return
        else:
            print(f"{RED}  ✖ pilihan invalid{RESET}")
            time.sleep(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{RED}Dihentikan.{RESET}")
    except Exception as e:
        print(f"\n{RED}Fatal error: {e}{RESET}")
