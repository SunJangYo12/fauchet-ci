<?php
set_time_limit(0);
ini_set('memory_limit', '-1');
error_reporting(0);
date_default_timezone_set('Asia/Jakarta');

const RST  = "\033[0m";
const BOLD = "\033[1m";
function fg($c) { return "\033[38;5;{$c}m"; }

const C_HDR_1 = 51;
const C_HDR_2 = 213;
const C_ACCENT = 226;
const C_OK = 115; 
const C_WARN = 208;
const C_ERR = 196;
const C_DIM = 240;
const C_TEXT = 252;

const HACK_GREEN = 115; 
const HACK_CYAN = 51;
const HACK_DIM = 255;
const HACK_YELLOW = 226;
const HACK_PINK = 218;
const HACK_ORANGE = 214;

const SOFT_YELLOW = 228;
const SOFT_ORANGE = 216;
const SOFT_BLUE   = 111;
const SOFT_WHITE  = 253; 
const BRIGHT_GREEN= 115; 
const BRIGHT_WHITE= 255;
const NEON_GREEN  = 115; 
const PASTEL_GREEN = 115; 
const SOFT_LIGHT_BLUE = 117;

const NEON_LIME = 118; 

$cookieFile = "clipcoin_cookie.txt";
$cookie = "";

// === FINGERPRINT ===
$fin_data = "fin%5BvideoCard%5D%5Bvendor%5D=Google+Inc.+%28ARM%29&fin%5BvideoCard%5D%5Brenderer%5D=ANGLE+%28ARM%2C+Mali-G76%2C+OpenGL+ES+3.2%29&fin%5BviewPort%5D%5Bh%5D=732&fin%5BviewPort%5D%5Bw%5D=412&fin%5BviewPort%5D%5BhM%5D=869&fin%5BviewPort%5D%5BwM%5D=412&fin%5Bplatform%5D=Linux+armv81&fin%5Bdpr%5D=1.75&fin%5Bmulti%5D%5Bspeakers%5D=1&fin%5Bmulti%5D%5Bmicros%5D=1&fin%5Bmulti%5D%5Bwebcams%5D=4&fin%5Bmulti%5D%5Bdevices%5D=1&fin%5Bori%5D%5Balpha%5D=72.9&fin%5Bori%5D%5Bbeta%5D=119.30000000000001&fin%5Bori%5D%5Bgamma%5D=-39.800000000000004&fin%5Bori%5D%5Bis%5D=1&fin%5Bv%5D=2.7&fin%5Bcl%5D%5Bx%5D=355&fin%5Bcl%5D%5By%5D=253&fin%5BwebDef%5D=false&fin%5BnavName%5D=Navigator&fin%5Btouch%5D=true&fin%5Bc%5D=139&fin%5Bmemory%5D=8&fin%5Bconcur%5D=8&fin%5Ben%5D%5Bar%5D=&fin%5Ben%5D%5Bb%5D=139&fin%5Ben%5D%5Bm%5D=SM-N975F&fin%5Ben%5D%5Bp%5D=Android&fin%5Ben%5D%5Bpv%5D=12.0.0&fin%5Bbat%5D%5Bcharging%5D=0&fin%5Bbat%5D%5Blvl%5D=0.82&fin%5Bx%5D%5Bgl%5D%5Btc%5D=astc%2Cetc%2Cetc1&fin%5Bx%5D%5Bgl%5D%5Bn%5D=24&fin%5Bx%5D%5Bgl%5D%5Bh%5D=9fb7d652&fin%5Bx%5D%5Bgl%5D%5Bp%5D=4096%7C16383%7C16383%7C1024%7C1024%7C31%7C16%7C4095.9375%7C23&fin%5Bx%5D%5Btp%5D%5Bt%5D=touch&fin%5Bx%5D%5Btp%5D%5Bpr%5D=1&fin%5Bx%5D%5Btp%5D%5Bw%5D=1.41&fin%5Bx%5D%5Btp%5D%5Bh%5D=1.41&fin%5Bx%5D%5Btp%5D%5Bd%5D=117&fin%5Bx%5D%5Btp%5D%5Btr%5D=1&fin%5Bx%5D%5Bmq%5D%5Bf%5D=1&fin%5Bx%5D%5Bmq%5D%5Bhv%5D=1&fin%5Bx%5D%5Bmq%5D%5Bc%5D=1&fin%5Bx%5D%5Bmq%5D%5Bmt%5D=5&fin%5Bx%5D%5Bmo%5D%5Bn%5D=1152&fin%5Bx%5D%5Bmo%5D%5Bg%5D=9.788&fin%5Bx%5D%5Bmo%5D%5Bs%5D=0.121&fin%5Bx%5D%5Bmo%5D%5Bz%5D=0&fin%5Bx%5D%5Btz%5D%5Bz%5D=Asia%2FJakarta&fin%5Bx%5D%5Btz%5D%5Bo%5D=-420&fin%5Bx%5D%5Btz%5D%5Bl%5D=id-ID%2Cen-US%2Cid&fin%5Bx%5D%5Bau%5D%5Bwd%5D=0&fin%5Bx%5D%5Bau%5D%5Bcdc%5D=0&fin%5Bx%5D%5Bau%5D%5Bcdp%5D=0&fin%5Bx%5D%5Bau%5D%5Bmv%5D=0&fin%5Bx%5D%5Bau%5D%5Bmt%5D=0&fin%5Bx%5D%5Bcn%5D%5Bt%5D=wifi&fin%5Bx%5D%5Bcn%5D%5Be%5D=4g&fin%5Bx%5D%5Bcn%5D%5Br%5D=100&fin%5Bx%5D%5Bcn%5D%5Bd%5D=10&fin%5Bx%5D%5Bbt%5D%5Bct%5D=-1&fin%5Bx%5D%5Bbt%5D%5Bdt%5D=10053482";

