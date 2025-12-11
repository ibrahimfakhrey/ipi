@echo off
echo Creating IPI Mobile App Files...

REM Create main.dart
(
echo import 'package:flutter/material.dart';
echo import 'package:flutter_localizations/flutter_localizations.dart';
echo import 'screens/login_screen.dart';
echo import 'screens/home_screen.dart';
echo.
echo void main^(^) {
echo   runApp^(const IPIApp^(^)^);
echo }
echo.
echo class IPIApp extends StatelessWidget {
echo   const IPIApp^({super.key}^);
echo.
echo   @override
echo   Widget build^(BuildContext context^) {
echo     return MaterialApp^(
echo       title: 'منصة الاستثمار العقاري',
echo       debugShowCheckedModeBanner: false,
echo       locale: const Locale^('ar', 'EG'^),
echo       supportedLocales: const [Locale^('ar', 'EG'^)],
echo       localizationsDelegates: const [
echo         GlobalMaterialLocalizations.delegate,
echo         GlobalWidgetsLocalizations.delegate,
echo         GlobalCupertinoLocalizations.delegate,
echo       ],
echo       theme: ThemeData^(
echo         brightness: Brightness.dark,
echo         primaryColor: const Color^(0xFFFFD700^),
echo         scaffoldBackgroundColor: const Color^(0xFF000000^),
echo         colorScheme: const ColorScheme.dark^(
echo           primary: Color^(0xFFFFD700^),
echo           secondary: Color^(0xFFFDB931^),
echo           surface: Color^(0xFF1A1A1A^),
echo         ^),
echo         appBarTheme: const AppBarTheme^(
echo           backgroundColor: Color^(0xFF1A1A1A^),
echo           elevation: 0,
echo           centerTitle: true,
echo         ^),
echo       ^),
echo       home: const LoginScreen^(^),
echo       routes: {
echo         '/home': ^(context^) =^> const HomeScreen^(^),
echo       },
echo     ^);
echo   }
echo }
) > lib\main.dart

echo ✓ Created main.dart

REM Create login_screen.dart
(
echo import 'package:flutter/material.dart';
echo import '../services/api_service.dart';
echo.
echo class LoginScreen extends StatefulWidget {
echo   const LoginScreen^({super.key}^);
echo   @override
echo   State^<LoginScreen^> createState^(^) =^> _LoginScreenState^(^);
echo }
echo.
echo class _LoginScreenState extends State^<LoginScreen^> {
echo   final _emailController = TextEditingController^(text: 'admin@apartmentshare.com'^);
echo   final _passwordController = TextEditingController^(text: 'admin123'^);
echo   final _apiService = ApiService^(^);
echo   bool _isLoading = false;
echo.
echo   Future^<void^> _login^(^) async {
echo     setState^(^(^) =^> _isLoading = true^);
echo     try {
echo       await _apiService.login^(_emailController.text, _passwordController.text^);
echo       if ^(mounted^) Navigator.pushReplacementNamed^(context, '/home'^);
echo     } catch ^(e^) {
echo       if ^(mounted^) ScaffoldMessenger.of^(context^).showSnackBar^(SnackBar^(content: Text^('Error: $e'^), backgroundColor: Colors.red^)^);
echo     } finally {
echo       if ^(mounted^) setState^(^(^) =^> _isLoading = false^);
echo     }
echo   }
echo.
echo   @override
echo   Widget build^(BuildContext context^) {
echo     return Scaffold^(
echo       body: Center^(
echo         child: SingleChildScrollView^(
echo           padding: const EdgeInsets.all^(24^),
echo           child: Column^(
echo             children: [
echo               const Icon^(Icons.apartment, size: 80, color: Color^(0xFFFFD700^)^),
echo               const SizedBox^(height: 16^),
echo               const Text^('IPI Investment Platform', style: TextStyle^(fontSize: 28, color: Color^(0xFFFFD700^)^)^),
echo               const SizedBox^(height: 48^),
echo               TextField^(controller: _emailController, decoration: const InputDecoration^(labelText: 'Email'^)^),
echo               const SizedBox^(height: 16^),
echo               TextField^(controller: _passwordController, decoration: const InputDecoration^(labelText: 'Password'^), obscureText: true^),
echo               const SizedBox^(height: 24^),
echo               ElevatedButton^(onPressed: _isLoading ? null : _login, child: _isLoading ? const CircularProgressIndicator^(^) : const Text^('Login'^)^),
echo             ],
echo           ^),
echo         ^),
echo       ^),
echo     ^);
echo   }
echo }
) > lib\screens\login_screen.dart

echo ✓ Created login_screen.dart

REM Create home_screen.dart  
(
echo import 'package:flutter/material.dart';
echo import '../services/api_service.dart';
echo.
echo class HomeScreen extends StatefulWidget {
echo   const HomeScreen^({super.key}^);
echo   @override
echo   State^<HomeScreen^> createState^(^) =^> _HomeScreenState^(^);
echo }
echo.
echo class _HomeScreenState extends State^<HomeScreen^> {
echo   final _apiService = ApiService^(^);
echo   Map^<String, dynamic^>? _data;
echo   bool _isLoading = true;
echo.
echo   @override
echo   void initState^(^) {
echo     super.initState^(^);
echo     _loadData^(^);
echo   }
echo.
echo   Future^<void^> _loadData^(^) async {
echo     try {
echo       final dashboard = await _apiService.getDashboard^(^);
echo       final apartments = await _apiService.getApartments^(^);
echo       setState^(^(^) {
echo         _data = {...dashboard, 'apartments': apartments};
echo         _isLoading = false;
echo       }^);
echo     } catch ^(e^) {
echo       if ^(mounted^) ScaffoldMessenger.of^(context^).showSnackBar^(SnackBar^(content: Text^('Error: $e'^)^)^);
echo       setState^(^(^) =^> _isLoading = false^);
echo     }
echo   }
echo.
echo   @override
echo   Widget build^(BuildContext context^) {
echo     return Scaffold^(
echo       appBar: AppBar^(title: const Text^('Dashboard'^)^),
echo       body: _isLoading ? const Center^(child: CircularProgressIndicator^(^)^) : ListView^(
echo         padding: const EdgeInsets.all^(16^),
echo         children: [
echo           Text^('Wallet: ${_data?['wallet_balance'] ?? 0}', style: const TextStyle^(fontSize: 24^)^),
echo           Text^('Invested: ${_data?['total_invested'] ?? 0}'^),
echo           Text^('Monthly Income: ${_data?['monthly_expected_income'] ?? 0}'^),
echo           const SizedBox^(height: 20^),
echo           const Text^('Apartments:', style: TextStyle^(fontSize: 20^)^),
echo           ...^(_data?['apartments'] as List? ?? []^).map^(^(apt^) =^> Card^(
echo             child: ListTile^(
echo               title: Text^(apt['title']^),
echo               subtitle: Text^('Price: ${apt['share_price']} - Available: ${apt['shares_available']}'^),
echo             ^),
echo           ^)^),
echo         ],
echo       ^),
echo     ^);
echo   }
echo }
) > lib\screens\home_screen.dart

echo ✓ Created home_screen.dart
echo.
echo ========================================
echo IPI Mobile App Created Successfully!
echo ========================================
echo.
echo Next: Run 'flutter run -d edge' to launch the app
pause
