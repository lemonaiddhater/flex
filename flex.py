#!/usr/bin/env python3
# ================= CRYPTOFLEX v3.1 - Prank Crypto Flexer Tool (100% SIMULATED) =================
import os, sys, json, time, random, string, datetime

DATA_DIR = os.path.expanduser("~/cryptoflex")
os.makedirs(DATA_DIR, exist_ok=True)
KEY_FILE, WALLET_FILE, LOG_FILE = (os.path.join(DATA_DIR, f) for f in ("keys.json", "wallet.json", "logs.json"))

# ---------- THEMES ----------
THEMES = ["green", "cyan", "red", "purple", "yellow", "blue", "rainbow"]
theme = "green"
COLS = {"green": "\033[92m", "cyan": "\033[96m", "red": "\033[91m",
        "purple": "\033[95m", "yellow": "\033[93m", "blue": "\033[94m"}
RAINBOW = ["\033[91m", "\033[93m", "\033[92m", "\033[96m", "\033[94m", "\033[95m"]
def paint(s):
    if theme == "rainbow":
        return "".join(RAINBOW[i % len(RAINBOW)] + ch + "\033[0m" for i, ch in enumerate(s))
    return COLS[theme] + s + "\033[0m"

BANNER = r"""
   ______  __ __  ______  ____  __ __  ______  __ __   ___   ____
  / ___/ |/ // / / / __ \/ __ \/ // / / ___/ |/ /  | / _ | / __/
 / (_ /    // /_/ / /_/ / /_/ / _  / / / _ |    /  |/ __ | _ \
 \___/_/|_/ \____/\____/____//_//_/ /_/  |_|_/_/ |_/____|/____/
"""
def banner():
    print(paint(BANNER))
    print(paint("  [ CRYPTOFLEX v3.1 :: SIMULATED FLEX ENGINE :: NOT REAL CRYPTO ]\n"))

def clear(): os.system("clear" if os.name != "nt" else "cls")

# ---------- STORAGE ----------
def load(f, default):
    try:
        with open(f) as fh: return json.load(fh)
    except Exception: return default
def save(f, d):
    with open(f, "w") as fh: json.dump(d, fh, indent=2)

# ---------- ANIMATIONS (SLOW / CINEMATIC) ----------
def anim(text, frames=12, delay=0.25):
    spin = ["|", "/", "-", "\\"]
    for i in range(frames):
        bar = "#" * int((i + 1) / frames * 30) + "-" * (30 - int((i + 1) / frames * 30))
        sys.stdout.write(f"\r{paint(text)} [{bar}] {spin[i % 4]} {int((i+1)/frames*100)}%")
        sys.stdout.flush(); time.sleep(delay)
    print()

def block_anim():
    chars = "0123456789abcdef"
    print(paint("  [ BLOCKCHAIN SYNC ANIMATION ]"))
    for i in range(10):
        h = "".join(random.choice(chars) for _ in range(48))
        sys.stdout.write(f"\r  block {random.randint(800000,900000)} :: {h[:40]}... ")
        sys.stdout.flush(); time.sleep(0.45)
    print()

# ---------- FAKE DATA ----------
def fake_txid(): return "".join(random.choice("0123456789abcdef") for _ in range(64))
def fake_block_hash(): return "00000000000000" + fake_txid()[:48]
def fake_addr(chain):
    p = {"BTC": ["1", "3", "bc1"], "ETH": ["0x"], "LTC": ["L", "M"], "DOGE": ["D"],
         "BCH": ["q", "1"], "TRX": ["T"], "XRP": ["r"], "SOL": [""], "ADA": ["addr1"],
         "DOT": ["1"], "MONERO": ["4"], "TON": ["UQ"]}.get(chain, ["0x"])
    n = {"BTC": 34, "ETH": 42, "LTC": 34, "DOGE": 34, "BCH": 42, "TRX": 34, "XRP": 33,
         "SOL": 44, "ADA": 45, "DOT": 47, "MONERO": 95, "TON": 48}.get(chain, 42)
    pre = random.choice(p)
    body = "".join(random.choice(string.ascii_letters + string.digits) for _ in range(max(n - len(pre), 8)))
    return pre + body

