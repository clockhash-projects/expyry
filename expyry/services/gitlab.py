import requests
from getpass import getpass
from expyry.utils import save_entry

def check_gitlab_pat(token: str, host: str = "https://gitlab.com") -> dict:
    """
    Makes a single API call to GitLab using the PAT.
    Reads expiry from the response.
    Token is NEVER saved anywhere after this function.
    """
    try:
        response = requests.get(
            f"{host}/api/v4/personal_access_tokens/self",
            headers={
                "PRIVATE-TOKEN": token
            },
            timeout=10
        )

        if response.status_code == 401:
            return {"success": False, "error": "Invalid token. Check and try again."}

        if response.status_code == 403:
            return {"success": False, "error": "Access forbidden. Check token permissions."}

        data = response.json()
        token_name = data.get("name", "unknown")
        expires_at = data.get("expires_at")

        if expires_at:
            return {
                "success": True,
                "token_name": token_name,
                "expires": expires_at,
                "never_expires": False
            }
        else:
            return {
                "success": True,
                "token_name": token_name,
                "expires": None,
                "never_expires": True
            }

    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "No internet connection."}
    except requests.exceptions.Timeout:
        return {"success": False, "error": "Request timed out."}
    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {str(e)}"}

def add_gitlab() -> None:

    print("\n🦊  Adding GitLab PAT\n")
    name = input("Label (e.g. 'GitLab Work PAT'): ").strip()

    print("\nIs this gitlab.com or a self hosted instance?")
    print("  gitlab.com   — hosted on gitlab.com")
    print("  self         — self hosted instance\n")

    choice = input("Type your choice: ").strip().lower()

    if choice == "self":
        host = input("Enter your GitLab host (e.g. https://gitlab.mycompany.com): ").strip()
        host = host.rstrip("/")
    elif choice == "gitlab.com":
        host = "https://gitlab.com"
    else:
        print(f"\n❌  '{choice}' not recognised. Type gitlab.com or self.\n")
        return

    token = getpass("\nPaste your GitLab PAT (hidden): ").strip()

    print(f"\n⏳  Checking token with GitLab...")
    result = check_gitlab_pat(token, host)

    if not result["success"]:
        print(f"\n❌  {result['error']}\n")
        return

    if result["never_expires"]:
        print(f"\n✅  Token valid for @{result['token_name']} — no expiration set.")
        save_entry(name, "gitlab", None)
    else:
        print(f"\n✅  Token valid for @{result['token_name']} — expires {result['expires']}")
        save_entry(name, "gitlab", result["expires"])