#!/usr/bin/env python3
# ================= CRYPTOFLEX v6.0 :: LIVE SIMULATED FLEX ENGINE =================
import os, sys, json, time, random, string, datetime, urllib.request, urllib.error, urllib.parse

DATA_DIR = os.path.expanduser("~/cryptoflex")
os.makedirs(DATA_DIR, exist_ok=True)
KEY_FILE, WALLET_FILE, LOG_FILE, CACHE_FILE = (os.path.join(DATA_DIR, f) for f in
    ("keys.json", "wallet.json", "logs.json", "price_cache.json"))

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
def header():
    w = load(WALLET_FILE, None)
    total, top_name, top_amt = 0.0, "-", 0.0
    if w:
        for c, b in w["balances"].items():
            usd = b * live_price(c)
            total += usd
            if usd > top_amt: top_amt, top_name = usd, f"{b:g} {c}"
    print(gradient(BANNER))
    print(f"  {OK}{BOLD}WALLET TOTAL:{RESET} ${total:,.2f}   {OK}{BOLD}TOP ASSET:{RESET} {top_name}   "
          f"{DIM}[{datetime.datetime.now().strftime('%H:%M:%S')}]{RESET}\n")

def clear(): os.system("clear" if os.name != "nt" else "cls")

# ================= STORAGE =================
def load(f, default):
    try:
        with open(f) as fh: return json.load(fh)
    except Exception: return default
def save(f, d):
    with open(f, "w") as fh: json.dump(d, fh, indent=2)

# ================= LIVE DATA (FREE PUBLIC APIS) =================
HTTP_HEADERS = {"User-Agent": "Mozilla/5.0 (Terminal; CryptoFlex Sim)"}

def http_json(url, timeout=8):
    try:
        req = urllib.request.Request(url, headers=HTTP_HEADERS)
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode())
    except Exception:
        return None

# --- LIVE PRICES: CoinGecko free API, 60s cache, offline fallback ---
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
_price_cache = load(CACHE_FILE, {})  # {sym: {"price": x, "chg": y, "ts": t}}