COINS = {
    "BTC":  {"name": "Bitcoin",       "price": 67000,  "chain": "BTC"},
    "ETH":  {"name": "Ethereum",      "price": 3400,   "chain": "ETH"},
    "USDT": {"name": "Tether",        "price": 1,      "chain": "ETH"},
    "USDC": {"name": "USD Coin",      "price": 1,      "chain": "ETH"},
    "BNB":  {"name": "BNB",           "price": 610,    "chain": "ETH"},
    "SOL":  {"name": "Solana",        "price": 165,    "chain": "SOL"},
    "XRP":  {"name": "XRP",           "price": 0.62,   "chain": "XRP"},
    "DOGE": {"name": "Dogecoin",      "price": 0.16,   "chain": "DOGE"},
    "LTC":  {"name": "Litecoin",      "price": 85,     "chain": "LTC"},
    "TRX":  {"name": "Tron",          "price": 0.13,   "chain": "TRX"},
    "BCH":  {"name": "Bitcoin Cash",  "price": 420,    "chain": "BCH"},
    "ADA":  {"name": "Cardano",       "price": 0.45,   "chain": "ADA"},
    "AVAX": {"name": "Avalanche",     "price": 28,     "chain": "ETH"},
    "MATIC":{"name": "Polygon",       "price": 0.52,   "chain": "ETH"},
    "DOT":  {"name": "Polkadot",      "price": 4.2,    "chain": "DOT"},
    "SHIB": {"name": "Shiba Inu",     "price": 0.000018, "chain": "ETH"},
    "PEPE": {"name": "Pepe",          "price": 0.000009, "chain": "ETH"},
    "MONERO":{"name": "Monero",       "price": 155,    "chain": "MONERO"},
    "TON":  {"name": "Toncoin",       "price": 5.3,    "chain": "TON"},
    "ARB":  {"name": "Arbitrum",      "price": 0.78,   "chain": "ETH"},
}
NETWORKS = {"BTC": "Bitcoin Mainnet", "ETH": "Ethereum Mainnet", "USDT": "ERC-20 / TRC-20",
            "USDC": "ERC-20", "BNB": "BEP-20", "SOL": "Solana Mainnet", "XRP": "XRP Ledger",
            "DOGE": "Dogecoin Mainnet", "LTC": "Litecoin Mainnet", "TRX": "Tron Mainnet",
            "BCH": "BCH Mainnet", "ADA": "Cardano Mainnet", "AVAX": "Avalanche C-Chain",
            "MATIC": "Polygon PoS", "DOT": "Polkadot Relay", "SHIB": "ERC-20",
            "PEPE": "ERC-20", "MONERO": "Monero Mainnet", "TON": "TON Mainnet", "ARB": "Arbitrum One"}

