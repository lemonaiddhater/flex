#!/usr/bin/env python3
# ================= CRYPTOFLEX v4.0 :: SIMULATED FLEX ENGINE =================
import os, sys, json, time, random, string, datetime, shutil

DATA_DIR = os.path.expanduser("~/cryptoflex")
os.makedirs(DATA_DIR, exist_ok=True)
KEY_FILE, WALLET_FILE, LOG_FILE = (os.path.join(DATA_DIR, f) for f in ("keys.json", "wallet.json", "logs.json"))

# ================= THEMES =================
THEMES = ["green", "cyan", "red", "purple", "yellow", "blue", "rainbow", "ice"]
theme = "green"
COLS = {"green": "\033[92m", "cyan": "\033[96m", "red": "\033[91m",
        "purple": "\033[95m", "yellow": "\033[93m", "blue": "\033[94m",
        "ice": "\033[36m"}
RAINBOW = ["\033[91m", "\033[93m", "\033[92m", "\033[96m", "\033[94m", "\033[95m"]
DIM, BOLD, RESET = "\033[2m", "\033[1m", "\033[0m"
OK, WARN, BAD = "\033[92m", "\033[93m", "\033[91m"

def paint(s):
    if theme == "rainbow":
        return "".join(RAINBOW[i % len(RAINBOW)] + ch + RESET for i, ch in enumerate(s))
    return COLS[theme] + s + RESET

def gradient(s):
    """Vertical gradient through rainbow for big text."""
    out = []
    for i, line in enumerate(s.split("\n")):
        c = COLS.get(theme) if theme != "rainbow" else RAINBOW[i % len(RAINBOW)]
        if theme == "rainbow": c = RAINBOW[i % len(RAINBOW)]
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
    """HUD header: wallet total + top token replace the old tagline."""
    w = load(WALLET_FILE, None)
    total, top_name, top_amt = 0.0, "-", 0.0
    if w:
        for c, b in w["balances"].items():
            usd = b * COINS.get(c, {"price": 0})["price"]
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

# ================= FANCY ANIMATIONS =================
def bar_frame(pct, width=34):
    fill = int(pct / 100 * width)
    solid = "━" * fill
    light = "╺" * max(width - fill, 0)
    return f"[{paint(solid)}{DIM}{light}{RESET}] {pct:3d}%"

def anim(title, frames=18, delay=0.4, sub=None):
    """Gradient progress bar with spinner + optional sub-status line."""
    spin = ["◐", "◓", "◑", "◒", "◓", "◒"]
    subs = sub or ["negotiating peers", "verifying signatures", "querying mempool",
                   "syncing headers", "finalizing"]
    for i in range(frames):
        pct = int((i + 1) / frames * 100)
        s = subs[i % len(subs)]
        sys.stdout.write(f"\r  {paint(title)} {spin[i % len(spin)]} {bar_frame(pct)} {DIM}{s}{RESET}   ")
        sys.stdout.flush(); time.sleep(delay)
    sys.stdout.write("\r" + " " * 100 + "\r")
    print(f"  {OK}✔{RESET} {paint(title)}")

def node_scan(title="ESTABLISHING SECURE CHANNEL"):
    """Animated node discovery — IPs fly by with latency readings."""
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
    """Classic falling-hex rain."""
    line = [" "] * cols
    trail = {}
    for r in range(rows):
        for c in range(cols):
            if random.random() < 0.15: trail[c] = random.randint(0, 2)
        out = ""
        for c in range(cols):
            if c in trail:
                out += paint(random.choice("0123456789ABCDEF"))
                trail[c] -= 1
                if trail[c] < 0: del trail[c]
            else:
                out += " "
        print("   " + out)
        time.sleep(delay)

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

# ================= KEY SYSTEM =================
def setup_keys():
    if not os.path.exists(KEY_FILE):
        key = new_key()
        save(KEY_FILE, {"owner_key": key, "users": {}})
        clear(); matrix_rain(rows=6, delay=0.3)
        print(f"\n  {paint(BOLD + '  [ FIRST RUN SETUP ]')}")
        time.sleep(2)
        type_line("  Generating your master access key...")
        anim("KEY GENERATION", 16, 0.5)
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
        anim("HANDSHAKE", 6, 0.45, sub=["tls exchange", "key derivation"])
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
            anim("LOCKING DOWN", 12, 0.5, sub=["wiping session", "sealing vault"])
            ans = input(paint("\n  Generate a NEW master key? Resets all user keys. (y/n): ")).strip().lower()
            if ans == "y":
                nk = new_key()
                save(KEY_FILE, {"owner_key": nk, "users": {}})
                add_log("system", {"event": "emergency key reset"})
                print(f"\n  {WARN}{BOLD}  [RECOVERY] NEW MASTER KEY: {nk}{RESET}")
                print(f"  {DIM}  All user keys wiped. Save this NOW!{RESET}")
                time.sleep(4)
                input(paint("  Key saved? (y/n): ")).strip().lower()
            else:
                print(paint("  No recovery. Closing..."))
            add_log("system", {"event": "lockout", "reason": "5 failed key attempts"})
            time.sleep(2); sys.exit(0)
    return None

