from expyry.config import CONFIG_PATH
from expyry.utils import parse_date, save_entry
from getpass import getpass
import requests
from datetime import datetime, timezone

def check_github_pat(token: str) -> dict:
    """
    Makes a single API call to GitHub using the PAT.
    Reads expiry from the response header.
    Token is NEVER saved anywhere after this function.
    """
    try:
        response = requests.get(
            "https://api.github.com/user",
            headers={
                "Authorization": f"token {token}",
                "Accept": "application/vnd.github+json"
            },
            timeout=10
        )
 
        # Token is invalid
        if response.status_code == 401:
            return {"success": False, "error": "Invalid token. Check and try again."}
 
        # Read expiry from header
        expiry_header = response.headers.get("github-authentication-token-expiration")
        username = response.json().get("login", "unknown")
 
        if expiry_header:
            # Header format: "2026-05-01 12:00:00 UTC"
            expiry_date = datetime.strptime(
                expiry_header, "%Y-%m-%d %H:%M:%S %Z"
            ).replace(tzinfo=timezone.utc)
            return {
                "success": True,
                "username": username,
                "expires": expiry_date.strftime("%Y-%m-%d"),
                "never_expires": False
            }
        else:
            # Token has no expiration set
            return {
                "success": True,
                "username": username,
                "expires": None,
                "never_expires": True
            }
 
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "No internet connection."}
    except requests.exceptions.Timeout:
        return {"success": False, "error": "Request timed out."}

def add_github():
    """Interactive wizard to add a GitHub PAT."""
    print("\n🔑  Adding GitHub PAT\n")
    name = input("Label for this token (e.g. 'GitHub Work PAT'): ").strip()
    print("Paste your GitHub PAT to auto-detect expiry (or press enter to set expiry manually): ")
    token = getpass("GitHub PAT (hidden, optional): ").strip()

    if token:
        # Auto detect from header
        print("\n⏳  Checking token with GitHub...")
        result = check_github_pat(token)

        if not result["success"]:
            print(f"\n❌  {result['error']}")
            return

        if result["never_expires"]:
            expires = None
            print(f"\n✅  Token valid for @{result['username']} — no expiration set.")
        else:
            expires = result["expires"]
            print(f"\n✅  Token valid for @{result['username']} — expires {expires}")

    else:
        # Manual entry
        print("\nEnter expiry date from GitHub's token settings page.")
        print("Accepted formats:")
        print("  YYYY-MM-DD")
        print("  DD/MM/YYYY")
        print("  Month Day Year")

        
        date_input = input("\nExpiry date: ").strip()
        expires, error = parse_date(date_input)
        if not expires:
            print(f"\n❌  {error}\n")
            return

        print(f"\n✅  Expiry set to {expires}")

    save_entry(name, "github", expires)
 
    print(f"💾  Saved to {CONFIG_PATH}. Token discarded — not stored anywhere.\n")