def add_log(kind, entry):
    logs = load(LOG_FILE, {})
    logs.setdefault(kind, []).append({**entry, "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
    save(LOG_FILE, logs)

def new_key():
    return "CFX-" + "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(4)) + "-" + \
           "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(4))

# ---------- KEY SYSTEM (SLOW REVEAL + "KEY SAVED?" + 5 TRIES) ----------
def setup_keys():
    if not os.path.exists(KEY_FILE):
        key = new_key()
        save(KEY_FILE, {"owner_key": key, "users": {}})
        print(paint("\n  [ FIRST RUN SETUP ]"))
        time.sleep(1.5)
        print(paint("  Generating your MASTER ACCESS KEY..."))
        time.sleep(2)
        print(paint(f"\n  MASTER ACCESS KEY: {key}"))
        print(paint("  This is the ONLY admin key. Write it down!"))
        time.sleep(3)
        while True:
            ans = input(paint("\n  Key saved? (y/n): ")).strip().lower()
            if ans == "y":
                print(paint("  Key confirmed. Locking in...")); time.sleep(2)
                break
            elif ans == "n":
                print("  Regenerating a new key... make sure to save it this time!")
                time.sleep(2)
                key = new_key()
                save(KEY_FILE, {"owner_key": key, "users": {}})
                print(paint(f"\n  NEW MASTER ACCESS KEY: {key}"))
                time.sleep(3)
            else:
                print("  Please type 'y' or 'n'.")
        time.sleep(2)
    return load(KEY_FILE, None)

def login(keys):
    for attempt in range(5):
        clear(); banner()
        print(paint(f"  [ ACCESS REQUIRED ]  Attempt {attempt + 1}/5\n"))
        k = input(paint("  Enter Access Key: ")).strip()
        if k == keys["owner_key"]:
            print(paint("  Access granted. Welcome, admin.")); time.sleep(2)
            return "admin"
        if k in keys["users"]:
            print(paint(f"  Access granted. Role: {keys['users'][k]}")); time.sleep(2)
            return keys["users"][k]
        left = 4 - attempt
        if left > 0:
            print(f"  Invalid key. {left} attempt(s) remaining.")
            time.sleep(2.5)
        else:
            print(paint("  [LOCKED] Too many failed attempts."))
            time.sleep(3)
            print(paint("  Securing files and closing..."))
            anim("LOCKING DOWN", 10, 0.3)
            add_log("system", {"event": "lockout", "reason": "5 failed key attempts"})
            print(paint("  Goodbye.")); time.sleep(2)
            sys.exit(0)
    return None

# ---------- WALLET ----------
def init_wallet():
    w = load(WALLET_FILE, None)
    if w: return w
    coin = random.choice(list(COINS.keys()))
    w = {"address": fake_addr(COINS[coin]["chain"]),
         "primary": coin, "balances": {coin: 1.0}, "seed": None, "txs": [], "pending": []}
    save(WALLET_FILE, w); return w

# ---------- MENU HELPERS ----------
def menu(title, options):
    clear(); banner()
    print(paint(f"  == {title} ==\n"))
    for i, label in enumerate(options, 1): print(f"  [{i}] {label}")
    print("  [0] Back")
    try: return int(input("\n  > ").strip())
    except ValueError: return 0

def pick(prompt, choices):
    print(paint(prompt))
    for i, c in enumerate(choices, 1): print(f"   [{i}] {c}")
    try: return choices[int(input("  > ").strip()) - 1]
    except Exception: return choices[0]

# ---------- FEATURE: TXID SPOOFER ----------
def tx_spoof():
    while True:
        m = menu("FAKE TX SPOOFER (SIMULATED)",
                 ["Generate fake TXID / block hash",
                  "Full spoofed transaction broadcast (fake)"])
        if m == 0: return
        if m == 1:
            txid, bh = fake_txid(), fake_block_hash()
            print(paint(f"\n  TXID       : {txid}"))
            print(paint(f"  BLOCK HASH : {bh}"))
            add_log("spoof", {"type": "hash", "txid": txid, "block_hash": bh})
            input("\n  Enter to continue..."); continue
        coin = pick("  Choose coin:", list(COINS.keys()))
        amt = float(input("  Amount: ") or 0)
        sender = input("  Sender (blank = random): ").strip() or fake_addr(COINS[coin]["chain"])
        recv = input("  Recipient: ").strip() or fake_addr(COINS[coin]["chain"])
        method = pick("  Spoof method:", ["mempool-inject (sim)", "double-spend (sim)",
                                          "flash-broadcast (sim)", "relay-flood (sim)"])
        print(paint(f"\n  Coin: {coin} | Amt: {amt} {coin} | Net: {NETWORKS[coin]}"))
        print(paint(f"  From: {sender}\n  To  : {recv}\n  Method: {method}"))
        anim("BROADCASTING TO MEMPOOL", 20, 0.25); block_anim()
        if random.random() < 0.5:
            txid = fake_txid()
            print(paint(f"\n  [SUCCESS] Fake TX broadcast confirmed!\n  TXID: {txid}\n  Block: {random.randint(800000,920000)}"))
            add_log("spoof", {"type": "tx", "coin": coin, "amount": amt, "txid": txid,
                              "from": sender, "to": recv, "method": method, "status": "SUCCESS"})
            w = load(WALLET_FILE, init_wallet())
            w.setdefault("pending", []).append({"coin": coin, "amount": amt, "txid": txid,
                                                "delay": random.randint(1, 3)})
            save(WALLET_FILE, w)
        else:
            print("\n  [FAILED] Broadcast rejected by network (simulated).")
            add_log("spoof", {"coin": coin, "amount": amt, "status": "FAILED", "method": method})
        input("\n  Enter to continue...")

# ---------- FEATURE: WALLET SNIFFER (SIMULATED) ----------
def sniffer():
    clear(); banner()
    print(paint("  == WALLET SNIFFER (100% SIMULATED / PRANK) ==\n"))
    url = input("  Target URL/platform: ").strip() or "unknown"
    addr = input("  Wallet address: ").strip() or fake_addr("BTC")
    anim("SCANNING DATABASES", 22, 0.25); block_anim()
    if random.random() < 0.5:
        pool = ["email: victim@{d}.com", "phone: +1-555-{n}", "password: {p}",
                "seed phrase: {s}", "2FA backup: {c}", "last login IP: 45.{a}.x.x",
                "exchange account: {e}", "API key: {k}"]
        count = random.choice([1, 2, 4, 8])
        print(paint(f"\n  [HIT] Found {count} record(s):"))
        found = []
        words = ["moon", "diamond", "satoshi", "lambo", "flex", "giga", "rocket"]
        for _ in range(count):
            t = random.choice(pool).format(
                d="".join(random.choices(string.ascii_lowercase, k=5)),
                n=random.randint(200, 999),
                p="".join(random.choices(string.ascii_letters + string.digits, k=10)),
                s=" ".join(random.choices(words, k=12)),
                c=str(random.randint(100000, 999999)),
                a=random.randint(1, 254),
                e=random.choice(["Binance", "Coinbase", "Kraken", "OKX"]),
                k=fake_txid()[:32])
            print("   - " + t); found.append(t)
        add_log("sniffer", {"url": url, "addr": addr, "findings": found, "result": "HIT"})
    else:
        print("\n  [MISS] No records found for this target (simulated).")
        add_log("sniffer", {"url": url, "addr": addr, "result": "MISS"})
    input("\n  Enter to continue...")

# ---------- FEATURE: WALLET ----------
def process_pending(w):
    for p in list(w.get("pending", [])):
        p["delay"] -= 1
        if p["delay"] <= 0:
            w["balances"][p["coin"]] = round(w["balances"].get(p["coin"], 0) + p["amount"], 8)
            w["txs"].append({"dir": "IN", "coin": p["coin"], "amount": p["amount"], "txid": p["txid"],
                             "from": "external", "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")})
            print(paint(f"  [RECEIVED] +{p['amount']} {p['coin']} confirmed! TXID: {p['txid'][:20]}..."))
            w["pending"].remove(p)
    return w

