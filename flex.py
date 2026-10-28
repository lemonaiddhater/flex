#!/usr/bin/env python3
# ================= CRYPTOFLEX v8.0 :: LIVE SIMULATED FLEX ENGINE =================
import os, sys, json, time, random, string, datetime, urllib.request

DATA_DIR = os.path.expanduser("~/cryptoflex")
os.makedirs(DATA_DIR, exist_ok=True)
KEY_FILE, WALLET_FILE, LOG_FILE, CACHE_FILE, CONF_FILE = (os.path.join(DATA_DIR, f) for f in
    ("keys.json", "wallet.json", "logs.json", "price_cache.json", "config.json"))

# ================= THEMES =================
THEMES = ["blue", "green", "cyan", "red", "purple", "yellow", "rainbow", "ice"]
theme = "blue"
COLS = {"blue": "\033[94m", "green": "\033[92m", "cyan": "\033[96m", "red": "\033[91m",
        "purple": "\033[95m", "yellow": "\033[93m", "ice": "\033[36m"}
RAINBOW = ["\033[91m", "\033[93m", "\033[92m", "\033[96m", "\033[94m", "\033[95m"]
DIM, BOLD, RESET = "\033[2m", "\033[1m", "\033[0m"
OK, WARN, BAD = "\033[92m", "\033[93m", "\033[91m"

def paint(s):
    if theme == "rainbow":
        return "".join(RAINBOW[i % len(RAINBOW)] + ch + RESET for i, ch in enumerate(s))
    return COLS.get(theme, COLS["blue"]) + s + RESET

def gradient(s):
    out = []
    for i, line in enumerate(s.split("\n")):
        c = RAINBOW[i % len(RAINBOW)] if theme == "rainbow" else COLS.get(theme, COLS["blue"])
        out.append(c + line + RESET)
    return "\n".join(out)

BANNER = r"""
    ____  ____________  ______  ____  __ __  ______  __ __   ___   ____
   / __ \/ ____/ ____/ / ____/ / __ \/ // / / ___/ |/ /  | / _ | / __/
  / /_/ / /   / /_    / /     / /_/ / _  / / / _ |    /  |/ __ | _ \
 / ____/ /___/ __/  / /___  / ____/ // / / /  |_|_/_/ |_/____|/____/
/_/    \____/____/  \____/ /_/   /_//_/ /_/ ========================>
"""

ASCII_ART = {
"TOOLS": r"""
  _______ _____ _____ __  __
 |__   __|_   _|_   _|  \/  |
    | |    | |   | | | \  / |
    | |    | |   | | | |\/| |
    | |   _| |_ _| |_| |  | |
    |_|  |_____|_____|_|  |_|
""",
"WALLET": r"""
  __        ___    _ _  __        __    _
  \ \      / / \  | | |/ /  __ _ / _|  | |__
   \ \ /\ / / _ \ | | ' /  / _` | |_   | '_ \
    \ V  V / ___ \| | . \ | (_| |  _|  | |_) |
     \_/\_/_/   \_\_|_|\_\ \__,_|_|(_)|_.__/
""",
"PORTFOLIO": r"""
   ___  _   _ _____ ___ _     ___ _____   _   _ ___ ___ ___  _  _ ___
  | _ \:|_| |_   _| __:|:|   |_ _|_   _| :| | | | __| __| _ \| \| | __|
  |  _/ | | | | | | _||_  _|  | |  | |    | |_| | _|| _|| v /|  ' | _|
  |_|   \_/  |_| |___| |_|   |___| |_|     \___/|___|___|_|_\|_|\_|___|
""",
"MARKET": r"""
  __  __    _    ____  __  ___ _   _
 |  \/  |  / \  |  _ \|  \/  | | | |
 | |\/| | / _ \ | |_) | |\/| | | | |
 | |  | |/ ___ \|  _ <| |  | | |_| |
 |_|  |_/_/   \_\_| \_\_|  |_|\___/
""",
"MINER": r"""
  __  __ ___ _  _ _____ ___ ___    ___ _    ___ ___  ___ __  __ ___ _  _   _
 |  \/  |_ _| \| |_   _|_ _/ __|  |_ _| |  | __| _ \|_ _|  \/  |_ _| \| | /_\
 | |\/| || || .  | | |  | | (__    | || |__| _||   / | || |\/| || ||  ' |/ _ \
 |_|  |_|___|_|\_| |_| |___\___|  |___|____|___|_|_\|___|_|  |_|___|_|\_|_/_/
""",
"DRAINER": r"""
  ____  _____ _   _ _____ _____ _____ ____
 |  _ \| ____| \ | |_   _|_   _| ____|  _ \
 | | | |  _| |  \| | | |   | | |  _| | |_) |
 | |_| | |___| |\  | | |   | | | |___|  _ <
 |____/|_____|_| \_| |_|   |_| |_____|_| \_\
""",
"SPOOF": r"""
  ____  ___  ____   ___  ____    ____  ___   ___  ____  ____  ____
 / ___|/ _ \|  _ \ / _ \|  _ \  / ___|/ _ \ / _ \|  _ \|  _ \|  _ \
 \___ \(_) | |_) |(_) | | | | | \___ \(_) |(_) | |_) | |_) | |_) |
  ___) \  _|  _ < \  _/| |_| |   ___) \  _| \  _/|  __/|  __/|  __/
 |____/ |_| |_| \_\ |_| |____/   |____/|_|   |_| |_|   |_|   |_|
""",
"SNIFFER": r"""
  ____  _   _ ___ _____ _    ___ _____ _   _ _____
 / ___|| | | |_ _|_   _| |  |_ _|_   _| \ | | ____|
 \___ \| | | || |  | | | |   | |  | | |  \| |  _|
  ___) | |_| || |  | | | |___| |  | | | |\  | |___
 |____/ \___/|___| |_| |_____|___| |_| |_| \_|_____|
""",
"FORGE": r"""
  ______  _____ ____  _   _ _____ _____
 |  ____|/ ____|  _ \| | | |_   _| ____|
 | |__  | (___ | |_) | | | | | | |  _|
 |  __|  \___ \|  _ <| | | | | | | |__
 | |____ ____) | | \ \ |_| | |_| |____|
 |______|_____/|_|  \_\___/  |___|_____|
""",
"ALERTS": r"""
   ####  ###  #####  ###  #####
  #     #   #   #   #   #   #
   ###  #####   #   #####   #
      # #   #   #   #   #   #
  ####  #   #   #   #   #   #
""",
"LEADERBOARD": r"""
  _    ___ _____ ___  _    ___ ___  ___  _
 | |  / __|_   _| _ \| |  |_ _|   \| _ \| |
 | |__\__ \ | | |   /| |__ | || |) |   /| |__
 |____|___/ |_| |_|_\|____|___|___/|_|_\|____|
""",
"PULSE": r"""
   ____  _   _ _____ _     ___ _   _ _____
  / ___|| | | | ____| |   |_ _| \ | | ____|
 | |  _| | | |  _|   |     | ||  \| |  _|
 | |_| | |_| | |___  |___  | || |\  | |___
  \____|\___/|_____|_____|___|_| \_|_____|
""",
"LOGS": r"""
  _     ___ ____ _   _  _   _ ____  _   _ ____
 | |   |_ _|  _ \ | | |/ / | | |  _ \| | | |  _ \
 | |    | || |_) | | | ' /  | | | |_) | | | | | | |
 | |___ | ||  _ <| |_| . \  |_| |  _ <| |_| | |_| |
 |_____|___|_| \_\____|_|\_\ ___/|_| \_\____/|____/
""",
"SETTINGS": r"""
  ____  _____ ____  ____    _    ____  _____ ____
 / ___|| ____|  _ \|  _ \  / \  |  _ \| ____|  _ \
 \___ \|  _| | |_) | |_) |/ _ \ | |_) |  _| | |_) |
  ___) | |___|  _ <|  _ </ ___ \|  _ <| |___|  _ <
 |____/|_____|_| \_\_| \_/_/   \_\_| \_\_____|_| \_\
""",
"ADMIN": r"""
    _    _   _ ____  ___ _____
   / \  | \ | |  _ \|_ _| ____|
  / _ \ |  \| | | | | | |  _|
 / ___ \| |\  | |_| | | | |___
/_/   \_\_| \_|____/ |___|_____|
""",
}