def refresh_prices(force=False):
    """Bulk-fetch all supported coin prices + 24h change from CoinGecko (free)."""
    global _price_cache
    if not force and _price_cache and time.time() - max(v["ts"] for v in _price_cache.values()) < 60:
        return True
    ids = ",".join(CG_IDS.values())
    d = http_json(f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=usd&include_24hr_change=true")
    if not d: return False
    rev = {v: k for k, v in CG_IDS.items()}
    for cid, data in d.items():
        sym = rev.get(cid)
        if sym and "usd" in data:
            _price_cache[sym] = {"price": data["usd"], "chg": data.get("usd_24h_change", 0.0),
                                 "ts": time.time()}
    save(CACHE_FILE, _price_cache)
    return True

def live_price(sym):
    """Live price if fresh, else last cached, else fallback. Never crashes."""
    p = _price_cache.get(sym)
    if p and time.time() - p["ts"] < 300: return p["price"]
    refresh_prices()
    p = _price_cache.get(sym)
    return p["price"] if p else FALLBACK_PRICES.get(sym, 1)

def live_change(sym):
    p = _price_cache.get(sym)
    return p.get("chg", 0.0) if p else 0.0

# --- LIVE BALANCES: read-only public chain indexes ---
def real_balance(addr, chain):
    """Returns (balance, tx_count) or None. BTC/ETH/LTC/BCH/DOGE via public APIs."""
    if chain == "BTC":
        d = http_json(f"https://blockstream.info/api/address/{addr}")
        if d and "chain_stats" in d:
            bal = (d["chain_stats"]["funded_txo_sum"] - d["chain_stats"]["spent_txo_sum"]) / 1e8
            return bal, d["chain_stats"]["tx_count"]
    elif chain == "LTC":
        d = http_json(f"https://api.blockcypher.com/v1/ltc/main/addrs/{addr}/balance")
        if d and "balance" in d: return d["balance"] / 1e8, d.get("n_tx", 0)
    elif chain == "BCH":
        d = http_json(f"https://api.blockcypher.com/v1/bch/main/addrs/{addr}/balance")
        if d and "balance" in d: return d["balance"] / 1e8, d.get("n_tx", 0)
    elif chain == "DOGE":
        d = http_json(f"https://api.blockcypher.com/v1/doge/main/addrs/{addr}/balance")
        if d and "balance" in d: return d["balance"] / 1e8, d.get("n_tx", 0)
    elif chain == "ETH":
        d = http_json(f"https://api.blockcypher.com/v1/eth/main/addrs/{addr}/balance")
        if d and "balance" in d: return d["balance"] / 1e18, d.get("n_tx", 0)
    return None

def real_eth_tokens(addr):
    """ERC-20 token holdings for an ETH address via Ethplorer free API (read-only)."""
    d = http_json(f"https://api.ethplorer.io/getAddressInfo/{addr}?apiKey=freekey")
    if not d: return []
    out = []
    for t in (d.get("tokens") or [])[:12]:
        info = t.get("tokenInfo", {})
        dec = int(info.get("decimals") or 18)
        raw = int(t.get("rawBalance") or 0)
        bal = raw / (10 ** dec)
        sym = info.get("symbol", "???")
        price = info.get("price", {})
        usd = (price.get("rate") or 0) * bal if isinstance(price, dict) else 0
        out.append({"sym": sym, "balance": bal, "usd": round(usd, 2)})
    return out

def detect_chain(addr):
    a = addr
    if a.startswith("0x") and len(a) == 42: return "ETH"
    if a.startswith(("bc1", "1", "3")) and 26 <= len(a) <= 62: return "BTC"
    if a.startswith(("L", "M")) and len(a) == 34: return "LTC"
    if a.startswith(("q", "bitcoincash")) : return "BCH"
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
            off = i % len(wave); wv = wave[-off:] + wave[:-off]; gfx = paint(wv[:16])
        elif style == "hexwall":
            gfx = paint("".join(random.choice("0123456789abcdef") for _ in range(10)))
        else:
            gfx = spin[i % len(spin)]
        sys.stdout.write(f"\r  {paint(title)} {gfx} {bar_frame(pct)} {DIM}{s}{RESET}   ")
        sys.stdout.flush(); time.sleep(delay)
    sys.stdout.write("\r" + " " * 110 + "\r")
    print(f"  {OK}✔{RESET} {paint(title)}")

def node_scan(title="ESTABLISHING SECURE CHANNEL"):
    print(f"  {paint(title)}")
    for _ in range(6):
        ip = ".".join(str(random.randint(2, 254)) for _ in range(4))
        port = random.choice([8333, 8334, 30303, 9050, 50001])
        lat = random.uniform(4, 260)
        flag = OK if lat < 60 else WARN if lat < 150 else BAD
        sys.stdout.write(f"\r    node {ip:<15}:{port}  {flag}▲ {lat:5.1f} ms{RESET}   ")
        sys.stdout.flush(); time.sleep(0.7)
    sys.stdout.write("\r" + " " * 70 + "\r")
    print(f"    {OK}✔ 6 peers connected{RESET}")

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
        h = fake_txid()
        sys.stdout.write(f"\r    ◼ block {random.randint(800000,930000)} :: {paint(h[:44])}   ")
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
    for i in range(6):
        print(art); time.sleep(0.45); clear()
    print(paint(art))
    print(f"  {OK}{BOLD}>>> {text} <<< {RESET}")
    for _ in range(10):
        sys.stdout.write(paint("◆ ")); sys.stdout.flush(); time.sleep(0.15)
    print()

def yn(prompt):
    return input(f"  {paint(prompt)} (y/n): ").strip().lower() == "y"

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

COIN_NAMES = {"BTC": "Bitcoin", "ETH": "Ethereum", "USDT": "Tether", "USDC": "USD Coin",
              "BNB": "BNB", "SOL": "Solana", "XRP": "XRP", "DOGE": "Dogecoin", "LTC": "Litecoin",
              "TRX": "Tron", "BCH": "Bitcoin Cash", "ADA": "Cardano", "AVAX": "Avalanche",
              "MATIC": "Polygon", "DOT": "Polkadot", "SHIB": "Shiba Inu", "PEPE": "Pepe",
              "MONERO": "Monero", "TON": "Toncoin", "ARB": "Arbitrum"}
COINS = list(CG_IDS.keys())  # all coins now live-priced
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

# ================= KEY SYSTEM =================
def setup_keys():
    if not os.path.exists(KEY_FILE):
        key = new_key()
        save(KEY_FILE, {"owner_key": key, "users": {}})
        clear(); matrix_rain(rows=6, delay=0.3)
        print(f"\n  {paint(BOLD + '  [ FIRST RUN SETUP ]')}")
        time.sleep(2)
        type_line("  Generating your master access key...")
        anim("KEY GENERATION", 16, 0.5, style="hexwall")
        print(f"\n  {WARN}{BOLD}  MASTER ACCESS KEY: {key}{RESET}")
        print(f"  {DIM}  This is the ONLY admin key. Write it down!{RESET}")
        time.sleep(4)
        while True:
            ans = input(paint("\n  Key saved? (y/n): ")).strip().lower()
            if ans == "y":
                type_line("  Key confirmed. Locking in...", 0.05); time.sleep(2.5); break
            elif ans == "n":
                type_line("  Regenerating... save it this time!", 0.05); time.sleep(2.5)
                key = new_key()
                save(KEY_FILE, {"owner_key": key, "users": {}})
                print(f"\n  {WARN}{BOLD}  NEW MASTER ACCESS KEY: {key}{RESET}")
                time.sleep(4)
            else:
                print("  Please type 'y' or 'n'.")
    return load(KEY_FILE, None)

def login(keys):
    for attempt in range(5):
        clear(); header()
        print(paint(f"  ══ ACCESS TERMINAL ══  attempt {attempt + 1}/5\n"))
        anim("HANDSHAKE", 6, 0.45, sub=["tls exchange", "key derivation"], style="pulse")
        k = input(paint("  Enter Access Key: ")).strip()
        if k == keys["owner_key"]:
            print(f"  {OK}✔ Access granted — welcome, admin.{RESET}"); time.sleep(2.5)
            return "admin"
        if k in keys["users"]:
            print(f"  {OK}✔ Access granted — role: {keys['users'][k]}{RESET}"); time.sleep(2.5)
            return keys["users"][k]
        left = 4 - attempt
        if left > 0:
            print(f"  {BAD}✘ Invalid key.{RESET} {left} attempt(s) remaining."); time.sleep(3)
        else:
            print(f"  {BAD}{BOLD}[LOCKED] Too many failed attempts.{RESET}"); time.sleep(3)
            anim("LOCKING DOWN", 12, 0.5, sub=["wiping session", "sealing vault"], style="hexwall")
            if yn("Generate a NEW master key? Resets all user keys."):
                nk = new_key()
                save(KEY_FILE, {"owner_key": nk, "users": {}})
                add_log("system", {"event": "emergency key reset"})
                print(f"\n  {WARN}{BOLD}  [RECOVERY] NEW MASTER KEY: {nk}{RESET}")
                print(f"  {DIM}  All user keys wiped. Save this NOW!{RESET}")
                time.sleep(4); input(paint("  Key saved? (y/n): ")).strip().lower()
            else:
                print(paint("  No recovery. Closing..."))
            add_log("system", {"event": "lockout", "reason": "5 failed key attempts"})
            time.sleep(2); sys.exit(0)
    return None

# ================= WALLET =================
def wallet_total(w):
    return sum(b * live_price(c) for c, b in w["balances"].items())

def init_wallet():
    w = load(WALLET_FILE, None)
    if w: return w
    coin = random.choice(COINS)
    w = {"address": fake_addr("BTC" if coin not in ("ETH",) else "ETH"), "primary": coin,
         "balances": {coin: 1.0}, "txs": [], "pending": [], "faucet": None}
    save(WALLET_FILE, w); return w

# ================= MENU =================
def menu(title, options, footer=True):
    clear(); header()
    print(paint(f"  ══ {title} ══\n"))
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
    return f"{paint(sym)} ${live_price(sym):,.6g} {col}{ch:+.1f}%{RESET}"

# ================= TOOLS: TXID FORGE =================
def txid_gen():
    clear(); header()
    print(paint("  ══ TXID / BLOCK HASH FORGE ══\n"))
    anim("FORGING HASHES", 14, 0.55, sub=["seeding entropy", "double-SHA passes", "hex-dressing"], style="hexwall")
    for _ in range(3):
        print(f"  {paint('TXID')}   {fake_txid()}")
        print(f"  {paint('BLK-H')}  {fake_block_hash()}\n")
        time.sleep(0.6)
    add_log("spoof", {"type": "hash", "txid": fake_txid()})
    input("\n  Enter...")

# ================= TOOLS: TX SPOOF =================
def tx_spoof():
    clear(); header()
    print(paint("  ══ SPOOFED TX BROADCAST ══\n"))
    coin = pick("Select network asset:", COINS)
    amt = float(input("  Amount: ") or 0)
    sender = input("  Sender (blank = random): ").strip() or fake_addr(CHAINS.get(coin, "ETH"))
    recv = input("  Recipient: ").strip() or fake_addr(CHAINS.get(coin, "ETH"))
    method = pick("Injection method:", ["mempool-inject", "double-spend", "flash-broadcast", "relay-flood"])
    print()
    type_line(f"  {amt} {coin} {DIM}(${amt * live_price(coin):,.2f}){RESET} | {NETWORKS[coin]} | {method}", 0.04)
    anim("BROADCASTING", 22, 0.55, sub=["signing payload", "flooding relays", "awaiting first confirm"], style="wave")
    node_scan(); block_stream(6, 0.55)
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

# ================= TOOLS: SNIFFER =================
def sniffer():
    clear(); header()
    print(paint("  ══ NETWORK RECON SCANNER ══\n"))
    url = input("  Target endpoint: ").strip() or "unknown"
    addr = input("  Address: ").strip() or fake_addr("BTC")
    anim("DEEP SCANNING", 24, 0.6, sub=["probing endpoints", "indexing leaks", "correlating records"], style="hexwall")
    block_stream(5, 0.55)
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
            print(f"   {WARN}▸{RESET} {t}"); found.append(t); time.sleep(0.4)
        add_log("sniffer", {"url": url, "addr": addr, "findings": found, "result": "HIT"})
    else:
        print(f"\n  {BAD}[NO RECORDS] target clean{RESET}")
        add_log("sniffer", {"url": url, "addr": addr, "result": "MISS"})
    input("\n  Enter...")

# ================= TOOLS: MINING RIG =================
def mining_rig():
    w = load(WALLET_FILE, init_wallet())
    clear(); header()
    print(paint("  ══ MINING RIG ══\n"))
    coin = pick("Coin to mine:", COINS)
    method = pick("Mining method:", ["solo", "pool", "merged-mining", "stratum-tcp"])
    try: duration = float(input("  Session duration in minutes (0 = until Ctrl+C): ") or 0)
    except ValueError: duration = 0
    hashrate = random.uniform(80, 420)
    print(f"\n  {paint('RIG')} CFX-RIG-01 | {price_tag(coin)} | {OK}{hashrate:.1f} MH/s{RESET} | {paint(method)}")
    print(f"  {DIM}50 shares per payout. Ctrl+C stops anytime, keeps earnings.{RESET}\n")
    shares, target, earned = 0, 50, 0.0
    end = time.time() + duration * 60 if duration > 0 else None
    try:
        while end is None or time.time() < end:
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
                earned += payout; save(WALLET_FILE, w)
                print(f"  {OK}{BOLD}◆ BLOCK MINED{RESET} +{payout} {coin}  ~${earned * live_price(coin):,.4f} session @ live price")
                time.sleep(1.2)
        print(f"\n  {paint('SESSION COMPLETE')} earnings: {round(earned, 8)} {coin} (~${earned * live_price(coin):,.4f})")
    except KeyboardInterrupt:
        print(f"\n  {paint('RIG OFFLINE')} session earnings: {round(earned, 8)} {coin}")
    add_log("system", {"event": "mining session", "coin": coin, "earned": earned, "method": method})
    input("\n  Enter...")

# ================= TOOLS: WALLET DRAINER (LIVE) =================
def drain_flow(w, coin, total_amt, n_mixers, validate):
    clear(); header()
    print(paint("  ══ DRAIN FLOW ══\n"))
    mixers = [fake_addr(CHAINS.get(coin, "ETH")) for _ in range(max(n_mixers, 1))]
    if validate:
        anim("VALIDATING MIXER WALLETS", 10, 0.5, sub=["pinging nodes", "checking balances"], style="pulse")
        for m in mixers: print(f"   {OK}✔{RESET} {m[:20]}... valid")
    remaining = total_amt
    chunk_max = total_amt / random.randint(6, 12) or total_amt
    i = 0
    anim("OPENING DRAIN CHANNEL", 12, 0.55, sub=["routing through mixers", "slicing amounts"], style="hexwall")
    while remaining > 0:
        i += 1
        amt = round(min(remaining, random.uniform(chunk_max * 0.3, chunk_max)), 8)
        remaining = round(remaining - amt, 8)
        to = random.choice(mixers)
        txid = fake_txid()
        anim(f"DRAIN TX {i} :: {amt} {coin}", 5, 0.35, sub=["routing", "mixing", "confirming"], style="wave")
        w["balances"][coin] = round(max(w["balances"].get(coin, 0) - amt, 0), 8)
        w["txs"].append({"dir": "OUT", "coin": coin, "amount": amt, "txid": txid, "to": to,
                         "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")})
        save(WALLET_FILE, w)
        print(f"   {BAD}→{RESET} sent {amt} {coin} → mixer {to[:16]}...  {DIM}left: {remaining}{RESET}")
        if remaining <= 0:
            print(f"\n  {OK}{BOLD}◆ WALLET FULLY DRAINED — {i} split transactions{RESET}")
            break
    add_log("drainer", {"stage": "drain-flow", "coin": coin, "total": total_amt, "mixers": n_mixers, "txs": i})
    input("\n  Enter...")

