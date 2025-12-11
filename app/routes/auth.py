"""
Authentication routes
Handles user registration, login, and logout
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from werkzeug.security import check_password_hash
from app.models import db, User

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration page"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validation
        if not all([name, email, password, confirm_password]):
            flash('جميع الحقول مطلوبة', 'error')
            return render_template('user/register.html')
        
        if password != confirm_password:
            flash('كلمات المرور غير متطابقة', 'error')
            return render_template('user/register.html')
        
        if len(password) < 6:
            flash('كلمة المرور يجب أن تكون 6 أحرف على الأقل', 'error')
            return render_template('user/register.html')
        
        # Check if user exists
        if User.query.filter_by(email=email).first():
            flash('البريد الإلكتروني مستخدم بالفعل', 'error')
            return render_template('user/register.html')
        
        # Create new user
        user = User(name=name, email=email, wallet_balance=0.0)  # Start with zero balance
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash('تم إنشاء الحساب بنجاح! يمكنك الآن تسجيل الدخول', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('user/register.html')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login page"""
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('user_views.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = request.form.get('remember', False)
        
        if not email or not password:
            flash('البريد الإلكتروني وكلمة المرور مطلوبان', 'error')
            return render_template('user/login.html')
        
        user = User.query.filter_by(email=email).first()
        
        # DEBUG: Log user details
        if user:
            print(f"DEBUG: User found - ID:{user.id}, Email:{user.email}, HasHash:{user.password_hash is not None}")
            if user.password_hash:
                print(f"DEBUG: Password hash length: {len(user.password_hash)}")
                print(f"DEBUG: Testing password '{password}'")
                password_check_result = user.check_password(password)
                print(f"DEBUG: Password check result: {password_check_result}")
        else:
            print(f"DEBUG: No user found with email: {email}")
        
        if user and user.check_password(password):
            login_user(user, remember=remember)
            
            # Redirect to next page or dashboard
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            
            if user.is_admin:
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('user_views.dashboard'))
        else:
            flash('البريد الإلكتروني أو كلمة المرور غير صحيحة', 'error')
    
    return render_template('user/login.html')


@bp.route('/logout')
def logout():
    """Logout current user"""
    logout_user()
    flash('تم تسجيل الخروج بنجاح', 'success')
    return redirect(url_for('main.index'))


@bp.route('/google/callback', methods=['POST'])
def google_callback():
    """Handle Google Sign-In callback for web users"""
    from app.auth_providers import verify_google_token
    from flask import jsonify
    
    try:
        data = request.get_json()
        
        if not data or not data.get('credential'):
            return jsonify({
                'success': False,
                'message': 'بيانات غير صالحة'
            }), 400
        
        # Verify Google token
        user_info = verify_google_token(data['credential'])
        
        if not user_info:
            return jsonify({
                'success': False,
                'message': 'فشل التحقق من حساب Google'
            }), 401
        
        # Extract user information
        google_user_id = user_info['user_id']
        email = user_info['email']
        name = user_info['name']
        
        # Check if user exists with Google auth
        user = User.query.filter_by(
            auth_provider='google',
            provider_user_id=google_user_id
        ).first()
        
        if not user:
            # Check if email exists with different auth method (account linking)
            user = User.query.filter_by(email=email).first()
            
            if user:
                # Link existing account to Google
                user.link_social_account('google', google_user_id, email)
                db.session.commit()
            else:
                # Create new user
                user = User(
                    name=name,
                    email=email,
                    auth_provider='google',
                    provider_user_id=google_user_id,
                    provider_email=email,
                    wallet_balance=0.0  # Start with zero balance
                )
                db.session.add(user)
                db.session.commit()
        
        # Log in the user using Flask-Login
        login_user(user, remember=True)
        
        # Determine redirect URL
        redirect_url = url_for('user_views.dashboard') if not user.is_admin else url_for('admin.dashboard')
        
        return jsonify({
            'success': True,
            'message': 'تم تسجيل الدخول بنجاح',
            'redirect_url': redirect_url
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'حدث خطأ أثناء تسجيل الدخول',
            'error': str(e)
        }), 500
