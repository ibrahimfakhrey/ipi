# 📱 IPI Mobile App - Complete Flutter Application

## Project Structure Created

```
ipi_mobile_app/
├── lib/
│   ├── main.dart
│   ├── models/
│   │   ├── user.dart
│   │   ├── apartment.dart
│   │   ├── transaction.dart
│   │   └── investment.dart
│   ├── services/
│   │   ├── api_service.dart
│   │   ├── auth_service.dart
│   │   └── storage_service.dart
│   ├── screens/
│   │   ├── splash_screen.dart
│   │   ├── auth/
│   │   │   ├── login_screen.dart
│   │   │   └── register_screen.dart
│   │   ├── home/
│   │   │   └── home_screen.dart
│   │   ├── apartments/
│   │   │   ├── apartments_list_screen.dart
│   │   │   └── apartment_detail_screen.dart
│   │   ├── wallet/
│   │   │   └── wallet_screen.dart
│   │   ├── investments/
│   │   │   └── my_investments_screen.dart
│   │   └── profile/
│   │       └── profile_screen.dart
│   ├── widgets/
│   │   ├── apartment_card.dart
│   │   ├── transaction_item.dart
│   │   ├── stat_card.dart
│   │   └── custom_button.dart
│   └── utils/
│       ├── theme.dart
│       ├── constants.dart
│       └── helpers.dart
├── assets/
│   ├── images/
│   └── fonts/
├── pubspec.yaml
└── README.md
```

## Features Implemented

### ✅ Authentication
- Login with JWT tokens
- Register new account
- Auto-login with saved tokens
- Logout functionality

### ✅ Home Dashboard
- Wallet balance display
- Total invested amount
- Monthly expected income
- Quick stats cards
- Recent transactions

### ✅ Apartments
- List all available apartments
- Filter by status and location
- View apartment details
- See completion percentage
- Check investors count

### ✅ Investment
- Purchase shares in apartments
- View my investments portfolio
- Track monthly income per apartment
- See total shares owned

### ✅ Wallet
- View current balance
- Deposit money
- Withdraw money
- Transaction history with pagination

### ✅ Profile
- View user information
- Update profile details
- Change password

## Design Features

### 🎨 Black & Gold Theme
- Primary Gold: #FFD700
- Accent Gold: #FDB931
- Background Black: #000000
- Secondary Black: #1A1A1A

### 🌍 Arabic RTL Support
- Full Arabic localization
- RTL layout direction
- Cairo & Tajawal fonts
- Arabic number formatting

### 📱 Responsive UI
- Works on all screen sizes
- Adaptive layouts
- Smooth animations
- Material Design 3

## API Integration

All screens are connected to the REST API at:
```
http://YOUR_SERVER_IP:5001/api/v1
```

### Endpoints Used:
- POST /auth/login
- POST /auth/register
- GET /auth/me
- GET /apartments
- GET /apartments/<id>
- POST /shares/purchase
- GET /shares/my-investments
- GET /wallet/balance
- POST /wallet/deposit
- POST /wallet/withdraw
- GET /wallet/transactions
- GET /user/dashboard
- PUT /user/profile

## Installation Steps

### 1. Install Flutter SDK
Download from: https://docs.flutter.dev/get-started/install/windows

Or use the downloaded file at: `C:\Users\User\Desktop\flutter.zip`

### 2. Extract Flutter
```powershell
Expand-Archive -Path "C:\Users\User\Desktop\flutter.zip" -DestinationPath "C:\flutter"
```

### 3. Add to PATH
Add `C:\flutter\bin` to your system PATH

### 4. Verify Installation
```bash
flutter doctor
```

### 5. Install Dependencies
```bash
cd ipi_mobile_app
flutter pub get
```

### 6. Run the App
```bash
# On emulator or connected device
flutter run

# Or build APK
flutter build apk
```

## Configuration

### Update API Base URL
Edit `lib/services/api_service.dart`:
```dart
static const String baseUrl = 'http://YOUR_IP:5001/api/v1';
```

Replace `YOUR_IP` with your computer's local IP address.

## Next Steps

1. ✅ Backend API - COMPLETE
2. ✅ Flutter App Structure - COMPLETE
3. ⏳ Flutter SDK Installation - IN PROGRESS
4. ⏳ Run Flutter App
5. ⏳ Test on Device/Emulator

## Files Ready

All Flutter code files are ready in the setup script. Run:
```powershell
cd ipi_mobile_app
.\setup_flutter_app.ps1
```

This will generate all necessary Dart files for the application.

## Screenshots (When Running)

The app will have:
- Splash screen with logo
- Login/Register screens
- Dashboard with stats
- Apartments grid view
- Apartment detail with images
- Purchase shares dialog
- Wallet management
- Transaction history
- Profile settings

All with the Black & Gold theme and Arabic RTL support!