def drainer():
    clear(); header()
    print(paint("  ══ WALLET DRAINER ══\n"))
    url = input("  Target URL / platform: ").strip() or "unknown"
    addr = input("  Wallet address: ").strip()
    chain = detect_chain(addr) if addr else None
    tokens = []
    if addr and chain:
        anim("CONTACTING LIVE CHAIN INDEX", 12, 0.5,
             sub=["blockstream", "blockcypher", "ethplorer", "rest-api"], style="pulse")
        real = real_balance(addr, chain)
        if real is not None:
            bal, txs = real
            px = live_price(chain)
            print(f"  {OK}{BOLD}[LIVE CHAIN DATA]{RESET} {paint(chain)}")
            print(f"   balance : {OK}{bal:g} {chain}{RESET}  {DIM}~${bal * px:,.2f} @ live price{RESET}")
            print(f"   txs     : {txs} on-chain")
        else:
            print(f"  {WARN}[!] index unreachable for {chain} — simulated profile{RESET}")
            bal = round(random.uniform(0, 12), 4)
            print(f"  {DIM}simulated balance: {bal} {chain}{RESET}")
        if chain == "ETH":
            anim("SCANNING TOKEN HOLDINGS", 10, 0.45, sub=["ethplorer index", "decoding ERC-20"], style="hexwall")
            tokens = real_eth_tokens(addr)
            if tokens:
                print(f"  {OK}{BOLD}[LIVE TOKENS FOUND: {len(tokens)}]{RESET}")
                for t in tokens:
                    print(f"   {WARN}▸{RESET} {t['sym']:<8} {t['balance']:.4f}  {DIM}~${t['usd']}{RESET}")
            else:
                print(f"  {DIM}no ERC-20 tokens found (or index offline){RESET}")
    else:
        print(f"  {DIM}address format not recognized — simulated profile mode{RESET}")
    print(f"\n  {paint('── ATTACK SURFACE SELECTION ──')}")
    has_platform = yn("Platform access available?")
    has_seed     = yn("Seed phrase available?")
    has_2fa      = yn("2FA code available?")
    has_email    = yn("Email access available?")
    has_pw       = yn("Password available?")
    have = sum([has_platform, has_seed, has_2fa, has_email, has_pw])
    print(f"\n  {paint('surface score')}: {have}/5")
    if have < 2:
        print(f"  {BAD}✘ INSUFFICIENT SURFACE — need at least 2 access vectors. Aborting.{RESET}")
        add_log("drainer", {"url": url, "addr": addr, "surface": have, "result": "ABORTED"})
        input("\n  Enter..."); return
    anim("BREACH ATTEMPT", 24, 0.6, sub=["assembling vectors", "bypassing session guard",
                                         "farming signature", "exfiltrating keys"], style="hexwall")
    block_stream(4, 0.5)
    if random.random() < 0.5:
        big_win("DRAINER COMPLETE")
        print(f"  {OK}{BOLD}✔ Keys extracted. Vault compromised.{RESET}")
        add_log("drainer", {"url": url, "addr": addr, "surface": have, "result": "SUCCESS"})
        if yn("\n  Start wallet drain flow?"):
            options = COINS + [f"token:{t['sym']}" for t in tokens]
            sel = pick("Coin / token to drain:", options)
            if sel.startswith("token:"):
                coin, amt = sel[6:], float(input("  Amount: ") or 0)
                add_log("drainer", {"stage": "token-drain", "token": coin, "amount": amt})
                # token drains still route through mixer sim but tracked separately
                coin = sel
                amt_token = amt
                # simulate using token symbol directly in flow
                w = load(WALLET_FILE, init_wallet())
                drain_flow(w, "ETH", amt, int(input("  How many mixer wallets: ") or 3), yn("Validate mixer wallets first?"))
                return
            amt = float(input("  Amount to drain: ") or 0)
            n_mixers = int(input("  How many mixer wallets: ") or 3)
            validate = yn("Validate mixer wallets before mixing?")
            drain_flow(load(WALLET_FILE, init_wallet()), coin, amt, n_mixers, validate)
    else:
        print(f"\n  {BAD}✘ DRAIN FAILED — signature guard tripped, session burned{RESET}")
        add_log("drainer", {"url": url, "addr": addr, "surface": have, "result": "FAILED"})
    input("\n  Enter...")