def clear(): os.system("clear" if os.name != "nt" else "cls")

# ================= STORAGE / CONFIG =================
def load(f, default):
    try:
        with open(f) as fh: return json.load(fh)
    except Exception: return default
def save(f, d):
    with open(f, "w") as fh: json.dump(d, fh, indent=2)

config = load(CONF_FILE, {})

CURRENCIES = {"usd": "US Dollar $", "eur": "Euro €", "gbp": "British Pound £", "jpy": "Japanese Yen ¥",
              "cad": "Canadian Dollar C$", "aud": "Australian Dollar A$", "chf": "Swiss Franc ₣",
              "cny": "Chinese Yuan ¥", "inr": "Indian Rupee ₹", "brl": "Brazilian Real R$",
              "rub": "Russian Ruble ₽", "krw": "Korean Won ₩", "sgd": "Singapore Dollar S$",
              "hkd": "Hong Kong Dollar HK$", "nzd": "NZ Dollar NZ$", "sek": "Swedish Krona kr",
              "nok": "Norwegian Krone kr", "try": "Turkish Lira ₺", "mxn": "Mexican Peso $",
              "zar": "South African Rand R"}
currency = config.get("currency", "usd")
SYMBOLS = {"usd": "$", "eur": "€", "gbp": "£", "jpy": "¥", "cad": "C$", "aud": "A$", "chf": "₣",
           "cny": "¥", "inr": "₹", "brl": "R$", "rub": "₽", "krw": "₩", "sgd": "S$", "hkd": "HK$",
           "nzd": "NZ$", "sek": "kr", "nok": "kr", "try": "₺", "mxn": "$", "zar": "R"}

def fmt_money(v):
    sym = SYMBOLS.get(currency, "$")
    if abs(v) >= 1000: return f"{sym}{v:,.2f}"
    if abs(v) >= 1: return f"{sym}{v:,.4f}".rstrip("0").rstrip(".")
    return f"{sym}{v:.8f}".rstrip("0")

def set_currency(new_cur):
    global currency
    currency = new_cur
    config["currency"] = new_cur
    save(CONF_FILE, config)

# ================= NOTIFICATIONS =================
def notify(w, msg, level=OK):
    w.setdefault("notifs", []).append({"msg": msg, "level": level,
                                       "time": datetime.datetime.now().strftime("%H:%M:%S")})
    w["notifs"] = w["notifs"][-6:]

def notif_bar(w):
    n = (w or {}).get("notifs") or []
    if not n: return
    latest = n[-1]
    col = {"ok": OK, "warn": WARN, "bad": BAD}.get(latest["level"], OK)
    print(f"  {col}⚡ {latest['time']}{RESET} {latest['msg']}"
          f"  {DIM}({len(n)} recent){RESET}")

# ================= HEADER =================
def header():
    w = load(WALLET_FILE, None)
    total, top_name, top_amt = 0.0, "-", 0.0
    if w:
        for c, b in w["balances"].items():
            usd = b * live_price(c)
            total += usd
            if usd > top_amt: top_amt, top_name = usd, f"{b:g} {c}"
    print(gradient(BANNER))
    cur = CURRENCIES.get(currency, currency.upper())
    pend = len((w or {}).get("pending", []))
    mixq = len((w or {}).get("drain_queue", []))
    print(f"  {OK}{BOLD}TOTAL:{RESET} {fmt_money(total)}   {OK}{BOLD}TOP ASSET:{RESET} {top_name}   "
          f"{WARN}{cur}{RESET}   {DIM}[{datetime.datetime.now().strftime('%H:%M:%S')}]{RESET}")
    if w: notif_bar(w)
    flags = []
    if pend: flags.append(f"{WARN}⧗{pend} incoming{RESET}")
    if mixq: flags.append(f"{BAD}⇄{mixq} mixer flows{RESET}")
    if flags: print("  " + "  ".join(flags))
    print()

# ================= LIVE DATA =================
HTTP_HEADERS = {"User-Agent": "Mozilla/5.0 (Terminal; CryptoFlex Sim)"}

def http_json(url, timeout=8):
    try:
        req = urllib.request.Request(url, headers=HTTP_HEADERS)
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode())
    except Exception:
        return None

CG_IDS = {"BTC": "bitcoin", "ETH": "ethereum", "USDT": "tether", "USDC": "usd-coin",
          "BNB": "binancecoin", "SOL": "solana", "XRP": "ripple", "DOGE": "dogecoin",
          "LTC": "litecoin", "TRX": "tron", "BCH": "bitcoin-cash", "ADA": "cardano",
          "AVAX": "avalanche-2", "MATIC": "matic-network", "DOT": "polkadot",
          "SHIB": "shiba-inu", "PEPE": "pepe", "MONERO": "monero", "TON": "the-open-network",
          "ARB": "arbitrum"}
FALLBACK_PRICES = {"BTC": 67000, "ETH": 3400, "USDT": 1, "USDC": 1, "BNB": 610, "SOL": 165,
                   "XRP": 0.62, "DOGE": 0.16, "LTC": 85, "TRX": 0.13, "BCH": 420, "ADA": 0.45,
                   "AVAX": 28, "MATIC": 0.52, "DOT": 4.2, "SHIB": 0.000018, "PEPE": 0.000009,
                   "MONERO": 155, "TON": 5.3, "ARB": 0.78}
_price_cache = load(CACHE_FILE, {})

def refresh_prices(force=False):
    global _price_cache
    if not force and _price_cache and time.time() - max(v["ts"] for v in _price_cache.values()) < 60:
        return True
    ids = ",".join(CG_IDS.values())
    url = (f"https://api.coingecko.com/api/v3/simple/price?ids={ids}"
           f"&vs_currencies={currency}&include_24hr_change=true")
    d = http_json(url)
    if not d or not isinstance(d, dict): return False
    rev = {v: k for k, v in CG_IDS.items()}
    fetched = 0
    for cid, data in d.items():
        sym = rev.get(cid)
        if sym and isinstance(data, dict) and currency in data:
            _price_cache[sym] = {"price": data[currency], "chg": data.get(f"{currency}_24h_change", 0.0),
                                 "ts": time.time(), "cur": currency}
            fetched += 1
    if fetched: save(CACHE_FILE, _price_cache)
    return fetched > 0

def live_price(sym):
    p = _price_cache.get(sym)
    if p and time.time() - p["ts"] < 300: return p["price"]
    refresh_prices()
    p = _price_cache.get(sym)
    return p["price"] if p else FALLBACK_PRICES.get(sym, 1)

def live_change(sym):
    p = _price_cache.get(sym)
    return p.get("chg", 0.0) if p else 0.0

def real_balance(addr, chain):
    if chain == "BTC":
        d = http_json(f"https://blockstream.info/api/address/{addr}")
        if d and isinstance(d, dict) and "chain_stats" in d:
            bal = (d["chain_stats"]["funded_txo_sum"] - d["chain_stats"]["spent_txo_sum"]) / 1e8
            return bal, d["chain_stats"]["tx_count"]
    elif chain == "ETH":
        d = http_json(f"https://api.blockcypher.com/v1/eth/main/addrs/{addr}/balance")
        if d and isinstance(d, dict) and "balance" in d: return d["balance"] / 1e18, d.get("n_tx", 0)
    elif chain in ("LTC", "BCH", "DOGE"):
        net = {"LTC": "ltc/main", "BCH": "bch/main", "DOGE": "doge/main"}[chain]
        d = http_json(f"https://api.blockcypher.com/v1/{net}/addrs/{addr}/balance")
        if d and isinstance(d, dict) and "balance" in d: return d["balance"] / 1e8, d.get("n_tx", 0)
    return None

