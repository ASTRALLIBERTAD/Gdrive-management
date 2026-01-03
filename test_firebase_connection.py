import os
import sys
import requests

FIREBASE_DB_URL = "https://gdrive-manager-479819-default-rtdb.asia-southeast1.firebasedatabase.app"

print("=" * 60)
print("Firebase Realtime Database Connection Test")
print("=" * 60)

print(f"\n1. Testing connection to: {FIREBASE_DB_URL}")

try:
    response = requests.get(f"{FIREBASE_DB_URL}/.json", timeout=10)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        print("   ✓ Connection successful!")
        data = response.json()
        print(f"   Data keys: {list(data.keys()) if data else 'Empty database'}")
    else:
        print(f"   ✗ Connection failed with status {response.status_code}")
except Exception as e:
    print(f"   ✗ Error: {e}")

print(f"\n2. Checking fcm_tokens path...")
try:
    response = requests.get(f"{FIREBASE_DB_URL}/fcm_tokens.json", timeout=10)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        if data:
            print(f"   ✓ Found {len(data)} registered devices:")
            for key, value in data.items():
                email = key.replace('_', '@', 1).replace('_', '.')
                print(f"     - {email}")
                print(f"       Token: {value.get('fcm_token', 'N/A')[:20]}...")
                print(f"       Platform: {value.get('platform', 'N/A')}")
        else:
            print("   ⚠ No tokens registered yet")
            print("   This is normal if no one has logged in on Android yet")
    else:
        print(f"   ⚠ Path not found (status {response.status_code})")
        print("   This is normal - tokens will be created when users login")
except Exception as e:
    print(f"   ✗ Error: {e}")

print(f"\n3. Testing manual token write...")
test_email = "test_gmail_com"
test_data = {
    "fcm_token": "test_token_123",
    "device_id": "test_device",
    "platform": "android",
    "timestamp": 1735738800000
}

try:
    response = requests.put(
        f"{FIREBASE_DB_URL}/fcm_tokens/{test_email}.json",
        json=test_data,
        timeout=10
    )
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        print("   ✓ Write successful!")
        
        response = requests.get(f"{FIREBASE_DB_URL}/fcm_tokens/{test_email}.json", timeout=10)
        if response.status_code == 200:
            print("   ✓ Read back successful!")
            
            response = requests.delete(f"{FIREBASE_DB_URL}/fcm_tokens/{test_email}.json", timeout=10)
            print("   ✓ Cleanup successful!")
    else:
        print(f"   ✗ Write failed with status {response.status_code}")
except Exception as e:
    print(f"   ✗ Error: {e}")

print("\n" + "=" * 60)
print("Next Steps:")
print("=" * 60)
print("1. Set environment variable:")
print(f"   export FIREBASE_DB_URL='{FIREBASE_DB_URL}'")
print("\n2. Download Firebase Admin credentials:")
print("   - Go to Firebase Console")
print("   - Project Settings → Service Accounts")
print("   - Generate new private key")
print("   - Save as 'firebase-admin-credentials.json'")
print("\n3. Install Firebase Admin SDK:")
print("   pip install firebase-admin --break-system-packages")
print("\n4. Test FCM service:")
print("   python test_fcm.py")
print("=" * 60)