# ================= TOOLS+ HUB =================
def tools():
    while True:
        m = menu("TOOLS +", ["TXID / Block Hash Forge",
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
            print(f"  {OK}◆ RECEIVED{RESET} +{p['amount']} {p['coin']} — {p['txid'][:20]}...")
            w["pending"].remove(p)
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
                usd = b * live_price(c)
                ch = live_change(c)
                col = OK if ch >= 0 else BAD
                print(f"   {paint(c):<10} {b:>14}  ${live_price(c):,.6g} {col}{ch:+.1f}%{RESET}  {DIM}~${usd:,.2f}{RESET}")
            print(f"\n   {paint('Address')} {w['address']}")
            if w.get("pending"): print(f"   {WARN}⧗ pending incoming: {len(w['pending'])}{RESET}")
            input("\n  Enter..."); continue
        if m == 2:
            coin = pick("Asset:", list(w["balances"].keys()))
            amt = float(input("  Amount: ") or 0)
            if amt <= w["balances"].get(coin, 0):
                to = input("  To address: ").strip() or fake_addr(CHAINS.get(coin, "ETH"))
                split = yn("Split into small transactions?")
                if split:
                    chunks = random.randint(5, 10)
                    left = amt
                    anim("OPENING SPLIT CHANNEL", 10, 0.5, style="hexwall")
                    for i in range(chunks):
                        a = round(left / (chunks - i), 8) if i < chunks - 1 else left
                        left = round(left - a, 8)
                        txid = fake_txid()
                        anim(f"SPLIT TX {i + 1}/{chunks}", 4, 0.3, style="wave")
                        w["balances"][coin] = round(max(w["balances"].get(coin, 0) - a, 0), 8)
                        w["txs"].append({"dir": "OUT", "coin": coin, "amount": a, "txid": txid, "to": to,
                                         "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")})
                        save(WALLET_FILE, w)
                        print(f"   {BAD}→{RESET} {a} {coin}  {DIM}tx {txid[:18]}...{RESET}")
                    print(f"  {OK}◆ SPLIT SEND COMPLETE{RESET}")
                else:
                    anim("SIGNING & BROADCASTING", 18, 0.6, sub=["ECDSA sign", "serializing", "relay flood"], style="wave")
                    if random.random() < 0.85:
                        w["balances"][coin] = round(w["balances"][coin] - amt, 8)
                        txid = fake_txid()
                        w["txs"].append({"dir": "OUT", "coin": coin, "amount": amt, "txid": txid, "to": to,
                                         "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")})
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

