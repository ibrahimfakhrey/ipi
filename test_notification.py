"""
Test script to send a notification to a specific user
Run this on PythonAnywhere to test notifications
"""

# Run in PythonAnywhere bash console:
# cd /home/amsfiles/ipi
# python3 test_notification.py

from app import create_app, db
from app.models import User
from app.utils.notification_service import send_push_notification, NotificationTemplates, initialize_firebase

app = create_app('production')

with app.app_context():
    # Find the user
    user = User.query.filter_by(email='a@aa.com').first()
    
    if user:
        print(f"✅ Found user: {user.name} ({user.email})")
        print(f"   User ID: {user.id}")
        print(f"   FCM Token: {user.fcm_token if user.fcm_token else '❌ NO TOKEN!'}")
        
        if user.fcm_token:
            # Initialize Firebase
            if initialize_firebase():
                print("\n✅ Firebase initialized")
                
                # Send test notification
                notification = NotificationTemplates.welcome(user.name)
                result = send_push_notification(
                    user_id=user.id,
                    title=notification["title"],
                    body=notification["body"],
                    data=notification.get("data")
                )
                
                if result:
                    print("🎉 Notification sent successfully!")
                else:
                    print("❌ Failed to send notification")
            else:
                print("❌ Failed to initialize Firebase - check FIREBASE_SERVICE_ACCOUNT")
        else:
            print("\n⚠️  User has no FCM token.")
            print("   The Flutter app needs to call POST /api/v1/user/update-fcm-token after login")
    else:
        print("❌ User not found: a@aa.com")
