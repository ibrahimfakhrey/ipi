@echo off
echo Fixing Dashboard and Colors...

REM Create improved home_screen.dart with better error handling
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
echo   String? _error;
echo.
echo   @override
echo   void initState^(^) {
echo     super.initState^(^);
echo     _loadData^(^);
echo   }
echo.
echo   Future^<void^> _loadData^(^) async {
echo     setState^(^(^) =^> _isLoading = true^);
echo     try {
echo       final dashboard = await _apiService.getDashboard^(^);
echo       final apartments = await _apiService.getApartments^(^);
echo       setState^(^(^) {
echo         _data = {...dashboard, 'apartments': apartments};
echo         _isLoading = false;
echo         _error = null;
echo       }^);
echo     } catch ^(e^) {
echo       setState^(^(^) {
echo         _error = e.toString^(^);
echo         _isLoading = false;
echo       }^);
echo     }
echo   }
echo.
echo   @override
echo   Widget build^(BuildContext context^) {
echo     return Scaffold^(
echo       appBar: AppBar^(
echo         title: const Text^('Dashboard', style: TextStyle^(color: Color^(0xFFFFD700^), fontWeight: FontWeight.bold^)^),
echo         backgroundColor: const Color^(0xFF1A1A1A^),
echo         actions: [IconButton^(icon: const Icon^(Icons.refresh, color: Color^(0xFFFFD700^)^), onPressed: _loadData^)],
echo       ^),
echo       backgroundColor: const Color^(0xFF000000^),
echo       body: _isLoading ? const Center^(child: CircularProgressIndicator^(color: Color^(0xFFFFD700^)^)^) : _error != null ? Center^(
echo         child: Column^(
echo           mainAxisAlignment: MainAxisAlignment.center,
echo           children: [
echo             const Icon^(Icons.error_outline, size: 60, color: Color^(0xFFFFD700^)^),
echo             const SizedBox^(height: 16^),
echo             Text^('Connection Error', style: const TextStyle^(fontSize: 20, color: Color^(0xFFFFD700^)^)^),
echo             const SizedBox^(height: 8^),
echo             Padding^(padding: const EdgeInsets.all^(16^), child: Text^(_error!, textAlign: TextAlign.center, style: const TextStyle^(color: Colors.white70^)^)^),
echo             const SizedBox^(height: 16^),
echo             ElevatedButton^(onPressed: _loadData, style: ElevatedButton.styleFrom^(backgroundColor: const Color^(0xFFFFD700^)^), child: const Text^('Retry', style: TextStyle^(color: Colors.black^)^)^),
echo           ],
echo         ^),
echo       ^) : SingleChildScrollView^(
echo         padding: const EdgeInsets.all^(16^),
echo         child: Column^(
echo           crossAxisAlignment: CrossAxisAlignment.start,
echo           children: [
echo             Row^(children: [
echo               Expanded^(child: _buildStatCard^('Wallet', '${_data?['wallet_balance'] ?? 0}', Icons.account_balance_wallet^)^),
echo               const SizedBox^(width: 12^),
echo               Expanded^(child: _buildStatCard^('Invested', '${_data?['total_invested'] ?? 0}', Icons.trending_up^)^),
echo             ]^),
echo             const SizedBox^(height: 12^),
echo             Row^(children: [
echo               Expanded^(child: _buildStatCard^('Monthly', '${_data?['monthly_expected_income'] ?? 0}', Icons.attach_money^)^),
echo               const SizedBox^(width: 12^),
echo               Expanded^(child: _buildStatCard^('Apartments', '${^(_data?['apartments'] as List?^)?.length ?? 0}', Icons.apartment^)^),
echo             ]^),
echo             const SizedBox^(height: 24^),
echo             const Text^('Available Apartments', style: TextStyle^(fontSize: 22, fontWeight: FontWeight.bold, color: Color^(0xFFFFD700^)^)^),
echo             const SizedBox^(height: 12^),
echo             ...^(_data?['apartments'] as List? ?? []^).map^(^(apt^) =^> Card^(
echo               color: const Color^(0xFF1A1A1A^),
echo               margin: const EdgeInsets.only^(bottom: 12^),
echo               child: ListTile^(
echo                 leading: const Icon^(Icons.apartment, color: Color^(0xFFFFD700^), size: 40^),
echo                 title: Text^(apt['title'] ?? '', style: const TextStyle^(color: Colors.white, fontWeight: FontWeight.bold^)^),
echo                 subtitle: Text^('Price: ${apt['share_price']} - Available: ${apt['shares_available']}', style: const TextStyle^(color: Colors.white70^)^),
echo                 trailing: const Icon^(Icons.arrow_forward_ios, color: Color^(0xFFFFD700^), size: 16^),
echo               ^),
echo             ^)^),
echo           ],
echo         ^),
echo       ^),
echo     ^);
echo   }
echo.
echo   Widget _buildStatCard^(String title, String value, IconData icon^) {
echo     return Card^(
echo       color: const Color^(0xFF1A1A1A^),
echo       child: Padding^(
echo         padding: const EdgeInsets.all^(16^),
echo         child: Column^(
echo           children: [
echo             Icon^(icon, color: const Color^(0xFFFFD700^), size: 32^),
echo             const SizedBox^(height: 8^),
echo             Text^(title, style: const TextStyle^(fontSize: 12, color: Colors.white70^)^),
echo             const SizedBox^(height: 4^),
echo             Text^(value, style: const TextStyle^(fontSize: 16, fontWeight: FontWeight.bold, color: Color^(0xFFFFD700^)^), maxLines: 1, overflow: TextOverflow.ellipsis^),
echo           ],
echo         ^),
echo       ^),
echo     ^);
echo   }
echo }
) > lib\screens\home_screen.dart

echo ✓ Updated home_screen.dart with Black ^& Gold theme and better error handling
echo.
echo Press 'R' in Flutter to reload!
pause
