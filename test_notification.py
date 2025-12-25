#!/usr/bin/env python3
"""
Test FCM Push Notification Script
Run: python3 test_notification.py
"""
from app.models import Driver
from app.utils.notification_service import send_driver_notification
from run import app

with app.app_context():
    print("=" * 50)
    print("FCM Notification Test")
    print("=" * 50)

    # Get all drivers
    drivers = Driver.query.all()

    if not drivers:
        print("No drivers found!")
        exit()

    # Show all drivers
    print("\nAvailable drivers:")
    for d in drivers:
        token_status = "HAS TOKEN" if d.fcm_token else "NO TOKEN"
        print(f"  [{d.id}] {d.name} - {token_status}")

    # Get first driver with FCM token
    driver = None
    for d in drivers:
        if d.fcm_token:
            driver = d
            break

    if not driver:
        print("\nNo driver has FCM token set!")
        print("The Flutter app needs to call /api/driver/update-fcm-token first.")
        exit()

    print(f"\nTesting with driver: {driver.name} (ID: {driver.id})")
    print(f"FCM Token: {driver.fcm_token[:60]}...")
    print(f"Token Updated: {driver.fcm_token_updated_at}")

    print("\nSending test notification...")

    try:
        result = send_driver_notification(
            driver.id,
            "اختبار الإشعارات",
            "هذه رسالة اختبار من السيرفر - Test notification",
            {"type": "test", "screen": "home"}
        )

        if result:
            print("SUCCESS! Notification sent.")
        else:
            print("FAILED! Check error logs for details.")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