def real_eth_tokens(addr):
    d = http_json(f"https://api.ethplorer.io/getAddressInfo/{addr}?apiKey=freekey")
    if not d or not isinstance(d, dict): return []
    out = []
    for t in (d.get("tokens") or [])[:12]:
        info = t.get("tokenInfo", {})
        dec = int(info.get("decimals") or 18)
        bal = int(t.get("rawBalance") or 0) / (10 ** dec)
        if bal <= 0: continue
        price = info.get("price") or {}
        usd = (price.get("rate") or 0) * bal if isinstance(price, dict) else 0
        out.append({"sym": info.get("symbol", "???"), "balance": bal, "usd": round(usd, 2)})
    return out

def detect_chain(addr):
    a = addr
    if a.startswith("0x") and len(a) == 42: return "ETH"
    if a.startswith(("bc1", "1", "3")) and 26 <= len(a) <= 62: return "BTC"
    if a.startswith(("L", "M")) and len(a) == 34: return "LTC"
    if a.lower().startswith(("q", "bitcoincash")): return "BCH"
    if a.startswith("D") and len(a) == 34: return "DOGE"
    if a.startswith("T") and len(a) == 34: return "TRX"
    if a.startswith("addr1"): return "ADA"
    return None

# ================= ANIMATIONS =================
def bar_frame(pct, width=34):
    fill = int(pct / 100 * width)
    return f"[{paint('━' * fill)}{DIM}{'╺' * max(width - fill, 0)}{RESET}] {pct:3d}%"

def anim(title, frames=18, delay=0.4, sub=None, style="bar"):
    spin = ["◐", "◓", "◑", "◒"]
    subs = sub or ["negotiating peers", "verifying signatures", "querying mempool",
                   "syncing headers", "finalizing"]
    wave = "▁▂▃▄▅▆▇█▇▆▅▄▃▂"
    for i in range(frames):
        pct = int((i + 1) / frames * 100)
        s = subs[i % len(subs)]
        if style == "pulse":
            gfx = paint("◉" * (1 + i % 8) + DIM + "○" * (8 - i % 8) + RESET)
        elif style == "wave":
            off = i % len(wave); gfx = paint((wave[-off:] + wave[:-off])[:16])
        elif style == "hexwall":
            gfx = paint("".join(random.choice("0123456789abcdef") for _ in range(10)))
        else:
            gfx = spin[i % len(spin)]
        sys.stdout.write(f"\r  {paint(title)} {gfx} {bar_frame(pct)} {DIM}{s}{RESET}   ")
        sys.stdout.flush(); time.sleep(delay)
    sys.stdout.write("\r" + " " * 110 + "\r")
    print(f"  {OK}✔{RESET} {paint(title)}")

def node_scan(title="ESTABLISHING SECURE CHANNEL", n=6, delay=0.7):
    print(f"  {paint(title)}")
    for _ in range(n):
        ip = ".".join(str(random.randint(2, 254)) for _ in range(4))
        port = random.choice([8333, 8334, 30303, 9050, 50001])
        lat = random.uniform(4, 260)
        flag = OK if lat < 60 else WARN if lat < 150 else BAD
        sys.stdout.write(f"\r    node {ip:<15}:{port}  {flag}▲ {lat:5.1f} ms{RESET}   ")
        sys.stdout.flush(); time.sleep(delay)
    sys.stdout.write("\r" + " " * 70 + "\r")
    print(f"    {OK}✔ {n} peers connected{RESET}")

def matrix_rain(rows=8, cols=48, delay=0.35):
    trail = {}
    for r in range(rows):
        for c in range(cols):
            if random.random() < 0.15: trail[c] = random.randint(0, 2)
        out = ""
        for c in range(cols):
            if c in trail:
                out += paint(random.choice("0123456789ABCDEF")); trail[c] -= 1
                if trail[c] < 0: del trail[c]
            else: out += " "
        print("   " + out); time.sleep(delay)

def block_stream(n=8, delay=0.5):
    print(f"  {paint('STREAMING BLOCKS')}")
    for _ in range(n):
        sys.stdout.write(f"\r    ◼ block {random.randint(800000,930000)} :: {paint(fake_txid()[:44])}   ")
        sys.stdout.flush(); time.sleep(delay)
    sys.stdout.write("\r" + " " * 90 + "\r")
    print(f"    {OK}✔ chain synced{RESET}")

def type_line(text, delay=0.035):
    for ch in text:
        sys.stdout.write(ch); sys.stdout.flush(); time.sleep(delay)
    print()

def big_win(text="DRAINER COMPLETE"):
    art = r"""
    ██████╗ ██████╗  █████╗ ██╗███╗   ██╗ ██████╗ ██████╗
    ██╔══██╗██╔══██╗██╔══██╗██║████╗  ██║██╔════╝ ██╔══██╗
    ██║  ██║██████╔╝███████║██║██╔██╗ ██║██║  ███╗██████╔╝
    ██║  ██║██╔══██╗██╔══██║██║██║╚██╗██║██║   ██║██╔═══╝
    ██████╔╝██║  ██║██║  ██║██║██║ ╚████║╚██████╔╝██║
    ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝ ╚═════╝ ╚═╝
              C O M P L E T E D
"""
    clear()
    for _ in range(5):
        print(paint(art)); time.sleep(0.4); clear()
    print(paint(art))
    print(f"  {OK}{BOLD}>>> {text} <<< {RESET}")
    for _ in range(10):
        sys.stdout.write(paint("◆ ")); sys.stdout.flush(); time.sleep(0.12)
    print()

def page(title):
    clear(); header()
    art = ASCII_ART.get(title)
    if art: print(gradient(art.strip("\n") + "\n"))

def yn(prompt):
    return input(f"  {paint(prompt)} (y/n): ").strip().lower() in ("y", "yes")

def ask_num(prompt, default=0.0, cast=float):
    try:
        v = input(f"  {prompt}: ").strip()
        return cast(v) if v else default
    except ValueError:
        return default

# ================= FAKE DATA =================
def fake_txid(): return "".join(random.choice("0123456789abcdef") for _ in range(64))
def fake_block_hash(): return "00000000000000" + fake_txid()[:48]
def fake_addr(chain):
    p = {"BTC": ["1", "3", "bc1"], "ETH": ["0x"], "LTC": ["L", "M"], "DOGE": ["D"],
         "BCH": ["q", "1"], "TRX": ["T"], "XRP": ["r"], "SOL": [""], "ADA": ["addr1"],
         "DOT": ["1"], "MONERO": ["4"], "TON": ["UQ"]}.get(chain, ["0x"])
    n = {"BTC": 34, "ETH": 42, "LTC": 34, "DOGE": 34, "BCH": 42, "TRX": 34, "XRP": 33,
         "SOL": 44, "ADA": 45, "DOT": 47, "MONERO": 95, "TON": 48}.get(chain, 42)
    pre = random.choice(p)
    return pre + "".join(random.choice(string.ascii_letters + string.digits)
                         for _ in range(max(n - len(pre), 8)))

