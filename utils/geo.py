import tldextract
import requests

def detect_geolocation(url):
    if not url:
        return "unknown"

    domain = tldextract.extract(url).registered_domain
    try:
        res = requests.get(f"https://ipapi.co/{domain}/json")
        if res.ok:
            data = res.json()
            return data.get("country_name", "unknown")
    except:
        return "unknown"
