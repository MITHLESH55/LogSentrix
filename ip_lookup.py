try:
    import requests
except ImportError:
    requests = None

import os
import logging
from datetime import datetime

# Configure debug logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ThreatIntelligence")

_lookup_cache = {}


# --------------------------------
# Get IP Location Info
# --------------------------------
def get_ip_info(ip):

    if not ip:
        return {
            "country": "Unknown",
            "city": "-",
            "isp": "-",
            "lat": 0.0,
            "lon": 0.0
        }

    if ip in _lookup_cache:
        return _lookup_cache[ip]

    # Handle private/local IPs
    if ip.startswith("192.168") or ip.startswith("127.") or ip.startswith("10."):
        result = {
            "country": "Local",
            "city": "Network",
            "isp": "Private",
            "lat": 0.0,
            "lon": 0.0
        }
        _lookup_cache[ip] = result
        return result

    if requests is None:
        result = {
            "country": "Unknown",
            "city": "-",
            "isp": "-",
            "lat": 0.0,
            "lon": 0.0
        }
        _lookup_cache[ip] = result
        return result

    static_ip_map = {
        "45.12.34.56": {"country": "United Kingdom", "city": "London", "isp": "Hosting API", "lat": 51.509865, "lon": -0.118092},
        "103.25.44.90": {"country": "Indonesia", "city": "Jakarta", "isp": "PT Telkom", "lat": -6.200000, "lon": 106.816666},
        "66.249.66.1": {"country": "United States", "city": "New York", "isp": "Google LLC", "lat": 40.7128, "lon": -74.0060},
        "95.161.229.130": {"country": "Russia", "city": "Moscow", "isp": "ER-Telecom", "lat": 55.7558, "lon": 37.6173},
        "123.125.114.144": {"country": "China", "city": "Beijing", "isp": "Baidu", "lat": 39.9042, "lon": 116.4074},
        "106.51.78.20": {"country": "India", "city": "Bangalore", "isp": "Reliance Jio", "lat": 12.9716, "lon": 77.5946},
        "176.9.0.1": {"country": "Germany", "city": "Berlin", "isp": "Hetzner Online", "lat": 52.5200, "lon": 13.4050}
    }

    if ip in static_ip_map:
        result = static_ip_map[ip]
        _lookup_cache[ip] = result
        return result

    try:
        url = f"http://ip-api.com/json/{ip}"
        response = requests.get(url, timeout=1)
        data = response.json()

        if data.get("status") == "success":
            result = {
                "country": data.get("country", "Unknown"),
                "city": data.get("city", "-"),
                "isp": data.get("isp", "-"),
                "lat": data.get("lat", 0.0),
                "lon": data.get("lon", 0.0)
            }
        else:
            result = {
                "country": "Unknown",
                "city": "-",
                "isp": "-",
                "lat": 0.0,
                "lon": 0.0
            }
    except Exception as e:
        print("[IP LOOKUP ERROR]", e)
        result = {
            "country": "Unknown",
            "city": "-",
            "isp": "-",
            "lat": 0.0,
            "lon": 0.0
        }

    _lookup_cache[ip] = result
    return result


# --------------------------------
# Threat Intelligence
# --------------------------------

# Known malicious IPs for fallback classification
KNOWN_MALICIOUS_IPS = [
    "103.25.44.90",
    "45.12.34.56",
    "66.249.66.1",
    "95.161.229.130",
    "123.125.114.144",
    "106.51.78.20",
    "176.9.0.1",
    "192.0.2.1",        # Example: Documentation IP
    "198.51.100.0"      # Example: TEST-NET-2
]

# API configuration with secure environment variable
def get_abuse_api_key():
    """Retrieve AbuseIPDB API key from environment variable."""
    api_key = os.getenv("ABUSEIPDB_API_KEY")
    if not api_key:
        logger.warning("ABUSEIPDB_API_KEY environment variable not set. Fallback classification only.")
    return api_key


