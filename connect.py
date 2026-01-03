"""
Test Vercel FCM API endpoints
Run this after:
1. Adding a test token to Firebase (manually or via add_test_token.py)
2. Fixing Vercel deployment protection
3. Deploying the new Vercel endpoints
"""

import requests
import json

print("=" * 70)
print("Vercel FCM API Test")
print("=" * 70)

BASE_URL = "https://lms-callback-git-main-astrallibertads-projects.vercel.app"

# Test 1: Get all tokens
print("\n[Test 1] GET /api/fcm/tokens")
print("=" * 70)
try:
    response = requests.get(f"{BASE_URL}/api/fcm/tokens", timeout=10)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("✓ Success!")
        print(f"Response: {json.dumps(data, indent=2)}")
        
        if data.get('success') and data.get('tokens'):
            print(f"\n✓ Found {data.get('count', 0)} tokens")
        else:
            print("\n⚠ No tokens found - add one first!")
    else:
        print(f"✗ Failed!")
        print(f"Response: {response.text[:500]}")
        
        if "Authentication Required" in response.text:
            print("\n⚠ Vercel protection is still enabled!")
            print("Fix it: See FIX_VERCEL_PROTECTION.md")
            
except Exception as e:
    print(f"✗ Error: {e}")

# Test 2: Get specific token
print("\n[Test 2] GET /api/fcm/token/[email]")
print("=" * 70)
test_email = "astrallibertad_gmail_com"  # Already sanitized
try:
    response = requests.get(f"{BASE_URL}/api/fcm/token/{test_email}", timeout=10)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("✓ Success!")
        print(f"Response: {json.dumps(data, indent=2)}")
    elif response.status_code == 404:
        print("⚠ Token not found - add one first!")
    else:
        print(f"✗ Failed!")
        print(f"Response: {response.text[:500]}")
        
except Exception as e:
    print(f"✗ Error: {e}")

# Test 3: Register new token (via Android endpoint)
print("\n[Test 3] POST /api/fcm/register")
print("=" * 70)
test_data = {
    "email": "test_user@example.com",
    "fcm_token": "TEST_TOKEN_FROM_API_" + str(int(requests.Session().get(f"{BASE_URL}/").elapsed.total_seconds() * 1000)),
    "device_id": "test_device_api",
    "platform": "test"
}

try:
    response = requests.post(
        f"{BASE_URL}/api/fcm/register",
        json=test_data,
        timeout=10
    )
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("✓ Success!")
        print(f"Response: {json.dumps(data, indent=2)}")
    else:
        print(f"✗ Failed!")
        print(f"Response: {response.text[:500]}")
        
except Exception as e:
    print(f"✗ Error: {e}")

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

print("""
If all tests pass:
✓ Vercel protection is disabled for FCM endpoints
✓ Firebase Database is accessible
✓ Python can communicate with Vercel
✓ Ready to test actual notification sending

If tests fail with "Authentication Required":
✗ Fix Vercel deployment protection
  See: FIX_VERCEL_PROTECTION.md

If tests fail with "Token not found":
✗ Add a test token to Firebase first
  See: MANUAL_TOKEN_ADDITION.md or run: python add_test_token.py

Next step: Test actual FCM notification sending
  Run: python test_send_notification.py
""")