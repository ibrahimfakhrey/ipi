@echo off
echo Updating IPI App Colors to Match Web App...

REM Update main.dart with exact Black & Gold theme
(
echo import 'package:flutter/material.dart';
echo import 'package:flutter_localizations/flutter_localizations.dart';
echo import 'screens/login_screen.dart';
echo import 'screens/home_screen.dart';
echo.
echo void main^(^) { runApp^(const IPIApp^(^)^); }
echo.
echo class IPIApp extends StatelessWidget {
echo   const IPIApp^({super.key}^);
echo   @override
echo   Widget build^(BuildContext context^) {
echo     return MaterialApp^(
echo       title: 'منصة الاستثمار العقاري',
echo       debugShowCheckedModeBanner: false,
echo       locale: const Locale^('ar', 'EG'^),
echo       supportedLocales: const [Locale^('ar', 'EG'^)],
echo       localizationsDelegates: const [GlobalMaterialLocalizations.delegate, GlobalWidgetsLocalizations.delegate, GlobalCupertinoLocalizations.delegate],
echo       theme: ThemeData^(
echo         brightness: Brightness.dark,
echo         primaryColor: const Color^(0xFFFFD700^),
echo         scaffoldBackgroundColor: const Color^(0xFF000000^),
echo         colorScheme: const ColorScheme.dark^(primary: Color^(0xFFFFD700^), secondary: Color^(0xFFFDB931^), surface: Color^(0xFF1A1A1A^), background: Color^(0xFF000000^)^),
echo         appBarTheme: const AppBarTheme^(backgroundColor: Color^(0xFF1A1A1A^), elevation: 0, centerTitle: true, titleTextStyle: TextStyle^(fontSize: 20, fontWeight: FontWeight.bold, color: Color^(0xFFFFD700^)^)^),
echo         elevatedButtonTheme: ElevatedButtonThemeData^(style: ElevatedButton.styleFrom^(backgroundColor: const Color^(0xFFFFD700^), foregroundColor: const Color^(0xFF000000^), padding: const EdgeInsets.symmetric^(horizontal: 32, vertical: 16^), shape: RoundedRectangleBorder^(borderRadius: BorderRadius.circular^(12^)^), textStyle: const TextStyle^(fontSize: 18, fontWeight: FontWeight.bold^)^)^),
echo         cardTheme: CardTheme^(color: const Color^(0xFF1A1A1A^), elevation: 4, shape: RoundedRectangleBorder^(borderRadius: BorderRadius.circular^(16^)^)^),
echo         inputDecorationTheme: InputDecorationTheme^(filled: true, fillColor: const Color^(0xFF1A1A1A^), border: OutlineInputBorder^(borderRadius: BorderRadius.circular^(12^), borderSide: BorderSide.none^), focusedBorder: OutlineInputBorder^(borderRadius: BorderRadius.circular^(12^), borderSide: const BorderSide^(color: Color^(0xFFFFD700^), width: 2^)^), labelStyle: const TextStyle^(color: Color^(0xFFB0B0B0^)^)^),
echo       ^),
echo       home: const LoginScreen^(^),
echo       routes: {'/home': ^(context^) =^> const HomeScreen^(^)},
echo     ^);
echo   }
echo }
) > lib\main.dart

echo ✓ Updated main.dart with Black ^& Gold theme
echo.
echo Colors updated to match web app:
echo   PRIMARY_GOLD: #FFD700
echo   ACCENT_GOLD: #FDB931  
echo   BACKGROUND_BLACK: #000000
echo   SECONDARY_BLACK: #1A1A1A
echo.
echo Press 'R' in the Flutter terminal to hot reload!
pause
