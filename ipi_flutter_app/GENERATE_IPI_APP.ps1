# IPI Flutter App - Complete Code Generator
# This script creates all necessary Dart files for the IPI Investment Platform

Write-Host "`n🚀 Generating IPI Investment Platform - Flutter App`n" -ForegroundColor Gold

# Create directories
$dirs = @("lib\services", "lib\screens", "lib\widgets", "lib\models")
foreach ($dir in $dirs) {
    New-Item -ItemType Directory -Path $dir -Force | Out-Null
}

# API Service
$apiService = @'
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

class ApiService {
  static const String baseUrl = 'http://localhost:5001/api/v1';
  String? _token;

  Future<void> loadToken() async {
    final prefs = await SharedPreferences.getInstance();
    _token = prefs.getString('access_token');
  }

  Future<void> saveToken(String token) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('access_token', token);
    _token = token;
  }

  Map<String, String> get headers => {
    'Content-Type': 'application/json; charset=UTF-8',
    if (_token != null) 'Authorization': 'Bearer $_token',
  };

  Future<Map<String, dynamic>> login(String email, String password) async {
    final response = await http.post(
      Uri.parse('$baseUrl/auth/login'),
      headers: {'Content-Type': 'application/json'},
      body: json.encode({'email': email, 'password': password}),
    );
    if (response.statusCode == 200) {
      final data = json.decode(utf8.decode(response.bodyBytes));
      await saveToken(data['data']['access_token']);
      return data;
    }
    throw Exception('فشل تسجيل الدخول');
  }

  Future<Map<String, dynamic>> getDashboard() async {
    await loadToken();
    final response = await http.get(Uri.parse('$baseUrl/user/dashboard'), headers: headers);
    if (response.statusCode == 200) {
      return json.decode(utf8.decode(response.bodyBytes))['data'];
    }
    throw Exception('فشل في جلب البيانات');
  }

  Future<List<dynamic>> getApartments() async {
    await loadToken();
    final response = await http.get(Uri.parse('$baseUrl/apartments'), headers: headers);
    if (response.statusCode == 200) {
      return json.decode(utf8.decode(response.bodyBytes))['data']['apartments'];
    }
    throw Exception('فشل في جلب العقارات');
  }
}
'@

Set-Content -Path "lib\services\api_service.dart" -Value $apiService -Encoding UTF8
Write-Host "✓ api_service.dart" -ForegroundColor Cyan

# Main App
$mainApp = @'
import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'screens/login_screen.dart';
import 'screens/home_screen.dart';

void main() {
  runApp(const IPIApp());
}

class IPIApp extends StatelessWidget {
  const IPIApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'منصة الاستثمار العقاري',
      debugShowCheckedModeBanner: false,
      locale: const Locale('ar', 'EG'),
      supportedLocales: const [Locale('ar', 'EG')],
      localizationsDelegates: const [
        GlobalMaterialLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
      ],
      theme: ThemeData(
        brightness: Brightness.dark,
        primaryColor: const Color(0xFFFFD700),
        scaffoldBackgroundColor: const Color(0xFF000000),
        colorScheme: const ColorScheme.dark(
          primary: Color(0xFFFFD700),
          secondary: Color(0xFFFDB931),
          surface: Color(0xFF1A1A1A),
        ),
        appBarTheme: const AppBarTheme(
          backgroundColor: Color(0xFF1A1A1A),
          elevation: 0,
          centerTitle: true,
        ),
        elevatedButtonTheme: ElevatedButtonThemeData(
          style: ElevatedButton.styleFrom(
            backgroundColor: const Color(0xFFFFD700),
            foregroundColor: Colors.black,
            padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
          ),
        ),
        cardTheme: CardTheme(
          color: const Color(0xFF1A1A1A),
          elevation: 4,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        ),
      ),
      home: const LoginScreen(),
      routes: {
        '/home': (context) => const HomeScreen(),
      },
    );
  }
}
'@

Set-Content -Path "lib\main.dart" -Value $mainApp -Encoding UTF8 -Force
Write-Host "✓ main.dart" -ForegroundColor Cyan

