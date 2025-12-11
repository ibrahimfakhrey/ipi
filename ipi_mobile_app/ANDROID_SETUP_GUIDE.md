# 🤖 Android Emulator Setup Guide

## 📥 Downloads in Progress

### 1. Flutter SDK
**File:** `C:\Users\User\Desktop\flutter.zip`
**Status:** ⏳ Downloading (536+ MB so far)
**Total Size:** ~1 GB

### 2. Android Studio
**File:** `C:\Users\User\Desktop\android-studio-installer.exe`
**Status:** ⏳ Downloading
**Total Size:** ~1.1 GB

---

## 🚀 Installation Steps (After Downloads Complete)

### Step 1: Install Flutter SDK

```powershell
# Extract Flutter
Expand-Archive -Path "C:\Users\User\Desktop\flutter.zip" -DestinationPath "C:\flutter" -Force

# Add to PATH (Run PowerShell as Administrator)
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";C:\flutter\bin", "Machine")

# Restart PowerShell, then verify
flutter doctor
```

### Step 2: Install Android Studio

1. **Run the installer:**
   ```powershell
   C:\Users\User\Desktop\android-studio-installer.exe
   ```

2. **During installation, make sure to check:**
   - ✅ Android SDK
   - ✅ Android SDK Platform
   - ✅ Android Virtual Device (AVD)

3. **Complete the setup wizard**

### Step 3: Configure Android SDK

After Android Studio opens:

1. Go to **File → Settings → Appearance & Behavior → System Settings → Android SDK**

2. In **SDK Platforms** tab, install:
   - ✅ Android 14.0 (API 34) - Latest
   - ✅ Android 13.0 (API 33)

3. In **SDK Tools** tab, install:
   - ✅ Android SDK Build-Tools
   - ✅ Android Emulator
   - ✅ Android SDK Platform-Tools
   - ✅ Intel x86 Emulator Accelerator (HAXM)

4. Click **Apply** and wait for downloads

### Step 4: Create Android Virtual Device (AVD)

1. In Android Studio, go to **Tools → Device Manager**

2. Click **Create Device**

3. Select a device:
   - Recommended: **Pixel 7 Pro** or **Pixel 6**

4. Select a system image:
   - Recommended: **Android 14.0 (API 34)** with **x86_64** architecture
   - Click **Download** if needed

5. Configure AVD:
   - Name: `Pixel_7_API_34`
   - Click **Finish**

### Step 5: Accept Android Licenses

```powershell
flutter doctor --android-licenses
# Press 'y' to accept all licenses
```

### Step 6: Verify Setup

```powershell
flutter doctor -v
```

You should see:
- ✅ Flutter (Channel stable)
- ✅ Android toolchain
- ✅ Android Studio
- ✅ Connected device (emulator)

---

## 🎮 Running the Emulator

### Option 1: From Android Studio
1. Open **Device Manager**
2. Click the **Play** button next to your AVD

### Option 2: From Command Line
```powershell
# List available emulators
flutter emulators

# Launch emulator
flutter emulators --launch Pixel_7_API_34
```

---

## 📱 Running Your Flutter App

Once the emulator is running:

```powershell
# Navigate to your Flutter project
cd C:\Users\User\Desktop\ipi-main\ipi_mobile_app

# Check connected devices
flutter devices

# Run the app
flutter run
```

The app will automatically install and launch on the emulator!

---

## 🔧 Troubleshooting

### If emulator is slow:
1. Enable **Hardware Acceleration** (HAXM)
2. Allocate more RAM in AVD settings (4GB recommended)
3. Enable **Graphics: Hardware - GLES 2.0**

### If "flutter doctor" shows issues:
```powershell
# Update Flutter
flutter upgrade

# Re-accept licenses
flutter doctor --android-licenses
```

### If emulator won't start:
1. Check BIOS virtualization is enabled (VT-x/AMD-V)
2. Disable Hyper-V if using Intel HAXM
3. Try creating a new AVD with different API level

---

## 📊 System Requirements

- **RAM:** 8GB minimum (16GB recommended)
- **Disk Space:** 15GB for Android Studio + SDK
- **Processor:** Intel/AMD with virtualization support
- **OS:** Windows 10/11 (64-bit)

---

## ⏱️ Estimated Times

- Flutter extraction: 2-3 minutes
- Android Studio installation: 5-10 minutes
- SDK downloads: 10-15 minutes
- First emulator boot: 2-3 minutes
- App compilation & run: 3-5 minutes

**Total setup time:** ~30-40 minutes

---

## 🎯 Quick Start Checklist

- [ ] Flutter SDK extracted and in PATH
- [ ] Android Studio installed
- [ ] Android SDK installed (API 33/34)
- [ ] Android licenses accepted
- [ ] AVD created
- [ ] Emulator launched successfully
- [ ] `flutter doctor` shows all green checkmarks
- [ ] Flutter app code generated
- [ ] App running on emulator

---

## 📝 Alternative: Use Physical Device

If you have an Android phone:

1. **Enable Developer Options:**
   - Go to Settings → About Phone
   - Tap "Build Number" 7 times

2. **Enable USB Debugging:**
   - Settings → Developer Options → USB Debugging

3. **Connect via USB:**
   ```powershell
   # Check device is connected
   flutter devices
   
   # Run app
   flutter run
   ```

This is often faster than using an emulator!

---

**Next:** Wait for downloads to complete, then follow the installation steps above.
