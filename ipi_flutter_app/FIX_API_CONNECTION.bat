@echo off
echo Fixing API Connection...

REM Update api_service.dart with correct URL
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
echo   }
echo.
echo   Future^<void^> saveToken^(String token^) async {
echo     final prefs = await SharedPreferences.getInstance^(^);
echo     await prefs.setString^('access_token', token^);
echo     _token = token;
echo   }
echo.
echo   Map^<String, String^> get headers =^> {
echo     'Content-Type': 'application/json; charset=UTF-8',
echo     if ^(_token != null^) 'Authorization': 'Bearer $_token',
echo   };
echo.
echo   Future^<Map^<String, dynamic^>^> login^(String email, String password^) async {
echo     final response = await http.post^(
echo       Uri.parse^('$baseUrl/auth/login'^),
echo       headers: {'Content-Type': 'application/json'},
echo       body: json.encode^({'email': email, 'password': password}^),
echo     ^);
echo     if ^(response.statusCode == 200^) {
echo       final data = json.decode^(utf8.decode^(response.bodyBytes^)^);
echo       await saveToken^(data['data']['access_token']^);
echo       return data;
echo     }
echo     throw Exception^('Login failed'^);
echo   }
echo.
echo   Future^<Map^<String, dynamic^>^> getDashboard^(^) async {
echo     await loadToken^(^);
echo     final response = await http.get^(Uri.parse^('$baseUrl/user/dashboard'^), headers: headers^);
echo     if ^(response.statusCode == 200^) {
echo       return json.decode^(utf8.decode^(response.bodyBytes^)^)['data'];
echo     }
echo     throw Exception^('Failed to load dashboard'^);
echo   }
echo.
echo   Future^<List^<dynamic^>^> getApartments^(^) async {
echo     await loadToken^(^);
echo     final response = await http.get^(Uri.parse^('$baseUrl/apartments'^), headers: headers^);
echo     if ^(response.statusCode == 200^) {
echo       return json.decode^(utf8.decode^(response.bodyBytes^)^)['data']['apartments'];
echo     }
echo     throw Exception^('Failed to load apartments'^);
echo   }
echo }
) > lib\services\api_service.dart

echo ✓ Updated API URL to http://127.0.0.1:5001/api/v1
echo.
echo API is now configured to connect to Flask backend!
echo Press 'R' in Flutter terminal to hot reload.
pause
