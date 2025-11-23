# 🚀 Quick Start - Run Flutter App in Browser (No Emulator Needed!)

## Step 1: Extract Flutter Manually

Since the file is locked, please:
1. Close any PowerShell windows that might be downloading
2. Right-click on `C:\Users\User\Desktop\flutter.zip`
3. Select "Extract All..."
4. Extract to `C:\flutter`

**OR** run this in a NEW PowerShell window:
```powershell
Expand-Archive -Path "C:\Users\User\Desktop\flutter.zip" -DestinationPath "C:\flutter" -Force
```

## Step 2: Add Flutter to PATH

Run PowerShell **as Administrator**, then:
```powershell
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";C:\flutter\bin", "Machine")
```

## Step 3: Restart PowerShell & Verify

Close and reopen PowerShell, then:
```powershell
flutter doctor
```

## Step 4: Enable Flutter Web

```powershell
flutter config --enable-web
```

## Step 5: Create Flutter Project Properly

```powershell
cd C:\Users\User\Desktop\ipi-main
flutter create ipi_mobile_app --org com.ipi --platforms web,android
```

This will create a proper Flutter project structure.

## Step 6: Copy Our Custom Code

After creating the project, we'll add our custom code:

```powershell
cd ipi_mobile_app

# Our code generation script will add:
# - API service
# - Authentication
# - All screens
# - Black & Gold theme
```

## Step 7: Update API URL

Edit `lib/utils/constants.dart`:
```dart
class AppConstants {
  static const String baseUrl = 'http://localhost:5001/api/v1';
}
```

## Step 8: Run in Browser!

```powershell
flutter run -d chrome
```

This will open the app in Chrome browser - **NO EMULATOR NEEDED!**

---

## Alternative: Quick Manual Steps

If you want to do it manually right now:

### 1. Extract Flutter
- Open File Explorer
- Navigate to `C:\Users\User\Desktop\`
- Right-click `flutter.zip` → Extract All → Choose `C:\` as destination

### 2. Add to PATH
- Search "Environment Variables" in Windows
- Click "Environment Variables"
- Under "System variables", select "Path"
- Click "Edit" → "New"
- Add: `C:\flutter\bin`
- Click OK on all windows

### 3. Restart Terminal & Test
```powershell
flutter --version
```

### 4. Run Web Version
```powershell
cd C:\Users\User\Desktop\ipi-main
flutter create ipi_mobile_app --platforms web
cd ipi_mobile_app
flutter run -d chrome
```

---

## ✅ Advantages of Web Version

- ✅ No emulator needed
- ✅ Faster startup
- ✅ Easier debugging
- ✅ Works immediately
- ✅ Same code as mobile

Later you can build for Android/iOS when ready!

---

**Next:** Extract Flutter, then I'll help you create and run the web version!