class State {
    public $user = "-";
    public $phase = "boot";
    public $action = "idle";
    public $start_time;
    public $requests_made = 0;
    public $errors = 0;
    public $usd_balance = 0.0;
    public $coins = 0;
    public $task_ready = false;
    public $last_status = "idle";
    public $next_claim = 0;
    
    public $total_tasks = 540;
    public $remaining_tasks = 540;
    public $watched_count = 0;
    
    public function __construct() {
        $this->start_time = time();
    }
}

function clear_screen() {
    echo "\033[2J\033[H\033[3J";
}

function type_colored_line($text, $delay = 0.04) {
    $pattern = '/(\x1b\[[0-9;]*m|.)/su';
    preg_match_all($pattern, $text, $matches);
    foreach ($matches[1] as $char) {
        echo $char;
        flush();
        if (strpos($char, "\033") === false) {
            usleep((int)($delay * 1000000));
        }
    }
    echo "\n";
}

function print_banner() {
    echo "\n"; 
    $inner_width = 56; 
    $left_margin = "  ";

    $art = [
        " ██████╗██╗     ██╗██████╗  ██████╗ ██████╗ ██╗███╗   ██╗",
        "██╔════╝██║     ██║██╔══██╗██╔════╝██╔═══██╗██║████╗  ██║",
        "██║     ██║     ██║██████╔╝██║     ██║   ██║██║██╔██╗ ██║",
        "██║     ██║     ██║██╔═══╝ ██║     ██║   ██║██║██║╚██╗██║",
        "╚██████╗███████╗██║██║     ╚██████╗╚██████╔╝██║██║ ╚████║",
        " ╚═════╝╚══════╝╚═╝╚═╝      ╚═════╝ ╚═════╝ ╚═╝╚═╝  ╚═══╝"
    ];

    $blue_purple_gradient = [27, 33, 63, 99, 141, 177]; 

    $make_line = function($text, $color) use ($inner_width) {
        $raw = preg_replace('/\x1b\[[0-9;]*m/', '', $text);
        $len = function_exists('mb_strlen') ? mb_strlen($raw, 'UTF-8') : strlen($raw);
        $pad_left = (int) floor(($inner_width - $len) / 2);
        if ($pad_left < 0) $pad_left = 0;
        $pad_right = $inner_width - $len - $pad_left;
        if ($pad_right < 0) $pad_right = 0;
        return fg(SOFT_YELLOW) . "│" . RST . str_repeat(" ", $pad_left) . $color . $text . RST . str_repeat(" ", $pad_right) . fg(SOFT_YELLOW) . "│" . RST;
    };

    foreach ($art as $index => $line) {
        $raw = preg_replace('/\x1b\[[0-9;]*m/', '', $line);
        $len = function_exists('mb_strlen') ? mb_strlen($raw, 'UTF-8') : strlen($raw);
        $pad = (int) floor(($inner_width - $len) / 2);
        if ($pad < 0) $pad = 0;
        
        $color_code = $blue_purple_gradient[$index % count($blue_purple_gradient)];
        echo $left_margin . str_repeat(" ", $pad) . BOLD . fg($color_code) . $line . RST . "\n";
    }
    
    echo $left_margin . fg(SOFT_YELLOW) . "┌" . str_repeat("─", $inner_width) . "┐" . RST . "\n";
    echo $left_margin . $make_line("ClipCoin Auto-Watcher", fg(HACK_ORANGE)) . "\n";
    
    // === TAMBAHAN LINK DI BAWAH AUTO-WATCHER ===
    echo $left_margin . $make_line("https://clipcoin.pro/u/llber", BOLD . fg(BRIGHT_WHITE)) . "\n";
    
    echo $left_margin . $make_line("Mod by Jendela Semesta REBORN", fg(HACK_CYAN)) . "\n";
    echo $left_margin . $make_line("Join my Group Telegram", fg(BRIGHT_WHITE)) . "\n";
    echo $left_margin . $make_line("https://t.me/jendelasemesta", fg(121)) . "\n";
    echo $left_margin . fg(SOFT_YELLOW) . "└" . str_repeat("─", $inner_width) . "┘" . RST . "\n\n";
}

