# Flutter App Setup Script
# This script creates all necessary Flutter files for the IPI Mobile App

Write-Host "Creating Flutter App Structure..." -ForegroundColor Green

# Create main.dart
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

Set-Content -Path "lib\main.dart" -Value $mainContent -Encoding UTF8

Write-Host "✓ Created main.dart" -ForegroundColor Cyan

# Create theme.dart
$themeContent = @'
import 'package:flutter/material.dart';

class AppTheme {
  // Black & Gold Color Palette
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
      
      // AppBar Theme
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
      
      // Text Theme
      textTheme: const TextTheme(
        displayLarge: TextStyle(fontFamily: 'Cairo', color: textLight, fontSize: 32, fontWeight: FontWeight.bold),
        displayMedium: TextStyle(fontFamily: 'Cairo', color: textLight, fontSize: 28, fontWeight: FontWeight.bold),
        displaySmall: TextStyle(fontFamily: 'Cairo', color: textLight, fontSize: 24, fontWeight: FontWeight.bold),
        headlineMedium: TextStyle(fontFamily: 'Cairo', color: textLight, fontSize: 20, fontWeight: FontWeight.w600),
        headlineSmall: TextStyle(fontFamily: 'Cairo', color: textLight, fontSize: 18, fontWeight: FontWeight.w600),
        titleLarge: TextStyle(fontFamily: 'Cairo', color: textLight, fontSize: 16, fontWeight: FontWeight.w500),
        bodyLarge: TextStyle(fontFamily: 'Tajawal', color: textLight, fontSize: 16),
        bodyMedium: TextStyle(fontFamily: 'Tajawal', color: textLight, fontSize: 14),
        bodySmall: TextStyle(fontFamily: 'Tajawal', color: textGray, fontSize: 12),
      ),
      
      // Button Theme
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: primaryGold,
          foregroundColor: backgroundBlack,
          padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
          textStyle: const TextStyle(
            fontFamily: 'Cairo',
            fontSize: 16,
            fontWeight: FontWeight.bold,
          ),
        ),
      ),
      
      // Card Theme
      cardTheme: CardTheme(
        color: secondaryBlack,
        elevation: 4,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      ),
      
      // Input Decoration Theme
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: secondaryBlack,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide.none,
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: primaryGold, width: 2),
        ),
        labelStyle: const TextStyle(color: textGray, fontFamily: 'Cairo'),
        hintStyle: const TextStyle(color: textGray, fontFamily: 'Tajawal'),
      ),
    );
  }
}
'@

Set-Content -Path "lib\utils\theme.dart" -Value $themeContent -Encoding UTF8
Write-Host "✓ Created theme.dart" -ForegroundColor Cyan

Write-Host "`nFlutter app structure created successfully!" -ForegroundColor Green
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Install Flutter SDK" -ForegroundColor White
Write-Host "2. Run 'flutter pub get' to install dependencies" -ForegroundColor White
Write-Host "3. Run 'flutter run' to start the app" -ForegroundColor White
