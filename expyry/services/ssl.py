import ssl
import socket
from datetime import datetime

from expyry.config import CONFIG_PATH
from expyry.utils import save_entry

def check_ssl(domain: str) -> dict:
    try:
        context = ssl.create_default_context()
        with socket.create_connection((domain, 443), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
                expiry_str = cert["notAfter"]
                # format: "May 15 12:00:00 2026 GMT"
                expiry = datetime.strptime(expiry_str, "%b %d %H:%M:%S %Y %Z")
                return {
                    "success": True,
                    "expires": expiry.strftime("%Y-%m-%d")
                }
    
    except socket.gaierror:
        return {"success": False, "error": f"Could not resolve domain '{domain}'. Check the spelling."}
    except socket.timeout:
        return {"success": False, "error": "Connection timed out."}
    except ssl.SSLError as e:
        return {"success": False, "error": f"SSL error: {str(e)}"}
    except ConnectionRefusedError:
        return {"success": False, "error": f"Connection refused on port 443. Is SSL enabled on this domain?"}
    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {str(e)}"}

def add_ssl() -> None:
    print("\n🔒  Adding SSL Certificate\n")
    name = input("Label (e.g. 'Production SSL'): ").strip()
    domain = input("Domain to check (e.g. yourapp.com): ").strip()

    if domain:
        domain = domain.replace("https://", "").replace("http://", "").strip("/")

        print(f"\n⏳  Checking SSL cert for {domain}...")
        result = check_ssl(domain)

        if not result["success"]:
            print(f"\n❌  {result['error']}")
            return

        print(f"\n✅  SSL cert valid — expires {result['expires']}")
        save_entry(name, "ssl", result["expires"], extra={"domain": domain})
    else:
        print("Invalid Domain!")
        return


