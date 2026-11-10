#!/usr/bin/env python3
# Python port of bot.php
# Dependency: python3 -m pip install requests

import json
import os
import random
import re
import sys
import time
from dataclasses import dataclass, field

import requests

BASE_URL = "https://clipcoin.pro"
COOKIE_FILE = "clipcoin_cookie.txt"
TIMEOUT = (30, 30)

RST = "\033[0m"
BOLD = "\033[1m"

def fg(color):
    return f"\033[38;5;{color}m"

C_HDR_1, C_ERR, C_WARN, C_OK = 51, 196, 208, 115
HACK_CYAN, HACK_YELLOW = 51, 226
HACK_ORANGE, BRIGHT_WHITE = 214, 255
BRIGHT_GREEN, NEON_LIME = 115, 118
SOFT_YELLOW, SOFT_WHITE, SOFT_LIGHT_BLUE = 228, 253, 117



# ========  AUTO LOGIN ========
from playwright.sync_api import sync_playwright

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
            page.goto(BASE_URL+"/home")
            page.wait_for_load_state("networkidle")  # tunggu redirect selesai

            if not sudah_login(page):
                print("Belum login, silakan login di jendela...")
                page.wait_for_url("**/home", timeout=300_000)  # tunggu sampai 5 menit
                print("Login berhasil, sesi tersimpan")
            else:
                print("Sudah login.")

                cookies = ctx.cookies(BASE_URL)      # hanya untuk situs tertentu

                # Ubah list of dict menjadi format "nama=nilai; nama2=nilai2"
                cookie_str = "; ".join(f"{c['name']}={c['value']}" for c in cookies)

                print(cookie_str)
                return cookie_str

                #with open("cookies.json", "w", encoding="utf-8") as f:
                #    json.dump(cookies, f, indent=2)

        finally:
            ctx.close()  # penting: tutup normal supaya sesi tertulis ke disk

# ========  AUTO LOGIN ========



@dataclass
class State:
    user: str = "-"
    phase: str = "boot"
    action: str = "idle"
    start_time: float = field(default_factory=time.time)
    requests_made: int = 0
    errors: int = 0
    usd_balance: float = 0.0
    coins: int = 0
    task_ready: bool = False
    last_status: str = "idle"
    next_claim: int = 0
    total_tasks: int = 540
    remaining_tasks: int = 540
    watched_count: int = 0