function curl_req($url, $method = 'GET', $data = [], $headers = [], &$state = null) {
    global $cookieFile, $cookie;
    if ($state) $state->requests_made++;
    
    $ch = curl_init();
    $options = [
        CURLOPT_URL            => $url,
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_HEADER         => false,
        CURLOPT_FOLLOWLOCATION => true,
        CURLOPT_SSL_VERIFYHOST => 0,
        CURLOPT_SSL_VERIFYPEER => false,
        CURLOPT_HTTPHEADER     => $headers,
        CURLOPT_CONNECTTIMEOUT => 30,
        CURLOPT_TIMEOUT        => 30,
        CURLOPT_COOKIEFILE     => $cookieFile,
        CURLOPT_COOKIEJAR      => $cookieFile
    ];
    
    if (!empty($cookie)) {
        $options[CURLOPT_COOKIE] = $cookie;
    }
    
    if (strtoupper($method) === 'POST') {
        $options[CURLOPT_POST] = true;
        $options[CURLOPT_POSTFIELDS] = $data;
    }
    
    curl_setopt_array($ch, $options);
    $response = curl_exec($ch);
    
    if ($response === false) {
        if ($state) $state->errors++;
        curl_close($ch);
        return "";
    }
    
    curl_close($ch);
    return $response;
}