def wallet():
    w = load(WALLET_FILE, init_wallet())
    w = process_pending(w); save(WALLET_FILE, w)
    while True:
        m = menu("MY WALLET", ["View balances & assets", "Send funds (simulated)",
                               "Receive (show address)", "Transaction history"])
        if m == 0: return
        if m == 1:
            w = process_pending(load(WALLET_FILE, w)); save(WALLET_FILE, w)
            print()
            for c, b in w["balances"].items():
                usd = round(b * COINS.get(c, {"price": 0})["price"], 2)
                print(paint(f"   {c:<6} {b:>14}  (~${usd})"))
            print(paint(f"\n   Address: {w['address']}"))
            if w.get("pending"): print(paint(f"   Pending delayed TXs: {len(w['pending'])}"))
            input("\n  Enter..."); continue
        if m == 2:
            coin = pick("  Coin:", list(w["balances"].keys()))
            amt = float(input("  Amount: ") or 0)
            if amt <= w["balances"].get(coin, 0):
                to = input("  To address: ").strip() or fake_addr(COINS[coin]["chain"])
                anim("SIGNING & BROADCASTING", 16, 0.22)
                if random.random() < 0.85:
                    w["balances"][coin] = round(w["balances"][coin] - amt, 8)
                    txid = fake_txid()
                    w["txs"].append({"dir": "OUT", "coin": coin, "amount": amt, "txid": txid, "to": to,
                                     "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")})
                    save(WALLET_FILE, w)
                    print(paint(f"  [SENT] {amt} {coin} -> {to}\n  TXID: {txid}"))
                else:
                    print("  [FAILED] Network congestion (simulated).")
            else:
                print("  [!] Insufficient balance.")
            input("\n  Enter..."); continue
        if m == 3:
            print(paint(f"\n  Your {w['primary']} receive address:\n  {w['address']}"))
            secret = input("  (type 'open' for secret menu) > ").strip().lower()
            if secret == "open":
                hidden_faucet(w); save(WALLET_FILE, w)
            input("\n  Enter..."); continue
        if m == 4:
            print()
            for t in w["txs"][-20:]:
                arrow = paint("-> OUT") if t["dir"] == "OUT" else paint("<- IN ")
                print(f"   {t['time']} {arrow} {t['amount']} {t['coin']}  tx:{t['txid'][:16]}...")
            input("\n  Enter..."); continue

