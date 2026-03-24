from datetime import datetime, timezone
from expyry.config import load_config

def check(quiet=False):
    """Check all tracked credentials and show expiry status."""
    config = load_config()
    services = config.get("services", [])
 
    if not services:
        if not quiet:
            print("\n⚠️   No services tracked yet\n")
        return
 
    today = datetime.now(timezone.utc).date()

    alerts = []
    for service in services:
        expires_str = service.get("expires")
        if not expires_str:
            continue
        expires = datetime.strptime(expires_str, "%Y-%m-%d").date()
        days_left = (expires - today).days
        if days_left <= 7:
            alerts.append((service["name"], expires_str, days_left))

    if quiet:
        # only print if something needs attention
        if alerts:
            print("\n⚠️   Expyry Alert:")
            for name, expires_str, days_left in alerts:
                if days_left <= 0:
                    print(f"   ❌  {name} EXPIRED on {expires_str}")
                elif days_left <= 7:
                    print(f"   🔴  {name} expires in {days_left} days — renew now")
            print()
        # if nothing expiring, complete silence
        return

    # full output for normal check
    print("\n📋  Expyry — Credential Status\n")
    print(f"  {'NAME':<25} {'TYPE':<15} {'EXPIRES':<15}  {'STATUS'}")
    print(f"  {'-'*25} {'-'*15} {'-'*15} {'-'*20}")

    for service in services:
        name = service["name"]
        type = service["type"]
        if service.get("never_expires"):
            print(f"  {name:<25} {type:<15} {'never':<15} ✅  No expiry set")
            continue
        expires_str = service.get("expires")
        if not expires_str:
            print(f"  {name:<25} {type:<15} {'unknown':<15} ⚠️   No date recorded")
            continue
        expires = datetime.strptime(expires_str, "%Y-%m-%d").date()
        days_left = (expires - today).days
        if days_left < 0:
            status = "❌  EXPIRED"
        elif days_left <= 7:
            status = f"🔴  URGENT — {days_left} days left"
        elif days_left <= 30:
            status = f"🟡  Renew soon — {days_left} days left"
        else:
            status = f"✅  {days_left} days left"
        print(f"  {name:<25} {type:<15} {expires_str:<15} {status}")
    print()