function check_cookie_validity(&$state) {
    $headers = [
        "host: clipcoin.pro",
        "content-type: application/x-www-form-urlencoded",
        "accept: application/json, text/plain, */*",
        "user-agent: Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Mobile Safari/537.36",
        "origin: https://clipcoin.pro",
        "referer: https://clipcoin.pro/watch"
    ];
    
    $res = curl_req("https://clipcoin.pro/api/user/", "POST", "method=getCurrentUser", $headers, $state);
    $json = json_decode($res, true);
    
    if (isset($json['status']) && $json['status'] == 'ok' && !empty($json['data']['id'])) {
        $state->usd_balance = floatval($json['data']['balance'] ?? 0);
        $state->coins = intval($json['data']['coins'] ?? 0);
        $state->user = $json['data']['email'] ?? '-';
        return true;
    }
    return false;
}

function get_task(&$state) {
    $headers = [
        "host: clipcoin.pro",
        "content-type: application/x-www-form-urlencoded",
        "accept: application/json, text/plain, */*",
        "user-agent: Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Mobile Safari/537.36",
        "origin: https://clipcoin.pro",
        "referer: https://clipcoin.pro/watch"
    ];
    
    $res = curl_req("https://clipcoin.pro/api/user/tasks/", "POST", "method=get", $headers, $state);
    $json = json_decode($res, true);
    
    if (isset($json['status']) && $json['status'] == 'ok' && !empty($json['data'])) {
        $task_data = $json['data'];
        
        if (isset($task_data['limitDayAll']) && isset($task_data['limitDay'])) {
            $state->total_tasks = (int)$task_data['limitDayAll'];
            $state->remaining_tasks = (int)$task_data['limitDay'];
            $state->watched_count = $state->total_tasks - $state->remaining_tasks;
        }
        
        return $task_data;
    }
    return null;
}

function start_task($task_id, &$state) {
    global $fin_data;
    
    $headers = [
        "host: clipcoin.pro",
        "content-type: application/x-www-form-urlencoded",
        "accept: application/json, text/plain, */*",
        "user-agent: Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Mobile Safari/537.36",
        "origin: https://clipcoin.pro",
        "referer: https://clipcoin.pro/watch"
    ];
    
    $payload = "TaskId=" . $task_id . "&" . $fin_data;
    $res = curl_req("https://clipcoin.pro/api/user/tasks/start/", "POST", $payload, $headers, $state);
    $json = json_decode($res, true);
    
    return (isset($json['status']) && $json['status'] == 'ok');
}

function claim_reward(&$state) {
    $headers = [
        "host: clipcoin.pro",
        "content-type: application/x-www-form-urlencoded",
        "accept: application/json, text/plain, */*",
        "user-agent: Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Mobile Safari/537.36",
        "origin: https://clipcoin.pro",
        "referer: https://clipcoin.pro/watch"
    ];
    
    $res = curl_req("https://clipcoin.pro/api/user/captcha/check/", "POST", "refreshTask=0", $headers, $state);
    $json = json_decode($res, true);
    
    if (isset($json['status']) && $json['status'] == 'ok') {
        return floatval($json['data']['reward'] ?? 0);
    }
    return false;
}