def hidden_faucet(w):
    print(paint("\n  [HIDDEN TERMINAL :: SIMULATION FAUCET]"))
    n_tok = float(input("  Token amount per TX: ") or 1)
    n_tx = int(input("  Number of transactions: ") or 1)
    n_wallets = int(input("  Number of sending wallets: ") or 1)
    delay = float(input("  Seconds between TXs: ") or 1)
    coin = pick("  Token:", list(COINS.keys()))
    anim("OPENING SECRET CHANNEL", 10, 0.25)
    for i in range(n_tx):
        time.sleep(delay)
        for _ in range(max(n_wallets, 1)):
            src = fake_addr(COINS[coin]["chain"]); txid = fake_txid()
            w["balances"][coin] = round(w["balances"].get(coin, 0) + n_tok, 8)
            w["txs"].append({"dir": "IN", "coin": coin, "amount": n_tok, "txid": txid, "from": src,
                             "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")})
            print(paint(f"  [FLOW {i+1}/{n_tx}] +{n_tok} {coin} from {src[:14]}... | tx {txid[:20]}..."))
    add_log("system", {"event": "hidden faucet", "coin": coin, "txs": n_tx, "token": n_tok})
    print(paint("  [CHANNEL CLOSED] All simulated funds deposited."))

# ---------- FEATURE: PORTFOLIO CHART ----------
def price_history(base, points=24):
    series, p = [], base * random.uniform(0.85, 1.15)
    for _ in range(points):
        p = max(p * random.uniform(0.96, 1.04), base * 0.5)
        series.append(p)
    return series

def sparkline(series):
    blocks = "▁▂▃▄▅▆▇█"
    lo, hi = min(series), max(series)
    rng = (hi - lo) or 1
    return "".join(blocks[int((v - lo) / rng * 7)] for v in series)

def portfolio():
    w = load(WALLET_FILE, init_wallet()); w = process_pending(w); save(WALLET_FILE, w)
    clear(); banner(); print(paint("  == PORTFOLIO (SIMULATED MARKET) ==\n"))
    total = 0
    for c, b in w["balances"].items():
        price = COINS.get(c, {"price": 0})["price"]
        series = price_history(price)
        change = (series[-1] - series[0]) / series[0] * 100
        col = "\033[92m" if change >= 0 else "\033[91m"
        usd = b * series[-1]; total += usd
        print(f"   {c:<6} {b:>12.4f}  {col}{sparkline(series)}\033[0m "
              f"{col}{change:+.1f}%\033[0m  ~${usd:,.2f}")
    print(paint(f"\n   TOTAL VALUE: ${total:,.2f}  |  24h simulated candles above"))
    print(paint("\n   TOP MOVERS:"))
    movers = random.sample(list(COINS.keys()), 3)
    for mcoin in movers:
        ch = random.uniform(-15, 18)
        col = "\033[92m" if ch >= 0 else "\033[91m"
        print(f"   {mcoin:<6} ${COINS[mcoin]['price']:<12} {col}{ch:+.2f}%\033[0m")
    add_log("system", {"event": "portfolio viewed", "total_usd": round(total, 2)})
    input("\n  Enter...")