class ClipCoinBot:
    def __init__(self):
        self.session = requests.Session()
        self.cookie = ""
        self.state = State()

        self.session.headers.update({
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": (
                "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/139.0.0.0 Mobile Safari/537.36"
            ),
            "Origin": BASE_URL,
            "Referer": BASE_URL + "/watch",
        })

    def clear_screen(self):
        os.system("cls" if os.name == "nt" else "clear")

    def type_colored_line(self, text, delay=0.04):
        parts = re.findall(r"\x1b\[[0-9;]*m|.", text, flags=re.S)

        for part in parts:
            print(part, end="", flush=True)

            if not part.startswith("\033"):
                time.sleep(delay)

        print()

    def print_banner(self):
        art = [
            " ██████╗██╗     ██╗██████╗  ██████╗ ██████╗ ██╗███╗   ██╗",
            "██╔════╝██║     ██║██╔══██╗██╔════╝██╔═══██╗██║████╗  ██║",
            "██║     ██║     ██║██████╔╝██║     ██║   ██║██║██╔██╗ ██║",
            "██║     ██║     ██║██╔═══╝ ██║     ██║   ██║██║██║╚██╗██║",
            "╚██████╗███████╗██║██║     ╚██████╗╚██████╔╝██║██║ ╚████║",
            " ╚═════╝╚══════╝╚═╝╚═╝      ╚═════╝ ╚═════╝ ╚═╝╚═╝  ╚═══╝",
        ]

        gradient = [27, 33, 63, 99, 141, 177]
        width = 56

        print()

        for i, line in enumerate(art):
            pad = max(0, (width - len(line)) // 2)

            print(
                "  " + " " * pad +
                BOLD + fg(gradient[i]) + line + RST
            )

        def framed(text, color):
            pad_left = max(0, (width - len(text)) // 2)
            pad_right = max(0, width - len(text) - pad_left)

            return (
                fg(SOFT_YELLOW) + "│" + RST +
                " " * pad_left +
                color + text + RST +
                " " * pad_right +
                fg(SOFT_YELLOW) + "│" + RST
            )

        print("  " + fg(SOFT_YELLOW) + "┌" + "─" * width + "┐" + RST)
        print("  " + framed("ClipCoin Auto-Watcher", fg(HACK_ORANGE)))
        print("  " + framed("https://clipcoin.pro/u/llber", BOLD + fg(BRIGHT_WHITE)))
        print("  " + framed("Mod by Jendela Semesta REBORN", fg(HACK_CYAN)))
        print("  " + framed("Join my Group Telegram", fg(BRIGHT_WHITE)))
        print("  " + framed("https://t.me/jendelasemesta", fg(121)))
        print("  " + fg(SOFT_YELLOW) + "└" + "─" * width + "┘" + RST + "\n")

    def load_cookie(self):
        try:
            with open(COOKIE_FILE, "r", encoding="utf-8") as f:
                self.cookie = f.read().strip()

        except FileNotFoundError:
            self.cookie = ""

        if self.cookie:
            self.session.headers["Cookie"] = self.cookie

    def save_cookie(self, value):
        self.cookie = value.strip()

        with open(COOKIE_FILE, "w", encoding="utf-8") as f:
            f.write(self.cookie)

        self.session.headers["Cookie"] = self.cookie

    def request(self, endpoint, data=None):
        self.state.requests_made += 1

        try:
            response = self.session.post(
                BASE_URL + endpoint,
                data=data or {},
                timeout=TIMEOUT,
            )

            response.raise_for_status()

            try:
                return response.json()

            except ValueError:
                print(f"\n{fg(C_ERR)}Respons server bukan JSON.{RST}")
                return None

        except requests.RequestException as exc:
            self.state.errors += 1

            print(f"\n{fg(C_ERR)}HTTP error: {exc}{RST}")

            return None

    def check_cookie_validity(self):
        result = self.request(
            "/api/user/",
            {"method": "getCurrentUser"}
        )

        if not isinstance(result, dict):
            return False

        data = result.get("data") or {}

        if result.get("status") == "ok" and data.get("id"):
            self.state.usd_balance = float(data.get("balance") or 0)
            self.state.coins = int(data.get("coins") or 0)
            self.state.user = data.get("email") or "-"

            return True

        return False

    def get_task(self):
        result = self.request(
            "/api/user/tasks/",
            {"method": "get"}
        )

        if not isinstance(result, dict):
            return None

        task_data = result.get("data")

        if result.get("status") == "ok" and task_data:

            if "limitDayAll" in task_data and "limitDay" in task_data:
                self.state.total_tasks = int(task_data["limitDayAll"])

                self.state.remaining_tasks = int(task_data["limitDay"])

                self.state.watched_count = (
                    self.state.total_tasks -
                    self.state.remaining_tasks
                )

            return task_data

        return None

    def start_task(self, task_id):
        result = self.request(
            "/api/user/tasks/start/",
            {"TaskId": str(task_id)}
        )

        return (
            isinstance(result, dict)
            and result.get("status") == "ok"
        )

    def claim_reward(self):
        result = self.request(
            "/api/user/captcha/check/",
            {"refreshTask": "0"}
        )

        if isinstance(result, dict) and result.get("status") == "ok":
            data = result.get("data") or {}

            return float(data.get("reward") or 0)

        return False

    def run_autowatch(self):

        while True:
            self.clear_screen()
            self.print_banner()

            print("⏳ Memvalidasi Cookie...\n")

            if self.check_cookie_validity():
                break

            self.clear_screen()
            self.print_banner()

            print(
                f"{fg(C_ERR)}"
                "❌ SESI LOGIN TIDAK VALID / COOKIE EXPIRED!"
                f"{RST}"
            )

            print(
                f"{fg(C_WARN)}"
                "Server ClipCoin menolak cookie."
                f"{RST}"
            )

            print(
                f"{fg(HACK_CYAN)}"
                "Masukkan Cookie Baru (ENTER untuk kembali ke menu): "
                f"{RST}",
                end=""
            )

            new_cookie = input().strip()

            if not new_cookie:
                return

            self.save_cookie(new_cookie)

            print(
                f"\n{fg(C_OK)}"
                "Cookie berhasil disimpan. Mengecek ulang..."
                f"{RST}"
            )

            time.sleep(1.5)

        self.clear_screen()
        self.print_banner()

        print("✅ Cookie valid. Memulai Auto-Watch...\n")

        self.state.phase = "watch"

        while True:

            delay = random.randint(2, 5)

            print(
                f"\r⏳ Mengambil task... (Jeda {delay} dtk)  ",
                end="",
                flush=True
            )

            time.sleep(delay)

            task = self.get_task()

            if not task:
                print(
                    f"\n{fg(C_WARN)}"
                    "⚠️ Gagal mendapat task / limit harian habis."
                    f"{RST}"
                )

                input(
                    "Tekan ENTER untuk mencoba lagi, "
                    "atau CTRL+C untuk kembali..."
                )

                continue

            task_id = task.get("id", "")

            duration = int(task.get("duration") or 12)

            task_num = self.state.watched_count + 1

            if not self.start_task(task_id):

                print(
                    f"\n{fg(HACK_CYAN)}"
                    f"❌ Gagal start task ID: {task_id}"
                    f"{RST}"
                )

                print(
                    f"{fg(BRIGHT_WHITE)}"
                    "Selesaikan CAPTCHA atau pemeriksaan "
                    "yang diminta melalui situs resmi."
                    f"{RST}"
                )

                input(
                    f"{fg(HACK_YELLOW)}"
                    "Tekan ENTER setelah selesai..."
                    f"{RST}"
                )

                continue

            watch_time = duration + random.randint(3, 7)

            end_time = time.time() + watch_time

            while time.time() < end_time:

                remaining = int(end_time - time.time())

                print(
                    f"\r🎦 Menunggu durasi task... "
                    f"(Sisa: {remaining}s)   ",
                    end="",
                    flush=True
                )

                time.sleep(1)

            print("\r\033[K", end="")

            reward = self.claim_reward()

            if reward is not False:

                self.check_cookie_validity()

                pause = random.randint(10, 25)

                distracted = random.randint(1, 100) <= 5

                if distracted:
                    pause += random.randint(30, 60)

                sep = fg(SOFT_WHITE) + "-" * 50 + RST

                self.type_colored_line(sep, 0.01)

                self.type_colored_line(
                    "⭐️ " + BOLD + fg(BRIGHT_WHITE) +
                    f"Total Tugas {self.state.total_tasks}" + RST,
                    0.03
                )

                self.type_colored_line(
                    "🍿 " + BOLD + fg(HACK_YELLOW) +
                    f"Ini Tugas ke {task_num}" + RST,
                    0.03
                )

                self.type_colored_line(
                    "🌱 " + fg(HACK_CYAN) +
                    "Tugas selesai" + RST,
                    0.03
                )

                self.type_colored_line(
                    "✅ Claim berhasil" + RST,
                    0.03
                )

                self.type_colored_line(
                    "💰 Reward           : $" +
                    f"{reward:.5f}" + RST,
                    0.04
                )

                self.type_colored_line(
                    "🕝 Sisa video ads   : " +
                    f"{self.state.remaining_tasks} video lagi" + RST,
                    0.04
                )

                self.type_colored_line(
                    "   TOTAL BALANCE    : $" +
                    f"{self.state.usd_balance:.5f} | "
                    f"{self.state.coins} Coins" + RST,
                    0.04
                )

                self.type_colored_line(sep, 0.01)

                note = " (Istirahat dulu)" if distracted else ""

                self.type_colored_line(
                    f"Next Claim dalam "
                    f"{fg(SOFT_LIGHT_BLUE)}"
                    f"{pause} detik{note}{RST}",
                    0.03
                )

                time.sleep(random.uniform(0.1, 0.9))

                time.sleep(pause)

            else:

                print(
                    f"{fg(C_ERR)}"
                    "❌ Klaim gagal atau ditolak server."
                    f"{RST}"
                )

                input("Tekan ENTER untuk melanjutkan...")

                time.sleep(5)

    def main(self):

        self.load_cookie()

        if not self.cookie:

            self.clear_screen()
            self.print_banner()

            value = ambil_cookie()

            #value = input(
            #    f"{fg(HACK_CYAN)}"
            #    "Masukkan Cookie ClipCoin: "
            #    f"{RST}"
            #).strip()

            if not value:

                print(
                    f"\n{fg(C_ERR)}"
                    "Cookie tidak boleh kosong!"
                    f"{RST}"
                )

                return

            self.save_cookie(value)

            print(
                f"\n{fg(C_OK)}"
                "Cookie berhasil disimpan!"
                f"{RST}"
            )

            time.sleep(1)

        while True:

            self.state = State()

            self.clear_screen()
            self.print_banner()

            print(f"{fg(HACK_CYAN)}Menu Garapan:{RST}\n")

            print(f"{fg(BRIGHT_WHITE)}1. Tonton Video{RST}")
            print(f"{fg(BRIGHT_WHITE)}2. Update Cookie{RST}")
            print(f"{fg(BRIGHT_WHITE)}3. Keluar{RST}\n")

            choice = "1" #input("▸ Pilih menu: ").strip()

            if choice == "1":

                try:
                    self.run_autowatch()

                except KeyboardInterrupt:

                    print(
                        f"\n\n{fg(C_WARN)}"
                        "Kembali ke menu..."
                        f"{RST}"
                    )

                    time.sleep(1)

            elif choice == "2":

                self.clear_screen()
                self.print_banner()

                value = input(
                    f"{fg(HACK_CYAN)}"
                    "Masukkan Cookie Baru: "
                    f"{RST}"
                ).strip()

                if value:

                    self.save_cookie(value)

                    print(
                        f"\n{fg(C_OK)}"
                        "Cookie berhasil disimpan!"
                        f"{RST}"
                    )

                else:

                    print(
                        f"\n{fg(C_ERR)}"
                        "Cookie kosong, update dibatalkan."
                        f"{RST}"
                    )

                input("\nTekan ENTER untuk kembali...")

            elif choice == "3":

                print(
                    f"\n{fg(C_HDR_1)}"
                    "Sampai jumpa."
                    f"{RST}\n"
                )

                return

            else:

                print(
                    f"\n{fg(C_ERR)}"
                    "Pilihan tidak valid."
                    f"{RST}"
                )

                time.sleep(1)


if __name__ == "__main__":

    try:
        ClipCoinBot().main()

    except KeyboardInterrupt:
        print("\nDihentikan oleh pengguna.")