function run_autowatch(&$state) {
    global $cookieFile, $cookie;
    
    // === FITUR AUTO-CHECK & AUTO-ASK COOKIE ===
    while (true) {
        clear_screen();
        print_banner();
        echo "⏳ Memvalidasi Cookie...\n\n";
        
        if (check_cookie_validity($state)) {
            break; 
        }
        
        clear_screen();
        print_banner();
        echo fg(C_ERR) . "❌ SESI LOGIN MATI (COOKIE EXPIRED)!" . RST . "\n";
        echo fg(C_WARN) . "Server ClipCoin menolak cookie lama kamu." . RST . "\n";
        echo fg(C_WARN) . "Silakan ambil Cookie baru dari browser (DevTools)." . RST . "\n\n";
        echo fg(HACK_CYAN) . "Masukkan Cookie Baru (Tekan ENTER untuk batal ke Menu) : " . RST;
        
        $newCookie = trim(fgets(STDIN));
        
        if (empty($newCookie)) {
            return;
        }
        
        file_put_contents($cookieFile, $newCookie);
        $cookie = $newCookie;
        
        echo "\n" . fg(C_OK) . "Cookie berhasil disimpan otomatis!" . RST . "\n";
        echo fg(BRIGHT_WHITE) . "Mengecek ulang validitas..." . RST . "\n";
        sleep(1.5);
    }
    
    clear_screen();
    print_banner();
    echo "✅ Cookie Valid. Memulai Auto-Watch...\n\n";
    
    $state->phase = "watch";

    while (true) {
        $pre_task_delay = rand(2, 5);
        echo "\r⏳ Mengambil task... (Jeda $pre_task_delay dtk)  ";
        sleep($pre_task_delay);

        $task = get_task($state);
        
        if (!$task) {
            echo "\n" . fg(C_WARN) . "⚠️ Gagal dapat task / Limit harian habis." . RST . "\n";
            echo fg(BRIGHT_WHITE) . "Tekan ENTER untuk coba lagi, atau CTRL+C untuk batal." . RST;
            fgets(STDIN);
            continue;
        }

        $task_id = $task['id'] ?? '';
        $duration = intval($task['duration'] ?? 12);
        $task_num = $state->watched_count + 1;

        // --- TANGKAP ERROR CAPTCHA / START GAGAL ---
        if (!start_task($task_id, $state)) {
            echo "\n" . fg(HACK_CYAN) . "❌ Gagal start task ID: $task_id" . RST . "\n";
            echo fg(BRIGHT_WHITE) . "Silakan buka browser, Tonton 1 Video lalu kerjakan CAPTCHA-nya." . RST . "\n";
            echo fg(HACK_YELLOW) . "Tekan ENTER jika CAPTCHA sudah selesai dikerjakan" . RST;
            fgets(STDIN);
            continue; // Coba ambil task lagi setelah user tekan enter
        }

        // Nonton (Durasi Asli + Jeda 3-7 detik)
        $watch_time = $duration + rand(3, 7);
        $end_time = time() + $watch_time;
        
        while (time() < $end_time) {
            $rem = $end_time - time();
            echo "\r🎦 Sedang menonton video... (Sisa: {$rem}s)   ";
            sleep(1);
        }
        echo "\r\033[K"; 

        $reward = claim_reward($state);
        
        if ($reward !== false) {
            check_cookie_validity($state);
            
            $jeda = rand(10, 25); 
            $is_distracted = rand(1, 100) <= 5; 
            if ($is_distracted) {
                $jeda += rand(30, 60);
            }

            $sep = fg(SOFT_WHITE) . str_repeat("-", 50) . RST;
            
            // === SUSUNAN LOG ===
            type_colored_line($sep, 0.01); 
            type_colored_line("⭐️ " . BOLD . fg(BRIGHT_WHITE) . "Total Tugas {$state->total_tasks}" . RST, 0.03);
            type_colored_line("🍿 " . BOLD . fg(HACK_YELLOW) . "Ini Tugas ke {$task_num}" . RST, 0.03);
            type_colored_line("🌱 " . fg(HACK_CYAN) . "Tugas Selesai Bos" . RST, 0.03);
            type_colored_line("✅️ " . fg(BRIGHT_GREEN) . "Claim SUKSES BRE!" . RST, 0.03);
            type_colored_line("💰 " . fg(BRIGHT_GREEN) . "Reward           : $" . number_format($reward, 5) . RST, 0.04);
            type_colored_line("🕝 " . fg(BRIGHT_WHITE) . "Sisa video ads   : " . $state->remaining_tasks . " video lagi" . RST, 0.04);
            type_colored_line("   " . fg(NEON_LIME) . "TOTAL BALANCE    : $" . number_format($state->usd_balance, 5) . " | " . $state->coins . " Coins" . RST, 0.04);
            type_colored_line($sep, 0.01); 
            
            if ($is_distracted) {
                type_colored_line("Next Claim dalam " . fg(SOFT_LIGHT_BLUE) . "{$jeda} detik (Istirahat dulu bre)" . RST, 0.03);
            } else {
                type_colored_line("Next Claim dalam " . fg(SOFT_LIGHT_BLUE) . "{$jeda} detik" . RST, 0.03);
            }
            
            // Eksekusi Jeda (Tanpa nunggu ENTER)
            usleep(rand(100000, 900000)); 
            sleep($jeda);
            
        } else {
            echo fg(C_ERR) . "❌ Gagal klaim (Anti-bot / Limit)." . RST . "\n";
            echo fg(BRIGHT_WHITE) . "Tekan ENTER untuk melanjutkan..." . RST;
            fgets(STDIN);
            sleep(5);
        }
    }
}

