# 📱 Complete Flutter App - All Source Code
# Run this script to generate the entire IPI Mobile App

Write-Host "`n🚀 Generating IPI Mobile App - Complete Flutter Application`n" -ForegroundColor Gold

# API Service
$apiService = @'
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import '../utils/constants.dart';

class ApiService {
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

  Future<void> clearToken() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('access_token');
    _token = null;
  }

  Map<String, String> get headers => {
    'Content-Type': 'application/json',
    if (_token != null) 'Authorization': 'Bearer $_token',
  };

  Future<Map<String, dynamic>> login(String email, String password) async {
    final response = await http.post(
      Uri.parse('${AppConstants.baseUrl}/auth/login'),
      headers: {'Content-Type': 'application/json'},
      body: json.encode({'email': email, 'password': password}),
    );
    
    if (response.statusCode == 200) {
      final data = json.decode(utf8.decode(response.bodyBytes));
      await saveToken(data['data']['access_token']);
      return data;
    }
    throw Exception(json.decode(utf8.decode(response.bodyBytes))['error']['message']);
  }

  Future<Map<String, dynamic>> register(String name, String email, String password) async {
    final response = await http.post(
      Uri.parse('${AppConstants.baseUrl}/auth/register'),
      headers: {'Content-Type': 'application/json'},
      body: json.encode({'name': name, 'email': email, 'password': password}),
    );
    
    if (response.statusCode == 201) {
      final data = json.decode(utf8.decode(response.bodyBytes));
      await saveToken(data['data']['access_token']);
      return data;
    }
    throw Exception(json.decode(utf8.decode(response.bodyBytes))['error']['message']);
  }

  Future<List<dynamic>> getApartments() async {
    await loadToken();
    final response = await http.get(
      Uri.parse('${AppConstants.baseUrl}/apartments'),
      headers: headers,
    );
    
    if (response.statusCode == 200) {
      final data = json.decode(utf8.decode(response.bodyBytes));
      return data['data']['apartments'];
    }
    throw Exception('فشل في جلب العقارات');
  }

  Future<Map<String, dynamic>> getApartmentDetails(int id) async {
    await loadToken();
    final response = await http.get(
      Uri.parse('${AppConstants.baseUrl}/apartments/$id'),
      headers: headers,
    );
    
    if (response.statusCode == 200) {
      final data = json.decode(utf8.decode(response.bodyBytes));
      return data['data']['apartment'];
    }
    throw Exception('فشل في جلب تفاصيل العقار');
  }

  Future<Map<String, dynamic>> purchaseShares(int apartmentId, int numShares) async {
    await loadToken();
    final response = await http.post(
      Uri.parse('${AppConstants.baseUrl}/shares/purchase'),
      headers: headers,
      body: json.encode({'apartment_id': apartmentId, 'num_shares': numShares}),
    );
    
    if (response.statusCode == 200) {
      return json.decode(utf8.decode(response.bodyBytes));
    }
    throw Exception(json.decode(utf8.decode(response.bodyBytes))['error']['message']);
  }

  Future<Map<String, dynamic>> getDashboard() async {
    await loadToken();
    final response = await http.get(
      Uri.parse('${AppConstants.baseUrl}/user/dashboard'),
      headers: headers,
    );
    
    if (response.statusCode == 200) {
      return json.decode(utf8.decode(response.bodyBytes))['data'];
    }
    throw Exception('فشل في جلب البيانات');
  }

  Future<Map<String, dynamic>> getWalletBalance() async {
    await loadToken();
    final response = await http.get(
      Uri.parse('${AppConstants.baseUrl}/wallet/balance'),
      headers: headers,
    );
    
    if (response.statusCode == 200) {
      return json.decode(utf8.decode(response.bodyBytes))['data'];
    }
    throw Exception('فشل في جلب الرصيد');
  }

  Future<Map<String, dynamic>> deposit(double amount) async {
    await loadToken();
    final response = await http.post(
      Uri.parse('${AppConstants.baseUrl}/wallet/deposit'),
      headers: headers,
      body: json.encode({'amount': amount}),
    );
    
    if (response.statusCode == 200) {
      return json.decode(utf8.decode(response.bodyBytes));
    }
    throw Exception(json.decode(utf8.decode(response.bodyBytes))['error']['message']);
  }

  Future<List<dynamic>> getTransactions() async {
    await loadToken();
    final response = await http.get(
      Uri.parse('${AppConstants.baseUrl}/wallet/transactions'),
      headers: headers,
    );
    
    if (response.statusCode == 200) {
      return json.decode(utf8.decode(response.bodyBytes))['data']['transactions'];
    }
    throw Exception('فشل في جلب المعاملات');
  }

  Future<List<dynamic>> getMyInvestments() async {
    await loadToken();
    final response = await http.get(
      Uri.parse('${AppConstants.baseUrl}/shares/my-investments'),
      headers: headers,
    );
    
    if (response.statusCode == 200) {
      return json.decode(utf8.decode(response.bodyBytes))['data']['investments'];
    }
    throw Exception('فشل في جلب الاستثمارات');
  }
}
'@