COINS = list(CG_IDS.keys())
NETWORKS = {"BTC": "Bitcoin Mainnet", "ETH": "Ethereum Mainnet", "USDT": "ERC-20 / TRC-20",
            "USDC": "ERC-20", "BNB": "BEP-20", "SOL": "Solana Mainnet", "XRP": "XRP Ledger",
            "DOGE": "Dogecoin Mainnet", "LTC": "Litecoin Mainnet", "TRX": "Tron Mainnet",
            "BCH": "BCH Mainnet", "ADA": "Cardano Mainnet", "AVAX": "Avalanche C-Chain",
            "MATIC": "Polygon PoS", "DOT": "Polkadot Relay", "SHIB": "ERC-20",
            "PEPE": "ERC-20", "MONERO": "Monero Mainnet", "TON": "TON Mainnet", "ARB": "Arbitrum One"}
CHAINS = {"BTC": "BTC", "ETH": "ETH", "LTC": "LTC", "BCH": "BCH", "DOGE": "DOGE"}

def add_log(kind, entry):
    logs = load(LOG_FILE, {})
    logs.setdefault(kind, []).append({**entry, "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
    save(LOG_FILE, logs)

def new_key():
    return "CFX-" + "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(4)) + "-" + \
           "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(4))

# ================= KEY SYSTEM (fast) =================
def setup_keys():
    if not os.path.exists(KEY_FILE):
        key = new_key()
        save(KEY_FILE, {"owner_key": key, "users": {}})
        clear(); matrix_rain(rows=6, delay=0.3)
        print(f"\n  {paint(BOLD + '  [ FIRST RUN SETUP ]')}")
        time.sleep(1.2)
        type_line("  Generating your master access key...")
        anim("KEY GENERATION", 10, 0.35, style="hexwall")
        print(f"\n  {WARN}{BOLD}  MASTER ACCESS KEY: {key}{RESET}")
        print(f"  {DIM}  This is the ONLY admin key. Write it down!{RESET}")
        time.sleep(2.5)
        while True:
            ans = input(paint("\n  Key saved? (y/n): ")).strip().lower()
            if ans in ("y", "yes"):
                time.sleep(1); break
            elif ans in ("n", "no"):
                key = new_key()
                save(KEY_FILE, {"owner_key": key, "users": {}})
                print(f"\n  {WARN}{BOLD}  NEW MASTER ACCESS KEY: {key}{RESET}")
                time.sleep(2.5)
            else:
                print("  Please type 'y' or 'n'.")
    return load(KEY_FILE, None)

def login(keys):
    for attempt in range(5):
        clear(); header()
        print(paint(f"  ══ ACCESS TERMINAL ══  attempt {attempt + 1}/5\n"))
        k = input(paint("  Enter Access Key: ")).strip()
        if k == keys["owner_key"]:
            print(f"  {OK}✔ Access granted — admin.{RESET}"); time.sleep(0.8)
            return "admin"
        if k in keys["users"]:
            print(f"  {OK}✔ Access granted — role: {keys['users'][k]}{RESET}"); time.sleep(0.8)
            return keys["users"][k]
        left = 4 - attempt
        if left > 0:
            print(f"  {BAD}✘ Invalid key.{RESET} {left} attempt(s) remaining."); time.sleep(1.5)
        else:
            print(f"  {BAD}{BOLD}[LOCKED] Too many failed attempts.{RESET}"); time.sleep(2)
            anim("LOCKING DOWN", 8, 0.35, sub=["sealing vault"], style="hexwall")
            if yn("Generate a NEW master key? Resets all user keys."):
                nk = new_key()
                save(KEY_FILE, {"owner_key": nk, "users": {}})
                add_log("system", {"event": "emergency key reset"})
                print(f"\n  {WARN}{BOLD}  [RECOVERY] NEW MASTER KEY: {nk}{RESET}")
                time.sleep(2.5)
                input(paint("  Key saved? (y/n): ")).strip().lower()
            else:
                print(paint("  No recovery. Closing..."))
            add_log("system", {"event": "lockout"})
            time.sleep(1); sys.exit(0)
    return None

# ================= WALLET =================
def wallet_total(w):
    return sum(b * live_price(c) for c, b in w["balances"].items())

def init_wallet():
    w = load(WALLET_FILE, None)
    if w: return w
    coin = random.choice(COINS)
    w = {"address": fake_addr(CHAINS.get(coin, "ETH")), "primary": coin,
         "balances": {coin: 1.0}, "txs": [], "pending": [], "faucet": None,
         "drain_queue": [], "notifs": []}
    save(WALLET_FILE, w); return w

# ================= MENU =================
def menu(title, options, footer=True):
    page(title)
    for i, label in enumerate(options, 1):
        col = OK if i % 2 else WARN
        print(f"  {paint('[')}{col}{i}{RESET}{paint(']')} {label}")
    if footer: print(f"  {paint('[')}{DIM}0{RESET}{paint(']')} Back")
    try: return int(input("\n  ➤ ").strip())
    except ValueError: return 0

def pick(prompt, choices):
    print(paint(prompt))
    for i, c in enumerate(choices, 1): print(f"   {paint('[')}{i}{paint(']')} {c}")
    try: return choices[int(input("  ➤ ").strip()) - 1]
    except Exception: return choices[0]

def price_tag(sym):
    ch = live_change(sym)
    col = OK if ch >= 0 else BAD
    return f"{paint(sym)} {fmt_money(live_price(sym))} {col}{ch:+.1f}%{RESET}"

# ================= TOOLS =================
def txid_gen():
    page("FORGE")
    anim("FORGING HASHES", 14, 0.5, sub=["seeding entropy", "double-SHA passes"], style="hexwall")
    for _ in range(3):
        print(f"  {paint('TXID')}   {fake_txid()}")
        print(f"  {paint('BLK-H')}  {fake_block_hash()}\n")
        time.sleep(0.5)
    add_log("spoof", {"type": "hash", "txid": fake_txid()})
    input("\n  Enter...")

def tx_spoof():
    page("SPOOF")
    coin = pick("Select network asset:", COINS)
    amt = ask_num("Amount")
    sender = input("  Sender (blank = random): ").strip() or fake_addr(CHAINS.get(coin, "ETH"))
    recv = input("  Recipient: ").strip() or fake_addr(CHAINS.get(coin, "ETH"))
    method = pick("Injection method:", ["mempool-inject", "double-spend", "flash-broadcast", "relay-flood"])
    print()
    type_line(f"  {amt} {coin} {DIM}({fmt_money(amt * live_price(coin))}){RESET} | {NETWORKS[coin]} | {method}", 0.04)
    anim("BROADCASTING", 20, 0.5, sub=["signing payload", "flooding relays"], style="wave")
    node_scan(); block_stream(6, 0.5)
    if random.random() < 0.5:
        txid = fake_txid()
        print(f"\n  {OK}{BOLD}✔ BROADCAST CONFIRMED{RESET}")
        print(f"  TXID: {paint(txid)}\n  Block: {random.randint(800000,930000)}")
        add_log("spoof", {"type": "tx", "coin": coin, "amount": amt, "txid": txid,
                          "to": recv, "method": method, "status": "SUCCESS"})
        w = load(WALLET_FILE, init_wallet())
        w.setdefault("pending", []).append({"coin": coin, "amount": amt, "txid": txid, "delay": random.randint(1, 3)})
        save(WALLET_FILE, w)
    else:
        print(f"\n  {BAD}✘ REJECTED — dropped by relays{RESET}")
        add_log("spoof", {"coin": coin, "amount": amt, "status": "REJECTED", "method": method})
    input("\n  Enter...")

def sniffer():
    page("SNIFFER")
    url = input("  Target endpoint: ").strip() or "unknown"
    addr = input("  Address: ").strip() or fake_addr("BTC")
    anim("DEEP SCANNING", 20, 0.55, sub=["probing endpoints", "indexing leaks"], style="hexwall")
    block_stream(5, 0.5)
    if random.random() < 0.5:
        pool = ["email: victim@{d}.com", "phone: +1-555-{n}", "password: {p}",
                "seed phrase: {s}", "2FA backup: {c}", "last login IP: 45.{a}.x.x",
                "exchange account: {e}", "API key: {k}"]
        count = random.choice([1, 2, 4, 8])
        print(f"\n  {OK}{BOLD}[HIT] {count} record(s) recovered:{RESET}")
        found, words = [], ["moon", "diamond", "satoshi", "lambo", "flex", "giga", "rocket"]
        for _ in range(count):
            t = random.choice(pool).format(
                d="".join(random.choices(string.ascii_lowercase, k=5)), n=random.randint(200, 999),
                p="".join(random.choices(string.ascii_letters + string.digits, k=10)),
                s=" ".join(random.choices(words, k=12)), c=str(random.randint(100000, 999999)),
                a=random.randint(1, 254), e=random.choice(["Binance", "Coinbase", "Kraken", "OKX"]),
                k=fake_txid()[:32])
            print(f"   {WARN}▸{RESET} {t}"); found.append(t); time.sleep(0.35)
        add_log("sniffer", {"url": url, "addr": addr, "findings": found, "result": "HIT"})
    else:
        print(f"\n  {BAD}[NO RECORDS] target clean{RESET}")
        add_log("sniffer", {"url": url, "addr": addr, "result": "MISS"})
    input("\n  Enter...")

def mining_rig():
    page("MINER")
    w = load(WALLET_FILE, init_wallet())
    coin = pick("Coin to mine:", COINS)
    method = pick("Mining method:", ["solo", "pool", "merged-mining", "stratum-tcp"])
    duration = ask_num("Session duration in minutes", 5.0)
    if duration <= 0: duration = 5.0
    hashrate = random.uniform(80, 420)
    print(f"\n  {paint('RIG')} CFX-RIG-01 | {price_tag(coin)} | {OK}{hashrate:.1f} MH/s{RESET} | {paint(method)}")
    print(f"  {DIM}50 shares per payout. Auto-stops after {duration} min.{RESET}\n")
    shares, target, earned = 0, 50, 0.0
    end = time.time() + duration * 60
    while time.time() < end:
        anim(f"HASHING SHARE {shares + 1}/{target}", 4, 0.12,
             sub=["rolling nonces", "checking difficulty"], style="wave")
        shares += 1
        if random.random() < 0.05:
            print(f"  {WARN}◆ lucky partial solution, nonce={random.randint(100000,999999)}{RESET}")
        if shares >= target:
            shares = 0
            payout = round(random.uniform(0.0001, 0.01), 8)
            txid = fake_txid()
            w["balances"][coin] = round(w["balances"].get(coin, 0) + payout, 8)
            w["txs"].append({"dir": "IN", "coin": coin, "amount": payout, "txid": txid,
                             "from": "mining-pool", "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")})
            notify(w, f"mining payout +{payout} {coin}", "ok")
            earned += payout; save(WALLET_FILE, w)
            print(f"  {OK}{BOLD}◆ BLOCK MINED{RESET} +{payout} {coin}  {fmt_money(earned * live_price(coin))} session")
            time.sleep(1.0)
    print(f"\n  {paint('SESSION COMPLETE')} earnings: {earned:.8f} {coin} ({fmt_money(earned * live_price(coin))})")
    add_log("system", {"event": "mining session", "coin": coin, "earned": earned, "method": method})
    input("\n  Enter...")