# ================= WALLET =================
def wallet_total(w):
    return sum(b * COINS.get(c, {"price": 0})["price"] for c, b in w["balances"].items())

def init_wallet():
    w = load(WALLET_FILE, None)
    if w: return w
    coin = random.choice(list(COINS.keys()))
    w = {"address": fake_addr(COINS[coin]["chain"]), "primary": coin,
         "balances": {coin: 1.0}, "txs": [], "pending": [], "faucet": None}
    save(WALLET_FILE, w); return w

# ================= MENU =================
def menu(title, options, footer=True):
    clear(); header()
    print(paint(f"  ══ {title} ══\n"))
    for i, label in enumerate(options, 1):
        col = OK if i % 2 else paint("")
        print(f"  {paint('[')}{col}{i}{RESET}{paint(']')} {label}")
    if footer: print(f"  {paint('[')}{DIM}0{RESET}{paint(']')} Back")
    try: return int(input("\n  ➤ ").strip())
    except ValueError: return 0

def pick(prompt, choices):
    print(paint(prompt))
    for i, c in enumerate(choices, 1): print(f"   {paint('[')}{i}{paint(']')} {c}")
    try: return choices[int(input("  ➤ ").strip()) - 1]
    except Exception: return choices[0]

# ================= TOOLS: TXID GENERATOR =================
def txid_gen():
    clear(); header()
    print(paint("  ══ TXID / BLOCK HASH FORGE ══\n"))
    anim("FORGING HASHES", 14, 0.55, sub=["seeding entropy", "double-SHA passes", "hex-dressing"])
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
    coin = pick("Select network asset:", list(COINS.keys()))
    amt = float(input("  Amount: ") or 0)
    sender = input("  Sender (blank = random): ").strip() or fake_addr(COINS[coin]["chain"])
    recv = input("  Recipient: ").strip() or fake_addr(COINS[coin]["chain"])
    method = pick("Injection method:", ["mempool-inject", "double-spend", "flash-broadcast", "relay-flood"])
    print()
    type_line(f"  {amt} {coin} | {NETWORKS[coin]} | {method}", 0.04)
    anim("BROADCASTING", 22, 0.55, sub=["signing payload", "flooding relays", "awaiting first confirm"])
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

# ================= TOOLS: SNIFFER (no hints) =================
def sniffer():
    clear(); header()
    print(paint("  ══ NETWORK RECON SCANNER ══\n"))
    url = input("  Target endpoint: ").strip() or "unknown"
    addr = input("  Address: ").strip() or fake_addr("BTC")
    anim("DEEP SCANNING", 24, 0.6, sub=["probing endpoints", "indexing leaks", "correlating records"])
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
                d="".join(random.choices(string.ascii_lowercase, k=5)),
                n=random.randint(200, 999),
                p="".join(random.choices(string.ascii_letters + string.digits, k=10)),
                s=" ".join(random.choices(words, k=12)),
                c=str(random.randint(100000, 999999)),
                a=random.randint(1, 254),
                e=random.choice(["Binance", "Coinbase", "Kraken", "OKX"]),
                k=fake_txid()[:32])
            print(f"   {WARN}▸{RESET} {t}"); found.append(t); time.sleep(0.4)
        add_log("sniffer", {"url": url, "addr": addr, "findings": found, "result": "HIT"})
    else:
        print(f"\n  {BAD}[NO RECORDS] target clean{RESET}")
        add_log("sniffer", {"url": url, "addr": addr, "result": "MISS"})
    input("\n  Enter...")

# ================= TOOLS: MINING RIG (faster now) =================
def mining_rig():
    w = load(WALLET_FILE, init_wallet())
    clear(); header()
    print(paint("  ══ MINING RIG ══\n"))
    coin = pick("Coin to mine:", list(COINS.keys()))
    hashrate = random.uniform(80, 420)
    print(f"\n  {paint('RIG')} CFX-RIG-01 | {paint(coin)} | {OK}{hashrate:.1f} MH/s{RESET}")
    print(f"  {DIM}50 shares per payout. Ctrl+C to stop and keep earnings.{RESET}\n")
    shares, target, earned = 0, 50, 0.0
    try:
        while True:
            anim(f"HASHING SHARE {shares + 1}/{target}", 4, 0.12,
                 sub=["rolling nonces", "checking difficulty"])
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
                print(f"  {OK}{BOLD}◆ BLOCK MINED{RESET} +{payout} {coin}  ~${round(earned * COINS[coin]['price'], 4)} session")
                time.sleep(1.2)
    except KeyboardInterrupt:
        print(f"\n  {paint('RIG OFFLINE')} session earnings: {round(earned, 8)} {coin}")
        add_log("system", {"event": "mining session", "coin": coin, "earned": earned})
        input("\n  Enter...")

