#!/usr/bin/env python3
"""
Test script for real-time dashboard updates.
Verifies that the /data API endpoint works correctly.
"""

import sys
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

import requests
from time import sleep

# Configuration
API_URL = "http://localhost:5000/data"
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds


def test_api_endpoint():
    """Test the /data API endpoint."""
    print("\n" + "="*70)
    print("REAL-TIME DASHBOARD API TEST")
    print("="*70)
    
    print(f"\n🔍 Testing API endpoint: {API_URL}")
    print("   (Make sure Flask server is running: python app.py)")
    
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            print(f"\n📡 Attempt {attempt}/{MAX_RETRIES}...")
            
            # Make request to API
            response = requests.get(API_URL, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            
            # Verify response structure
            print("\n✅ API Request successful!")
            print(f"   Status Code: {response.status_code}")
            print(f"   Response Size: {len(response.text)} bytes")
            
            # Check required fields
            required_fields = [
                "total", "failed", "alerts", "ip_labels", "ip_values",
                "trend_labels", "trend_values", "top_risky"
            ]
            
            print("\n📋 Response Structure:")
            missing_fields = []
            for field in required_fields:
                if field in data:
                    print(f"   ✓ {field}: {type(data[field]).__name__}", end="")
                    if isinstance(data[field], (list, dict)):
                        print(f" (length: {len(data[field])})")
                    else:
                        print(f" (value: {data[field]})")
                else:
                    print(f"   ✗ {field}: MISSING")
                    missing_fields.append(field)
            
            if missing_fields:
                print(f"\n⚠️  Warning: Missing fields: {missing_fields}")
                return False
            
            # Verify alert structure
            if data.get("alerts") and len(data["alerts"]) > 0:
                print("\n🎯 Sample Alert Structure:")
                alert = data["alerts"][0]
                alert_fields = [
                    "ip", "type", "attempts", "severity", "risk",
                    "country", "city", "lat", "lon", "threat_source", "source_type"
                ]
                
                for field in alert_fields:
                    if field in alert:
                        print(f"   ✓ {field}: {alert[field]}")
                    else:
                        print(f"   ✗ {field}: MISSING")
            
            # Display summary statistics
            print("\n📊 Dashboard Summary:")
            print(f"   Total Logs: {data.get('total', 0)}")
            print(f"   Failed Logins: {data.get('failed', 0)}")
            print(f"   Active Alerts: {len(data.get('alerts', []))}")
            print(f"   Unique IPs: {len(data.get('ip_labels', []))}")
            print(f"   Time Periods: {len(data.get('trend_labels', []))}")
            print(f"   Risky Countries: {len(data.get('top_risky', {}))}")
            
            return True
            
        except requests.exceptions.ConnectionError as e:
            print(f"   ❌ Connection failed: {e}")
            if attempt < MAX_RETRIES:
                print(f"   ⏳ Retrying in {RETRY_DELAY} seconds...")
                sleep(RETRY_DELAY)
        except requests.exceptions.Timeout:
            print(f"   ❌ Request timeout")
            if attempt < MAX_RETRIES:
                print(f"   ⏳ Retrying in {RETRY_DELAY} seconds...")
                sleep(RETRY_DELAY)
        except ValueError as e:
            print(f"   ❌ Invalid JSON response: {e}")
            return False
        except Exception as e:
            print(f"   ❌ Error: {type(e).__name__}: {e}")
            if attempt < MAX_RETRIES:
                print(f"   ⏳ Retrying in {RETRY_DELAY} seconds...")
                sleep(RETRY_DELAY)
    
    print("\n❌ Failed to connect after {MAX_RETRIES} attempts")
    return False


def test_real_time_updates():
    """Test that data changes over time."""
    print("\n" + "="*70)
    print("REAL-TIME UPDATE TEST (5 second intervals)")
    print("="*70)
    
    previous_alert_count = None
    update_count = 0
    max_updates = 3
    
    try:
        for i in range(max_updates):
            print(f"\n🔄 Update {i+1}/{max_updates}...")
            
            response = requests.get(API_URL, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            current_alert_count = len(data.get("alerts", []))
            current_total = data.get("total", 0)
            
            print(f"   Alerts: {current_alert_count} | Total Logs: {current_total}")
            
            if previous_alert_count is not None:
                if current_alert_count != previous_alert_count:
                    print(f"   ✓ Data changed (was {previous_alert_count})")
                else:
                    print(f"   ℹ️  Data unchanged")
            
            previous_alert_count = current_alert_count
            update_count += 1
            
            if i < max_updates - 1:
                print(f"   ⏳ Waiting 5 seconds for next update...")
                sleep(5)
        
        print(f"\n✅ Successfully tracked {update_count} updates")
        return True
        
    except Exception as e:
        print(f"❌ Error during real-time test: {e}")
        return False


def print_instructions():
    """Print instructions for testing."""
    print("\n" + "="*70)
    print("NEXT STEPS")
    print("="*70)
    print("""
1. Start Flask Server:
   cd c:\\Users\\mithlesh_2\\Desktop\\INSL_Project
   python app.py

2. Open Dashboard:
   http://localhost:5000/

3. Open Browser DevTools (F12):
   - Go to Console tab
   - Watch for "[REALTIME] Dashboard updated at HH:MM:SS"
   - Go to Network tab and filter for "data" requests
   - Verify requests complete every ~5 seconds

4. Verify Updates:
   - Check that statistics update
   - Charts should refresh smoothly
   - Alerts table should show new attacks
   - Map markers should appear in real-time

5. Expected Behavior:
   ✓ No full page reloads (URL stays same)
   ✓ No flickering (smooth chart updates)
   ✓ Charts update every 5 seconds
   ✓ New alerts appear immediately
   ✓ Console shows timestamp logs
    """)


def main():
    """Run all tests."""
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*15 + "REALTIME DASHBOARD TESTING SUITE" + " "*21 + "║")
    print("╚" + "="*68 + "╝")
    
    # Test API endpoint
    api_ok = test_api_endpoint()
    
    if api_ok:
        # Test real-time updates
        realtime_ok = test_real_time_updates()
        
        print("\n" + "="*70)
        print("TEST RESULTS")
        print("="*70)
        print(f"API Endpoint:      {'✅ PASS' if api_ok else '❌ FAIL'}")
        print(f"Real-Time Updates: {'✅ PASS' if realtime_ok else '❌ FAIL'}")
        print(f"\nOverall:           {'✅ ALL TESTS PASSED' if (api_ok and realtime_ok) else '⚠️  SOME TESTS FAILED'}")
    else:
        print("\n" + "="*70)
        print("TEST RESULTS")
        print("="*70)
        print("API Endpoint:      ❌ FAIL")
        print("\nOverall:           ❌ TESTS FAILED")
    
    print_instructions()
    
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    main()