# ================= TOOLS: WALLET DRAINER (auto-drain into YOUR wallet) =================
def drainer():
    page("DRAINER")
    url = input("  Target URL / platform: ").strip() or "unknown"
    addr = input("  Wallet address: ").strip()
    chain = detect_chain(addr) if addr else None
    haul = []  # [(sym, amount, usd_value)] — everything found, goes to YOUR wallet

    if addr and chain:
        anim("LIVE CHAIN LOOKUP", 12, 0.45, sub=["blockstream", "blockcypher", "ethplorer"], style="pulse")
        real = real_balance(addr, chain)
        if real is not None:
            bal, txs = real
            print(f"  {OK}{BOLD}[LIVE CHAIN DATA]{RESET} {paint(chain)}")
            print(f"   balance : {OK}{bal:g} {chain}{RESET}  {DIM}{fmt_money(bal * live_price(chain))}{RESET}")
            print(f"   txs     : {txs} on-chain")
            if bal > 0: haul.append((chain, bal))
        else:
            sim = round(random.uniform(0.05, 12), 4)
            print(f"  {WARN}[!] index unreachable — simulated target profile{RESET}")
            print(f"   balance : {sim} {chain}")
            haul.append((chain, sim))
        if chain == "ETH":
            anim("SCANNING TOKEN HOLDINGS", 10, 0.4, sub=["ethplorer index", "decoding ERC-20"], style="hexwall")
            tokens = real_eth_tokens(addr)
            if tokens:
                print(f"  {OK}{BOLD}[LIVE TOKENS FOUND: {len(tokens)}]{RESET}")
                for t in tokens:
                    print(f"   {WARN}▸{RESET} {t['sym']:<8} {t['balance']:.4f}  {DIM}{fmt_money(t['usd'])}{RESET}")
                    haul.append((t["sym"], t["balance"]))
            else:
                print(f"  {DIM}no ERC-20 tokens found (or index offline){RESET}")
    else:
        sim_chain = random.choice(["BTC", "ETH"])
        sim = round(random.uniform(0.05, 12), 4)
        print(f"  {DIM}address not recognized — simulated target: {sim} {sim_chain}{RESET}")
        haul.append((sim_chain, sim))

    print(f"\n  {paint('── ATTACK SURFACE SELECTION ──')}")
    collected = []
    if yn("Platform access available?"):
        collected.append("platform: " + (input("  Enter platform name: ").strip() or "unknown"))
    if yn("Seed phrase available?"):
        collected.append("seed phrase: " + (input("  Enter seed phrase (words): ").strip() or "recovered"))
    if yn("2FA code available?"):
        collected.append("2FA code: " + (input("  Enter 2FA code: ").strip() or str(random.randint(100000, 999999))))
    if yn("Email access available?"):
        collected.append("email: " + (input("  Enter email: ").strip() or "user@mail.com"))
    if yn("Password available?"):
        collected.append("password: " + (input("  Enter password: ").strip() or "hunter2"))
    have = len(collected)
    print(f"\n  {paint('surface score')}: {have}/5  {DIM}| target haul: "
          f"{', '.join(f'{a:g} {s}' for s, a in haul) or 'empty'}{RESET}")
    if have < 2:
        print(f"  {BAD}✘ INSUFFICIENT SURFACE — need at least 2 access vectors. Aborting.{RESET}")
        add_log("drainer", {"url": url, "addr": addr, "surface": have, "result": "ABORTED"})
        input("\n  Enter..."); return

    anim("BREACH ATTEMPT", 20, 0.55, sub=["assembling vectors", "bypassing session guard",
                                          "farming signature", "exfiltrating keys"], style="hexwall")
    block_stream(4, 0.45)
    if random.random() < 0.5:
        big_win("DRAINER COMPLETE")
        print(f"  {OK}{BOLD}✔ Vault compromised. Extracted:{RESET}")
        for c in collected: print(f"   {OK}▸{RESET} {c}")
        total_usd = 0
        for sym, bal in haul:
            px = live_price(sym) if sym in CG_IDS else 0
            total_usd += bal * px
        print(f"\n  {OK}{BOLD}◆ TARGET HAUL QUEUED FOR MIXER FLOW → YOUR WALLET{RESET}")
        for sym, bal in haul:
            px = live_price(sym) if sym in CG_IDS else 0
            print(f"   {WARN}◆{RESET} {bal:.6g} {sym}  {DIM}{fmt_money(bal * px)}{RESET}")
        print(f"   {paint('TOTAL')}: {fmt_money(total_usd)}")
        w = load(WALLET_FILE, init_wallet())
        # AUTO-QUEUE: split each asset into small mixer chunks, processed back at main menu
        for sym, bal in haul:
            splits = random.randint(8, 20)
            w.setdefault("drain_queue", []).append(
                {"sym": sym, "remaining": bal, "total": bal, "splits": splits,
                 "delay": random.uniform(2, 6), "next": time.time() + random.uniform(1, 4)})
        notify(w, f"drainer haul queued: {len(haul)} asset(s) via mixers", "warn")
        add_log("drainer", {"url": url, "addr": addr, "surface": have,
                            "vectors": collected, "haul": [(s, a) for s, a in haul], "result": "SUCCESS"})
        print(f"\n  {OK}◆ Mixer transaction flow armed — returning to menu, flows will stream in.{RESET}")
        save(WALLET_FILE, w)
        time.sleep(2)
    else:
        print(f"\n  {BAD}✘ DRAIN FAILED — signature guard tripped, session burned{RESET}")
        add_log("drainer", {"url": url, "addr": addr, "surface": have, "result": "FAILED"})
        time.sleep(2)