# ================= HIDDEN BACKGROUND FAUCET =================
def setup_faucet(w):
    clear(); header()
    print(paint("  ══ PRIVATE CHANNEL ══\n"))
    try:
        per = float(input("  Total token amount: ") or 1)
        n_tx = int(input("  Number of split transactions: ") or 1)
        n_w = int(input("  Number of sending wallets: ") or 1)
        delay = float(input("  Seconds between TXs: ") or 3)
        coin = pick("Token:", COINS)
    except Exception:
        return
    w["faucet"] = {"coin": coin, "total": per, "remaining": per, "splits": n_tx,
                   "wallets": max(n_w, 1), "delay": max(delay, 1.0), "next": time.time() + delay}
    add_log("system", {"event": "channel armed", "coin": coin, "total": per, "splits": n_tx})
    anim("ARMING CHANNEL", 8, 0.5, sub=["opening sockets", "handshakes", "queueing flows"], style="pulse")
    print(f"  {OK}◆ Channel armed — {per} {coin} will flow in {n_tx} splits. Returning...{RESET}")
    time.sleep(2)

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
        print(f"  {OK}◆ INCOMING{RESET} +{amt} {f['coin']} from {src[:14]}... {DIM}tx {txid[:20]}...{RESET}")
    f["remaining"] = round(f["remaining"] - amt, 8)
    f["splits"] -= 1
    f["next"] = time.time() + f["delay"]
    if f["splits"] <= 0 or f["remaining"] <= 0:
        w["faucet"] = None
        print(f"  {OK}◆ Channel complete — full amount flowed in.{RESET}")
    save(WALLET_FILE, w)
    return w

