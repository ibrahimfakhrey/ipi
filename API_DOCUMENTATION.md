# 📱 IPI Platform - REST API Documentation

## Base URL
```
http://localhost:5001/api/v1
```

## Authentication
All protected endpoints require a JWT token in the Authorization header:
```
Authorization: Bearer <your_access_token>
```

---

## 🔐 Authentication Endpoints

### Register New User
**POST** `/auth/register`

**Request Body:**
```json
{
  "name": "أحمد محمد",
  "email": "ahmed@example.com",
  "password": "password123",
  "phone": "01234567890"
}
```

**Response:**
```json
{
  "success": true,
  "message": "تم إنشاء الحساب بنجاح",
  "data": {
    "user": { ... },
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }
}
```

### Login
**POST** `/auth/login`

**Request Body:**
```json
{
  "email": "ahmed@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "success": true,
  "message": "تم تسجيل الدخول بنجاح",
  "data": {
    "user": {
      "id": 1,
      "name": "أحمد محمد",
      "email": "ahmed@example.com",
      "wallet_balance": 500000.0,
      "rewards_balance": 0.0,
      "total_invested": 0.0,
      "monthly_expected_income": 0.0
    },
    "access_token": "...",
    "refresh_token": "..."
  }
}
```

### Get Current User
**GET** `/auth/me`

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "success": true,
  "message": "تم جلب بيانات المستخدم بنجاح",
  "data": {
    "user": { ... }
  }
}
```

### Refresh Token
**POST** `/auth/refresh`

**Headers:** `Authorization: Bearer <refresh_token>`

**Response:**
```json
{
  "success": true,
  "message": "تم تحديث الرمز بنجاح",
  "data": {
    "access_token": "new_access_token_here"
  }
}
```

---

## 🏢 Apartment Endpoints

### List Apartments
**GET** `/apartments?status=available&location=القاهرة&page=1&per_page=10`

**Query Parameters:**
- `status` (optional): `available`, `closed`, `new`
- `location` (optional): Filter by location
- `page` (optional): Page number (default: 1)
- `per_page` (optional): Items per page (default: 10)

**Response:**
```json
{
  "success": true,
  "message": "تم جلب العقارات بنجاح",
  "data": {
    "apartments": [
      {
        "id": 1,
        "title": "شقة فاخرة في التجمع الخامس",
        "description": "...",
        "image": "apartment1.jpg",
        "total_price": 5000000.0,
        "total_shares": 100,
        "shares_available": 45,
        "shares_sold": 55,
        "share_price": 50000.0,
        "monthly_rent": 25000.0,
        "location": "التجمع الخامس",
        "is_closed": false,
        "status": "متاح",
        "completion_percentage": 55.0,
        "investors_count": 12
      }
    ],
    "total": 6,
    "page": 1,
    "per_page": 10,
    "total_pages": 1
  }
}
```

### Get Apartment Details
**GET** `/apartments/<id>`

**Response:**
```json
{
  "success": true,
  "message": "تم جلب تفاصيل العقار بنجاح",
  "data": {
    "apartment": {
      "id": 1,
      "title": "...",
      "images": ["image1.jpg", "image2.jpg"],
      ...
    }
  }
}
```

---

## 💰 Investment/Shares Endpoints

### Purchase Shares
**POST** `/shares/purchase`

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "apartment_id": 1,
  "num_shares": 5
}
```

**Response:**
```json
{
  "success": true,
  "message": "تم شراء الحصص بنجاح",
  "data": {
    "new_balance": 250000.0,
    "shares_purchased": 5,
    "total_cost": 250000.0,
    "apartment": { ... }
  }
}
```

### Get My Investments
**GET** `/shares/my-investments`

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "success": true,
  "message": "تم جلب الاستثمارات بنجاح",
  "data": {
    "investments": [
      {
        "apartment": { ... },
        "shares_owned": 5,
        "total_invested": 250000.0,
        "monthly_income": 1250.0
      }
    ],
    "total_invested": 250000.0,
    "monthly_expected_income": 1250.0,
    "total_apartments": 1
  }
}
```

---

## 💼 Wallet Endpoints

### Get Wallet Balance
**GET** `/wallet/balance`

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "success": true,
  "message": "تم جلب الرصيد بنجاح",
  "data": {
    "wallet_balance": 500000.0,
    "rewards_balance": 0.0,
    "total_balance": 500000.0
  }
}
```