def tools():
    while True:
        m = menu("TOOLS", ["TXID / Block Hash Forge",
                           "Spoofed TX Broadcast",
                           "Network Recon Scanner",
                           "Wallet Drainer — live balances & tokens",
                           "Mining Rig"])
        if m == 0: return
        [None, txid_gen, tx_spoof, sniffer, drainer, mining_rig][min(m, 5)]()

# ================= WALLET =================
def process_pending(w):
    for p in list(w.get("pending", [])):
        p["delay"] -= 1
        if p["delay"] <= 0:
            w["balances"][p["coin"]] = round(w["balances"].get(p["coin"], 0) + p["amount"], 8)
            w["txs"].append({"dir": "IN", "coin": p["coin"], "amount": p["amount"], "txid": p["txid"],
                             "from": "external", "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")})
            notify(w, f"received +{p['amount']} {p['coin']}", "ok")
            w["pending"].remove(p)
    return w

def run_drain_queue(w):
    """Background mixer flows: target haul streams into YOUR wallet in small chunks."""
    q = w.get("drain_queue") or []
    if not q: return w
    now = time.time()
    still = []
    for item in q:
        if item["splits"] <= 0 or item["remaining"] <= 0:
            continue
        if now < item.get("next", 0):
            still.append(item); continue
        chunk = item["remaining"] / max(item["splits"], 1)
        amt = round(min(item["remaining"], chunk * random.uniform(0.5, 1.5) or item["remaining"]), 8)
        amt = max(amt, 0.00000001)
        mixer = fake_addr("ETH" if not item["sym"].startswith(("BTC", "LTC", "DOGE")) else "BTC")
        txid = fake_txid()
        w["balances"][item["sym"]] = round(w["balances"].get(item["sym"], 0) + amt, 8)
        w["txs"].append({"dir": "IN", "coin": item["sym"], "amount": amt, "txid": txid,
                         "from": f"mixer:{mixer[:10]}", "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")})
        notify(w, f"mixer flow +{amt:.6g} {item['sym']} → wallet", "ok")
        print(f"  {OK}◆ MIXER FLOW{RESET} +{amt:.6g} {item['sym']} {DIM}via {mixer[:16]}... tx {txid[:18]}...{RESET}")
        item["remaining"] = round(item["remaining"] - amt, 8)
        item["splits"] -= 1
        item["next"] = now + item["delay"]
        if item["remaining"] <= 0 or item["splits"] <= 0:
            notify(w, f"mixer flow complete: {item['sym']} fully landed", "warn")
        else:
            still.append(item)
    w["drain_queue"] = still
    return w

def wallet():
    w = load(WALLET_FILE, init_wallet())
    w = process_pending(w); save(WALLET_FILE, w)
    while True:
        m = menu("WALLET", ["Balances & Assets — live valued", "Send", "Receive", "Transaction History"])
        if m == 0: return
        if m == 1:
            w = process_pending(load(WALLET_FILE, w)); save(WALLET_FILE, w)
            print()
            for c, b in w["balances"].items():
                ch = live_change(c)
                col = OK if ch >= 0 else BAD
                print(f"   {paint(c):<10} {b:>14}  {fmt_money(live_price(c))} {col}{ch:+.1f}%{RESET}  "
                      f"{DIM}{fmt_money(b * live_price(c))}{RESET}")
            print(f"\n   {paint('Address')} {w['address']}")
            if w.get("pending"): print(f"   {WARN}⧗ pending incoming: {len(w['pending'])}{RESET}")
            input("\n  Enter..."); continue
        if m == 2:
            coin = pick("Asset:", list(w["balances"].keys()))
            amt = ask_num("Amount")
            if amt <= w["balances"].get(coin, 0):
                to = input("  To address: ").strip() or fake_addr(CHAINS.get(coin, "ETH"))
                split = yn("Split into small transactions?")
                if split:
                    chunks = random.randint(5, 10)
                    left = amt
                    anim("OPENING SPLIT CHANNEL", 10, 0.45, style="hexwall")
                    for i in range(chunks):
                        a = round(left / (chunks - i), 8) if i < chunks - 1 else left
                        left = round(left - a, 8)
                        txid = fake_txid()
                        anim(f"SPLIT TX {i + 1}/{chunks}", 4, 0.28, style="wave")
                        w["balances"][coin] = round(max(w["balances"].get(coin, 0) - a, 0), 8)
                        w["txs"].append({"dir": "OUT", "coin": coin, "amount": a, "txid": txid, "to": to,
                                         "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")})
                        save(WALLET_FILE, w)
                        print(f"   {BAD}→{RESET} {a} {coin}  {DIM}tx {txid[:18]}...{RESET}")
                    notify(w, f"split send {amt} {coin} complete", "ok")
                    print(f"  {OK}◆ SPLIT SEND COMPLETE{RESET}")
                else:
                    anim("SIGNING & BROADCASTING", 16, 0.55, sub=["ECDSA sign", "serializing", "relay flood"], style="wave")
                    if random.random() < 0.85:
                        w["balances"][coin] = round(w["balances"][coin] - amt, 8)
                        txid = fake_txid()
                        w["txs"].append({"dir": "OUT", "coin": coin, "amount": amt, "txid": txid, "to": to,
                                         "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")})
                        notify(w, f"sent {amt} {coin}", "ok")
                        save(WALLET_FILE, w)
                        print(f"  {OK}◆ SENT{RESET} {amt} {coin} → {to}\n  {DIM}tx {txid}{RESET}")
                    else:
                        print(f"  {BAD}✘ network congestion, retry later{RESET}")
            else:
                print(f"  {BAD}[!] insufficient balance{RESET}")
            input("\n  Enter..."); continue
        if m == 3:
            print(f"\n  {paint('Your ' + w['primary'] + ' address:')} {OK}{w['address']}{RESET}\n")
            secret = input("  ➤ ").strip().lower()
            if secret == "open":
                setup_faucet(w); save(WALLET_FILE, w)
            input("\n  Enter..."); continue
        if m == 4:
            print()
            for t in w["txs"][-20:]:
                arrow = f"{BAD}→ OUT{RESET}" if t["dir"] == "OUT" else f"{OK}← IN {RESET}"
                print(f"   {DIM}{t['time']}{RESET} {arrow} {t['amount']} {t['coin']}  {DIM}{t['txid'][:16]}...{RESET}")
            input("\n  Enter..."); continue

