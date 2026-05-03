#!/usr/bin/env python3
"""
Test script for the enhanced threat intelligence system.
Tests the check_ip_reputation() function with various scenarios.
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from ip_lookup import check_ip_reputation, _is_local_ip, KNOWN_MALICIOUS_IPS


def test_local_ips():
    """Test that local IPs return 'Low Risk' without API calls."""
    print("\n" + "="*60)
    print("TEST 1: Local/Private IPs")
    print("="*60)
    
    local_ips = [
        "192.168.1.1",
        "127.0.0.1",
        "10.0.0.1",
        "172.16.0.1",
        "172.31.255.255"
    ]
    
    for ip in local_ips:
        result = check_ip_reputation(ip)
        status = "✓ PASS" if result == "Low Risk" else "✗ FAIL"
        print(f"  {status}: {ip} -> {result}")


def test_known_malicious():
    """Test that known malicious IPs are correctly classified."""
    print("\n" + "="*60)
    print("TEST 2: Known Malicious IPs")
    print("="*60)
    
    for ip in KNOWN_MALICIOUS_IPS:
        result = check_ip_reputation(ip)
        status = "✓ PASS" if result == "Malicious" else "✗ FAIL"
        print(f"  {status}: {ip} -> {result}")


def test_valid_classification_types():
    """Test that all returns are one of the three valid types."""
    print("\n" + "="*60)
    print("TEST 3: Valid Classification Types")
    print("="*60)
    
    test_ips = [
        "8.8.8.8",           # Google DNS - likely Low Risk
        "203.0.113.1",       # TEST-NET-3 (may vary)
        "198.51.100.1",      # TEST-NET-2 (in known list)
        "192.0.2.1",         # TEST-NET-1 (in known list)
    ]
    
    valid_classifications = ["Malicious", "Suspicious", "Low Risk"]
    
    for ip in test_ips:
        result = check_ip_reputation(ip)
        is_valid = result in valid_classifications
        status = "✓ PASS" if is_valid else "✗ FAIL"
        print(f"  {status}: {ip} -> {result} (valid: {is_valid})")


def test_is_local_ip():
    """Test the _is_local_ip helper function."""
    print("\n" + "="*60)
    print("TEST 4: Local IP Detection Function")
    print("="*60)
    
    test_cases = [
        ("192.168.1.1", True),
        ("127.0.0.1", True),
        ("10.0.0.1", True),
        ("172.16.0.1", True),
        ("172.31.255.255", True),
        ("8.8.8.8", False),
        ("203.0.113.1", False),
    ]
    
    for ip, expected in test_cases:
        result = _is_local_ip(ip)
        status = "✓ PASS" if result == expected else "✗ FAIL"
        print(f"  {status}: _is_local_ip('{ip}') -> {result} (expected: {expected})")


def test_api_key_configuration():
    """Test API key configuration."""
    print("\n" + "="*60)
    print("TEST 5: API Key Configuration")
    print("="*60)
    
    api_key = os.getenv("ABUSEIPDB_API_KEY")
    
    if api_key:
        masked_key = api_key[:8] + "*" * (len(api_key) - 16) + api_key[-8:]
        print(f"  ✓ PASS: API key is set: {masked_key}")
    else:
        print(f"  ⚠ WARNING: ABUSEIPDB_API_KEY not set")
        print(f"            System will use fallback classification only")


def test_empty_invalid_input():
    """Test handling of invalid inputs."""
    print("\n" + "="*60)
    print("TEST 6: Invalid Input Handling")
    print("="*60)
    
    test_cases = [
        ("", "Low Risk", "empty string"),
        (None, "Low Risk", "None value"),
    ]
    
    for ip, expected, description in test_cases:
        try:
            result = check_ip_reputation(ip)
            status = "✓ PASS" if result == expected else "✗ FAIL"
            print(f"  {status}: {description} -> {result} (expected: {expected})")
        except Exception as e:
            print(f"  ✗ FAIL: {description} raised {type(e).__name__}: {e}")


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("THREAT INTELLIGENCE SYSTEM - TEST SUITE")
    print("="*60)
    
    test_local_ips()
    test_known_malicious()
    test_api_key_configuration()
    test_is_local_ip()
    test_empty_invalid_input()
    test_valid_classification_types()
    
    print("\n" + "="*60)
    print("TEST SUITE COMPLETED")
    print("="*60)
    print("\nNote: Some tests may require API connectivity to fully validate.")
    print("Check the debug logs for detailed information about API calls.")


if __name__ == "__main__":
    main()