### Deposit Money
**POST** `/wallet/deposit`

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "amount": 10000
}
```

**Response:**
```json
{
  "success": true,
  "message": "تم الإيداع بنجاح",
  "data": {
    "new_balance": 510000.0,
    "amount_deposited": 10000.0
  }
}
```

### Withdraw Money
**POST** `/wallet/withdraw`

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "amount": 5000
}
```

**Response:**
```json
{
  "success": true,
  "message": "تم السحب بنجاح",
  "data": {
    "new_balance": 505000.0,
    "amount_withdrawn": 5000.0
  }
}
```

### Get Transaction History
**GET** `/wallet/transactions?page=1&per_page=20`

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "success": true,
  "message": "تم جلب المعاملات بنجاح",
  "data": {
    "transactions": [
      {
        "id": 1,
        "amount": -250000.0,
        "transaction_type": "share_purchase",
        "type_arabic": "شراء حصة",
        "date": "2025-11-22T14:30:00",
        "description": null
      }
    ],
    "total": 10,
    "page": 1,
    "per_page": 20,
    "total_pages": 1
  }
}
```

---

## 👤 User Endpoints

### Get Dashboard Data
**GET** `/user/dashboard`

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "success": true,
  "message": "تم جلب بيانات لوحة التحكم بنجاح",
  "data": {
    "user": { ... },
    "wallet_balance": 500000.0,
    "rewards_balance": 0.0,
    "total_invested": 250000.0,
    "monthly_expected_income": 1250.0,
    "apartments_count": 1,
    "total_shares": 5,
    "recent_transactions": [ ... ]
  }
}
```

### Update Profile
**PUT** `/user/profile`

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "name": "أحمد محمد الجديد",
  "phone": "01234567890"
}
```

**Response:**
```json
{
  "success": true,
  "message": "تم تحديث الملف الشخصي بنجاح",
  "data": {
    "user": { ... }
  }
}
```

---

## ❌ Error Responses

All errors follow this format:

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "رسالة الخطأ بالعربية",
    "details": { ... }
  }
}
```

### Common Error Codes
- `MISSING_FIELDS` - Required fields missing
- `EMAIL_EXISTS` - Email already registered
- `INVALID_CREDENTIALS` - Wrong email/password
- `USER_NOT_FOUND` - User doesn't exist
- `APARTMENT_NOT_FOUND` - Apartment doesn't exist
- `INSUFFICIENT_BALANCE` - Not enough money in wallet
- `PURCHASE_FAILED` - Share purchase failed
- `INVALID_AMOUNT` - Invalid amount value

---

## 🧪 Testing with cURL

### Register
```bash
curl -X POST http://localhost:5001/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name":"أحمد","email":"test@test.com","password":"pass123"}'
```

### Login
```bash
curl -X POST http://localhost:5001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"pass123"}'
```

### Get Apartments (with token)
```bash
curl -X GET http://localhost:5001/api/v1/apartments \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Purchase Shares
```bash
curl -X POST http://localhost:5001/api/v1/shares/purchase \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"apartment_id":1,"num_shares":2}'
```

---

## 📱 Flutter Integration Example

```dart
import 'package:http/http.dart' as http;
import 'dart:convert';

class ApiService {
  final String baseUrl = 'http://YOUR_IP:5001/api/v1';
  String? _token;

  Future<Map<String, dynamic>> login(String email, String password) async {
    final response = await http.post(
      Uri.parse('$baseUrl/auth/login'),
      headers: {'Content-Type': 'application/json'},
      body: json.encode({'email': email, 'password': password}),
    );

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      _token = data['data']['access_token'];
      return data;
    }
    throw Exception('Login failed');
  }

  Future<List<dynamic>> getApartments() async {
    final response = await http.get(
      Uri.parse('$baseUrl/apartments'),
      headers: {'Authorization': 'Bearer $_token'},
    );

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      return data['data']['apartments'];
    }
    throw Exception('Failed to load apartments');
  }
}
```