# ================= PORTFOLIO (LIVE) =================
def portfolio():
    refresh_prices()
    w = load(WALLET_FILE, init_wallet()); w = process_pending(w); save(WALLET_FILE, w)
    clear(); header()
    print(paint("  ══ PORTFOLIO ══ {DIM}(live prices via CoinGecko){RESET}\n".replace("{DIM}", DIM).replace("{RESET}", RESET)))
    total = 0
    for c, b in w["balances"].items():
        price = live_price(c); ch = live_change(c)
        col = OK if ch >= 0 else BAD
        usd = b * price; total += usd
        print(f"   {paint(c):<12} {b:>12.4f}  ${price:,.6g} {col}{ch:+.1f}%{RESET}  {DIM}~${usd:,.2f}{RESET}")
    print(f"\n   {paint(BOLD + 'TOTAL')}: ${total:,.2f}")
    print(f"\n  {paint('TOP MOVERS — LIVE 24H')}")
    movers = sorted(_price_cache.items(), key=lambda kv: -abs(kv[1].get("chg", 0)))[:3] if _price_cache else []
    if movers:
        for sym, p in movers:
            ch = p.get("chg", 0); col = OK if ch >= 0 else BAD
            print(f"   {paint(sym):<12} ${p['price']:,.6g} {col}{ch:+.2f}%{RESET}")
    else:
        print(f"   {DIM}offline — cached data unavailable{RESET}")
    add_log("system", {"event": "portfolio viewed", "total_usd": round(total, 2)})
    input("\n  Enter...")