def setup_faucet(w):
    page("WALLET")
    print(paint("  ══ PRIVATE CHANNEL ══\n"))
    per = ask_num("Total token amount", 1.0)
    n_tx = int(ask_num("Number of split transactions", 10))
    n_w = int(ask_num("Number of sending wallets", 1))
    delay = ask_num("Seconds between TXs", 3.0)
    coin = pick("Token:", COINS)
    w["faucet"] = {"coin": coin, "total": per, "remaining": per, "splits": max(n_tx, 1),
                   "wallets": max(n_w, 1), "delay": max(delay, 1.0), "next": time.time() + delay}
    add_log("system", {"event": "channel armed", "coin": coin, "total": per, "splits": n_tx})
    anim("ARMING CHANNEL", 8, 0.4, sub=["opening sockets", "queueing flows"], style="pulse")
    notify(w, f"channel armed: {per} {coin} in {n_tx} splits", "warn")
    print(f"  {OK}◆ Channel armed — {per} {coin} will flow in {n_tx} splits. Returning...{RESET}")
    time.sleep(1.5)

def run_faucet(w):
    f = w.get("faucet")
    if not f or f["splits"] <= 0: return w
    if time.time() < f["next"]: return w
    chunk = round(f["total"] / max(f["splits"], 1), 8)
    left = round(f["remaining"], 8)
    amt = chunk if left >= chunk else left
    for _ in range(f["wallets"]):
        src, txid = fake_addr(CHAINS.get(f["coin"], "ETH")), fake_txid()
        w["balances"][f["coin"]] = round(w["balances"].get(f["coin"], 0) + amt, 8)
        w["txs"].append({"dir": "IN", "coin": f["coin"], "amount": amt, "txid": txid,
                         "from": src, "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")})
    notify(w, f"incoming +{amt} {f['coin']} ×{f['wallets']}", "ok")
    print(f"  {OK}◆ INCOMING{RESET} +{amt} {f['coin']} ×{f['wallets']}  {DIM}tx {txid[:20]}...{RESET}")
    f["remaining"] = round(f["remaining"] - amt, 8)
    f["splits"] -= 1
    f["next"] = time.time() + f["delay"]
    if f["splits"] <= 0 or f["remaining"] <= 0:
        w["faucet"] = None
        notify(w, "channel complete — full amount flowed in", "warn")
    save(WALLET_FILE, w)
    return w

# ================= PORTFOLIO / MARKET =================
def portfolio():
    page("PORTFOLIO")
    refresh_prices()
    w = load(WALLET_FILE, init_wallet()); w = process_pending(w); save(WALLET_FILE, w)
    total = 0
    for c, b in w["balances"].items():
        price = live_price(c); ch = live_change(c)
        col = OK if ch >= 0 else BAD
        usd = b * price; total += usd
        print(f"   {paint(c):<12} {b:>12.4f}  {fmt_money(price)} {col}{ch:+.1f}%{RESET}  {DIM}{fmt_money(usd)}{RESET}")
    print(f"\n   {paint(BOLD + 'TOTAL')}: {fmt_money(total)}")
    print(f"\n  {paint('TOP MOVERS — LIVE 24H')}")
    movers = sorted(_price_cache.items(), key=lambda kv: -abs(kv[1].get("chg", 0)))[:3]
    for sym, p in movers:
        ch = p.get("chg", 0); col = OK if ch >= 0 else BAD
        print(f"   {paint(sym):<12} {fmt_money(p['price'])} {col}{ch:+.2f}%{RESET}")
    add_log("system", {"event": "portfolio viewed", "total": round(total, 2)})
    input("\n  Enter...")

def market_watch():
    page("MARKET")
    print(f"\n  {paint('FETCHING LIVE MARKET…')}")
    ok = refresh_prices(force=True)
    src = f"{OK}LIVE{RESET}" if ok else f"{WARN}CACHE{RESET}"
    print(f"\n   {'ASSET':<8} {'PRICE':>16}  {'24H':>9}   source: {src}  fiat: {currency.upper()}")
    print(f"   {'-' * 52}")
    for sym in COINS:
        p = _price_cache.get(sym)
        price = p["price"] if p else FALLBACK_PRICES[sym]
        ch = p.get("chg", 0) if p else 0
        col = OK if ch >= 0 else BAD
        row = f"   {sym:<8} {fmt_money(price):>16}  {col}{ch:>+8.1f}%{RESET}"
        print(row)
    add_log("system", {"event": "market watch", "live": ok})
    input("\n  Enter...")

# ================= WHALES / ALERTS / PULSE =================
def whales():
    page("LEADERBOARD")
    anim("SNIPING WHALE WALLETS", 12, 0.5, sub=["tracking clusters", "scoring holdings"], style="wave")
    rows = sorted([(fake_addr(random.choice(list(CHAINS.values()))), random.uniform(1, 9000)) for _ in range(8)],
                  key=lambda x: -x[1])
    for i, (a, v) in enumerate(rows, 1):
        medal = ["🥇", "🥈", "🥉"][i - 1] if i <= 3 else f"{i}."
        print(f"   {medal} {a[:22]}...  {paint(fmt_money(v))}")
    me = load(WALLET_FILE, init_wallet())
    print(f"\n   {paint('YOU')}: rank #{random.randint(9, 9999)} with {fmt_money(wallet_total(me))}")
    input("\n  Enter...")

def alerts():
    page("ALERTS")
    coin = pick("Asset to monitor:", COINS)
    anim("LINKING MARKET FEEDS", 10, 0.5, sub=["coingecko live", "subscribing ticker"], style="pulse")
    base = live_price(coin)
    for i in range(5):
        refresh_prices()
        p = live_price(coin)
        drift = (p - base) / base * 100 if base else 0
        col = OK if drift >= 0 else BAD
        print(f"   tick {i + 1}: {coin} {col}{fmt_money(p)}{RESET} {DIM}({drift:+.2f}% since start){RESET}")
        time.sleep(1.4)
    ch = live_change(coin)
    if abs(ch) > 3:
        print(f"\n  {WARN}{BOLD}🔔 LIVE ALERT — {coin} at {ch:+.1f}% / 24h!{RESET}")
        w = load(WALLET_FILE, init_wallet())
        notify(w, f"ALERT: {coin} {ch:+.1f}% / 24h", "warn"); save(WALLET_FILE, w)
        add_log("system", {"event": "price alert", "coin": coin, "chg": ch, "triggered": True})
    else:
        print(f"\n  {DIM}no triggers — market quiet ({ch:+.1f}% / 24h){RESET}")
        add_log("system", {"event": "price alert", "coin": coin, "chg": ch, "triggered": False})
    input("\n  Enter...")

def live_pulse():
    page("PULSE")
    duration = ask_num("Dashboard duration in seconds", 30.0)
    if duration <= 0: duration = 30.0
    print(f"  {DIM}running for {duration}s…{RESET}")
    end = time.time() + duration
    while time.time() < end:
        w = load(WALLET_FILE, init_wallet())
        w = run_faucet(w); w = run_drain_queue(w); w = process_pending(w); save(WALLET_FILE, w)
        tot = wallet_total(w)
        sym = random.choice(COINS)
        ch = live_change(sym)
        col = OK if ch >= 0 else BAD
        sys.stdout.write(
            f"\r  {paint('Σ')} {fmt_money(tot):>16}  {sym} {fmt_money(live_price(sym))} {col}{ch:+.2f}%{RESET} "
            f"pend {len(w.get('pending', []))}  mix {len(w.get('drain_queue', []))}  txs {len(w['txs'])}   ")
        sys.stdout.flush()
        time.sleep(2)
    print(f"\n  {paint('PULSE COMPLETE')}")
    input("\n  Enter...")

