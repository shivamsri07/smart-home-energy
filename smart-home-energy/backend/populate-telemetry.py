import requests
import random
import time
import uuid
import os
from datetime import datetime, timedelta, timezone

# --- Configuration ---
# The script will use credentials from environment variables if they exist,
# otherwise it falls back to our seeded user.
BASE_URL = "http://localhost:8000/api/v1"
EMAIL = os.getenv("TEST_USER_EMAIL", "user_1@example.com")
PASSWORD = os.getenv("TEST_USER_PASSWORD", "password")
NUM_DEVICES = 3
DAYS_OF_DATA = 7  # Generate 7 days of data

def get_auth_token(email, password):
    """Logs in a user and returns their JWT access token."""
    print(f"Attempting to log in as {email}...")
    login_payload = {
        "username": email,
        "password": password
    }
    try:
        response = requests.post(f"{BASE_URL}/auth/login", data=login_payload)
        response.raise_for_status()  # Raises an exception for 4XX/5XX errors
        print("Login successful.")
        return response.json()["access_token"]
    except requests.exceptions.HTTPError as e:
        print(f"Login failed: {e.response.status_code} {e.response.json()}")
        raise
    except requests.exceptions.RequestException as e:
        print(f"Could not connect to the server: {e}")
        raise

def setup_devices(token, num_required):
    """Ensures the user has enough devices, creating them if necessary."""
    print("Setting up devices...")
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/devices/", headers=headers)
        response.raise_for_status()
        existing_devices = response.json()
        
        device_ids = [d["id"] for d in existing_devices]
        
        devices_to_create = num_required - len(device_ids)
        
        if devices_to_create > 0:
            print(f"Found {len(device_ids)} devices. Creating {devices_to_create} more...")
            for i in range(devices_to_create):
                device_name = f"Device {i+1}"
                create_response = requests.post(f"{BASE_URL}/devices/", headers=headers, json={"name": device_name})
                create_response.raise_for_status()
                new_device = create_response.json()
                device_ids.append(new_device["id"])
                print(f"  - Created device: {new_device['name']} ({new_device['id']})")
        
        print(f"Using {len(device_ids)} devices for data generation.")
        return device_ids
        
    except requests.exceptions.RequestException as e:
        print(f"Failed to set up devices: {e}")
        raise


if __name__ == "__main__":
    try:
        # 1. Authenticate and get a token
        auth_token = get_auth_token(EMAIL, PASSWORD)
        
        # 2. Get or create device IDs for the user
        device_ids_to_populate = setup_devices(auth_token, NUM_DEVICES)
        
        # --- Main Data Generation Loop ---
        print("\nStarting telemetry data generation...")
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Calculate start date (7 days ago)
        end_date = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        start_date = end_date - timedelta(days=DAYS_OF_DATA)
        
        # Calculate total number of requests for progress tracking
        total_requests = len(device_ids_to_populate) * 24 * 60 * DAYS_OF_DATA
        request_count = 0
        
        # Generate data for each day
        current_date = start_date
        while current_date <= end_date:
            print(f"\nGenerating data for {current_date.date()}")
            
            # One reading per hour for 24 hours
            for t in range(0, 24 * 60, 60):
                ts = (current_date + timedelta(seconds=t)).isoformat().replace('+00:00', 'Z')
                for dev_id in device_ids_to_populate:
                    request_count += 1
                    
                    payload = {
                        "deviceId": dev_id,
                        "timestamp": ts,
                        "energyWatts": round(random.uniform(5.0, 450.0), 4)
                    }
                    
                    try:
                        requests.post(f"{BASE_URL}/telemetry/", headers=headers, json=payload, timeout=5)
                        if request_count % 100 == 0:  # Print progress every 100 requests
                            print(f"Progress: {request_count}/{total_requests} ({round(request_count/total_requests*100, 1)}%)")
                    except requests.exceptions.RequestException as e:
                        print(f"  - Failed to submit data: {e}")
                    
                # A small sleep to not overwhelm the server instantly
                time.sleep(0.05)
            
            current_date += timedelta(days=1)
            
        print("\nData population script finished successfully.")
        
    except Exception as e:
        print(f"\nAn error occurred during script execution: {e}")