def _is_local_ip(ip):
    """Check if IP is a local/private IP address."""
    local_prefixes = ("192.168.", "127.", "10.", "172.16.", "172.31.")
    return any(ip.startswith(prefix) for prefix in local_prefixes)


def _classify_from_fallback(ip):
    """
    Fallback classification when API is unavailable.
    Returns threat classification based on known malicious IP list.
    """
    logger.debug(f"Using fallback classification for IP: {ip}")
    
    if ip in KNOWN_MALICIOUS_IPS:
        logger.debug(f"IP {ip} found in known malicious list")
        return "Malicious"
    
    # Default to Low Risk if not in malicious list
    return "Low Risk"


def _classify_from_abuse_score(abuse_score):
    """
    Classify IP threat level based on AbuseIPDB confidence score.
    
    Classification thresholds:
    - Malicious: score > 75
    - Suspicious: score > 30
    - Low Risk: score <= 30
    """
    if abuse_score > 75:
        return "Malicious"
    elif abuse_score > 30:
        return "Suspicious"
    else:
        return "Low Risk"


def check_ip_reputation(ip):
    """
    Check IP reputation using AbuseIPDB API with fallback logic.
    
    Args:
        ip (str): IP address to check
        
    Returns:
        str: One of ["Malicious", "Suspicious", "Low Risk"]
    
    Note:
        - Local/private IPs are NOT checked against API (returns Low Risk)
        - API failures trigger fallback to known malicious IP list
        - All classifications return only the three defined categories
    """
    logger.debug(f"Checking reputation for IP: {ip}")
    
    # Validate input
    if not ip:
        logger.warning("Empty IP address provided")
        return "Low Risk"
    
    # Local/private IP - always Low Risk (don't call API)
    if _is_local_ip(ip):
        logger.debug(f"IP {ip} is local/private - returning Low Risk")
        return "Low Risk"
    
    # Check known malicious list first (faster than API)
    if ip in KNOWN_MALICIOUS_IPS:
        logger.info(f"IP {ip} found in known malicious list - Malicious")
        return "Malicious"
    
    # Try API call if key is available
    api_key = get_abuse_api_key()
    if not api_key:
        logger.warning(f"No API key available, using fallback for IP: {ip}")
        return _classify_from_fallback(ip)
    
    if requests is None:
        logger.warning("requests library not available, using fallback classification")
        return _classify_from_fallback(ip)
    
    try:
        url = "https://api.abuseipdb.com/api/v2/check"
        
        headers = {
            "Key": api_key,
            "Accept": "application/json"
        }
        
        params = {
            "ipAddress": ip,
            "maxAgeInDays": 90
        }
        
        logger.debug(f"Making API request to AbuseIPDB for IP: {ip}")
        response = requests.get(url, headers=headers, params=params, timeout=5)
        response.raise_for_status()  # Raise exception for HTTP errors
        
        data = response.json()
        logger.debug(f"API Response for {ip}: HTTP {response.status_code} - {data}")
        
        # Check for API response validity
        if "data" not in data:
            logger.warning(f"Invalid API response for {ip}: missing 'data' key")
            return _classify_from_fallback(ip)
        
        # Extract abuse confidence score
        abuse_score = data["data"].get("abuseConfidenceScore", 0)
        classification = _classify_from_abuse_score(abuse_score)
        
        logger.info(f"IP {ip} classified as {classification} (score: {abuse_score})")
        return classification
        
    except requests.exceptions.Timeout:
        logger.error(f"API request timeout for IP {ip} (5 second threshold)")
        return _classify_from_fallback(ip)
        
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Connection error contacting AbuseIPDB for IP {ip}: {e}")
        return _classify_from_fallback(ip)
        
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error from AbuseIPDB for IP {ip}: {e}")
        return _classify_from_fallback(ip)
        
    except ValueError as e:
        logger.error(f"JSON decode error in API response for IP {ip}: {e}")
        return _classify_from_fallback(ip)
        
    except Exception as e:
        logger.error(f"Unexpected error checking reputation for IP {ip}: {type(e).__name__}: {e}")
        return _classify_from_fallback(ip)