# ================= MARKET WATCH (new: live coin table) =================
def market_watch():
    clear(); header()
    print(paint("  ══ MARKET WATCH — LIVE ══\n"))
    anim("FETCHING LIVE MARKET", 12, 0.4, sub=["coingecko api", "parsing 24h stats"], style="pulse")
    ok = refresh_prices(force=True)
    if not ok:
        print(f"  {BAD}[OFFLINE] falling back to cached/fallback prices{RESET}")
    print(f"\n   {'ASSET':<12}{'PRICE':>16}{'24H':>10}   {DIM}source: {'LIVE' if ok else 'CACHE'}{RESET}")
    for sym in COINS:
        p = _price_cache.get(sym)
        price = p["price"] if p else FALLBACK_PRICES[sym]
        ch = p.get("chg", 0) if p else 0
        col = OK if ch >= 0 else BAD
        print(f"   {paint(sym):<12}{price:>16,.6g} {col}{ch:>+9.1f}%{RESET}")
        time.sleep(0.08)
    input("\n  Enter...")

# ================= WHALE LEADERBOARD =================
def whales():
    clear(); header()
    print(paint("  ══ WHALE LEADERBOARD ══\n"))
    anim("SNIPING WHALE WALLETS", 14, 0.55, sub=["tracking clusters", "scoring holdings"], style="wave")
    rows = sorted([(fake_addr(random.choice(list(CHAINS.values()))), random.uniform(1, 9000)) for _ in range(8)],
                  key=lambda x: -x[1])
    for i, (a, v) in enumerate(rows, 1):
        medal = ["🥇", "🥈", "🥉"][i - 1] if i <= 3 else f"{i}."
        print(f"   {medal} {a[:22]}...  {paint(f'${v:,.0f}')}")
    me = load(WALLET_FILE, init_wallet())
    print(f"\n   {paint('YOU')}: rank #{random.randint(9, 9999)} with ${wallet_total(me):,.2f}")
    input("\n  Enter...")

# ================= PRICE ALERTS (LIVE) =================
def alerts():
    clear(); header()
    print(paint("  ══ PRICE ALERT ENGINE ══\n"))
    coin = pick("Asset to monitor:", COINS)
    anim("LINKING MARKET FEEDS", 12, 0.55, sub=["coingecko live", "subscribing ticker"], style="pulse")
    base = live_price(coin)
    for i in range(6):
        refresh_prices()
        p = live_price(coin)
        drift = (p - base) / base * 100 if base else 0
        col = OK if drift >= 0 else BAD
        print(f"   tick {i + 1}: {coin} {col}${p:,.6g}{RESET} {DIM}({drift:+.2f}% since start){RESET}")
        time.sleep(1.6)
    ch = live_change(coin)
    if abs(ch) > 3:
        print(f"\n  {WARN}{BOLD}🔔 LIVE ALERT — {coin} at {ch:+.1f}% / 24h!{RESET}")
        add_log("system", {"event": "price alert", "coin": coin, "chg": ch, "triggered": True})
    else:
        print(f"\n  {DIM}no triggers — market quiet ({ch:+.1f}% / 24h){RESET}")
        add_log("system", {"event": "price alert", "coin": coin, "chg": ch, "triggered": False})
    input("\n  Enter...")