# ================= TOOLS HUB =================
def tools():
    while True:
        m = menu("TOOL VAULT", ["TXID / Block Hash Forge",
                                "Spoofed TX Broadcast",
                                "Network Recon Scanner",
                                "Mining Rig"])
        if m == 0: return
        [None, txid_gen, tx_spoof, sniffer, mining_rig][min(m, 4)]()

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
        m = menu("VAULT", ["Balances & Assets", "Send", "Receive", "Transaction History"])
        if m == 0: return
        if m == 1:
            w = process_pending(load(WALLET_FILE, w)); save(WALLET_FILE, w)
            print()
            for c, b in w["balances"].items():
                usd = round(b * COINS.get(c, {"price": 0})["price"], 2)
                print(f"   {paint(c):<18} {b:>14}  {DIM}~${usd}{RESET}")
            print(f"\n   {paint('Address')} {w['address']}")
            if w.get("pending"): print(f"   {WARN}⧗ pending incoming: {len(w['pending'])}{RESET}")
            input("\n  Enter..."); continue
        if m == 2:
            coin = pick("Asset:", list(w["balances"].keys()))
            amt = float(input("  Amount: ") or 0)
            if amt <= w["balances"].get(coin, 0):
                to = input("  To address: ").strip() or fake_addr(COINS[coin]["chain"])
                anim("SIGNING & BROADCASTING", 18, 0.6, sub=["ECDSA sign", "serializing", "relay flood"])
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
            # no hints — hidden trigger stays invisible
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
        per = float(input("  Token amount per TX: ") or 1)
        n_tx = int(input("  Number of transactions: ") or 1)
        n_w = int(input("  Number of sending wallets: ") or 1)
        delay = float(input("  Seconds between TXs: ") or 3)
        coin = pick("Token:", list(COINS.keys()))
    except Exception:
        return
    w["faucet"] = {"coin": coin, "per": per, "remaining": n_tx, "wallets": max(n_w, 1),
                   "delay": max(delay, 1.0), "next": time.time() + delay}
    add_log("system", {"event": "channel armed", "coin": coin, "txs": n_tx, "per": per})
    anim("ARMING CHANNEL", 8, 0.5, sub=["opening sockets", "handshakes", "queueing flows"])
    print(f"  {OK}◆ Channel armed — {n_tx} flows queued. Returning to main menu...{RESET}")
    time.sleep(2)

def run_faucet(w):
    """Non-blocking: fires one flow when due. Called from the main loop."""
    f = w.get("faucet")
    if not f or f["remaining"] <= 0: return w
    if time.time() < f["next"]: return w
    for _ in range(f["wallets"]):
        src, txid = fake_addr(COINS[f["coin"]]["chain"]), fake_txid()
        w["balances"][f["coin"]] = round(w["balances"].get(f["coin"], 0) + f["per"], 8)
        w["txs"].append({"dir": "IN", "coin": f["coin"], "amount": f["per"], "txid": txid,
                         "from": src, "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")})
        print(f"  {OK}◆ INCOMING{RESET} +{f['per']} {f['coin']} from {src[:14]}... {DIM}tx {txid[:20]}...{RESET}")
    f["remaining"] -= 1
    f["next"] = time.time() + f["delay"]
    if f["remaining"] <= 0:
        w["faucet"] = None
        print(f"  {OK}◆ Channel complete — all flows deposited.{RESET}")
    save(WALLET_FILE, w)
    return w

# ================= PORTFOLIO =================
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
    clear(); header()
    print(paint("  ══ PORTFOLIO ══\n"))
    total = 0
    for c, b in w["balances"].items():
        price = COINS.get(c, {"price": 0})["price"]
        series = price_history(price)
        change = (series[-1] - series[0]) / series[0] * 100
        col = OK if change >= 0 else BAD
        usd = b * series[-1]; total += usd
        print(f"   {paint(c):<20} {b:>12.4f}  {col}{sparkline(series)} {change:+.1f}%{RESET}  ~${usd:,.2f}")
    print(f"\n   {paint(BOLD + 'TOTAL')}: ${total:,.2f}")
    print(f"\n  {paint('TOP MOVERS')}")
    for mc in random.sample(list(COINS.keys()), 3):
        ch = random.uniform(-15, 18)
        col = OK if ch >= 0 else BAD
        print(f"   {paint(mc):<20} ${COINS[mc]['price']:<12} {col}{ch:+.2f}%{RESET}")
    add_log("system", {"event": "portfolio viewed", "total_usd": round(total, 2)})
    input("\n  Enter...")