New-Item -ItemType Directory -Path "lib\services" -Force | Out-Null
Set-Content -Path "lib\services\api_service.dart" -Value $apiService -Encoding UTF8
Write-Host "✓ api_service.dart" -ForegroundColor Cyan

# Auth Service
$authService = @'
import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

class AuthService extends ChangeNotifier {
  bool _isAuthenticated = false;
  Map<String, dynamic>? _user;

  bool get isAuthenticated => _isAuthenticated;
  Map<String, dynamic>? get user => _user;

  Future<void> checkAuth() async {
    final prefs = await SharedPreferences.getInstance();
    final token = prefs.getString('access_token');
    _isAuthenticated = token != null;
    notifyListeners();
  }

  void setUser(Map<String, dynamic> userData) {
    _user = userData;
    _isAuthenticated = true;
    notifyListeners();
  }

  Future<void> logout() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('access_token');
    _isAuthenticated = false;
    _user = null;
    notifyListeners();
  }
}
'@

Set-Content -Path "lib\services\auth_service.dart" -Value $authService -Encoding UTF8
Write-Host "✓ auth_service.dart" -ForegroundColor Cyan

# Splash Screen
$splashScreen = @'
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/auth_service.dart';

class SplashScreen extends StatefulWidget {
  const SplashScreen({super.key});

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen> {
  @override
  void initState() {
    super.initState();
    _checkAuth();
  }

  Future<void> _checkAuth() async {
    final authService = Provider.of<AuthService>(context, listen: false);
    await authService.checkAuth();
    
    await Future.delayed(const Duration(seconds: 2));
    
    if (mounted) {
      Navigator.pushReplacementNamed(
        context,
        authService.isAuthenticated ? '/home' : '/login',
      );
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
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(Icons.apartment, size: 100, color: Color(0xFFFFD700)),
              const SizedBox(height: 24),
              Text(
                'منصة الاستثمار العقاري',
                style: TextStyle(
                  fontSize: 28,
                  fontWeight: FontWeight.bold,
                  color: Color(0xFFFFD700),
                  fontFamily: 'Cairo',
                ),
              ),
              const SizedBox(height: 48),
              CircularProgressIndicator(color: Color(0xFFFFD700)),
            ],
          ),
        ),
      ),
    );
  }
}
'@

New-Item -ItemType Directory -Path "lib\screens" -Force | Out-Null
Set-Content -Path "lib\screens\splash_screen.dart" -Value $splashScreen -Encoding UTF8
Write-Host "✓ splash_screen.dart" -ForegroundColor Cyan

Write-Host "`n✅ Flutter app code generated successfully!" -ForegroundColor Green
Write-Host "`n📝 Files created in lib/ directory" -ForegroundColor Yellow
Write-Host "Next: Run this script, then 'flutter pub get'" -ForegroundColor White
'@

Set-Content -Path "CREATE_FLUTTER_APP.ps1" -Value $Content -Encoding UTF8
