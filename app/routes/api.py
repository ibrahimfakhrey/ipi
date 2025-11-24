"""
REST API Blueprint for Mobile App
Provides JWT-authenticated endpoints for Flutter mobile application
Version: v1
Language: Arabic
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity, get_jwt
)
from app.models import db, User, Apartment, Share, Transaction, ApartmentImage, Car, CarShare, InvestmentRequest, ReferralTree
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash
import os

# Create API blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api/v1')


# ==================== Helper Functions ====================

def success_response(data=None, message="نجح", status=200):
    """Standard success response format"""
    response = {
        "success": True,
        "message": message
    }
    if data is not None:
        response["data"] = data
    return jsonify(response), status


def error_response(message="حدث خطأ", code="ERROR", details=None, status=400):
    """Standard error response format"""
    response = {
        "success": False,
        "error": {
            "code": code,
            "message": message
        }
    }
    if details:
        response["error"]["details"] = details
    return jsonify(response), status


def serialize_user(user):
    """Convert User object to dictionary"""
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "wallet_balance": user.wallet_balance,
        "rewards_balance": user.rewards_balance,
        "is_admin": user.is_admin,
        "date_joined": user.date_joined.isoformat() if user.date_joined else None,
        "phone": user.phone,
        "total_invested": user.get_total_invested(),
        "monthly_expected_income": user.get_monthly_expected_income()
    }


def serialize_apartment(apartment, include_images=False):
    """Convert Apartment object to dictionary"""
    data = {
        "id": apartment.id,
        "title": apartment.title,
        "description": apartment.description,
        "image": apartment.image,
        "total_price": apartment.total_price,
        "total_shares": apartment.total_shares,
        "shares_available": apartment.shares_available,
        "shares_sold": apartment.shares_sold,
        "share_price": apartment.share_price,
        "monthly_rent": apartment.monthly_rent,
        "location": apartment.location,
        "is_closed": apartment.is_closed,
        "status": apartment.status,
        "completion_percentage": apartment.completion_percentage,
        "investors_count": apartment.investors_count,
        "date_created": apartment.date_created.isoformat() if apartment.date_created else None,
        "last_payout_date": apartment.last_payout_date.isoformat() if apartment.last_payout_date else None
    }
    
    if include_images:
        data["images"] = apartment.images
    
    return data


def serialize_transaction(transaction):
    """Convert Transaction object to dictionary"""
    return {
        "id": transaction.id,
        "amount": transaction.amount,
        "transaction_type": transaction.transaction_type,
        "type_arabic": transaction.type_arabic,
        "date": transaction.date.isoformat() if transaction.date else None,
        "description": transaction.description
    }


def serialize_share(share):
    """Convert Share object to dictionary"""
    return {
        "id": share.id,
        "apartment_id": share.apartment_id,
        "apartment_title": share.apartment.title if share.apartment else None,
        "share_price": share.share_price,
        "date_purchased": share.date_purchased.isoformat() if share.date_purchased else None,
        "monthly_income": share.apartment.monthly_rent / share.apartment.total_shares if share.apartment else 0
    }


# ==================== Authentication Endpoints ====================

@api_bp.route('/auth/register', methods=['POST'])
def register():
    """
    Register new user account
    POST /api/v1/auth/register
    Body: {
        "name": "أحمد محمد",
        "email": "ahmed@example.com",
        "password": "password123",
        "phone": "01234567890" (optional)
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or not data.get('email') or not data.get('password') or not data.get('name'):
            return error_response(
                message="البريد الإلكتروني والاسم وكلمة المرور مطلوبة",
                code="MISSING_FIELDS"
            )
        
        # Check if user already exists
        if User.query.filter_by(email=data['email']).first():
            return error_response(
                message="البريد الإلكتروني مستخدم بالفعل",
                code="EMAIL_EXISTS",
                status=409
            )
        
        # Create new user
        user = User(
            name=data['name'],
            email=data['email'],
            phone=data.get('phone'),
            wallet_balance=500000.0  # Default starting balance
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        # Create JWT tokens
        access_token = create_access_token(identity=str(user.id), expires_delta=timedelta(days=7))
        refresh_token = create_refresh_token(identity=str(user.id), expires_delta=timedelta(days=30))
        
        return success_response(
            data={
                "user": serialize_user(user),
                "access_token": access_token,
                "refresh_token": refresh_token
            },
            message="تم إنشاء الحساب بنجاح",
            status=201
        )
        
    except Exception as e:
        db.session.rollback()
        return error_response(
            message="حدث خطأ أثناء إنشاء الحساب",
            code="REGISTRATION_ERROR",
            details=str(e),
            status=500
        )


@api_bp.route('/auth/login', methods=['POST'])
def login():
    """
    User login
    POST /api/v1/auth/login
    Body: {
        "email": "ahmed@example.com",
        "password": "password123"
    }
    """
    try:
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('password'):
            return error_response(
                message="البريد الإلكتروني وكلمة المرور مطلوبة",
                code="MISSING_CREDENTIALS"
            )
        
        # Find user
        user = User.query.filter_by(email=data['email']).first()
        
        if not user or not user.check_password(data['password']):
            return error_response(
                message="البريد الإلكتروني أو كلمة المرور غير صحيحة",
                code="INVALID_CREDENTIALS",
                status=401
            )
        
        # Create JWT tokens
        access_token = create_access_token(identity=str(user.id), expires_delta=timedelta(days=7))
        refresh_token = create_refresh_token(identity=str(user.id), expires_delta=timedelta(days=30))
        
        return success_response(
            data={
                "user": serialize_user(user),
                "access_token": access_token,
                "refresh_token": refresh_token
            },
            message="تم تسجيل الدخول بنجاح"
        )
        
    except Exception as e:
        return error_response(
            message="حدث خطأ أثناء تسجيل الدخول",
            code="LOGIN_ERROR",
            details=str(e),
            status=500
        )


@api_bp.route('/auth/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """
    Get current authenticated user info
    GET /api/v1/auth/me
    Headers: Authorization: Bearer <token>
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        if not user:
            return error_response(
                message="المستخدم غير موجود",
                code="USER_NOT_FOUND",
                status=404
            )
        
        return success_response(
            data={"user": serialize_user(user)},
            message="تم جلب بيانات المستخدم بنجاح"
        )
        
    except Exception as e:
        return error_response(
            message="حدث خطأ أثناء جلب البيانات",
            code="FETCH_ERROR",
            details=str(e),
            status=500
        )


@api_bp.route('/auth/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """
    Refresh access token
    POST /api/v1/auth/refresh
    Headers: Authorization: Bearer <refresh_token>
    """
    try:
        user_id = get_jwt_identity()
        access_token = create_access_token(identity=str(user_id), expires_delta=timedelta(days=7))
        
        return success_response(
            data={"access_token": access_token},
            message="تم تحديث الرمز بنجاح"
        )
        
    except Exception as e:
        return error_response(
            message="حدث خطأ أثناء تحديث الرمز",
            code="REFRESH_ERROR",
            details=str(e),
            status=500
        )


# ==================== Apartment Endpoints ====================

@api_bp.route('/apartments', methods=['GET'])
def get_apartments():
    """
    Get list of apartments with optional filters
    GET /api/v1/apartments?status=available&location=القاهرة&page=1&per_page=10
    """
    try:
        # Get query parameters
        status = request.args.get('status')  # 'available', 'closed', 'new'
        location = request.args.get('location')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Build query
        query = Apartment.query
        
        # Apply filters
        if status == 'available':
            query = query.filter(Apartment.is_closed == False, Apartment.shares_available > 0)
        elif status == 'closed':
            query = query.filter(Apartment.is_closed == True)
        elif status == 'new':
            query = query.filter(Apartment.shares_available == Apartment.total_shares)
        
        if location:
            query = query.filter(Apartment.location.contains(location))
        
        # Paginate
        pagination = query.order_by(Apartment.date_created.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        apartments = [serialize_apartment(apt, include_images=True) for apt in pagination.items]
        
        return success_response(
            data={
                "apartments": apartments,
                "total": pagination.total,
                "page": page,
                "per_page": per_page,
                "total_pages": pagination.pages
            },
            message="تم جلب العقارات بنجاح"
        )
        
    except Exception as e:
        return error_response(
            message="حدث خطأ أثناء جلب العقارات",
            code="FETCH_ERROR",
            details=str(e),
            status=500
        )


@api_bp.route('/apartments/<int:apartment_id>', methods=['GET'])
def get_apartment_details(apartment_id):
    """
    Get apartment details by ID
    GET /api/v1/apartments/1
    """
    try:
        apartment = Apartment.query.get(apartment_id)
        
        if not apartment:
            return error_response(
                message="العقار غير موجود",
                code="APARTMENT_NOT_FOUND",
                status=404
            )
        
        return success_response(
            data={"apartment": serialize_apartment(apartment, include_images=True)},
            message="تم جلب تفاصيل العقار بنجاح"
        )
        
    except Exception as e:
        return error_response(
            message="حدث خطأ أثناء جلب التفاصيل",
            code="FETCH_ERROR",
            details=str(e),
            status=500
        )


# ==================== Investment/Shares Endpoints ====================

@api_bp.route('/shares/purchase', methods=['POST'])
@jwt_required()
def purchase_shares():
    """
    Purchase shares in an apartment
    POST /api/v1/shares/purchase
    Headers: Authorization: Bearer <token>
    Body: {
        "apartment_id": 1,
        "num_shares": 5
    }
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        if not user:
            return error_response(
                message="المستخدم غير موجود",
                code="USER_NOT_FOUND",
                status=404
            )
        
        data = request.get_json()
        
        if not data or not data.get('apartment_id') or not data.get('num_shares'):
            return error_response(
                message="معرف العقار وعدد الحصص مطلوبة",
                code="MISSING_FIELDS"
            )
        
        apartment_id = data['apartment_id']
        num_shares = data['num_shares']
        
        # Validate num_shares
        if num_shares <= 0:
            return error_response(
                message="عدد الحصص يجب أن يكون أكبر من صفر",
                code="INVALID_SHARES"
            )
        
        # Get apartment
        apartment = Apartment.query.get(apartment_id)
        
        if not apartment:
            return error_response(
                message="العقار غير موجود",
                code="APARTMENT_NOT_FOUND",
                status=404
            )
        
        # Attempt purchase
        success, message = apartment.purchase_shares(user, num_shares)
        
        if not success:
            return error_response(
                message=message,
                code="PURCHASE_FAILED"
            )
        
        db.session.commit()
        
        return success_response(
            data={
                "new_balance": user.wallet_balance,
                "shares_purchased": num_shares,
                "total_cost": apartment.share_price * num_shares,
                "apartment": serialize_apartment(apartment)
            },
            message="تم شراء الحصص بنجاح"
        )
        
    except Exception as e:
        db.session.rollback()
        return error_response(
            message="حدث خطأ أثناء شراء الحصص",
            code="PURCHASE_ERROR",
            details=str(e),
            status=500
        )


@api_bp.route('/shares/my-investments', methods=['GET'])
@jwt_required()
def get_my_investments():
    """
    Get user's investment portfolio
    GET /api/v1/shares/my-investments
    Headers: Authorization: Bearer <token>
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        if not user:
            return error_response(
                message="المستخدم غير موجود",
                code="USER_NOT_FOUND",
                status=404
            )
        
        # Get all shares grouped by apartment
        shares_by_apartment = {}
        for share in user.shares:
            apt_id = share.apartment_id
            if apt_id not in shares_by_apartment:
                shares_by_apartment[apt_id] = {
                    "apartment": serialize_apartment(share.apartment),
                    "shares_owned": 0,
                    "total_invested": 0,
                    "monthly_income": 0
                }
            shares_by_apartment[apt_id]["shares_owned"] += 1
            shares_by_apartment[apt_id]["total_invested"] += share.share_price
            if share.apartment:
                shares_by_apartment[apt_id]["monthly_income"] += share.apartment.monthly_rent / share.apartment.total_shares
        
        investments = list(shares_by_apartment.values())
        
        return success_response(
            data={
                "investments": investments,
                "total_invested": user.get_total_invested(),
                "monthly_expected_income": user.get_monthly_expected_income(),
                "total_apartments": len(investments)
            },
            message="تم جلب الاستثمارات بنجاح"
        )
        
    except Exception as e:
        return error_response(
            message="حدث خطأ أثناء جلب الاستثمارات",
            code="FETCH_ERROR",
            details=str(e),
            status=500
        )


# ==================== Wallet Endpoints ====================

@api_bp.route('/wallet/balance', methods=['GET'])
@jwt_required()
def get_wallet_balance():
    """
    Get user's wallet balance
    GET /api/v1/wallet/balance
    Headers: Authorization: Bearer <token>
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        if not user:
            return error_response(
                message="المستخدم غير موجود",
                code="USER_NOT_FOUND",
                status=404
            )
        
        return success_response(
            data={
                "wallet_balance": user.wallet_balance,
                "rewards_balance": user.rewards_balance,
                "total_balance": user.wallet_balance + user.rewards_balance
            },
            message="تم جلب الرصيد بنجاح"
        )
        
    except Exception as e:
        return error_response(
            message="حدث خطأ أثناء جلب الرصيد",
            code="FETCH_ERROR",
            details=str(e),
            status=500
        )


@api_bp.route('/wallet/deposit', methods=['POST'])
@jwt_required()
def deposit_to_wallet():
    """
    Deposit money to wallet
    POST /api/v1/wallet/deposit
    Headers: Authorization: Bearer <token>
    Body: {
        "amount": 10000
    }
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        if not user:
            return error_response(
                message="المستخدم غير موجود",
                code="USER_NOT_FOUND",
                status=404
            )
        
        data = request.get_json()
        
        if not data or not data.get('amount'):
            return error_response(
                message="المبلغ مطلوب",
                code="MISSING_AMOUNT"
            )
        
        amount = float(data['amount'])
        
        if amount <= 0:
            return error_response(
                message="المبلغ يجب أن يكون أكبر من صفر",
                code="INVALID_AMOUNT"
            )
        
        # Add to wallet
        user.add_to_wallet(amount, 'deposit')
        db.session.commit()
        
        return success_response(
            data={
                "new_balance": user.wallet_balance,
                "amount_deposited": amount
            },
            message="تم الإيداع بنجاح"
        )
        
    except Exception as e:
        db.session.rollback()
        return error_response(
            message="حدث خطأ أثناء الإيداع",
            code="DEPOSIT_ERROR",
            details=str(e),
            status=500
        )


@api_bp.route('/wallet/withdraw', methods=['POST'])
@jwt_required()
def withdraw_from_wallet():
    """
    Withdraw money from wallet
    POST /api/v1/wallet/withdraw
    Headers: Authorization: Bearer <token>
    Body: {
        "amount": 5000
    }
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        if not user:
            return error_response(
                message="المستخدم غير موجود",
                code="USER_NOT_FOUND",
                status=404
            )
        
        data = request.get_json()
        
        if not data or not data.get('amount'):
            return error_response(
                message="المبلغ مطلوب",
                code="MISSING_AMOUNT"
            )
        
        amount = float(data['amount'])
        
        if amount <= 0:
            return error_response(
                message="المبلغ يجب أن يكون أكبر من صفر",
                code="INVALID_AMOUNT"
            )
        
        if user.wallet_balance < amount:
            return error_response(
                message="رصيد المحفظة غير كافي",
                code="INSUFFICIENT_BALANCE",
                details={
                    "required": amount,
                    "available": user.wallet_balance
                }
            )
        
        # Deduct from wallet
        user.deduct_from_wallet(amount, 'withdrawal')
        db.session.commit()
        
        return success_response(
            data={
                "new_balance": user.wallet_balance,
                "amount_withdrawn": amount
            },
            message="تم السحب بنجاح"
        )
        
    except Exception as e:
        db.session.rollback()
        return error_response(
            message="حدث خطأ أثناء السحب",
            code="WITHDRAWAL_ERROR",
            details=str(e),
            status=500
        )


@api_bp.route('/wallet/transactions', methods=['GET'])
@jwt_required()
def get_transactions():
    """
    Get user's transaction history
    GET /api/v1/wallet/transactions?page=1&per_page=20
    Headers: Authorization: Bearer <token>
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        if not user:
            return error_response(
                message="المستخدم غير موجود",
                code="USER_NOT_FOUND",
                status=404
            )
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Paginate transactions
        pagination = user.transactions.order_by(Transaction.date.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        transactions = [serialize_transaction(t) for t in pagination.items]
        
        return success_response(
            data={
                "transactions": transactions,
                "total": pagination.total,
                "page": page,
                "per_page": per_page,
                "total_pages": pagination.pages
            },
            message="تم جلب المعاملات بنجاح"
        )
        
    except Exception as e:
        return error_response(
            message="حدث خطأ أثناء جلب المعاملات",
            code="FETCH_ERROR",
            details=str(e),
            status=500
        )


# ==================== User Dashboard Endpoint ====================

@api_bp.route('/user/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard():
    """
    Get user dashboard data
    GET /api/v1/user/dashboard
    Headers: Authorization: Bearer <token>
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        if not user:
            return error_response(
                message="المستخدم غير موجود",
                code="USER_NOT_FOUND",
                status=404
            )
        
        # Get recent transactions
        recent_transactions = [
            serialize_transaction(t) 
            for t in user.transactions.order_by(Transaction.date.desc()).limit(5).all()
        ]
        
        # Count apartments invested in
        apartments_count = db.session.query(db.func.count(db.func.distinct(Share.apartment_id)))\
            .filter(Share.user_id == user.id).scalar() or 0
        
        return success_response(
            data={
                "user": serialize_user(user),
                "wallet_balance": user.wallet_balance,
                "rewards_balance": user.rewards_balance,
                "total_invested": user.get_total_invested(),
                "monthly_expected_income": user.get_monthly_expected_income(),
                "apartments_count": apartments_count,
                "total_shares": user.shares.count(),
                "recent_transactions": recent_transactions
            },
            message="تم جلب بيانات لوحة التحكم بنجاح"
        )
        
    except Exception as e:
        return error_response(
            message="حدث خطأ أثناء جلب البيانات",
            code="FETCH_ERROR",
            details=str(e),
            status=500
        )

@api_bp.route('/user/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """
    Update user profile
    PUT /api/v1/user/profile
    Headers: Authorization: Bearer <token>
    Body: {
        "name": "أحمد محمد الجديد",
        "phone": "01234567890"
    }
    """
    try:
        data = request.get_json()
        
        if not data or not data.get('name'):
            return error_response(
                message="الاسم مطلوب",
                code="MISSING_FIELDS"
            )
        
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        if not user:
            return error_response(
                message="المستخدم غير موجود",
                code="USER_NOT_FOUND",
                status=404
            )
        
        user.name = data['name']
        if data.get('phone'):
            user.phone = data['phone']
            
        db.session.commit()
        
        return success_response(
            data={"user": serialize_user(user)},
            message="تم تحديث الملف الشخصي بنجاح"
        )
        
    except Exception as e:
        db.session.rollback()
        return error_response(
            message="حدث خطأ أثناء تحديث الملف الشخصي",
            code="UPDATE_ERROR",
            details=str(e),
            status=500
        )


# ==================== Car Endpoints ====================

def serialize_car(car):
    """Convert Car object to dictionary"""
    return {
        "id": car.id,
        "title": car.title,
        "description": car.description,
        "image": car.image,
        "total_price": car.total_price,
        "total_shares": car.total_shares,
        "shares_available": car.shares_available,
        "shares_sold": car.shares_sold,
        "share_price": car.share_price,
        "monthly_rent": car.monthly_rent,
        "location": car.location,
        "is_closed": car.is_closed,
        "status": car.status,
        "completion_percentage": car.completion_percentage,
        "investors_count": car.investors_count,
        "brand": car.brand,
        "model": car.model,
        "year": car.year,
        "date_created": car.date_created.isoformat() if car.date_created else None
    }

@api_bp.route('/cars', methods=['GET'])
def get_cars():
    """
    Get list of cars
    GET /api/v1/cars
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        query = Car.query.order_by(Car.date_created.desc())
        
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        cars = [serialize_car(car) for car in pagination.items]
        
        return success_response(
            data={
                "cars": cars,
                "total": pagination.total,
                "page": page,
                "per_page": per_page,
                "total_pages": pagination.pages
            },
            message="تم جلب السيارات بنجاح"
        )
    except Exception as e:
        return error_response(message="حدث خطأ أثناء جلب السيارات", details=str(e), status=500)

@api_bp.route('/cars/<int:car_id>', methods=['GET'])
def get_car_details(car_id):
    """Get car details"""
    try:
        car = Car.query.get(car_id)
        if not car:
            return error_response(message="السيارة غير موجودة", status=404)
        return success_response(data={"car": serialize_car(car)}, message="تم جلب تفاصيل السيارة بنجاح")
    except Exception as e:
        return error_response(message="حدث خطأ", details=str(e), status=500)

@api_bp.route('/cars/purchase', methods=['POST'])
@jwt_required()
def purchase_car_shares():
    """Purchase shares in a car"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        data = request.get_json()
        
        if not data or not data.get('car_id') or not data.get('num_shares'):
            return error_response(message="البيانات ناقصة")
            
        car = Car.query.get(data['car_id'])
        if not car:
            return error_response(message="السيارة غير موجودة", status=404)
            
        success, msg = car.purchase_shares(user, data['num_shares'])
        if not success:
            return error_response(message=msg)
            
        db.session.commit()
        return success_response(
            data={
                "new_balance": user.wallet_balance,
                "shares_purchased": data['num_shares'],
                "car": serialize_car(car)
            },
            message="تم شراء حصص السيارة بنجاح"
        )
    except Exception as e:
        db.session.rollback()
        return error_response(message="حدث خطأ أثناء الشراء", details=str(e), status=500)

@api_bp.route('/cars/my-investments', methods=['GET'])
@jwt_required()
def get_my_car_investments():
    """Get user's car investments"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        # Group shares by car
        shares_by_car = {}
        for share in user.car_shares:
            car_id = share.car_id
            if car_id not in shares_by_car:
                shares_by_car[car_id] = {
                    "car": serialize_car(share.car),
                    "shares_owned": 0,
                    "total_invested": 0,
                    "monthly_income": 0
                }
            shares_by_car[car_id]["shares_owned"] += 1
            shares_by_car[car_id]["total_invested"] += share.share_price
            if share.car:
                shares_by_car[car_id]["monthly_income"] += share.car.monthly_rent / share.car.total_shares

        return success_response(
            data={"investments": list(shares_by_car.values())},
            message="تم جلب استثمارات السيارات بنجاح"
        )
    except Exception as e:
        return error_response(message="حدث خطأ", details=str(e), status=500)


# ==================== Admin Endpoints ====================

@api_bp.route('/admin/stats', methods=['GET'])
@jwt_required()
def get_admin_stats():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        if not user or not user.is_admin:
            return error_response(
                message='غير مصرح لك بالوصول',
                code='UNAUTHORIZED',
                status=403
            )
        
        total_users = User.query.count()
        total_apartments = Apartment.query.count()
        total_cars = Car.query.count()
        pending_requests = InvestmentRequest.query.filter_by(status='pending').count()
        approved_requests = InvestmentRequest.query.filter_by(status='approved').count()
        total_investments = Share.query.count()
        
        total_apartment_value = db.session.query(db.func.sum(Apartment.total_price)).scalar() or 0
        total_car_value = db.session.query(db.func.sum(Car.total_price)).scalar() or 0
        
        return success_response(
            data={
                'total_users': total_users,
                'total_apartments': total_apartments,
                'total_cars': total_cars,
                'pending_requests': pending_requests,
                'approved_requests': approved_requests,
                'total_investments': total_investments,
                'total_platform_value': total_apartment_value + total_car_value
            },
            message='تم جلب الإحصائيات بنجاح'
        )
    except Exception as e:
        return error_response(message='حدث خطأ أثناء جلب الإحصائيات', details=str(e), status=500)


@api_bp.route('/admin/investment-requests', methods=['GET'])
@jwt_required()
def get_investment_requests():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        if not user or not user.is_admin:
            return error_response(message='غير مصرح لك بالوصول', code='UNAUTHORIZED', status=403)
        
        status_filter = request.args.get('status')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        query = InvestmentRequest.query
        if status_filter:
            query = query.filter_by(status=status_filter)
        
        query = query.order_by(InvestmentRequest.date_submitted.desc())
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        requests_list = []
        for req in pagination.items:
            requests_list.append({
                'id': req.id,
                'user_id': req.user_id,
                'user_name': req.user.name,
                'user_email': req.user.email,
                'apartment_id': req.apartment_id,
                'apartment_title': req.apartment.title if req.apartment else None,
                'shares_requested': req.shares_requested,
                'total_amount': req.total_amount,
                'status': req.status,
                'status_arabic': req.status_arabic,
                'full_name': req.full_name,
                'phone': req.phone,
                'national_id': req.national_id,
                'date_submitted': req.date_submitted.isoformat() if req.date_submitted else None,
                'admin_notes': req.admin_notes
            })
        
        return success_response(
            data={
                'requests': requests_list,
                'total': pagination.total,
                'page': page,
                'per_page': per_page,
                'total_pages': pagination.pages
            },
            message='تم جلب الطلبات بنجاح'
        )
    except Exception as e:
        return error_response(message='حدث خطأ أثناء جلب الطلبات', details=str(e), status=500)


@api_bp.route('/admin/investment-requests/<int:request_id>/action', methods=['POST'])
@jwt_required()
def admin_request_action(request_id):
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        if not user or not user.is_admin:
            return error_response(message='غير مصرح لك بالوصول', code='UNAUTHORIZED', status=403)
        
        data = request.get_json()
        action = data.get('action')
        admin_notes = data.get('admin_notes', '')
        
        if action not in ['approve', 'reject']:
            return error_response(message='الإجراء غير صحيح', code='INVALID_ACTION')
        
        inv_request = InvestmentRequest.query.get(request_id)
        if not inv_request:
            return error_response(message='الطلب غير موجود', status=404)
        
        if action == 'approve':
            inv_request.status = 'approved'
            apartment = inv_request.apartment
            investor = inv_request.user
            
            for _ in range(inv_request.shares_requested):
                share = Share(
                    user_id=investor.id,
                    apartment_id=apartment.id,
                    share_price=apartment.share_price
                )
                db.session.add(share)
            
            apartment.shares_available -= inv_request.shares_requested
            if apartment.shares_available == 0:
                apartment.is_closed = True
        else:
            inv_request.status = 'rejected'
        
        inv_request.admin_notes = admin_notes
        inv_request.date_reviewed = datetime.utcnow()
        inv_request.reviewed_by = user.id
        
        db.session.commit()
        
        return success_response(
            data={'request': {
                'id': inv_request.id,
                'status': inv_request.status,
                'status_arabic': inv_request.status_arabic
            }},
            message=f'تم {inv_request.status_arabic} الطلب بنجاح'
        )
    except Exception as e:
        db.session.rollback()
        return error_response(message='حدث خطأ أثناء معالجة الطلب', details=str(e), status=500)


# ==================== KYC & Investment Request Endpoints ====================

@api_bp.route('/user/kyc', methods=['POST'])
@jwt_required()
def submit_kyc():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        if not user:
            return error_response(message='المستخدم غير موجود', status=404)
        
        data = request.get_json()
        
        user.phone = data.get('phone', user.phone)
        user.national_id = data.get('national_id', user.national_id)
        user.address = data.get('address', user.address)
        user.date_of_birth = data.get('date_of_birth', user.date_of_birth)
        user.nationality = data.get('nationality', user.nationality)
        user.occupation = data.get('occupation', user.occupation)
        
        db.session.commit()
        
        return success_response(
            data={
                'kyc_completed': all([user.phone, user.national_id, user.address, 
                                     user.date_of_birth, user.nationality, user.occupation])
            },
            message='تم تحديث معلومات KYC بنجاح'
        )
    except Exception as e:
        db.session.rollback()
        return error_response(message='حدث خطأ أثناء تحديث المعلومات', details=str(e), status=500)


@api_bp.route('/investments/request', methods=['POST'])
@jwt_required()
def create_investment_request():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        # Check if request is multipart/form-data
        if not request.files and not request.form:
             return error_response(message='يجب إرسال البيانات بصيغة multipart/form-data', code='INVALID_CONTENT_TYPE')

        data = request.form
        files = request.files
        
        required_fields = ['apartment_id', 'shares_requested', 'full_name', 'phone', 
                          'national_id', 'address', 'date_of_birth', 'nationality', 'occupation']
        
        for field in required_fields:
            if not data.get(field):
                return error_response(message=f'الحقل {field} مطلوب', code='MISSING_FIELDS')
        
        # Validate files
        required_files = ['id_document_front', 'id_document_back', 'proof_of_address']
        for file_field in required_files:
            if file_field not in files or files[file_field].filename == '':
                 return error_response(message=f'الملف {file_field} مطلوب', code='MISSING_FILES')

        apartment = Apartment.query.get(data['apartment_id'])
        if not apartment:
            return error_response(message='الشقة غير موجودة', status=404)
        
        shares_requested = int(data['shares_requested'])
        if apartment.shares_available < shares_requested:
            return error_response(message='عدد الحصص المطلوبة غير متاح', code='INSUFFICIENT_SHARES')
        
        referred_by_user_id = None
        if data.get('referred_by_code'):
            referral = ReferralTree.query.filter_by(
                referral_code=data['referred_by_code'],
                apartment_id=apartment.id
            ).first()
            if referral:
                referred_by_user_id = referral.user_id
        
        # Save files
        from flask import current_app
        upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'documents')
        os.makedirs(upload_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        front_file = files['id_document_front']
        front_filename = secure_filename(f"{timestamp}_front_{user.id}_{front_file.filename}")
        front_file.save(os.path.join(upload_dir, front_filename))
        
        back_file = files['id_document_back']
        back_filename = secure_filename(f"{timestamp}_back_{user.id}_{back_file.filename}")
        back_file.save(os.path.join(upload_dir, back_filename))
        
        address_file = files['proof_of_address']
        address_filename = secure_filename(f"{timestamp}_address_{user.id}_{address_file.filename}")
        address_file.save(os.path.join(upload_dir, address_filename))

        inv_request = InvestmentRequest(
            user_id=user.id,
            apartment_id=apartment.id,
            shares_requested=shares_requested,
            referred_by_user_id=referred_by_user_id,
            full_name=data['full_name'],
            phone=data['phone'],
            national_id=data['national_id'],
            address=data['address'],
            date_of_birth=data['date_of_birth'],
            nationality=data['nationality'],
            occupation=data['occupation'],
            id_document_front=front_filename,
            id_document_back=back_filename,
            proof_of_address=address_filename,
            status='pending'
        )
        
        db.session.add(inv_request)
        db.session.commit()
        
        return success_response(
            data={
                'request_id': inv_request.id,
                'status': inv_request.status,
                'status_arabic': inv_request.status_arabic,
                'total_amount': inv_request.total_amount
            },
            message='تم إرسال طلب الاستثمار بنجاح'
        )
    except Exception as e:
        db.session.rollback()
        return error_response(message='حدث خطأ أثناء إنشاء الطلب', details=str(e), status=500)


@api_bp.route('/investments/requests', methods=['GET'])
@jwt_required()
def get_user_investment_requests():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        requests = InvestmentRequest.query.filter_by(user_id=user.id).order_by(InvestmentRequest.date_submitted.desc()).all()
        
        requests_list = []
        for req in requests:
            requests_list.append({
                'id': req.id,
                'apartment_id': req.apartment_id,
                'apartment_title': req.apartment.title if req.apartment else None,
                'shares_requested': req.shares_requested,
                'total_amount': req.total_amount,
                'status': req.status,
                'status_arabic': req.status_arabic,
                'date_submitted': req.date_submitted.isoformat() if req.date_submitted else None,
                'admin_notes': req.admin_notes if req.status in ['rejected', 'documents_missing'] else None
            })
        
        return success_response(
            data={'requests': requests_list},
            message='تم جلب طلبات الاستثمار بنجاح'
        )
    except Exception as e:
        return error_response(message='حدث خطأ', details=str(e), status=500)