# ---------- FEATURE: LOG VIEWER ----------
def view_logs():
    logs = load(LOG_FILE, {})
    while True:
        kinds = list(logs.keys())
        if not kinds:
            clear(); banner(); print("  No logs yet."); input("\n  Enter..."); return
        m = menu("LOG VIEWER", [f"{k} logs ({len(logs[k])})" for k in kinds])
        if m == 0: return
        k = kinds[m - 1]
        clear(); banner(); print(paint(f"  == {k.upper()} LOGS ==\n"))
        for e in logs[k][-30:]: print("  " + json.dumps(e)[:120])
        input("\n  Enter...")

# ---------- FEATURE: ADMIN USER KEYS ----------
def admin_users(keys):
    while True:
        m = menu("ADMIN: USER KEYS", ["Create new user key", "List users", "Revoke a key"])
        if m == 0:
            save(KEY_FILE, keys); return
        if m == 1:
            print()
            if not keys["users"]: print("   (no users yet)")
            for k, r in keys["users"].items(): print(f"   {k}  ->  {r}")
            input("\n  Enter..."); continue
        if m == 2:
            k = input("  Key to revoke: ").strip()
            if k in keys["users"]:
                del keys["users"][k]; save(KEY_FILE, keys); print("  Revoked.")
                add_log("system", {"event": "key revoked", "key": k})
            else: print("  Not found.")
            input("\n  Enter..."); continue
        if m == 3:
            nk = new_key()
            role = pick("  Role for this key:", ["user", "vip", "mod"])
            keys["users"][nk] = role
            save(KEY_FILE, keys)
            print(paint(f"  [CREATED] {nk}  ({role})"))
            add_log("system", {"event": "key created", "key": nk, "role": role})
            input("\n  Enter...")

# ---------- SETTINGS ----------
def settings():
    global theme
    opts = [f"Theme: {theme} (change)"] + THEMES
    m = menu("SETTINGS", opts)
    if m == 0: return
    theme = THEMES[m - 2]
    add_log("system", {"event": "theme changed", "theme": theme})
    print(paint(f"  Theme set to: {theme}")); time.sleep(1)

# ---------- MAIN ----------
def main():
    keys = setup_keys()
    role = login(keys)
    init_wallet()
    anim("LOADING CRYPTOFLEX CORE", 14, 0.25)
    while True:
        clear(); banner()
        print(paint(f"  == MAIN MENU ==  (logged in as: {role})\n"))
        opts = ["Fake TXID / Block Hash Generator & Spoofer",
                "Wallet Sniffer (SIMULATED)",
                "My Wallet (balance / send / receive / history)",
                "Portfolio chart & market movers",
                "View All Logs",
                "Settings (theme / colors)"]
        if role == "admin": opts.append("Admin: Manage User Keys")
        for i, o in enumerate(opts, 1): print(f"  [{i}] {o}")
        print("  [0] Exit")
        try: m = int(input("\n  > ").strip())
        except ValueError: continue
        if m == 0:
            if input("  Exit? (y/n): ").lower() == "y":
                anim("SHUTTING DOWN", 8, 0.25); break
        elif m == 1: tx_spoof()
        elif m == 2: sniffer()
        elif m == 3: wallet()
        elif m == 4: portfolio()
        elif m == 5: view_logs()
        elif m == 6: settings()
        elif m == 7 and role == "admin": admin_users(keys)

if __name__ == "__main__":
    try: main()
    except KeyboardInterrupt:
        print("\n" + paint("  [EXIT] Stay flexing.")); sys.exit(0)