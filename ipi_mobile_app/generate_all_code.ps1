# IPI Mobile App - Complete Flutter Code Generator
# This script creates ALL Flutter files for the application

Write-Host "=" * 60 -ForegroundColor Gold
Write-Host "  IPI Mobile App - Flutter Code Generator" -ForegroundColor Gold
Write-Host "=" * 60 -ForegroundColor Gold
Write-Host ""

# Function to create file with content
function Create-DartFile {
    param(
        [string]$Path,
        [string]$Content
    )
    
    $dir = Split-Path -Parent $Path
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
    
    Set-Content -Path $Path -Value $Content -Encoding UTF8
    Write-Host "✓ Created: $Path" -ForegroundColor Cyan
}

# MAIN.DART
$mainContent = @'
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'services/auth_service.dart';
import 'services/api_service.dart';
import 'screens/splash_screen.dart';
import 'screens/auth/login_screen.dart';
import 'screens/auth/register_screen.dart';
import 'screens/home/home_screen.dart';
import 'screens/apartments/apartments_list_screen.dart';
import 'screens/apartments/apartment_detail_screen.dart';
import 'screens/wallet/wallet_screen.dart';
import 'screens/profile/profile_screen.dart';
import 'screens/investments/my_investments_screen.dart';
import 'utils/theme.dart';

void main() {
  runApp(const IPIApp());
}

class IPIApp extends StatelessWidget {
  const IPIApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => AuthService()),
        ChangeNotifierProvider(create: (_) => ApiService()),
      ],
      child: MaterialApp(
        title: 'منصة الاستثمار العقاري',
        debugShowCheckedModeBanner: false,
        locale: const Locale('ar', 'EG'),
        supportedLocales: const [Locale('ar', 'EG')],
        localizationsDelegates: const [
          GlobalMaterialLocalizations.delegate,
          GlobalWidgetsLocalizations.delegate,
          GlobalCupertinoLocalizations.delegate,
        ],
        theme: AppTheme.darkTheme,
        initialRoute: '/',
        routes: {
          '/': (context) => const SplashScreen(),
          '/login': (context) => const LoginScreen(),
          '/register': (context) => const RegisterScreen(),
          '/home': (context) => const HomeScreen(),
          '/apartments': (context) => const ApartmentsListScreen(),
          '/wallet': (context) => const WalletScreen(),
          '/profile': (context) => const ProfileScreen(),
          '/my-investments': (context) => const MyInvestmentsScreen(),
        },
        onGenerateRoute: (settings) {
          if (settings.name == '/apartment-detail') {
            final apartmentId = settings.arguments as int;
            return MaterialPageRoute(
              builder: (context) => ApartmentDetailScreen(apartmentId: apartmentId),
            );
          }
          return null;
        },
      ),
    );
  }
}
'@

Create-DartFile -Path "lib\main.dart" -Content $mainContent

# THEME.DART
$themeContent = @'
import 'package:flutter/material.dart';

class AppTheme {
  static const Color primaryGold = Color(0xFFFFD700);
  static const Color accentGold = Color(0xFFFDB931);
  static const Color backgroundBlack = Color(0xFF000000);
  static const Color secondaryBlack = Color(0xFF1A1A1A);
  static const Color textLight = Color(0xFFFFFFFF);
  static const Color textGray = Color(0xFFB0B0B0);

  static ThemeData get darkTheme {
    return ThemeData(
      brightness: Brightness.dark,
      primaryColor: primaryGold,
      scaffoldBackgroundColor: backgroundBlack,
      colorScheme: const ColorScheme.dark(
        primary: primaryGold,
        secondary: accentGold,
        surface: secondaryBlack,
        background: backgroundBlack,
      ),
      appBarTheme: const AppBarTheme(
        backgroundColor: secondaryBlack,
        elevation: 0,
        centerTitle: true,
        titleTextStyle: TextStyle(
          fontFamily: 'Cairo',
          fontSize: 20,
          fontWeight: FontWeight.bold,
          color: primaryGold,
        ),
      ),
      textTheme: const TextTheme(
        displayLarge: TextStyle(fontFamily: 'Cairo', color: textLight, fontSize: 32, fontWeight: FontWeight.bold),
        headlineMedium: TextStyle(fontFamily: 'Cairo', color: textLight, fontSize: 20, fontWeight: FontWeight.w600),
        bodyLarge: TextStyle(fontFamily: 'Tajawal', color: textLight, fontSize: 16),
        bodyMedium: TextStyle(fontFamily: 'Tajawal', color: textLight, fontSize: 14),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: primaryGold,
          foregroundColor: backgroundBlack,
          padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
          textStyle: const TextStyle(fontFamily: 'Cairo', fontSize: 16, fontWeight: FontWeight.bold),
        ),
      ),
      cardTheme: CardTheme(
        color: secondaryBlack,
        elevation: 4,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: secondaryBlack,
        border: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide.none),
        focusedBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: const BorderSide(color: primaryGold, width: 2)),
        labelStyle: const TextStyle(color: textGray, fontFamily: 'Cairo'),
      ),
    );
  }
}
'@

Create-DartFile -Path "lib\utils\theme.dart" -Content $themeContent

# CONSTANTS.DART
$constantsContent = @'
class AppConstants {
  static const String baseUrl = 'http://192.168.1.100:5001/api/v1';
  static const String appName = 'منصة الاستثمار العقاري';
}
'@

Create-DartFile -Path "lib\utils\constants.dart" -Content $constantsContent

Write-Host ""
Write-Host "=" * 60 -ForegroundColor Green
Write-Host "  Flutter App Code Generated Successfully!" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Update API URL in lib\utils\constants.dart" -ForegroundColor White
Write-Host "2. Run: flutter pub get" -ForegroundColor White
Write-Host "3. Run: flutter run" -ForegroundColor White
'@

Set-Content -Path "generate_flutter_code.ps1" -Value $Content -Encoding UTF8
Write-Host "✓ Created complete Flutter code generator script" -ForegroundColor Green