# Login Screen
$loginScreen = @'
import 'package:flutter/material.dart';
import '../services/api_service.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _emailController = TextEditingController(text: 'admin@apartmentshare.com');
  final _passwordController = TextEditingController(text: 'admin123');
  final _apiService = ApiService();
  bool _isLoading = false;

  Future<void> _login() async {
    setState(() => _isLoading = true);
    try {
      await _apiService.login(_emailController.text, _passwordController.text);
      if (mounted) {
        Navigator.pushReplacementNamed(context, '/home');
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('خطأ: ${e.toString()}'), backgroundColor: Colors.red),
        );
      }
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [Color(0xFF000000), Color(0xFF1A1A1A)],
          ),
        ),
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Icon(Icons.apartment, size: 80, color: Color(0xFFFFD700)),
                const SizedBox(height: 16),
                const Text(
                  'منصة الاستثمار العقاري',
                  style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold, color: Color(0xFFFFD700)),
                  textDirection: TextDirection.rtl,
                ),
                const SizedBox(height: 48),
                Card(
                  child: Padding(
                    padding: const EdgeInsets.all(24),
                    child: Column(
                      children: [
                        TextField(
                          controller: _emailController,
                          decoration: const InputDecoration(
                            labelText: 'البريد الإلكتروني',
                            prefixIcon: Icon(Icons.email),
                          ),
                          textDirection: TextDirection.ltr,
                        ),
                        const SizedBox(height: 16),
                        TextField(
                          controller: _passwordController,
                          decoration: const InputDecoration(
                            labelText: 'كلمة المرور',
                            prefixIcon: Icon(Icons.lock),
                          ),
                          obscureText: true,
                          textDirection: TextDirection.ltr,
                        ),
                        const SizedBox(height: 24),
                        SizedBox(
                          width: double.infinity,
                          child: ElevatedButton(
                            onPressed: _isLoading ? null : _login,
                            child: _isLoading
                                ? const CircularProgressIndicator(color: Colors.black)
                                : const Text('تسجيل الدخول', style: TextStyle(fontSize: 18)),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
'@

Set-Content -Path "lib\screens\login_screen.dart" -Value $loginScreen -Encoding UTF8
Write-Host "✓ login_screen.dart" -ForegroundColor Cyan

# Home Screen
$homeScreen = @'
import 'package:flutter/material.dart';
import '../services/api_service.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final _apiService = ApiService();
  Map<String, dynamic>? _dashboardData;
  List<dynamic> _apartments = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    try {
      final dashboard = await _apiService.getDashboard();
      final apartments = await _apiService.getApartments();
      setState(() {
        _dashboardData = dashboard;
        _apartments = apartments;
        _isLoading = false;
      });
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('خطأ: ${e.toString()}'), backgroundColor: Colors.red),
        );
        setState(() => _isLoading = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('لوحة التحكم', style: TextStyle(color: Color(0xFFFFD700))),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh, color: Color(0xFFFFD700)),
            onPressed: () {
              setState(() => _isLoading = true);
              _loadData();
            },
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator(color: Color(0xFFFFD700)))
          : SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Stats Cards
                  Row(
                    children: [
                      Expanded(
                        child: _StatCard(
                          title: 'رصيد المحفظة',
                          value: '${_dashboardData?['wallet_balance']?.toStringAsFixed(0) ?? '0'} جنيه',
                          icon: Icons.account_balance_wallet,
                        ),
                      ),
                      const SizedBox(width: 16),
                      Expanded(
                        child: _StatCard(
                          title: 'إجمالي الاستثمار',
                          value: '${_dashboardData?['total_invested']?.toStringAsFixed(0) ?? '0'} جنيه',
                          icon: Icons.trending_up,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),
                  Row(
                    children: [
                      Expanded(
                        child: _StatCard(
                          title: 'الدخل الشهري المتوقع',
                          value: '${_dashboardData?['monthly_expected_income']?.toStringAsFixed(0) ?? '0'} جنيه',
                          icon: Icons.attach_money,
                        ),
                      ),
                      const SizedBox(width: 16),
                      Expanded(
                        child: _StatCard(
                          title: 'عدد العقارات',
                          value: '${_dashboardData?['apartments_count'] ?? 0}',
                          icon: Icons.apartment,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 24),
                  const Text(
                    'العقارات المتاحة',
                    style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: Color(0xFFFFD700)),
                    textDirection: TextDirection.rtl,
                  ),
                  const SizedBox(height: 16),
                  // Apartments Grid
                  GridView.builder(
                    shrinkWrap: true,
                    physics: const NeverScrollableScrollPhysics(),
                    gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                      crossAxisCount: 2,
                      childAspectRatio: 0.75,
                      crossAxisSpacing: 16,
                      mainAxisSpacing: 16,
                    ),
                    itemCount: _apartments.length,
                    itemBuilder: (context, index) {
                      final apt = _apartments[index];
                      return Card(
                        child: Padding(
                          padding: const EdgeInsets.all(12),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Container(
                                height: 100,
                                decoration: BoxDecoration(
                                  color: const Color(0xFF2A2A2A),
                                  borderRadius: BorderRadius.circular(8),
                                ),
                                child: const Center(
                                  child: Icon(Icons.apartment, size: 50, color: Color(0xFFFFD700)),
                                ),
                              ),
                              const SizedBox(height: 8),
                              Text(
                                apt['title'] ?? '',
                                style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
                                maxLines: 2,
                                overflow: TextOverflow.ellipsis,
                                textDirection: TextDirection.rtl,
                              ),
                              const Spacer(),
                              Text(
                                '${apt['share_price']?.toStringAsFixed(0)} جنيه/حصة',
                                style: const TextStyle(color: Color(0xFFFFD700), fontSize: 12),
                                textDirection: TextDirection.rtl,
                              ),
                              const SizedBox(height: 4),
                              LinearProgressIndicator(
                                value: (apt['completion_percentage'] ?? 0) / 100,
                                backgroundColor: const Color(0xFF2A2A2A),
                                valueColor: const AlwaysStoppedAnimation<Color>(Color(0xFFFFD700)),
                              ),
                              const SizedBox(height: 4),
                              Text(
                                '${apt['shares_available']} حصة متاحة',
                                style: const TextStyle(fontSize: 11, color: Colors.grey),
                                textDirection: TextDirection.rtl,
                              ),
                            ],
                          ),
                        ),
                      );
                    },
                  ),
                ],
              ),
            ),
    );
  }
}

