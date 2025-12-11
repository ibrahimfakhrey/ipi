@echo off
echo Fixing JWT Token Authentication...

REM Update api_service.dart with proper token handling
(
echo import 'dart:convert';
echo import 'package:http/http.dart' as http;
echo import 'package:shared_preferences/shared_preferences.dart';
echo.
echo class ApiService {
echo   static const String baseUrl = 'http://127.0.0.1:5001/api/v1';
echo   String? _token;
echo.
echo   Future^<void^> loadToken^(^) async {
echo     final prefs = await SharedPreferences.getInstance^(^);
echo     _token = prefs.getString^('access_token'^);
echo     print^('Loaded token: ${_token?.substring^(0, 20^)}...'^);
echo   }
echo.
echo   Future^<void^> saveToken^(String token^) async {
echo     final prefs = await SharedPreferences.getInstance^(^);
echo     await prefs.setString^('access_token', token^);
echo     _token = token;
echo     print^('Saved token: ${token.substring^(0, 20^)}...'^);
echo   }
echo.
echo   Map^<String, String^> get headers =^> {
echo     'Content-Type': 'application/json; charset=UTF-8',
echo     if ^(_token != null^) 'Authorization': 'Bearer $_token',
echo   };
echo.
echo   Future^<Map^<String, dynamic^>^> login^(String email, String password^) async {
echo     try {
echo       final response = await http.post^(
echo         Uri.parse^('$baseUrl/auth/login'^),
echo         headers: {'Content-Type': 'application/json; charset=UTF-8'},
echo         body: json.encode^({'email': email, 'password': password}^),
echo       ^);
echo       print^('Login response: ${response.statusCode}'^);
echo       if ^(response.statusCode == 200^) {
echo         final data = json.decode^(utf8.decode^(response.bodyBytes^)^);
echo         final token = data['data']['access_token'];
echo         await saveToken^(token^);
echo         return data;
echo       }
echo       throw Exception^('Login failed: ${response.statusCode}'^);
echo     } catch ^(e^) {
echo       print^('Login error: $e'^);
echo       rethrow;
echo     }
echo   }
echo.
echo   Future^<Map^<String, dynamic^>^> getDashboard^(^) async {
echo     try {
echo       await loadToken^(^);
echo       if ^(_token == null^) throw Exception^('No token found. Please login first.'^);
echo       final response = await http.get^(
echo         Uri.parse^('$baseUrl/user/dashboard'^),
echo         headers: headers,
echo       ^);
echo       print^('Dashboard response: ${response.statusCode}'^);
echo       if ^(response.statusCode == 200^) {
echo         return json.decode^(utf8.decode^(response.bodyBytes^)^)['data'];
echo       }
echo       throw Exception^('Dashboard failed: ${response.statusCode} - ${response.body}'^);
echo     } catch ^(e^) {
echo       print^('Dashboard error: $e'^);
echo       rethrow;
echo     }
echo   }
echo.
echo   Future^<List^<dynamic^>^> getApartments^(^) async {
echo     try {
echo       await loadToken^(^);
echo       if ^(_token == null^) throw Exception^('No token found'^);
echo       final response = await http.get^(
echo         Uri.parse^('$baseUrl/apartments'^),
echo         headers: headers,
echo       ^);
echo       print^('Apartments response: ${response.statusCode}'^);
echo       if ^(response.statusCode == 200^) {
echo         return json.decode^(utf8.decode^(response.bodyBytes^)^)['data']['apartments'];
echo       }
echo       throw Exception^('Apartments failed: ${response.statusCode}'^);
echo     } catch ^(e^) {
echo       print^('Apartments error: $e'^);
echo       rethrow;
echo     }
echo   }
echo }
) > lib\services\api_service.dart

echo ✓ Updated API service with proper JWT token handling
echo.
echo Press 'R' in Flutter to reload and try logging in again!
pause