# ================= LOGS =================
def view_logs():
    logs = load(LOG_FILE, {})
    while True:
        kinds = list(logs.keys())
        if not kinds:
            page("LOGS"); print("  No logs yet."); input("\n  Enter..."); return
        m = menu("LOGS", [f"{k} — {len(logs[k])} entries" for k in kinds])
        if m == 0: return
        k = kinds[m - 1]
        page("LOGS")
        print(paint(f"  ══ {k.upper()} ══\n"))
        for e in logs[k][-30:]:
            print(f"   {DIM}{e['time']}{RESET} " + json.dumps({x: y for x, y in e.items() if x != 'time'})[:110])
        input("\n  Enter...")

# ================= ADMIN =================
def admin_users(keys):
    while True:
        m = menu("ADMIN", ["Create user key", "List users", "Revoke key", "Change user role"])
        if m == 0:
            save(KEY_FILE, keys); return
        if m == 1:
            nk = new_key()
            role = pick("Role:", ["user", "vip", "mod"])
            keys["users"][nk] = role
            save(KEY_FILE, keys)
            anim("MINTING KEY", 8, 0.4, sub=["deriving", "registering"], style="hexwall")
            print(f"  {OK}{BOLD}◆ NEW KEY: {nk}{RESET}  {DIM}({role}){RESET}")
            add_log("system", {"event": "key created", "key": nk, "role": role})
            input("\n  Enter..."); continue
        if m == 2:
            print()
            if not keys["users"]: print(f"   {DIM}no users yet{RESET}")
            for k, r in keys["users"].items(): print(f"   {paint(k)}  →  {r}")
            input("\n  Enter..."); continue
        if m == 3:
            k = input("  Key to revoke: ").strip()
            if k in keys["users"]:
                del keys["users"][k]; save(KEY_FILE, keys)
                print(f"  {OK}✔ revoked{RESET}")
                add_log("system", {"event": "key revoked", "key": k})
            else: print(f"  {BAD}not found{RESET}")
            input("\n  Enter..."); continue
        if m == 4:
            k = input("  Key to change: ").strip()
            if k in keys["users"]:
                keys["users"][k] = pick("New role:", ["user", "vip", "mod"])
                save(KEY_FILE, keys); print(f"  {OK}✔ updated{RESET}")
            else: print(f"  {BAD}not found{RESET}")
            input("\n  Enter..."); continue

# ================= SETTINGS (currency / theme / WASH WALLET) =================
def wash_wallet():
    clear(); header()
    print(paint("  ══ WASH WALLET ══\n"))
    print(f"  {BAD}{BOLD}This wipes ALL coins, transactions, pending flows,")
    print(f"  mixer queues, faucet state and notifications.{RESET}")
    print(f"  {DIM}Access keys, currency and theme are KEPT.{RESET}\n")
    if yn("Confirm wallet wash?"):
        anim("WASHING VAULT", 14, 0.4, sub=["burning tx history", "rotating addresses", "cleaning balances"], style="hexwall")
        cur = currency  # preserved via config file anyway
        coin = random.choice(COINS)
        fresh = {"address": fake_addr(CHAINS.get(coin, "ETH")), "primary": coin,
                 "balances": {coin: 1.0}, "txs": [], "pending": [], "faucet": None,
                 "drain_queue": [], "notifs": [{"msg": "vault washed — fresh wallet minted",
                                                "level": "warn",
                                                "time": datetime.datetime.now().strftime("%H:%M:%S")}]}
        save(WALLET_FILE, fresh)
        add_log("system", {"event": "wallet washed"})
        print(f"\n  {OK}{BOLD}✔ VAULT WASHED — fresh wallet with 1 {coin}.{RESET}")
        print(f"  {DIM}New address: {fresh['address']}{RESET}")
    else:
        print("  Wash cancelled.")
    input("\n  Enter...")

def settings():
    global theme
    while True:
        m = menu("SETTINGS", [f"Currency — current: {currency.upper()}",
                              "Wash Wallet — reset coins & history",
                              "Force price cache refresh",
                              f"Cycle theme — current: {theme}"])
        if m == 0: return
        if m == 1:
            new = pick("Select fiat currency:", list(CURRENCIES.keys()))
            set_currency(new)
            anim("REVALUATING PORTFOLIO", 8, 0.3, sub=[f"coingecko vs {new}"], style="pulse")
            refresh_prices(force=True)
            notify_flag = f"currency → {new.upper()}"
            w = load(WALLET_FILE, init_wallet())
            notify(w, notify_flag, "warn"); save(WALLET_FILE, w)
            print(f"  {OK}✔ Currency → {CURRENCIES[new]}{RESET}")
            add_log("system", {"event": "currency changed", "currency": new})
            input("\n  Enter..."); continue
        if m == 2:
            wash_wallet(); continue
        if m == 3:
            anim("SYNCING LIVE PRICES", 10, 0.35, sub=["coingecko", "blockstream", "ethplorer"], style="pulse")
            ok = refresh_prices(force=True)
            print(f"  {OK}✔ prices updated — {len(_price_cache)} coins live{RESET}" if ok
                  else f"  {BAD}✘ network unreachable — cache kept{RESET}")
            add_log("system", {"event": "price refresh", "ok": ok})
            input("\n  Enter..."); continue
        if m == 4:
            theme = THEMES[(THEMES.index(theme) + 1) % len(THEMES)]
            add_log("system", {"event": "theme changed", "theme": theme})
            print(paint(f"  Theme → {theme}")); time.sleep(0.8)

# ================= MAIN =================
def main():
    clear()
    matrix_rain(rows=8, delay=0.25)
    keys = setup_keys()
    role = login(keys)
    w = init_wallet()
    anim("BOOTING CRYPTOFLEX CORE", 14, 0.35, sub=["loading modules", "mounting vault"], style="wave")
    anim("SYNCING LIVE PRICES", 6, 0.25, sub=["coingecko market feed"], style="pulse")
    refresh_prices(force=True)
    node_scan(n=4, delay=0.5)
    matrix_rain(rows=4, delay=0.2)
    while True:
        w = load(WALLET_FILE, w)
        w = run_faucet(w)
        w = run_drain_queue(w)
        w = process_pending(w)
        save(WALLET_FILE, w)
        clear(); header()
        print(paint(f"  ══ MAIN MENU ══  {DIM}role: {role}{RESET}\n"))
        opts = ["TOOLS — forge / spoof / recon / drainer / rig",
                "WALLET — balances, send, receive, history",
                "PORTFOLIO — live charts & movers",
                "MARKET WATCH — live prices all coins",
                "WHALE LEADERBOARD",
                "PRICE ALERT ENGINE — live",
                "LIVE PULSE — realtime dashboard",
                "LOG ARCHIVE",
                "SETTINGS"]
        if role == "admin": opts.append("ADMIN CONSOLE")
        for i, o in enumerate(opts, 1):
            col = OK if i % 2 else WARN
            print(f"  {paint('[')}{col}{i}{RESET}{paint(']')} {o}")
        print(f"  {paint('[')}{DIM}0{RESET}{paint(']')} Exit")
        try: m = int(input("\n  ➤ ").strip())
        except ValueError: continue
        if m == 0:
            if input("  Exit? (y/n): ").strip().lower() in ("y", "yes"):
                anim("SHUTTING DOWN", 8, 0.4, sub=["closing sockets", "flushing vault"], style="hexwall")
                break
        elif m == 1: tools()
        elif m == 2: wallet()
        elif m == 3: portfolio()
        elif m == 4: market_watch()
        elif m == 5: whales()
        elif m == 6: alerts()
        elif m == 7: live_pulse()
        elif m == 8: view_logs()
        elif m == 9: settings()
        elif m == 10 and role == "admin": admin_users(keys)

if __name__ == "__main__":
    try: main()
    except KeyboardInterrupt:
        print("\n" + paint("  [EXIT] Stay flexing.")); sys.exit(0)