# ================= WHALE LEADERBOARD (new) =================
def whales():
    clear(); header()
    print(paint("  ══ WHALE LEADERBOARD ══\n"))
    anim("SNIPING WHALE WALLETS", 14, 0.55, sub=["tracking clusters", "scoring holdings"])
    rows = sorted([(fake_addr(random.choice(list(COINS.keys()))), random.uniform(1, 9000)) for _ in range(8)],
                  key=lambda x: -x[1])
    for i, (a, v) in enumerate(rows, 1):
        medal = ["🥇", "🥈", "🥉"][i - 1] if i <= 3 else f"{i}."
        print(f"   {medal} {a[:22]}...  {paint(f'${v:,.0f}')}")
    me = load(WALLET_FILE, init_wallet())
    print(f"\n   {paint('YOU')}: rank #{random.randint(9, 9999)} with ${wallet_total(me):,.2f}")
    input("\n  Enter...")

# ================= PRICE ALERTS (new) =================
def alerts():
    clear(); header()
    print(paint("  ══ PRICE ALERT ENGINE ══\n"))
    coin = pick("Asset to monitor:", list(COINS.keys()))
    anim("LINKING MARKET FEEDS", 12, 0.55, sub=["websocket up", "subscribing book"])
    for i in range(6):
        p = COINS[coin]["price"] * random.uniform(0.97, 1.03)
        col = OK if random.random() > 0.5 else BAD
        print(f"   tick {i + 1}: {coin} {col}${p:,.2f}{RESET}")
        time.sleep(1.4)
    hit = random.random() < 0.5
    if hit:
        print(f"\n  {WARN}{BOLD}🔔 ALERT TRIGGERED — {coin} moved 8.4% in 5m!{RESET}")
        add_log("system", {"event": "price alert", "coin": coin, "triggered": True})
    else:
        print(f"\n  {DIM}no triggers — market quiet{RESET}")
        add_log("system", {"event": "price alert", "coin": coin, "triggered": False})
    input("\n  Enter...")

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
        for e in logs[k][-30:]: print(f"   {DIM}{e['time']}{RESET} " + json.dumps({x: y for x, y in e.items() if x != 'time'})[:110])
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
            anim("MINTING KEY", 10, 0.5, sub=["deriving", "registering"])
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
    opts = ["Cycle to next theme"] + [f"Use {t} theme" for t in THEMES if t != theme]
    m = menu("SETTINGS", opts)
    if m == 0: return
    global THEMES_ORDER
    theme = THEMES[(THEMES.index(theme) + 1) % len(THEMES)] if m == 1 else \
        [t for t in THEMES if t != theme][m - 2]
    add_log("system", {"event": "theme changed", "theme": theme})
    print(paint(f"  Theme → {theme}")); time.sleep(1.5)

# ================= MAIN =================
def main():
    clear()
    matrix_rain(rows=10, delay=0.3)
    keys = setup_keys()
    role = login(keys)
    w = init_wallet()
    anim("BOOTING CRYPTOFLEX CORE", 20, 0.6, sub=["loading modules", "mounting vault", "calibrating rig"])
    node_scan(); matrix_rain(rows=5, delay=0.25)
    while True:
        w = load(WALLET_FILE, w)
        w = run_faucet(w)
        w = process_pending(w)
        save(WALLET_FILE, w)
        clear(); header()
        print(paint(f"  ══ MAIN MENU ══  {DIM}role: {role}{RESET}\n"))
        opts = ["TOOLS + ",
                "WALLET — wallet & transactions",
                "PORTFOLIO — charts & movers",
                "WHALE LEADERBOARD",
                "PRICE ALERT ENGINE",
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
                anim("SHUTTING DOWN", 10, 0.5, sub=["closing sockets", "flushing vault"])
                break
        elif m == 1: tools()
        elif m == 2: wallet()
        elif m == 3: portfolio()
        elif m == 4: whales()
        elif m == 5: alerts()
        elif m == 6: view_logs()
        elif m == 7: settings()
        elif m == 8 and role == "admin": admin_users(keys)

if __name__ == "__main__":
    try: main()
    except KeyboardInterrupt:
        print("\n" + paint("  [EXIT] Stay flexing.")); sys.exit(0)