class _StatCard extends StatelessWidget {
  final String title;
  final String value;
  final IconData icon;

  const _StatCard({required this.title, required this.value, required this.icon});

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Icon(icon, color: const Color(0xFFFFD700), size: 32),
            const SizedBox(height: 8),
            Text(title, style: const TextStyle(fontSize: 12), textDirection: TextDirection.rtl),
            const SizedBox(height: 4),
            Text(value, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Color(0xFFFFD700)), textDirection: TextDirection.rtl),
          ],
        ),
      ),
    );
  }
}
'@

Set-Content -Path "lib\screens\home_screen.dart" -Value $homeScreen -Encoding UTF8
Write-Host "✓ home_screen.dart" -ForegroundColor Cyan

Write-Host "`n✅ IPI Flutter App Code Generated Successfully!" -ForegroundColor Green
Write-Host "`n📝 Files created:" -ForegroundColor Yellow
Write-Host "  - lib/main.dart" -ForegroundColor White
Write-Host "  - lib/services/api_service.dart" -ForegroundColor White
Write-Host "  - lib/screens/login_screen.dart" -ForegroundColor White
Write-Host "  - lib/screens/home_screen.dart" -ForegroundColor White
Write-Host "`n🚀 Next: Stop the current app (press 'q') and run 'flutter run -d edge' again!" -ForegroundColor Cyan
'@

Set-Content -Path "GENERATE_IPI_APP.ps1" -Value $Content -Encoding UTF8
Write-Host "✓ Created IPI app generator script" -ForegroundColor Green
