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
            anim("LOCKING DOWN", 10, 0.3)
            # ---- EMERGENCY RECOVERY PROMPT ----
            ans = input(paint("\n  Generate a NEW master key? This resets all existing keys. (y/n): ")).strip().lower()
            if ans == "y":
                new = new_key()
                save(KEY_FILE, {"owner_key": new, "users": {}})
                add_log("system", {"event": "emergency key reset"})
                print(paint(f"\n  [RECOVERY] NEW MASTER ACCESS KEY: {new}"))
                print(paint("  All user keys were wiped. Save this key NOW!"))
                time.sleep(4)
                confirm = input(paint("  Key saved? (y/n): ")).strip().lower()
                if confirm == "y":
                    print(paint("  Restart the tool and log in with your new key.")); time.sleep(3)
                else:
                    print(paint("  Key is already saved to file. Restart to see it via recovery again.")); time.sleep(3)
            else:
                print(paint("  No recovery. Closing..."))
            add_log("system", {"event": "lockout", "reason": "5 failed key attempts"})
            print(paint("  Goodbye.")); time.sleep(2)
            sys.exit(0)
    return None