# ================= LIVE PULSE =================
def live_pulse():
    clear(); header()
    print(paint("  ══ LIVE PULSE ══  {DIM}(Ctrl+C to exit){RESET}\n".replace("{DIM}", DIM).replace("{RESET}", RESET)))
    try:
        while True:
            w = load(WALLET_FILE, init_wallet())
            w = run_faucet(w); w = process_pending(w); save(WALLET_FILE, w)
            tot = wallet_total(w)
            sym = random.choice(COINS)
            ch = live_change(sym)
            col = OK if ch >= 0 else BAD
            sys.stdout.write(
                f"\r  {paint('Σ')} ${tot:>12,.2f}  {paint(sym)} ${live_price(sym):,.6g} {col}{ch:+.2f}%{RESET} "
                f"{paint('pend')} {len(w.get('pending', []))}  {paint('txs')} {len(w['txs'])}   ")
            sys.stdout.flush(); time.sleep(2)
    except KeyboardInterrupt:
        print("\n")

# ================= LOGS =================
def view_logs():
    logs = load(LOG_FILE, {})
    while True:
        kinds = list(logs.keys())
        if not kinds:
            clear(); header(); print("  No logs yet."); input("\n  Enter..."); return
        m = menu("LOG ARCHIVE", [f"{k} — {len(logs[k])} entries" for k in kinds])
        if m == 0: return
        k = kinds[m - 1]
        clear(); header(); print(paint(f"  ══ {k.upper()} ══\n"))
        for e in logs[k][-30:]:
            print(f"   {DIM}{e['time']}{RESET} " + json.dumps({x: y for x, y in e.items() if x != 'time'})[:110])
        input("\n  Enter...")

# ================= ADMIN =================
def admin_users(keys):
    while True:
        m = menu("ADMIN CONSOLE", ["Create user key", "List users", "Revoke key", "Change user role"])
        if m == 0:
            save(KEY_FILE, keys); return
        if m == 1:
            nk = new_key()
            role = pick("Role:", ["user", "vip", "mod"])
            keys["users"][nk] = role
            save(KEY_FILE, keys)
            anim("MINTING KEY", 10, 0.5, sub=["deriving", "registering"], style="hexwall")
            print(f"  {OK}{BOLD}◆ NEW KEY: {nk}{RESET}  {DIM}({role}){RESET}")
            print(f"  {DIM}Works instantly — master key untouched.{RESET}")
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

# ================= SETTINGS =================
def settings():
    global theme
    opts = ["Cycle to next theme", "Force price cache refresh"] + \
           [f"Use {t} theme" for t in THEMES if t != theme]
    m = menu("SETTINGS", opts)
    if m == 0: return
    if m == 1:
        theme = THEMES[(THEMES.index(theme) + 1) % len(THEMES)]
    elif m == 2:
        anim("SYNCING LIVE PRICES", 12, 0.4, sub=["coingecko", "blockstream", "ethplorer"], style="pulse")
        ok = refresh_prices(force=True)
        print(f"  {OK}✔ prices updated — {len(_price_cache)} coins live{RESET}" if ok
              else f"  {BAD}✘ network unreachable — cache kept{RESET}")
        add_log("system", {"event": "price refresh", "ok": ok})
        input("\n  Enter..."); return
    else:
        theme = [t for t in THEMES if t != theme][m - 3]
    add_log("system", {"event": "theme changed", "theme": theme})
    print(paint(f"  Theme → {theme}")); time.sleep(1.5)

# ================= MAIN =================
def main():
    clear()
    matrix_rain(rows=10, delay=0.3)
    keys = setup_keys()
    role = login(keys)
    w = init_wallet()
    anim("BOOTING CRYPTOFLEX CORE", 20, 0.6, sub=["loading modules", "mounting vault", "calibrating rig"], style="wave")
    anim("SYNCING LIVE PRICES", 10, 0.45, sub=["coingecko market feed"], style="pulse")
    refresh_prices(force=True)
    node_scan(); matrix_rain(rows=5, delay=0.25)
    while True:
        w = load(WALLET_FILE, w)
        w = run_faucet(w)
        w = process_pending(w)
        save(WALLET_FILE, w)
        clear(); header()
        print(paint(f"  ══ MAIN MENU ══  {DIM}role: {role}{RESET}\n"))
        opts = ["TOOLS + — forge / spoof / recon / drainer / rig",
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
            if input("  Exit? (y/n): ").lower() == "y":
                anim("SHUTTING DOWN", 10, 0.5, sub=["closing sockets", "flushing vault"], style="hexwall")
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