import sys
import signal
from getpass import getpass

from expyry.config import load_config, save_config
from expyry.services.ssl import add_ssl, check_ssl
from expyry.services.custom import add_custom
from expyry.check import check
from expyry.notify import enable_shell_notification, disable_shell_notification
from expyry.services.github import add_github, check_github_pat
from expyry.utils import parse_date

def handle_sigint(sig, frame):
    print("\n\nSession Expyrd o7\n")
    sys.exit(0)

signal.signal(signal.SIGINT, handle_sigint)

def main():

    args = sys.argv[1:]

    if "--version" in args or "-v" in args:
        print("expyry 0.1.0")
        return

    if not args:
        print("\nUsage:")
        print("  expyry add                 — add a credential expiry")
        print("  expyry list                — check all expiry dates")
        print("  expyry notify enable       — enable shell notifications")
        print("  expyry notify disable      — disable shell notifications")
        print("  expyry remove <name>       — remove a credential expiry")
        print("  expyry update <name>       — update a credential expiry")
        print("  expyry --version           — show version information")
        return

    command = args[0]

    if command == "add":
        if len(args) < 2:
            add()
        else:
            service = args[1]
            if service == "github":
                add_github()
            elif service == "ssl":
                add_ssl()
            elif service == "custom":
                add_custom()
            else:
                print(f"\n❌  Unknown service '{service}'.")
                print("    Use: github, ssl or custom\n")

    elif command == "list":
        quiet = "--quiet" in args
        check(quiet=quiet)

    elif command == "notify":
        if len(args) < 2:
            print("\n❌  Usage:")
            print("    expyry notify enable    — enable shell notifications")
            print("    expyry notify disable   — disable shell notifications\n")
        elif args[1] == "enable":
            enable_shell_notification()
        elif args[1] == "disable":
            disable_shell_notification()
        else:
            print(f"\n❌  Unknown option '{args[1]}'")
            print("    Use: enable or disable\n")

    elif command == "remove":
        if len(args) < 2:
            print("\n❌  Please provide a name. Use: expyry remove <name>\n")
        else:
            name = " ".join(args[1:])
            remove(name)

    elif command == "update":
        if len(args) < 2:
            print("\n❌  Please provide a name. Use: expyry update <name>\n")
        else:
            name = " ".join(args[1:])
            update(name)

    else:
        print(f"\n❌  Unknown command: '{command}'")
        print("    Run 'expyry' to see available commands.\n")

def add():
    print("\n➕  What would you like to track?\n")
    print("  github    — GitHub PAT")
    print("  ssl       — SSL Certificate")
    print("  custom    — Custom credential\n")

    choice = input("Type your choice: ").strip().lower()

    if choice == "github":
        add_github()
    elif choice == "ssl":
        add_ssl()
    elif choice == "custom":
        add_custom()
    else:
        print(f"\n❌  '{choice}' not recognised. Type github, ssl or custom.\n")
        add()

def update(service_name: str):
    config = load_config()
    services = config.get("services", [])

    if not services:
        print("\n⚠️   No credentials tracked yet.\n")
        return

    match = next((s for s in services if s["name"] == service_name), None)

    if not match:
        print(f"\n❌  '{service_name}' not found. Check the name and try again.\n")
        return

    print(f"\n🔄  Updating '{service_name}' ({match['type']})\n")

    if match["type"] == "ssl":
        domain = match.get("domain")
        if not domain:
            domain = input("Domain to check: ").strip()
        print(f"⏳  Rechecking {domain}...")
        result = check_ssl(domain)
        if not result["success"]:
            print(f"\n❌  {result['error']}\n")
            return
        match["expires"] = result["expires"]
        print(f"✅  Updated — expires {result['expires']}")

    elif match["type"] == "github":
        token = getpass("Paste updated GitHub PAT (or press enter for manual date): ").strip()
        if token:
            result = check_github_pat(token)
            if not result["success"]:
                print(f"\n❌  {result['error']}\n")
                return
            match["expires"] = result["expires"]
            print(f"✅  Updated — expires {result['expires']}")
        else:
            date_input = input("New expiry date: ").strip()
            expires, error = parse_date(date_input)
            if not expires:
                print(f"\n❌  {error}\n")
                return
            match["expires"] = expires
            print(f"✅  Updated — expires {expires}")
    
    else:
        date_input = input("New expiry date: ").strip()
        expires, error = parse_date(date_input)
        if not expires:
            print(f"\n❌  {error}\n")
            return
        match["expires"] = expires
        print(f"✅  Updated — expires {expires}")

    updated_services = []

    for s in services:
        if s["name"] != service_name:
            updated_services.append(s)
        else:
            updated_services.append(match)

    config["services"] = updated_services
    save_config(config)
    print(f"💾  Saved.\n")

def remove(service_name: str):
    config = load_config()
    services = config.get("services", [])

    if not services:
        print("\n⚠️   No credentials tracked yet.\n")
        return

    match = next((s for s in services if s["name"] == service_name), None)

    if not match:
        print(f"\n❌  '{service_name}' not found. Check the name and try again.\n")
        return

    confirm = input(f"\n⚠️   Remove '{service_name}'? [y/N]: ").strip().lower()

    if confirm != "y":
        print("\n⏭️   Cancelled.\n")
        return

    config["services"] = [s for s in services if s["name"]!=service_name]
    save_config(config)
    print(f"\n✅  '{service_name}' removed.\n")



if __name__ == "__main__":
    main()