if (function_exists('pcntl_signal')) {
    pcntl_async_signals(true);
    pcntl_signal(SIGINT, function() {
        throw new Exception("User Interrupt");
    });
}

// ==========================================
// LOGIKA MINTA COOKIE DI AWAL (SEBELUM MENU)
// ==========================================
if (file_exists($cookieFile)) {
    $cookie = trim(file_get_contents($cookieFile));
}

if (empty($cookie)) {
    clear_screen();
    print_banner();
    echo fg(HACK_CYAN) . "Masukkan Cookie ClipCoin : " . RST; 
    $inputCookie = trim(fgets(STDIN));
    
    if (!empty($inputCookie)) {
        file_put_contents($cookieFile, $inputCookie); 
        $cookie = $inputCookie;
        echo "\n" . fg(C_OK) . "Cookie berhasil disimpan!" . RST . "\n";
        sleep(1);
    } else {
        echo "\n" . fg(C_ERR) . "Cookie tidak boleh kosong!" . RST . "\n";
        sleep(2);
        exit;
    }
}
// ==========================================

while (true) {
    try {
        $state = new State();
        
        clear_screen();
        print_banner();
        
        echo fg(HACK_CYAN) . "Menu Garapan :" . RST . "\n\n";
        echo fg(BRIGHT_WHITE) . "1. Tonton Video" . RST . "\n";
        echo fg(BRIGHT_WHITE) . "2. Update Cookie" . RST . "\n";
        echo fg(BRIGHT_WHITE) . "3. Keluar" . RST . "\n\n";
        echo "▸ Pilih menu : ";
        
        $choice = trim(fgets(STDIN));
        
        if ($choice == "1") {
            run_autowatch($state);
            
        } elseif ($choice == "2") {
            clear_screen();
            print_banner();
            echo fg(HACK_CYAN) . "Masukkan Cookie Baru : " . RST;
            $newCookie = trim(fgets(STDIN));
            if (!empty($newCookie)) {
                file_put_contents($cookieFile, $newCookie); 
                $cookie = $newCookie;
                echo "\n" . fg(C_OK) . "Cookie berhasil disimpan otomatis!" . RST . "\n";
            } else {
                echo "\n" . fg(C_ERR) . "Cookie kosong, update dibatalkan." . RST . "\n";
            }
            echo "\nTekan Enter untuk kembali...";
            fgets(STDIN);
            
        } elseif ($choice == "3") {
            echo "\n" . fg(C_HDR_1) . "Sampai jumpa, Bos." . RST . "\n\n";
            exit;
            
        } else {
            echo "\n" . fg(C_ERR) . "Pilihan tidak valid." . RST;
            sleep(1);
        }
        
    } catch (Exception $e) {
        if ($e->getMessage() === "User Interrupt") {
            echo "\n\n" . fg(C_WARN) . "Kembali ke menu..." . RST . "\n";
            sleep(1);
        } else {
            echo "\n\n" . fg(C_ERR) . "Critical Error: " . $e->getMessage() . RST . "\n";
            sleep(2);
        }
    }
}
