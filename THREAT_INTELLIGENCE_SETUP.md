# Threat Intelligence Enhancement Setup Guide

## Overview

The cybersecurity dashboard now features an enhanced threat intelligence system that classifies IPs into three categories:

- **Malicious** - High-confidence threats (confidence score > 75%)
- **Suspicious** - Medium-confidence threats (confidence score > 30%)
- **Low Risk** - Low-confidence threats (confidence score ≤ 30%)

## Configuration

### 1. Set Up Environment Variable

Create a `.env` file in the project root (or use existing `.env` if available):

```bash
# Copy the example file
cp .env.example .env

# Edit the .env file and add your AbuseIPDB API key
ABUSEIPDB_API_KEY=your_api_key_here
```

### 2. Get AbuseIPDB API Key

1. Visit https://www.abuseipdb.com/register
2. Create a free account
3. Go to Account > API
4. Generate an API key
5. Copy the key and add it to your `.env` file

### 3. Load Environment Variables

Make sure your application loads the `.env` file on startup. You can use the `python-dotenv` library:

```python
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Now access the API key
api_key = os.getenv("ABUSEIPDB_API_KEY")
```

## Features

### ✅ Three-Tier Classification

- Returns only: `Malicious`, `Suspicious`, or `Low Risk`
- No ambiguous classifications like "Multiple Sources" or "Local Network"

### ✅ Secure API Key Management

- API key stored in environment variable (not hardcoded)
- Gracefully handles missing API key (fallback mode)

### ✅ Fallback Logic

- If API is unavailable: Uses known malicious IP list
- If API times out: Returns fallback classification
- If API fails: Automatically retries with fallback

### ✅ Timeout Handling

- 5-second timeout for API requests (prevents hanging)
- Automatic timeout detection and fallback

### ✅ Debug Logging

- Detailed logging with timestamps and severity levels
- Track API responses and classification decisions
- Monitor fallback usage

## Usage

### Checking IP Reputation

```python
from ip_lookup import check_ip_reputation

# Check an IP address
reputation = check_ip_reputation("203.0.113.45")
print(reputation)  # Output: "Malicious", "Suspicious", or "Low Risk"
```

### Local/Private IPs

Local IPs (192.168.x.x, 127.x.x.x, 10.x.x.x, etc.) automatically return `"Low Risk"` without API calls.

### Known Malicious IPs

The system maintains a fallback list:

- 103.25.44.90
- 45.12.34.56
- 192.0.2.1
- 198.51.100.0

To add more, edit `KNOWN_MALICIOUS_IPS` in `ip_lookup.py`.

## Logging

Logs are output with the logger name `"ThreatIntelligence"`:

```
2026-04-22 14:30:45,123 - ThreatIntelligence - DEBUG - Checking reputation for IP: 203.0.113.45
2026-04-22 14:30:45,234 - ThreatIntelligence - DEBUG - Making API request to AbuseIPDB for IP: 203.0.113.45
2026-04-22 14:30:46,567 - ThreatIntelligence - INFO - IP 203.0.113.45 classified as Malicious (score: 92)
```

## API Thresholds

| Score Range | Classification |
| ----------- | -------------- |
| > 75        | Malicious      |
| 31-75       | Suspicious     |
| ≤ 30        | Low Risk       |

## Error Handling

The system handles multiple failure scenarios:

| Scenario                 | Behavior                          |
| ------------------------ | --------------------------------- |
| Missing API key          | Uses fallback classification      |
| API timeout (>5s)        | Returns fallback classification   |
| Connection error         | Logs error and returns fallback   |
| Invalid response         | Logs warning and returns fallback |
| requests library missing | Uses fallback only                |

## Integration with Flask Dashboard

The `get_threat_source()` function in `app.py` now:

1. Uses `check_ip_reputation()` for API-based classification
2. Escalates severity based on attack indicators
3. Combines reputation with attack type for final assessment

Example flow:

```
Alert triggered → Extract IP, severity, attempts
                → Get IP reputation (Malicious/Suspicious/Low Risk)
                → Compare with attack severity
                → Return escalated or reputation-based classification
```

## Performance Optimization

- **Local IPs**: Skip API calls entirely (immediate response)
- **Known malicious list**: Check before API call (faster for known threats)
- **Timeout**: Prevents slow API from blocking application
- **Fallback**: Ensures classification always available (no "Unknown" responses)

## Requirements

Ensure `python-dotenv` is installed:

```bash
pip install python-dotenv
```

The project requires:

- requests (for API calls)
- python-dotenv (for environment variable management)

## Testing

Test the configuration:

```bash
python -c "from ip_lookup import check_ip_reputation; print(check_ip_reputation('8.8.8.8'))"
```

You should see either `Malicious`, `Suspicious`, or `Low Risk` (with debug logs showing the API call).
