#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FarmBuddies Auto Claim — HACKER EDITION (Aligned Menu + Beep MP3 + Rank + Bintang + Kembali)
"""

import os
import sys
import json
import time
import re
import base64
import random
import string
import uuid
import signal
import threading
import urllib.parse
import traceback
import urllib3
from datetime import datetime

# --- FIX ERROR EMOJI DI TERMUX ---
try:
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
    if sys.stderr.encoding != 'utf-8':
        sys.stderr.reconfigure(encoding='utf-8')
except AttributeError:
    pass

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

try:
    import requests
except ImportError:
    print("Library 'requests' belum ada. Menginstall otomatis...")
    os.system("pip install requests")
    import requests

# ═══════════════════════════════════════════════════════════════════════════
# KONSTANTA & THEME
# ═══════════════════════════════════════════════════════════════════════════
CONFIG_FILE       = "config.json"
DEFAULT_BASE_URL  = "https://farm-buddies-api.nhathaybip2000.workers.dev/api"
DASHBOARD_MS      = 1000

RST  = "\033[0m"
BOLD = "\033[1m"
def fg(c): return f"\033[38;5;{c}m"

C_HDR_1, C_HDR_2 = 51, 213
C_ACCENT         = 226
C_OK, C_WARN, C_ERR = 46, 208, 196
C_DIM, C_TEXT, C_SUB = 240, 252, 245

HACK_GREEN  = 46
HACK_CYAN   = 51
HACK_DIM    = 255
HACK_YELLOW = 226
HACK_PINK   = 218
HACK_ORANGE = 214
HACK_PASTEL_GREEN = 121 
HACK_BLUE   = 39 
SOFT_BLUE   = 117  # biru soft/pastel

# --- RATING BINTANG PER BIBIT (edit sesuai selera) ---
CROP_STARS = {
    "wheat":    5,
    "carrot":   5,
    "corn":     4,
    "tomato":   5,
    "eggplant": 3,
    "pumpkin":  4,
}

def get_crop_stars(cid):
    """Ambil rating bintang crop. Default 3 jika tidak terdaftar."""
    return "🌟" * CROP_STARS.get(cid, 3)
# -----------------------------------------------------

def clear_screen():
    sys.stdout.write("\033[2J\033[H\033[3J")
    sys.stdout.flush()

# --- TAMBAHAN SUARA MP3 KOIN ---
def play_beep():
    """Fungsi untuk memutar file koin.mp3 di background"""
    def play_sound():
        try:
            os.system('termux-media-player play koin.mp3 > /dev/null 2>&1')
        except Exception:
            pass
    threading.Thread(target=play_sound, daemon=True).start()
# -------------------------------






# =============== TAMBAHAN AUTO LOGIN ===============
import json, re, time
from urllib.parse import urlparse, parse_qs, quote
from playwright.sync_api import sync_playwright

BOT = "FarmBuddiesBot"        # username bot, tanpa @
APP = ""               # short name Mini App (kosong kalau pakai tombol di chat)
START = ""             # parameter startapp (opsional)
TIMEOUT = 60           # detik menunggu Mini App muncul
PEER_ID = "8974289291"
NAMA_CHAT = "Farm Buddies"
# Reverse enginering peer_id
#<a class="... chatlist-chat ... active"
#   href="#8974289291"
#   data-peer-id="8974289291">
#    <span class="peer-title">Farm Buddies</span>
#</a>
# jika lokasi tombol untuk buka minapp tambahkan di bagian ini page.get_by_role("button", name=re.compile(r"^(launch|open|confirm|farm)"

PATCH = """
(() => {
  if (location.hash.includes('tgWebAppPlatform=')) {
    const h = location.hash.replace(/tgWebAppPlatform=[^&]*/, 'tgWebAppPlatform=android');
    history.replaceState(null, '', location.pathname + location.search + h);
  }
})();
"""


def cari_init_data(ctx, verbose=False):
    for pg in ctx.pages:
        for fr in pg.frames:
            if verbose:
                print("FRAME:", fr.url[:120])
            if "tgWebAppData" in fr.url:
                val = parse_qs(urlparse(fr.url).fragment).get("tgWebAppData")
                if val:
                    return val[0]
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



def masuk_chat(page):
    # 1) tunggu daftar chat termuat
    page.wait_for_selector("a.chatlist-chat", timeout=30000)
    print("[+] list chat loaded")

    # 2) klik chat lewat peer id; cadangan lewat nama chat
    kandidat = [
        page.locator(f'a.chatlist-chat[data-peer-id="{PEER_ID}"] .peer-title'),
        page.locator("a.chatlist-chat", has_text=NAMA_CHAT).locator(".peer-title"),
    ]
    for loc in kandidat:
        try:
            loc.first.click(timeout=5000)
            return True
        except Exception:
            print("[-] tidak ada nama chat ditemukan")
            continue

    # 3) cadangan terakhir: cari lewat kolom search
    try:
        page.locator(".input-search-input").first.click()
        page.keyboard.type(BOT, delay=50)
        page.wait_for_timeout(1500)
        page.locator(f'a[data-peer-id="{PEER_ID}"]').first.click(timeout=5000)

        print("[+] ditemukan nama chat dari pencarian")
        return True
    except Exception:
        print("[-] nama chat tidak ada di list/pencarian")
        return False


def buka_mini_app(page):
    if APP:
        addr = f"tg://resolve?domain={BOT}&appname={APP}"
        if START:
            addr += f"&startapp={START}"
        page.goto("https://web.telegram.org/k/#?tgaddr=" + quote(addr, safe=""))
    else:
        if not masuk_chat(page):
            print("Chat tidak ditemukan otomatis, klik manual di jendela.")

        # tunggu chat terbuka lalu klik tombol Mini App
        try:
            page.wait_for_selector(
                ".new-message-bot-commands.is-view, button.reply-markup-button.is-web-view",
                timeout=20000,
            )
        except Exception:
            print("Chat bot belum terbuka.")

        kandidat = [
            page.locator(".new-message-bot-commands.is-view"),             # Claim BTC
            page.locator("button.reply-markup-button.is-web-view").last,   # Open Faucet
            page.locator("button.peer-profile-open-app-button"),           # Open App
        ]
        klik = False
        for loc in kandidat:
            try:
                loc.first.click(timeout=5000)
                klik = True
                break
            except Exception:
                continue
        if not klik:
            print("Tombol tidak ditemukan otomatis, klik manual di jendela.")

    # dialog konfirmasi "Launch" kalau muncul pertama kali
    try:
        page.get_by_role("button", name=re.compile(r"^(launch|open|confirm|farm)", re.I)).first.click(timeout=4000)
        print("[+] Launch tombol")
        print("[+] Wait 20s...")
        time.sleep(20)
    except Exception:
        pass

def tunggu_miniapp_siap(ctx, timeout=60):
    mulai = time.time()

    while time.time() - mulai < timeout:
        for pg in ctx.pages:
            for fr in pg.frames:
                try:
                    status = fr.evaluate("""
                        () => ({
                            url: location.href,
                            ready: document.readyState,
                            title: document.title,
                            text: (document.body?.innerText || '').trim(),
                            initData: !!window.Telegram?.WebApp?.initData
                        })
                    """)

                    if (
                        status["initData"]
                        and status["ready"] == "complete"
                        and len(status["text"]) > 20
                    ):
                        print("[OK] Mini App terdeteksi")
                        print("[OK] URL:", status["url"])
                        print("[OK] Title:", status["title"])
                        print("[OK] Konten tersedia")

                        return True

                except Exception:
                    continue

        time.sleep(1)

    print("[TIMEOUT] Mini App belum terdeteksi sepenuhnya")
    return False

def ambil_initdata_auto(
    profile_dir="./tg_profile",
    device_name="Pixel 7",
    output_file="init_data.txt",
    timeout=TIMEOUT,
    headless=False,
    simpan=True,
):
    """Buka Telegram Web, buka mini app, lalu ambil init_data.
    Return: string init_data, atau None jika tidak ketemu."""
    with sync_playwright() as p:
        d = p.devices[device_name]
        ctx = p.chromium.launch_persistent_context(
            profile_dir,
            headless=headless,
            no_viewport=True,
            user_agent=d["user_agent"],
            args=["--window-size=460,800", "--window-position=0,0"],
        )
        try:
            ctx.add_init_script(PATCH)
            page = ctx.pages[0] if ctx.pages else ctx.new_page()

            page.goto("https://web.telegram.org/k/")
            page.wait_for_timeout(4000)

            if page.locator("canvas, .qr-container, input[type=tel]").count() > 0:
                # Belum login: login manual dulu di jendela
                # input("Belum login. Login dulu, lalu tekan Enter...")
                pass

            page.add_locator_handler(
                page.get_by_role("button", name="Launch"),   # sesuaikan teks tombolnya Launch/Cancel
                lambda btn: btn.click()
            )

            buka_mini_app(page)

            init_data = None
            mulai = time.time()
            while time.time() - mulai < timeout:
                init_data = cari_init_data(ctx)
                if init_data:
                    break
                time.sleep(2)

            if init_data:
                if simpan:
                    with open(output_file, "w") as f:
                        f.write(init_data)
                print("Tersimpan di", output_file, "| panjang:", len(init_data))
            else:
                print("Tidak ketemu. Daftar frame saat ini:")
                cari_init_data(ctx, verbose=True)

            return init_data
        finally:
            ctx.close()

# =============== TAMBAHAN AUTO LOGIN ===============








def strip_ansi(s):
    return re.sub(r'\x1b\[[0-9;]*m', '', s)

def gradient(text, start=51, end=213):
    if len(text) <= 1:
        return fg(start) + text + RST
    n = len(text)
    out = ""
    for i, ch in enumerate(text):
        t = i / max(1, n - 1)
        out += fg(int(round(start + (end - start) * t))) + ch
    return out + RST

def fmt_uptime(s):
    s = int(s)
    return f"{s // 3600:02d}:{(s % 3600) // 60:02d}:{s % 60:02d}"

def interruptible_sleep(state, seconds):
    end = time.time() + seconds
    while time.time() < end and not state.shutdown:
        time.sleep(min(0.2, end - time.time()))

def generate_random_id(prefix):
    if prefix == "dev_":
        return "dev_" + str(uuid.uuid4())
    else:
        return uuid.uuid4().hex

def typing_effect(text, delay=0.03):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

# ═══════════════════════════════════════════════════════════════════════════
# STATE
# ═══════════════════════════════════════════════════════════════════════════
class AppState:
    def __init__(self):
        self.user = "-"
        self.first_name = "-"
        self.phase = "boot"
        self.action = "init"
        self.start_time = time.time()
        self.ads_used = 0
        self.ads_max = 200
        self.coins = 0
        self.usdt = 0.0
        self.ads_done = 0
        self.today_earned = 0
        self.level = 1
        self.xp = 0
        self.xp_max = 3200
        self.water = 0
        self.water_max = 10
        self.farm_level = 1
        self.plots = []
        self.tasks = []
        self.crops = []
        self.streak_day = 0
        self.streak_claimed = False
        self.claimed_ids = set()
        self.cooldowns = {}
        self.session_gained = 0
        self.requests_made = 0
        self.errors = 0
        self.logs = []
        self.shutdown = False
        
        self._ICONS = {
            "i":  f"{fg(HACK_CYAN)}[SYS]{RST}",
            "ok": f"{fg(HACK_GREEN)}[ ✅️ ]{RST}",
            "er": f"{fg(C_ERR)}[FAIL]{RST}",
            "wr": f"{fg(C_WARN)}[WARN]{RST}",
            "in": f"{fg(HACK_PINK)}[INFO]{RST}",
            "g":  f"{fg(HACK_GREEN)}[EXEC]{RST}",
            "f":  f"{fg(HACK_GREEN)}[FARM]{RST}",
            "s":  f"{fg(HACK_PINK)}[SEED]{RST}", 
            "w":  f"{fg(HACK_BLUE)}[H2O ]{RST}",
        }

    def log(self, msg, tag="i"):
        icon = self._ICONS.get(tag, f"{fg(HACK_CYAN)}[SYS]{RST}")
        self.logs.append(f"{icon} {msg}")
        if len(self.logs) > 6:
            self.logs.pop(0)

    def on_cooldown(self, key):
        return time.time() < self.cooldowns.get(key, 0)

    def set_cooldown(self, key, sec):
        self.cooldowns[key] = time.time() + sec

# ═══════════════════════════════════════════════════════════════════════════
# DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════
class Dashboard:
    def __init__(self, state):
        self.state = state
        self._running = False
        self._thread = None

    def start(self):
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=1.5)

    def _loop(self):
        while self._running:
            try:
                self.render()
            except Exception:
                pass
            time.sleep(DASHBOARD_MS / 1000)

    def render(self):
        s = self.state
        out = []
        
        title_text = "Mode Kerja Rodi (Tanam, Siram, Panen + Ads)" if s.phase == "brutal" else "FARMBUDDIES CORE OVERRIDE ACTIVE"
        
        out.append(f"\n{fg(HACK_GREEN)}┌────────────────────────────────────────────────────────┐{RST}\n")
        out.append(f"{fg(HACK_GREEN)}│{RST} {fg(HACK_YELLOW)}{BOLD}{title_text}{RST} {fg(HACK_GREEN)}│{RST}\n")
        out.append(f"{fg(HACK_GREEN)}└────────────────────────────────────────────────────────┘{RST}\n")

        uptime = fmt_uptime(time.time() - s.start_time)
        
        if s.action == "Semua tanaman sudah disiram":
            if int(time.time()) % 2 == 0:
                exec_action = f"{fg(HACK_BLUE)}{BOLD}{s.action}{RST}"
            else:
                exec_action = f"{fg(HACK_DIM)}{s.action}{RST}"
        elif s.action.startswith("Menunggu panen"):
            if int(time.time()) % 2 == 0:
                exec_action = f"{fg(HACK_PASTEL_GREEN)}{BOLD}{s.action}{RST}"
            else:
                exec_action = f"{fg(HACK_DIM)}{s.action}{RST}"
        elif s.action == "Mode Brutal Berjalan...":
            if int(time.time()) % 2 == 0:
                exec_action = f"{fg(HACK_GREEN)}{BOLD}{s.action}{RST}"
            else:
                exec_action = f"{fg(C_ERR)}{BOLD}{s.action}{RST}"
        else:
            exec_action = f"{fg(C_WARN)}{s.action}{RST}"

        out.append(f" {fg(HACK_DIM)}[NODE]{RST} {fg(HACK_GREEN)}0x{s.user[:12].ljust(12)}{RST}  {fg(HACK_DIM)}[PING]{RST} {fg(HACK_CYAN)}{uptime}{RST}  {fg(HACK_DIM)}[MEM]{RST} {fg(HACK_GREEN)}{s.requests_made}/{s.errors}{RST}\n")
        out.append(f" {fg(HACK_DIM)}[MODE]{RST} {fg(C_ACCENT)}{s.phase.upper().ljust(12)}{RST}  {fg(HACK_DIM)}[SYS_STATUS]{RST} {fg(HACK_GREEN)}SECURE{RST}\n")
        out.append(f" {fg(HACK_DIM)}[EXEC]{RST} {exec_action}\n")
        out.append(f"{fg(HACK_GREEN)}──────────────────────────────────────────────────────────{RST}\n")

        out.append(f" {fg(HACK_GREEN)}< INFO PENDAPATAN >{RST}\n")
        out.append(f" {fg(HACK_DIM)}COIN:{RST} {fg(HACK_GREEN)}{s.coins:>8,}{RST}  │ {fg(HACK_DIM)}USDT:{RST} {fg(HACK_GREEN)}{s.usdt:.5f}{RST}  │ {fg(HACK_DIM)}ADS:{RST} {fg(HACK_GREEN)}{s.ads_done:>4,}{RST}\n")
        
        w_pct = int((s.water / max(1, s.water_max)) * 10)
        w_bar = f"{fg(HACK_BLUE)}[{'█' * w_pct}{'░' * (10 - w_pct)}]{RST}"
        out.append(f" {fg(HACK_DIM)}TANGKI AIR:{RST} {w_bar} {fg(HACK_BLUE)}{s.water}/{s.water_max}{RST}\n")
        out.append(f"{fg(HACK_GREEN)}──────────────────────────────────────────────────────────{RST}\n")

        if s.phase == "task":
            out.append(f" {fg(HACK_YELLOW)}TARGET_NODES (ADS & TASKS ONLY){RST}\n")
            shown = 0
            for t in s.tasks:
                if t.get("state") == "done": continue
                if shown >= 5: break
                
                tid   = t.get("id", "?")
                title = (t.get("title") or "Task")[:15].ljust(15)
                target, prog = t.get("target", 10), t.get("progress", 0)
                pct = int((prog / max(1, target)) * 100)
                filled = int(8 * pct / 100)
                bar = f"{fg(HACK_GREEN)}[{'█' * filled}{'░' * (8 - filled)}]{RST}"
                
                out.append(f"  {fg(HACK_DIM)}T{tid:<2}{RST} {fg(HACK_CYAN)}{title}{RST} {bar} {fg(HACK_DIM)}{prog}/{target}{RST}\n")
                shown += 1
            if shown == 0:
                out.append(f"  {fg(HACK_DIM)}>> NO ACTIVE TARGETS{RST}\n")
            out.append(f"{fg(HACK_GREEN)}──────────────────────────────────────────────────────────{RST}\n")
        else:
            out.append(f" {fg(HACK_YELLOW)}< INFO PERTUMBUHAN >{RST}\n")
            out.append(f" 🍅  🥕  🌽  🍆  🎃  🥦  🥒  🥬  🌶️  🍄\n")
            
            crop_icons = {
                "wheat": "🌾", "carrot": "🥕", "corn": "🌽",
                "tomato": "🍅", "eggplant": "🍆", "pumpkin": "🎃"
            }
            
            shown_p = 0
            for p in s.plots:
                if shown_p >= 6: break
                idx = p.get("idx", 0)
                name = (p.get("name") or "---")
                pstate = (p.get("state") or "empty").upper()
                
                crop_id = p.get("crop")
                crop_info = next((c for c in s.crops if c.get("id") == crop_id), {})
                cost = crop_info.get("plantCost", 0)
                cost_str = f"({cost})" if cost > 0 else ""
                
                display_name = f"{name[:10]}{cost_str}".ljust(14)
                
                if pstate == "EMPTY":
                    icon = "➖"
                else:
                    icon = crop_icons.get(crop_id, "🌱")
                
                is_ready = (pstate == "READY")
                ready_at = p.get("readyAt", 0)
                now_ms = int(time.time() * 1000)
                
                if not is_ready and pstate == "GROWING" and ready_at > 0:
                    if ready_at <= now_ms:
                        is_ready = True
                        
                if is_ready:
                    st = f"{fg(HACK_GREEN)}[READY]{RST}"
                elif pstate == "GROWING":
                    if ready_at and ready_at > now_ms:
                        rem_sec = (ready_at - now_ms) // 1000
                        m, s_val = divmod(rem_sec, 60)
                        st = f"{fg(HACK_PASTEL_GREEN)}[GROW {m:02d}m {s_val:02d}s]{RST}"
                    else:
                        st = f"{fg(HACK_PASTEL_GREEN)}[GROWING]{RST}"
                else:
                    st = f"{fg(HACK_DIM)}[EMPTY]{RST}"

                if p.get("watered"):
                    st += f" {fg(HACK_BLUE)}(💧){RST}"
                    
                out.append(f"  {fg(HACK_DIM)}P{idx:<2}{RST} {icon} {fg(HACK_CYAN)}{display_name}{RST} {st}\n")
                shown_p += 1
            out.append(f"{fg(HACK_GREEN)}──────────────────────────────────────────────────────────{RST}\n")

        out.append(f" {fg(HACK_YELLOW)}SYS EVENT STREAM{RST}\n")
        for i in range(6):
            if i < len(s.logs):
                out.append(f" {s.logs[i]}\n")
            else:
                out.append(f" {fg(HACK_DIM)} >> waiting for event...{RST}\n")
                
        out.append(f"{fg(HACK_GREEN)}└── {fg(HACK_CYAN)}SYSTEM INTEGRITY: 100%{RST}\n")
        out.append(f"{fg(HACK_ORANGE)}Tekan CTRL+C Untuk Kembali ke Menu{RST}\n")

        clear_screen()
        sys.stdout.write("".join(out))
        sys.stdout.flush()

# ═══════════════════════════════════════════════════════════════════════════
# CONFIG & PARSER
# ═══════════════════════════════════════════════════════════════════════════
class Config:
    def __init__(self, data=None):
        data = data or {}
        self.init_data   = data.get("init_data", "")
        self.device_id   = data.get("device_id", "")
        self.fingerprint = data.get("fingerprint", "")
        self.base_url    = data.get("base_url", DEFAULT_BASE_URL)
        self.poll_interval = int(data.get("poll_interval", 20))
        self.idle_limit    = int(data.get("idle_limit", 3))
        self.idle_sleep    = int(data.get("idle_sleep", 300))
        self.extra_watch   = float(data.get("extra_watch_sec", 2))

    def to_dict(self):
        return {
            "init_data": self.init_data, "device_id": self.device_id,
            "fingerprint": self.fingerprint, "base_url": self.base_url,
            "poll_interval": self.poll_interval, "idle_limit": self.idle_limit,
            "idle_sleep": self.idle_sleep, "extra_watch_sec": self.extra_watch,
        }

    def save(self):
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=4, ensure_ascii=False)

    @classmethod
    def load(cls):
        if not os.path.exists(CONFIG_FILE):
            return None
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return cls(json.load(f))
        except Exception:
            return None

    def is_valid(self):
        return bool(self.init_data and self.device_id and self.fingerprint)

def parse_initdata(init_data_str):
    if not init_data_str: return None
    parts = urllib.parse.parse_qsl(init_data_str, keep_blank_values=True)
    fields = dict(parts)
    try:
        if "user" in fields:
            fields["user"] = json.loads(fields["user"])
    except Exception: pass
    dc = sorted([(k, v) for k, v in parts if k != "hash"], key=lambda x: x[0])
    try: auth_date = int(fields.get("auth_date", 0) or 0)
    except (ValueError, TypeError): auth_date = 0
    return {
        "data_check_string": "\n".join(f"{k}={v}" for k, v in dc),
        "signature": fields.get("signature", ""),
        "user_id": str((fields.get("user") or {}).get("id", "")),
        "auth_date": auth_date, "hash": fields.get("hash", ""),
        "username": (fields.get("user") or {}).get("username", ""),
    }

def validate_initdata(init_data_str, max_age_hours=24):
    if not init_data_str: return False, "init_data kosong", {}
    try: parsed = parse_initdata(init_data_str)
    except Exception as e: return False, f"parse error: {e}", {}
    if not parsed: return False, "format tidak valid", {}

    auth_date = parsed.get("auth_date", 0)
    if auth_date <= 0: return False, "auth_date hilang/invalid", parsed

    now = int(time.time())
    age = now - auth_date
    info = {"auth_date": auth_date, "age_sec": age, "age_hour": age / 3600, "user_id": parsed.get("user_id", ""), "username": parsed.get("username", "")}

    if age < 0: return False, "auth_date di masa depan", info
    if age > max_age_hours * 3600: return False, f"expired (~{age / 3600:.1f} jam)", info
    return True, "format & umur OK", info

# ═══════════════════════════════════════════════════════════════════════════
# API CLIENT
# ═══════════════════════════════════════════════════════════════════════════
class APIClient:
    UA = "Mozilla/5.0 (Linux; Android 16; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.8010.36 Mobile Safari/537.36 Telegram-Android/12.9.2"

    def __init__(self, config: Config, state: AppState):
        self.config  = config
        self.state   = state
        self.base    = config.base_url.rstrip("/")
        self.token   = None
        self.session = requests.Session()
        self.session.verify = False
        self.session.trust_env = False
        self.session.headers.update({
            "User-Agent": self.UA, "Accept": "*/*",
            "Origin": "https://farm-buddies-4g5.pages.dev",
            "Referer": "https://farm-buddies-4g5.pages.dev/",
            "x-requested-with": "org.telegram.messenger.web",
        })

    def _headers(self):
        return {"Content-Type": "application/json", "authorization": f"Bearer {self.token}", "x-farm-fp": self.config.fingerprint}

    def authenticate(self):
        self.state.action = "Bypassing Auth Security..."
        try:
            res = self.session.post(f"{self.base}/auth/telegram", headers={"Content-Type": "application/json"}, json={"initData": self.config.init_data, "deviceId": self.config.device_id, "fingerprint": self.config.fingerprint}, timeout=15)
            self.state.requests_made += 1
            if res.status_code == 200:
                data = res.json()
                if data.get("ok") and data.get("token"):
                    self.token = data["token"]
                    self.state.log("Bearer token acquired successfully", "ok")
                    return True
            self.state.errors += 1
            self.state.log(f"Auth failed status={res.status_code}", "er")
        except Exception as e:
            self.state.errors += 1
            self.state.log(f"Auth error: {str(e)[:40]}", "er")
        return False

    def request(self, method, endpoint, body=None, retries=3):
        if not self.token and not self.authenticate(): return None
        url = f"{self.base}{endpoint}"
        for attempt in range(retries):
            if self.state.shutdown: return None
            try:
                if method.upper() == "GET":
                    res = self.session.get(url, headers=self._headers(), timeout=15)
                else:
                    res = self.session.post(url, headers=self._headers(), json=body if body is not None else {}, timeout=15)
                self.state.requests_made += 1

                if res.status_code == 401:
                    self.state.log("Token expired, refreshing...", "wr")
                    if self.authenticate(): continue
                    return None
                if 500 <= res.status_code < 600 and attempt < retries - 1:
                    time.sleep(2 ** attempt + random.uniform(0, 1))
                    continue
                return res
            except requests.RequestException as e:
                self.state.errors += 1
                self.state.log(f"Req err {endpoint}: {str(e)[:30]}", "er")
                if attempt < retries - 1: time.sleep(2 ** attempt + random.uniform(0, 1))
                else: return None
        return None

def test_auth_validity(config):
    try:
        tmp = requests.Session()
        tmp.verify = False
        tmp.trust_env = False
        tmp.headers.update({"User-Agent": APIClient.UA, "Accept": "*/*", "Origin": "https://farm-buddies-4g5.pages.dev", "Referer": "https://farm-buddies-4g5.pages.dev/", "x-requested-with": "org.telegram.messenger.web"})
        res = tmp.post(f"{config.base_url.rstrip('/')}/auth/telegram", headers={"Content-Type": "application/json"}, json={"initData": config.init_data, "deviceId": config.device_id, "fingerprint": config.fingerprint}, timeout=15)
        if res.status_code == 200:
            try: d = res.json()
            except Exception: return False, "respons bukan JSON"
            if d.get("ok") and d.get("token"): return True, "server terima token"
            return False, f"ditolak: {d.get('message', 'unknown')}"
        if res.status_code in (401, 403): return False, f"HTTP {res.status_code} (expired)"
        return False, f"HTTP {res.status_code}"
    except requests.RequestException as e:
        return False, f"koneksi error: {str(e)[:30]}"

# ═══════════════════════════════════════════════════════════════════════════
# ACTIONS & SCANNER
# ═══════════════════════════════════════════════════════════════════════════
class Actions:
    def __init__(self, client: APIClient, state: AppState, config: Config):
        self.client = client
        self.state  = state
        self.config = config

    @staticmethod
    def _ok_json(res):
        if not res or res.status_code != 200: return None
        try: d = res.json()
        except Exception: return None
        return d if d.get("ok") else None

    def claim_task(self, task_id, title, expected_reward=0):
        self.state.action = f"Extracting Task {task_id}..."
        for ep in (f"/tasks/{task_id}/claim", f"/tasks/{task_id}/complete"):
            r = self.client.request("POST", ep, {})
            if not r or r.status_code in (404, 405): continue
            if r.status_code == 409: self.state.claimed_ids.add(task_id); return "cooldown"
            if r.status_code != 200: continue
            try: d = r.json()
            except Exception: continue
            if d.get("ok"):
                gain = (d.get("reward") or d.get("coins") or d.get("claimedCoins") or expected_reward or 0)
                self.state.claimed_ids.add(task_id)
                self.state.session_gained += gain
                self.state.log(f"Payload extracted: {title} [+{gain} COIN]", "ok")
                play_beep()
                return "success"
            self.state.claimed_ids.add(task_id)
            return "skip"
        self.state.claimed_ids.add(task_id)
        return "failed"

    def watch_ad_task(self, task_id, title):
        self.state.action = f"Injecting Ad Payload..."
        r = self.client.request("POST", f"/ads/task/{task_id}/session", {"slotIndex": -1})
        if not r: return "failed"
        if r.status_code == 409: return "cooldown"
        d = self._ok_json(r)
        if not d: return "failed"
        sid = d.get("sessionId"); mw = d.get("minWatchSec", 8) + self.config.extra_watch; slot = d.get("slotIndex", 0); prov = d.get("provider", "adsgram")
        self.state.log(f"Waiting for Ad Timeout: {mw:.0f}s", "in")
        interruptible_sleep(self.state, mw)
        r2 = self.client.request("POST", f"/ads/task/{task_id}/complete", {"sessionId": sid, "slotIndex": slot, "provider": prov, "clicked": True, "adsgramClicked": False})
        d2 = self._ok_json(r2)
        if d2:
            gain = d2.get("reward") or 0
            self.state.session_gained += gain
            self.state.log(f"Payload extracted: {title} [+{gain} COIN]", "ok")
            play_beep()
            return "success"
        return "failed"

    def adsgram_task(self, task_id, title, block_id):
        self.state.action = f"Decrypting Adsgram Node..."
        r = self.client.request("POST", f"/ads/task/{task_id}/reward", {})
        if not r: return "failed"
        if r.status_code == 409: self.state.log("Adsgram node on cooldown", "wr"); return "cooldown"
        if r.status_code != 200: self.state.log(f"Adsgram HTTP {r.status_code}", "er"); return "failed"
        try: d = r.json()
        except Exception: return "failed"
        if not d.get("ok"): self.state.log(f"Adsgram: {d.get('message', 'failed')}", "er"); return "failed"
        if d.get("already"): self.state.log("Node already cracked", "wr"); return "skip"
        rew = d.get("reward", 0)
        self.state.session_gained += rew
        self.state.log(f"Payload extracted: {title} [+{rew} COIN]", "ok")
        play_beep()
        prof = d.get("profile", {})
        if prof:
            self.state.coins = prof.get("coins", self.state.coins)
            self.state.today_earned = prof.get("todayEarned", self.state.today_earned)
            self.state.ads_done = prof.get("totalAds", self.state.ads_done)
        return "success"

    def link_task(self, task_id, title, url, dwell=15):
        self.state.action = f"Bypassing Link Security..."
        start_reward = 0
        r = self.client.request("POST", f"/tasks/{task_id}/start", {})
        if r and r.status_code == 409: self.state.log(f"[LINK] cooldown", "wr"); return "cooldown"
        if r and r.status_code == 200:
            try:
                d = r.json()
                if d.get("ok"):
                    start_reward = d.get("reward", 0) or 0
                    if start_reward:
                        self.state.session_gained += start_reward
                        self.state.log(f"Link injected: +{start_reward}", "ok")
            except Exception: pass
        if url:
            try:
                requests.get(url, verify=False, headers={"User-Agent": self.client.UA, "Referer": "https://farm-buddies-4g5.pages.dev/"}, timeout=20, allow_redirects=True)
                self.state.log(f"Target URL visited", "in")
            except Exception: pass
        interruptible_sleep(self.state, dwell + 3)
        r2 = self.client.request("POST", f"/tasks/{task_id}/claim", {})
        if r2 and r2.status_code == 409: self.state.log(f"[LINK] cooldown", "wr"); return "cooldown"
        if r2 and r2.status_code == 200:
            try:
                d2 = r2.json()
                if d2.get("ok"):
                    gain = (d2.get("reward") or start_reward)
                    self.state.session_gained += gain
                    self.state.claimed_ids.add(task_id)
                    self.state.log(f"Payload extracted: {title} [+{gain} COIN]", "ok")
                    play_beep()
                    return "success"
                self.state.claimed_ids.add(task_id)
            except Exception: pass
        return "failed"
        
    def harvest(self, idx):
        self.state.action = f"Harvesting P{idx}..."
        r = self.client.request("POST", "/ads/harvest/session", {"idx": idx})
        if not r: return "failed"
        if r.status_code == 409: return "cooldown"
        d = self._ok_json(r)
        if not d: return "failed"
        sid = d.get("sessionId"); mw = d.get("minWatchSec", 8) + self.config.extra_watch
        self.state.log(f"Harvesting wait {mw:.0f}s", "in")
        interruptible_sleep(self.state, mw)
        r2 = self.client.request("POST", "/ads/harvest/complete", {"sessionId": sid, "provider": "adsgram", "clicked": True, "adsgramClicked": False})
        if self._ok_json(r2): return "success"
        return "failed"

    def water(self, idx):
        self.state.action = f"Watering Node P{idx}..."
        r = self.client.request("POST", "/farm/water", {"idx": idx})
        if self._ok_json(r): 
            self.state.log(f"Siram P{idx} sukses", "w")
            return "success"
        return "failed"
        
    def plant(self, idx, crop_id):
        self.state.action = f"Planting {crop_id} at P{idx}..."
        r = self.client.request("POST", "/farm/plant", {"idx": idx, "crop": crop_id})
        d = self._ok_json(r)
        if d: return "success"
        if r and r.status_code == 400:
            body = r.text.lower()
            if any(k in body for k in ("coin", "insufficient", "balance", "funds")):
                self.state.log("Coin tidak cukup untuk menanam.", "wr"); return "need_action"
        return "failed"

    def refill_water(self):
        self.state.action = "Refilling Water Tank (Ads)..."
        r = self.client.request("POST", "/ads/farm/session", {"ref": "water"})
        if not r: return "failed"
        if r.status_code == 409: return "cooldown"
        d = self._ok_json(r)
        if not d: return "failed"
        sid = d.get("sessionId"); mw = d.get("minWatchSec", 6) + self.config.extra_watch
        self.state.log(f"Nonton iklan air {mw:.0f}s", "in")
        interruptible_sleep(self.state, mw)
        r2 = self.client.request("POST", "/ads/farm/complete", {"sessionId": sid, "ref": "water", "provider": "adsgram", "clicked": True, "adsgramClicked": False})
        if self._ok_json(r2): 
            self.state.log("Air diisi penuh (+10)", "w")
            return "success"
        return "failed"

def fetch_state(client: APIClient, state: AppState) -> bool:
    r = client.request("GET", "/user/bootstrap")
    if not r: return False
    if r.status_code != 200: return False
    try: d = r.json()
    except Exception: return False
    if not d.get("ok"): return False
    profile = d.get("profile", {}); farm = d.get("farm", {}); streak = d.get("streak", {}); cap = d.get("ads", {}).get("cap", {})
    
    state.user = profile.get("username", "")
    state.first_name = profile.get("firstName") or state.user or "Unknown"
    
    state.coins = int(profile.get("coins", 0)); state.usdt = float(profile.get("usdt", 0))
    state.level = profile.get("level", 1); state.xp = profile.get("xp", 0); state.xp_max = profile.get("xpMax", 3200)
    state.ads_done = profile.get("totalAds", 0); state.today_earned = profile.get("todayEarned", 0)
    state.water = farm.get("water", 0); state.water_max = farm.get("waterMax", 10)
    state.plots = farm.get("plots", []); state.crops = farm.get("crops", []); state.tasks = d.get("tasks", [])
    state.ads_used = cap.get("used", 0); state.ads_max = cap.get("max", 200)
    state.streak_claimed = streak.get("claimedToday", False)
    return True

# ═══════════════════════════════════════════════════════════════════════════
# UI / MENU & SETUP
# ═══════════════════════════════════════════════════════════════════════════
def banner_pak_tani():
    art = [
        "██████╗  █████╗ ██╗  ██╗    ████████╗ █████╗ ███╗   ██╗██╗",
        "██╔══██╗██╔══██╗██║ ██╔╝    ╚══██╔══╝██╔══██╗████╗  ██║██║",
        "██████╔╝███████║█████╔╝        ██║   ███████║██╔██╗ ██║██║",
        "██╔═══╝ ██╔══██║██╔═██╗        ██║   ██╔══██║██║╚██╗██║██║",
        "██║     ██║  ██║██║  ██╗       ██║   ██║  ██║██║ ╚████║██║"
    ]
    orange_colors = [214, 208, 202, 166, 130]
    colored_art = []
    for y, line in enumerate(art):
        color = orange_colors[y % len(orange_colors)]
        colored = ""
        for ch in line:
            if ch == " ": colored += ch
            else: colored += f"\033[1m\033[38;5;{color}m{ch}"
        colored_art.append(colored + RST)

    t2 = "Farm Buddy Edisi Ngasal"
    t3 = "Mod by Jendela Semesta REBORN"
    t4 = "Join my Group Telegram"
    t5 = "https://t.me/jendelasemesta"
    t6 = "🍅  🥕  🌽  🍆  🎃  🥦  🥒  🥬  🌶️  🍄"
    
    width = max(len(line) for line in art)

    def center(text, w):
        plain_len = len(strip_ansi(text))
        pad = max(0, (w - plain_len) // 2)
        return " " * pad + text

    lines = []
    for line in colored_art: lines.append(center(line, width))
    lines.append(center(f"\033[38;5;226m{BOLD}{t2}{RST}", width))
    lines.append(center(f"\033[38;5;51m{t3}{RST}", width))
    lines.append(center(f"\033[38;5;255m{t4}{RST}", width))
    lines.append(center(f"\033[38;5;214m{t5}{RST}", width))
    
    veg_line = center(f"{t6}", width)
    if veg_line.startswith("   "):
        veg_line = veg_line[3:]
    lines.append(veg_line)
    
    lines.append(center(f"\033[1m\033[38;5;214m" + "_" * width + RST, width))
    return "\n".join(lines)



def isi_data():
    existing = Config.load()
    clear_screen()
    print("\n" + banner_pak_tani() + "\n")
    try:
        print("[+] Mengambl initData")
        init_data = ambil_initdata_auto()
        #init_data = input(f"{fg(C_HDR_1)}Masukkan Init Data :{RST} ").strip()
    except (KeyboardInterrupt, EOFError): return False

    if not init_data and existing: init_data = existing.init_data
    if not init_data: print(f"\n  {fg(C_ERR)}Init data tidak boleh kosong.{RST}"); time.sleep(2); return False

    cfg = existing or Config()
    cfg.init_data = init_data
    if not cfg.device_id or len(cfg.device_id) < 10: cfg.device_id = generate_random_id("dev_")
    if not cfg.fingerprint or len(cfg.fingerprint) < 10: cfg.fingerprint = generate_random_id("fp_")
    cfg.save()
    
    clear_screen()
    print("\n" + banner_pak_tani() + "\n\n")
    time.sleep(0.5)
    typing_effect(f"{fg(C_OK)}Device ID Mode AUTO ✅️{RST}", delay=0.03)
    time.sleep(0.2)
    typing_effect(f"{fg(C_OK)}Finger Print Mode AUTO ✅️{RST}", delay=0.03)
    time.sleep(0.2)
    typing_effect(f"{fg(C_OK)}Init Data ✅️{RST}", delay=0.03)
    print("\n")
    time.sleep(0.8)
    return True

def initial_setup():
    cfg = Config.load()
    if not cfg or not cfg.is_valid():
        if not isi_data(): return None
        cfg = Config.load()
        if not cfg: return None

    while True:
        print(f"\n{fg(C_TEXT)}{BOLD}VALIDASI INIT DATA{RST}\n")
        local_ok, local_msg, info = validate_initdata(cfg.init_data)
        if local_ok: print(f"  {fg(C_OK)}Format OK{RST} — OK {fg(C_SUB)}(umur {info.get('age_hour', 0):.1f} jam){RST}")
        else: print(f"  {fg(C_ERR)}Format GAGAL{RST} — {local_msg}")

        print(f"  {fg(C_HDR_2)}Server{RST} — menguji...", end="", flush=True)
        server_ok, server_msg = test_auth_validity(cfg)
        print("\r" + " " * 40 + "\r", end="", flush=True)
        mark = f"{fg(C_OK)}OK{RST}" if server_ok else f"{fg(C_ERR)}GAGAL{RST}"
        print(f"  {fg(C_HDR_2)}Server{RST} — {mark} {fg(C_SUB)}({server_msg}){RST}")

        if local_ok and server_ok:
            print(f"\n  {fg(C_OK)}Init data valid. Lanjut ke menu...{RST}"); time.sleep(1.5); return cfg

        print(f"\n  {fg(C_WARN)}Init data bermasalah.{RST}")
        try: p = input(f"  {fg(C_HDR_2)}Isi ulang init data? [y/N]:{RST} ").strip().lower()
        except (KeyboardInterrupt, EOFError): return None
        if p != "y": return None
        if not isi_data(): return None
        cfg = Config.load()
        if not cfg: return None

def get_rank_title(level):
    if level < 5: return "Novice Farmer"
    elif level < 10: return "Seedling Planter"
    elif level < 15: return "Crop Cultivator"
    elif level < 20: return "Skilled Harvester"
    elif level < 30: return "Harvest Master" 
    elif level < 40: return "Farm Tycoon"
    else: return "Legendary Farmer"

def ask_plant_strategy(cfg=None):
    """Pilihan strategi menanam KHUSUS menu 2."""
    while True:
        print()
        print(f"{fg(HACK_CYAN)}{BOLD}PILIH STRATEGI MENANAM :{RST} {fg(SOFT_BLUE)}(Sesuaikan coinmu){RST}")
        print(f"{fg(C_ACCENT)}1.{RST} {fg(231)}🌱 Tanam Bibit yg Murah{RST} {fg(SOFT_BLUE)}(Jemat, cepat, murah){RST}")
        print(f"{fg(C_ACCENT)}2.{RST} {fg(231)}🌱 Tanam Bibit yg Mehong{RST} {fg(SOFT_BLUE)}(Profit besar mantap){RST}")
        print(f"{fg(C_ACCENT)}3.{RST} {fg(231)}🥕 Tanam Bibit CUSTOM{RST} {fg(SOFT_BLUE)}(Tentukan Sendiri){RST}")
        print(f"{fg(C_ACCENT)}4.{RST} {fg(231)}🏠  Kembali ke menu..{RST}")
        print()
        try:
            pilih = input(f" {fg(C_HDR_2)}▸ Pilih strategi [1/2/3/4] :{RST} ").strip()
        except (KeyboardInterrupt, EOFError):
            print(f"{fg(HACK_ORANGE)}" + "_" * 56 + RST)
            return None
        print(f"{fg(HACK_ORANGE)}" + "_" * 56 + RST)
        if pilih == "1":
            return "cheap"
        if pilih == "2":
            return "expensive"
        if pilih == "3":
            result = ask_custom_seeds(cfg)
            if result is not None:
                return result
            continue
        if pilih == "4":
            return None

def ask_custom_seeds(cfg=None):
    """Menu CUSTOM: tampilkan list bibit + coin, user pilih beberapa sekaligus."""
    if cfg is None:
        cfg = Config.load()
    if not cfg:
        print(f"{fg(C_ERR)}Config tidak ditemukan.{RST}")
        time.sleep(1.5)
        return None

    tmp_state  = AppState()
    tmp_client = APIClient(cfg, tmp_state)

    print(f"{fg(C_DIM)}  [ Fetching farm data... ]{RST}", end="", flush=True)
    ok = tmp_client.authenticate() and fetch_state(tmp_client, tmp_state)
    print("\r" + " " * 40 + "\r", end="", flush=True)

    if not ok:
        print(f"{fg(C_ERR)}Gagal ambil data farm. Coba lagi.{RST}")
        time.sleep(1.5)
        return None

    crops  = tmp_state.crops or []
    coins  = tmp_state.coins

    unlocked = [c for c in crops if not c.get("locked", True)]
    if not unlocked:
        unlocked = list(crops)

    if not unlocked:
        print(f"{fg(C_ERR)}Data bibit tidak tersedia.{RST}")
        time.sleep(1.5)
        return None

    crop_icons = {
        "wheat": "🌾", "carrot": "🥕", "corn": "🌽",
        "tomato": "🍅", "eggplant": "🍆", "pumpkin": "🎃"
    }

    while True:
        print()
        print(f"{fg(HACK_CYAN)}{BOLD}List Bibit + Harganya :{RST}")
        print(f"{fg(HACK_CYAN)}Coin kamu :{RST} {fg(HACK_GREEN)}{BOLD}{coins:,}{RST} {fg(HACK_DIM)}Coin{RST}")
        print()

        for i, c in enumerate(unlocked, 1):
            cid  = c.get("id", "")
            name = c.get("name", cid)
            cost = c.get("plantCost", 0)
            icon = crop_icons.get(cid, "🌱")
            display_name = name[:10].ljust(14)
            stars = get_crop_stars(cid)
            print(
                f"{fg(HACK_YELLOW)}{i}. {icon} {display_name}{RST}"
                f" {fg(HACK_DIM)}:{RST} "
                f"{fg(HACK_GREEN)}{str(cost).rjust(3)}{RST}"
                f" {fg(HACK_DIM)}Coin{RST} {stars}"
            )

        back_idx = len(unlocked) + 1
        print(f"{fg(C_ACCENT)}{back_idx}.{RST} {fg(231)}🏠 Kembali ke menu Sebelumnya{RST}")

        print()
        try:
            pilihan = input(f"{fg(HACK_YELLOW)}{BOLD}Silahkan Pilih contoh 1,3,5 :{RST} ").strip()
        except (KeyboardInterrupt, EOFError):
            print(f"{fg(HACK_ORANGE)}" + "_" * 56 + RST)
            return None
        print(f"{fg(HACK_ORANGE)}" + "_" * 56 + RST)

        if not pilihan:
            continue

        # Kembali ke menu sebelumnya (kalau input tunggal "back_idx")
        if pilihan == str(back_idx):
            return None

        try:
            indices = [int(x.strip()) for x in pilihan.replace(" ", "").split(",") if x.strip()]
        except ValueError:
            print(f"{fg(C_ERR)}Format salah. Contoh: 1,3,5{RST}")
            time.sleep(1.5)
            continue

        # Kalau ada input back_idx di antara list (misal "1,7"), anggap batal
        if back_idx in indices:
            return None

        selected_ids = []
        valid = True
        for idx in indices:
            if 1 <= idx <= len(unlocked):
                cid = unlocked[idx - 1].get("id")
                if cid and cid not in selected_ids:
                    selected_ids.append(cid)
            else:
                print(f"{fg(C_ERR)}Nomor {idx} tidak valid (1-{back_idx}){RST}")
                valid = False
                break

        if valid and selected_ids:
            return selected_ids

        time.sleep(1.5)

def show_main_menu(cfg):
    coins_str, balance_str, ads_str = "—", "—", "—"
    fetch_ok, user_str, err_msg = False, "", ""
    
    first_name = "Unknown"
    level = 1
    
    try:
        tmp_state = AppState(); tmp_client = APIClient(cfg, tmp_state)
        if tmp_client.authenticate():
            if fetch_state(tmp_client, tmp_state):
                coins_str = f"{tmp_state.coins:,}"; balance_str = f"{tmp_state.usdt:.5f} USDT"
                ads_str = f"{tmp_state.ads_done:,}"; 
                user_str = tmp_state.user
                first_name = tmp_state.first_name
                level = tmp_state.level
                fetch_ok = True
            else: err_msg = "bootstrap gagal"
        else: err_msg = "auth gagal"
    except Exception as e: err_msg = str(e).replace('\n', ' ')[:25]

    clear_screen()
    print("\n" + banner_pak_tani() + "\n")
    
    if fetch_ok:
        rank_title = get_rank_title(level)
        print(f"{fg(C_HDR_2)}Username  :{RST} {fg(C_OK)}🧓 {first_name}{RST}")
        print(f"{fg(C_HDR_2)}Peringkat :{RST} {fg(C_OK)}🌱 {rank_title}{RST}\n")
    
    warn = "" if fetch_ok else f" {fg(C_WARN)}({err_msg}){RST}"
    
    print(f"💰 Total Coin             : {fg(C_OK)}{coins_str}{RST}{warn}")
    print(f"💰 Total Balance          : {fg(C_OK)}{balance_str}{RST}{warn}")
    print(f"🖥  Total Ads dikerjakan   : {fg(C_OK)}{ads_str}{RST}{warn}\n")
    
    print(f"{fg(HACK_CYAN)}DAFTAR HARGA BIBIT :{RST}")
    crops_data = tmp_state.crops if 'tmp_state' in locals() else []
    crop_icons = {
        "wheat": "🌾", "carrot": "🥕", "corn": "🌽",
        "tomato": "🍅", "eggplant": "🍆", "pumpkin": "🎃"
    }
    if crops_data:
        for c in crops_data:
            cid   = c.get("id", "")
            name  = c.get("name", cid)
            cost  = c.get("plantCost", 0)
            icon  = crop_icons.get(cid, "🌱")
            
            display_name = name[:10].ljust(14)
            stars = get_crop_stars(cid)
            
            print(
                f"{fg(HACK_YELLOW)}{icon} {display_name}{RST}"
                f" {fg(HACK_DIM)}:{RST} "
                f"{fg(HACK_GREEN)}{str(cost).rjust(3)}{RST}"
                f" {fg(HACK_DIM)}Coin{RST} {stars}"
            )
    else:
        print(f"{fg(C_WARN)}Data bibit tidak tersedia{RST}")
    
    print() 
    print(f"{fg(C_HDR_1)}{BOLD}Pilihan Menu :{RST}\n")

    menu_items = [
        ("1", "Mengerjakan Tugas"), 
        ("2", "Mulai Bercocok Tanam"), 
        ("3", "Menyiram Tanaman"), 
        ("4", "Memanen Semua Tanaman"), 
        ("5", "Kerja Rodi Auto Menanam, Menyiram + Panen"), 
        ("6", "Update Init Data"),
        ("7", "Keluar")
    ]
    for num, text in menu_items: print(f"{fg(C_ACCENT)}{num}.{RST} {fg(231)}{text}{RST}")

    print()

    try:
        if len(sys.argv) > 1:
            pilihan = sys.argv[1]
        else:
            pilihan = input(f" {fg(C_HDR_2)}▸ Pilih menu :{RST} ").strip()

    except (KeyboardInterrupt, EOFError):
        pilihan = "7"

    print(f"{fg(HACK_ORANGE)}" + "_" * 56 + RST)

    return pilihan

# ═══════════════════════════════════════════════════════════════════════════
# FOCUSED RUNNER
# ═══════════════════════════════════════════════════════════════════════════
def run_focused(cfg, mode, strategy="payout"):
    state = AppState(); client = APIClient(cfg, state); actions = Actions(client, state, cfg); dashboard = Dashboard(state)
    
    user_cancelled = False
    def _sigint(s, f): 
        nonlocal user_cancelled
        user_cancelled = True
        state.shutdown = True
        
    old = signal.signal(signal.SIGINT, _sigint)
    dashboard.start()

    try:
        if not client.authenticate(): state.log("auth gagal", "er"); interruptible_sleep(state, 3); return
        if not fetch_state(client, state): state.log("sync gagal", "er"); interruptible_sleep(state, 3); return
        
        state.phase = mode
        idle = 0
        
        while not state.shutdown and idle < 5:
            acted = False
            
            if mode == "task":
                for t in state.tasks:
                    if t.get("state") == "done" and t.get("id") not in state.claimed_ids:
                        if actions.claim_task(t.get("id"), t.get("title", "?"), t.get("reward", 0)) == "success":
                            acted = True
                            break
                if acted: 
                    fetch_state(client, state)
                    interruptible_sleep(state, 1)
                    continue

                if not acted and not state.on_cooldown("ad"):
                    for t in state.tasks:
                        if t.get("type") == "ad" and not t.get("adsgramTask") and t.get("state") == "open":
                            if t.get("progress", 0) < t.get("target", 10):
                                res = actions.watch_ad_task(t.get("id"), t.get("title", "Ad"))
                                if res == "success": acted = True; break
                                if res == "cooldown": state.set_cooldown("ad", 60); break
                
                if not acted and not state.on_cooldown("adsgram"):
                    for t in state.tasks:
                        if t.get("adsgramTask") and t.get("state") == "open":
                            res = actions.adsgram_task(t.get("id"), t.get("title", "Adg"), t.get("blockId"))
                            if res == "success": acted = True; break
                            if res == "cooldown": state.set_cooldown("adsgram", 60); break
                            
                if not acted and not state.on_cooldown("link"):
                    for t in state.tasks:
                        if t.get("type") in ("link", "telegram") and t.get("state") == "open" and t.get("id") not in state.claimed_ids:
                            title_lower = t.get("title", "").lower()
                            url_lower = t.get("url", "").lower()
                            is_shortlink = (
                                "smarlink" in title_lower or 
                                "profitableratecpmnetwork" in url_lower or 
                                "omg10" in url_lower or 
                                "gigapub.tech" in url_lower
                            )
                            if is_shortlink: continue 
                            if t.get("url") and t.get("progress", 0) < t.get("target", 1):
                                res = actions.link_task(t.get("id"), t.get("title", "Link"), t.get("url"), t.get("dwellSec", 15))
                                if res == "success": acted = True; break
                                if res == "cooldown": state.claimed_ids.add(t.get("id")); continue
                                state.claimed_ids.add(t.get("id"))

            elif mode == "brutal":
                now_ms = int(time.time() * 1000)

                def is_crop_ready(p):
                    if p.get("state") == "ready": return True
                    if p.get("state") == "growing":
                        ready_at = p.get("readyAt", 0)
                        if ready_at > 0 and ready_at <= now_ms:
                            return True
                    return False

                for p in state.plots:
                    if is_crop_ready(p):
                        name = p.get("name") or "Tanaman"
                        idx = p.get("idx")
                        res = actions.harvest(idx)
                        if res == "success":
                            fetch_state(client, state)
                            state.log(f"{BOLD}{fg(HACK_GREEN)}Claim Sukses! Panen {name} (P{idx}){RST}", "ok")
                            state.log(f"Saldo: {state.coins:,} Coin | {state.usdt:.5f} USDT", "in")
                            play_beep()
                            acted = True
                            break
                if acted: continue

                needs_water = [p for p in state.plots if p.get("state") in ("growing", "ready") and not p.get("watered", False)]
                if needs_water:
                    target_plot = needs_water[0]
                    idx = target_plot.get("idx")
                    if state.water > 0:
                        res = actions.water(idx)
                        if res == "success":
                            fetch_state(client, state)
                            acted = True
                    else:
                        res = actions.refill_water()
                        if res == "success":
                            fetch_state(client, state)
                            acted = True
                        elif res == "cooldown":
                            state.set_cooldown("refill", 60)
                if acted: continue

                empty = [p for p in state.plots if p.get("state") == "empty" and not p.get("locked", False)]
                if empty:
                    crop_id, cost = best_affordable_crop(state.crops, state.coins, "random")
                    if state.coins >= cost:
                        crop_info = next((c for c in state.crops if c.get("id") == crop_id), {})
                        grow_min = crop_info.get("growMinutes", 20)
                        res = actions.plant(empty[0].get("idx"), crop_id)
                        if res == "success":
                            fetch_state(client, state)
                            state.log(f"Tanam {crop_id.upper()} P{empty[0].get('idx')} | Modal: {cost}", "s")
                            acted = True
                        elif res == "need_action":
                            state.log("Coin tidak cukup untuk menanam.", "wr")

            elif mode == "harvest":
                now_ms = int(time.time() * 1000)
                for p in state.plots:
                    is_ready = (p.get("state") == "ready")
                    ready_at = p.get("readyAt", 0)
                    if not is_ready and p.get("state") == "growing" and ready_at > 0 and ready_at <= now_ms:
                        is_ready = True
                        
                    if is_ready:
                        name = p.get("name") or "Tanaman"
                        idx = p.get("idx")
                        res = actions.harvest(idx)
                        if res == "success":
                            fetch_state(client, state)
                            state.log(f"{BOLD}{fg(HACK_GREEN)}Claim Sukses! Panen {name} (P{idx}){RST}", "ok")
                            state.log(f"Saldo: {state.coins:,} Coin | {state.usdt:.5f} USDT", "in")
                            play_beep()
                            acted = True
                            break
                            
            elif mode == "water":
                needs_water = [p for p in state.plots if p.get("state") in ("growing", "ready") and not p.get("watered", False)]
                if needs_water:
                    target_plot = needs_water[0]
                    idx = target_plot.get("idx")
                    if state.water > 0:
                        res = actions.water(idx)
                        if res == "success":
                            fetch_state(client, state)
                            acted = True
                    else:
                        res = actions.refill_water()
                        if res == "success":
                            fetch_state(client, state)
                            acted = True
                        elif res == "cooldown":
                            state.set_cooldown("refill", 60)
                            
            elif mode == "plant":
                harvested = False
                now_ms = int(time.time() * 1000)
                for p in state.plots:
                    is_ready = (p.get("state") == "ready")
                    ready_at = p.get("readyAt", 0)
                    if not is_ready and p.get("state") == "growing" and ready_at > 0 and ready_at <= now_ms:
                        is_ready = True

                    if is_ready:
                        name = p.get("name") or "Tanaman"
                        res = actions.harvest(p.get("idx"))
                        if res == "success":
                            fetch_state(client, state)
                            state.log(f"{BOLD}{fg(HACK_GREEN)}Claim Sukses! Panen {name} (P{p.get('idx')}){RST}", "ok")
                            state.log(f"Saldo: {state.coins:,} Coin | {state.usdt:.5f} USDT", "in")
                            play_beep()
                            acted = True
                            harvested = True
                            break
                if harvested: continue

                empty = [p for p in state.plots if p.get("state") == "empty" and not p.get("locked", False)]
                if empty:
                    crop_id, cost = best_affordable_crop(state.crops, state.coins, strategy)
                    crop_info = next((c for c in state.crops if c.get("id") == crop_id), {})
                    grow_min = crop_info.get("growMinutes", 20)
                    res = actions.plant(empty[0].get("idx"), crop_id)
                    if res == "success":
                        fetch_state(client, state)
                        state.log(f"Tanam {crop_id.upper()} P{empty[0].get('idx')} | Modal: {cost}", "s")
                        acted = True
                    elif res == "need_action":
                        state.log("Coin tidak cukup untuk menanam.", "wr")

            if acted:
                idle = 0
                fetch_state(client, state)
                interruptible_sleep(state, 1)
            else:
                has_growing = any(p.get("state") == "growing" for p in state.plots)
                has_ready = any(p.get("state") == "ready" for p in state.plots)

                if mode == "brutal":
                    if not has_ready and not has_growing:
                        idle = 0 
                        state.action = "Menunggu saldo atau bibit baru..."
                    else:
                        idle = 0
                        closest = None
                        min_time = 999999999
                        now_ms = int(time.time() * 1000)
                        for p in state.plots:
                            if p.get("state") == "growing" and p.get("readyAt"):
                                rem = p.get("readyAt") - now_ms
                                if 0 < rem < min_time:
                                    min_time = rem
                                    closest = p
                        if closest:
                            m, s_val = divmod(min_time // 1000, 60)
                            name = closest.get("name", "Tanaman")
                            state.action = f"Menunggu panen {name[:5]}... ({m}m {s_val}s)"
                        else:
                            state.action = "Mode Brutal Berjalan..."
                    interruptible_sleep(state, 2)
                elif mode == "harvest":
                    if has_growing:
                        idle = 0
                        state.action = "Menunggu tanaman siap panen..."
                        interruptible_sleep(state, 2)
                    elif not has_ready and not has_growing:
                        idle += 1
                        state.action = f"Kebun kosong / tidak ada panen ({idle}/5)"
                        interruptible_sleep(state, 2)
                elif mode == "water":
                    idle += 1
                    state.action = "Semua tanaman sudah disiram"
                    interruptible_sleep(state, 2)
                elif mode == "plant":
                    if has_growing:
                        idle = 0
                        state.action = "Menunggu panen..."
                        interruptible_sleep(state, 5)
                    else:
                        idle += 1
                        state.action = f"IDLE SCANNING ({idle}/5)"
                        interruptible_sleep(state, 2)
                
        if not user_cancelled:
            state.log(f"{fg(C_WARN)}Tanaman masih dalam pertumbuhan Bre!{RST}", "wr")
            interruptible_sleep(state, 1.5)
            
    except KeyboardInterrupt:
        user_cancelled = True
    finally:
        signal.signal(signal.SIGINT, old)
        dashboard.stop()
    
    if not user_cancelled:
        try: input(f"\n{fg(C_DIM)}[ PRESS ENTER TO DISCONNECT ]{RST}")
        except (KeyboardInterrupt, EOFError): pass

def best_affordable_crop(crops, coins, strategy="payout"):
    """
    strategy:
      'payout'    -> default/original: payout tertinggi
      'cheap'     -> menu 2 pilihan 1: plantCost termurah yg afford
      'expensive' -> menu 2 pilihan 2: plantCost termahal yg afford
      'random'    -> menu 5 (Kerja Rodi): acak antara termurah & termahal yg afford
      list[str]   -> menu 2 pilihan 3 (CUSTOM): pilih dari bibit yg dipilih user
    """
    if not crops: return "wheat", 30
    unlocked = [c for c in crops if not c.get("locked", True)]
    if not unlocked: return "wheat", 30

    if isinstance(strategy, list):
        custom_crops = [c for c in unlocked if c.get("id") in strategy]
        if not custom_crops:
            custom_crops = unlocked

        affordable = [c for c in custom_crops if c.get("plantCost", 0) <= coins]
        if affordable:
            best = random.choice(affordable)
            return best.get("id", "wheat"), best.get("plantCost", 0)

        cheapest = min(custom_crops, key=lambda x: x.get("plantCost", 999999))
        return cheapest.get("id", "wheat"), cheapest.get("plantCost", 999999)

    affordable = [c for c in unlocked if c.get("plantCost", 0) <= coins]
    if affordable:
        if strategy == "cheap":
            best = min(affordable, key=lambda x: x.get("plantCost", 999999))
        elif strategy == "expensive":
            best = max(affordable, key=lambda x: x.get("plantCost", 0))
        elif strategy == "random":
            cheapest = min(affordable, key=lambda x: x.get("plantCost", 999999))
            priciest = max(affordable, key=lambda x: x.get("plantCost", 0))
            best = random.choice([cheapest, priciest])
        else:
            best = max(affordable, key=lambda x: x.get("payout", 0))
        return best.get("id", "wheat"), best.get("plantCost", 0)

    cheapest = min(unlocked, key=lambda x: x.get("plantCost", 999999))
    return cheapest.get("id", "wheat"), cheapest.get("plantCost", 999999)

# ═══════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════
def main():
    cfg = initial_setup()
    if not cfg:
        print(f"\n{fg(C_ERR)}Tidak bisa jalan tanpa init data valid.{RST}"); sys.exit(1)

    while True:
        pilih = show_main_menu(cfg)
        if pilih == "1": run_focused(cfg, "task")
        elif pilih == "2":
            strat = ask_plant_strategy(cfg)
            if strat is None:
                continue
            run_focused(cfg, "plant", strat)
        elif pilih == "3": run_focused(cfg, "water")
        elif pilih == "4": run_focused(cfg, "harvest")
        elif pilih == "5": run_focused(cfg, "brutal")
        elif pilih == "6":
            if isi_data(): cfg = Config.load() or cfg
        elif pilih == "7" or pilih == "0":
            print(f"\n{fg(C_HDR_1)}Sampai jumpa, Bos.{RST}\n"); sys.exit(0)
        else:
            print(f"\n{fg(C_ERR)}Pilihan tidak valid.{RST}"); time.sleep(1)

        sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n\n{fg(C_ERR)}=== CRITICAL SYSTEM FAILURE ==={RST}")
        traceback.print_exc()
        print(f"{fg(C_ERR)}==============================={RST}")
        input("\nTekan Enter untuk keluar...")
