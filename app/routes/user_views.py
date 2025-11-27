"""
User-facing view routes
Dashboard, wallet, and share purchase functionality
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, session
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, TextAreaField, IntegerField, BooleanField, SelectField
from wtforms.validators import DataRequired, Email, Length, Regexp
from werkzeug.utils import secure_filename
from app.models import db, Apartment, Share, Transaction, InvestmentRequest, User, Car, CarShare, CarInvestmentRequest, CarReferralTree
from sqlalchemy import desc
import os
from datetime import datetime
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


def optimize_uploaded_file(file_path):
    """Optimize uploaded image files for faster processing"""
    if not PIL_AVAILABLE:
        return
    
    try:
        # Check if it's an image file
        if file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
            with Image.open(file_path) as img:
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                
                # Resize if too large (max 1024x1024)
                if img.width > 1024 or img.height > 1024:
                    img.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
                
                # Save with optimization
                img.save(file_path, optimize=True, quality=85)
    except Exception:
        # If optimization fails, keep original file
        pass

bp = Blueprint('user_views', __name__, url_prefix='/user')


# Investment Request Form
class InvestmentRequestForm(FlaskForm):
    full_name = StringField('الاسم الكامل', validators=[DataRequired(message='مطلوب')])
    phone = StringField('رقم الهاتف', validators=[DataRequired(message='مطلوب'), 
                                                   Regexp(r'^\+?[\d\s-]{10,}$', message='رقم هاتف غير صحيح')])
    national_id = StringField('الرقم القومي', validators=[DataRequired(message='مطلوب'),
                                                           Length(min=10, max=20, message='رقم غير صحيح')])
    address = TextAreaField('العنوان', validators=[DataRequired(message='مطلوب')])
    date_of_birth = StringField('تاريخ الميلاد', validators=[DataRequired(message='مطلوب')])
    nationality = StringField('الجنسية', validators=[DataRequired(message='مطلوب')])
    occupation = StringField('المهنة', validators=[DataRequired(message='مطلوب')])
    referral_code = StringField('كود الإحالة (اختياري)', validators=[])
    id_document_front = FileField('صورة وجه البطاقة', validators=[
        FileRequired(message='مطلوب'),
        FileAllowed(['jpg', 'jpeg', 'png', 'pdf'], 'صور أو PDF فقط')
    ])
    id_document_back = FileField('صورة ظهر البطاقة', validators=[
        FileRequired(message='مطلوب'),
        FileAllowed(['jpg', 'jpeg', 'png', 'pdf'], 'صور أو PDF فقط')
    ])
    proof_of_address = FileField('إثبات العنوان', validators=[
        FileRequired(message='مطلوب'),
        FileAllowed(['jpg', 'jpeg', 'png', 'pdf'], 'صور أو PDF فقط')
    ])
    agree_terms = BooleanField('أوافق على الشروط', validators=[DataRequired(message='يجب الموافقة')])



@bp.route('/dashboard')
@login_required
def dashboard():
    """User dashboard showing investments and statistics across units and cars"""
    # Apartments investments grouped
    apt_shares = Share.query.filter_by(user_id=current_user.id).all()
    apt_investments_map = {}
    for share in apt_shares:
        apt_id = share.apartment_id
        if apt_id not in apt_investments_map:
            apartment = share.apartment
            apt_investments_map[apt_id] = {
                'type': 'unit',
                'title': apartment.title,
                'location': apartment.location,
                'status': apartment.status,
                'is_closed': apartment.is_closed,
                'total_shares': apartment.total_shares,
                'shares_sold': apartment.total_shares - apartment.shares_available,
                'investors_count': apartment.investors_count,
                'shares_count': 0,
                'total_invested': 0,
                'monthly_income': 0
            }
        apt_investments_map[apt_id]['shares_count'] += 1
        apt_investments_map[apt_id]['total_invested'] += share.share_price
        apartment = share.apartment
        if apartment.total_shares > 0:
            apt_investments_map[apt_id]['monthly_income'] += apartment.monthly_rent * (1 / apartment.total_shares)

    # Cars investments grouped
    car_shares = CarShare.query.filter_by(user_id=current_user.id).all()
    car_investments_map = {}
    for cshare in car_shares:
        car_id = cshare.car_id
        if car_id not in car_investments_map:
            car = cshare.car
            car_investments_map[car_id] = {
                'type': 'car',
                'title': car.title,
                'location': car.location,
                'status': car.status,
                'is_closed': car.is_closed,
                'total_shares': car.total_shares,
                'shares_sold': car.total_shares - car.shares_available,
                'investors_count': car.investors_count,
                'shares_count': 0,
                'total_invested': 0,
                'monthly_income': 0
            }
        car_investments_map[car_id]['shares_count'] += 1
        car_investments_map[car_id]['total_invested'] += cshare.share_price
        car = cshare.car
        if car.total_shares > 0:
            car_investments_map[car_id]['monthly_income'] += car.monthly_rent * (1 / car.total_shares)

    # Merge into one list
    investments = list(apt_investments_map.values()) + list(car_investments_map.values())
    
    # Calculate totals
    # Totals across both assets
    total_invested = (current_user.get_total_invested() or 0) + \
                     (db.session.query(db.func.sum(CarShare.share_price)).filter(CarShare.user_id == current_user.id).scalar() or 0)
    # Expected monthly across both
    expected_monthly = 0
    for inv in investments:
        expected_monthly += inv['monthly_income']
    
    # Get recent transactions
    recent_transactions = Transaction.query.filter_by(user_id=current_user.id)\
        .order_by(desc(Transaction.date)).limit(10).all()
    
    return render_template('user/dashboard.html',
                         investments=investments,
                         total_invested=total_invested,
                         expected_monthly=expected_monthly,
                         recent_transactions=recent_transactions)


@bp.route('/wallet')
@login_required
def wallet():
    """User wallet page with transaction history"""
    page = request.args.get('page', 1, type=int)
    
    # Get transactions with pagination
    transactions = Transaction.query.filter_by(user_id=current_user.id)\
        .order_by(desc(Transaction.date))\
        .paginate(page=page, per_page=20, error_out=False)
    
    # Calculate statistics
    total_deposits = db.session.query(db.func.sum(Transaction.amount))\
        .filter(Transaction.user_id == current_user.id,
                Transaction.transaction_type == 'deposit').scalar() or 0
    
    total_withdrawals = db.session.query(db.func.sum(Transaction.amount))\
        .filter(Transaction.user_id == current_user.id,
                Transaction.transaction_type == 'withdrawal').scalar() or 0
    
    total_invested = db.session.query(db.func.sum(Share.share_price))\
        .filter(Share.user_id == current_user.id).scalar() or 0
    
    total_rental_income = db.session.query(db.func.sum(Transaction.amount))\
        .filter(Transaction.user_id == current_user.id,
                Transaction.transaction_type == 'rental_income').scalar() or 0
    
    stats = {
        'current_balance': current_user.wallet_balance,
        'total_deposits': total_deposits,
        'total_withdrawals': abs(total_withdrawals),
        'total_invested': total_invested,
        'total_rental_income': total_rental_income
    }
    
    return render_template('user/wallet.html',
                         transactions=transactions,
                         stats=stats)


@bp.route('/wallet/deposit', methods=['POST'])
@login_required
def deposit():
    """Deposit money to wallet"""
    amount = float(request.form.get('amount', 0))
    
    if amount <= 0:
        flash('المبلغ يجب أن يكون أكبر من صفر', 'error')
        return redirect(url_for('user_views.wallet'))
    
    current_user.add_to_wallet(amount, 'deposit')
    db.session.commit()
    
    flash(f'تم إيداع {amount:,.0f} جنيه بنجاح', 'success')
    return redirect(url_for('user_views.wallet'))


@bp.route('/wallet/withdraw', methods=['POST'])
@login_required
def withdraw():
    """Withdraw money from wallet"""
    amount = float(request.form.get('amount', 0))
    
    if amount <= 0:
        flash('المبلغ يجب أن يكون أكبر من صفر', 'error')
        return redirect(url_for('user_views.wallet'))
    
    if current_user.wallet_balance < amount:
        flash('الرصيد غير كافي', 'error')
        return redirect(url_for('user_views.wallet'))
    
    current_user.deduct_from_wallet(amount, 'withdrawal')
    db.session.commit()
    
    flash(f'تم سحب {amount:,.0f} جنيه بنجاح', 'success')
    return redirect(url_for('user_views.wallet'))


@bp.route('/buy-shares/<int:apartment_id>', methods=['GET', 'POST'])
@login_required
def buy_shares(apartment_id):
    """Buy shares page - redirects to investment request"""
    apartment = Apartment.query.get_or_404(apartment_id)
    
    if request.method == 'POST':
        num_shares = int(request.form.get('num_shares', 1))
        
        if num_shares < 1:
            flash('يجب شراء حصة واحدة على الأقل', 'error')
            return render_template('user/buy_shares.html', apartment=apartment)
        
        # Redirect to investment request form instead of direct purchase
        return redirect(url_for('user_views.investment_request', 
                              apartment_id=apartment_id, 
                              shares=num_shares))
    
    return render_template('user/buy_shares.html', apartment=apartment)


@bp.route('/buy-car-shares/<int:car_id>', methods=['GET', 'POST'])
@login_required
def buy_car_shares(car_id):
    """Buy car shares page - redirects to car investment request"""
    car = Car.query.get_or_404(car_id)

    if request.method == 'POST':
        num_shares = int(request.form.get('num_shares', 1))
        if num_shares < 1:
            flash('يجب شراء حصة واحدة على الأقل', 'error')
            return render_template('user/buy_car_shares.html', car=car)
        return redirect(url_for('user_views.car_investment_request', car_id=car_id, shares=num_shares))

    return render_template('user/buy_car_shares.html', car=car)


@bp.route('/my-investments')
@login_required
def my_investments():
    """Detailed view of all user investments (apartments + cars)"""
    # Apartments
    shares = Share.query.filter_by(user_id=current_user.id).all()
    apt_investments = {}
    for share in shares:
        apt_id = share.apartment_id
        if apt_id not in apt_investments:
            apartment = share.apartment
            apt_investments[apt_id] = {
                'apartment': apartment,
                'shares': [],
                'shares_count': 0,
                'total_invested': 0,
                'monthly_income': 0,
                'roi_percentage': 0
            }

        apt_investments[apt_id]['shares'].append(share)
        apt_investments[apt_id]['shares_count'] += 1
        apt_investments[apt_id]['total_invested'] += share.share_price

        apartment = share.apartment
        if apartment.total_shares > 0:
            share_percentage = 1 / apartment.total_shares
            monthly_per_share = apartment.monthly_rent * share_percentage
            apt_investments[apt_id]['monthly_income'] += monthly_per_share
            if apt_investments[apt_id]['total_invested'] > 0:
                yearly_income = monthly_per_share * 12 * apt_investments[apt_id]['shares_count']
                apt_investments[apt_id]['roi_percentage'] = (yearly_income / apt_investments[apt_id]['total_invested']) * 100

    # Cars
    cshares = CarShare.query.filter_by(user_id=current_user.id).all()
    car_investments = {}
    for cshare in cshares:
        car_id = cshare.car_id
        if car_id not in car_investments:
            car = cshare.car
            car_investments[car_id] = {
                'car': car,
                'shares': [],
                'shares_count': 0,
                'total_invested': 0,
                'monthly_income': 0,
                'roi_percentage': 0
            }
        car_investments[car_id]['shares'].append(cshare)
        car_investments[car_id]['shares_count'] += 1
        car_investments[car_id]['total_invested'] += cshare.share_price

        car = cshare.car
        if car.total_shares > 0:
            share_percentage = 1 / car.total_shares
            monthly_per_share = car.monthly_rent * share_percentage
            car_investments[car_id]['monthly_income'] += monthly_per_share
            if car_investments[car_id]['total_invested'] > 0:
                yearly_income = monthly_per_share * 12 * car_investments[car_id]['shares_count']
                car_investments[car_id]['roi_percentage'] = (yearly_income / car_investments[car_id]['total_invested']) * 100

    return render_template('user/my_investments.html',
                         investments=list(apt_investments.values()),
                         car_investments=list(car_investments.values()))


@bp.route('/profile')
@login_required
def profile():
    """User profile page"""
    return render_template('user/profile.html')


@bp.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    """Update user profile"""
    name = request.form.get('name')
    
    if name:
        current_user.name = name
        db.session.commit()
        flash('تم تحديث الملف الشخصي بنجاح', 'success')
    else:
        flash('الاسم مطلوب', 'error')
    
    return redirect(url_for('user_views.profile'))


@bp.route('/profile/change-password', methods=['POST'])
@login_required
def change_password():
    """Change user password"""
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    if not current_user.check_password(current_password):
        flash('كلمة المرور الحالية غير صحيحة', 'error')
        return redirect(url_for('user_views.profile'))
    
    if new_password != confirm_password:
        flash('كلمة المرور الجديدة غير متطابقة', 'error')
        return redirect(url_for('user_views.profile'))
    
    if len(new_password) < 6:
        flash('كلمة المرور يجب أن تكون 6 أحرف على الأقل', 'error')
        return redirect(url_for('user_views.profile'))
    
    current_user.set_password(new_password)
    db.session.commit()
    
    flash('تم تغيير كلمة المرور بنجاح', 'success')
    return redirect(url_for('user_views.profile'))


@bp.route('/investment-request/<int:apartment_id>', methods=['GET', 'POST'])
@login_required
def investment_request(apartment_id):
    """Submit investment request with KYC documents"""
    apartment = Apartment.query.get_or_404(apartment_id)
    
    # Get shares count from session or query params
    shares_count = int(request.args.get('shares', 1))
    total_amount = apartment.share_price * shares_count
    
    # Check for referral code in session
    referral_code = None
    referrer_tree = None
    if 'referral_code' in session and session.get('referral_apartment') == apartment_id:
        referral_code = session['referral_code']
        from app.models import ReferralTree
        referrer_tree = ReferralTree.query.filter_by(
            apartment_id=apartment_id,
            referral_code=referral_code
        ).first()
    
    form = InvestmentRequestForm()
    
    # Pre-populate referral code field if in session
    if referral_code and request.method == 'GET':
        form.referral_code.data = referral_code
    
    if form.validate_on_submit():
        # Check for manual referral code entry (overrides session)
        manual_referral_code = form.referral_code.data
        if manual_referral_code:
            from app.models import ReferralTree
            referrer_tree = ReferralTree.query.filter_by(
                apartment_id=apartment_id,
                referral_code=manual_referral_code.strip()
            ).first()
            if not referrer_tree:
                flash('كود الإحالة غير صحيح أو غير موجود لهذه الوحدة', 'error')
                return render_template('user/investment_request.html',
                                     form=form,
                                     apartment=apartment,
                                     shares_count=shares_count,
                                     total_amount=total_amount,
                                     referral_code=manual_referral_code,
                                     referrer=None)
        # Create uploads directories if they don't exist - use absolute path
        from flask import current_app
        upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'documents')
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save uploaded files with optimization
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        try:
            # Process front document
            front_file = form.id_document_front.data
            front_filename = secure_filename(f"{timestamp}_front_{current_user.id}_{front_file.filename}")
            front_path = os.path.join(upload_dir, front_filename)
            front_file.save(front_path)
            optimize_uploaded_file(front_path)
            
            # Process back document
            back_file = form.id_document_back.data
            back_filename = secure_filename(f"{timestamp}_back_{current_user.id}_{back_file.filename}")
            back_path = os.path.join(upload_dir, back_filename)
            back_file.save(back_path)
            optimize_uploaded_file(back_path)
            
            # Process address proof
            address_file = form.proof_of_address.data
            address_filename = secure_filename(f"{timestamp}_address_{current_user.id}_{address_file.filename}")
            address_path = os.path.join(upload_dir, address_filename)
            address_file.save(address_path)
            optimize_uploaded_file(address_path)
            
        except Exception as e:
            flash('حدث خطأ أثناء رفع الملفات. يرجى المحاولة مرة أخرى.', 'error')
            return render_template('user/investment_request.html',
                                 form=form,
                                 apartment=apartment,
                                 shares_count=shares_count,
                                 total_amount=total_amount,
                                 referral_code=referral_code,
                                 referrer=User.query.get(referrer_tree.user_id) if referrer_tree else None)
        
        # Create investment request
        inv_request = InvestmentRequest(
            user_id=current_user.id,
            apartment_id=apartment_id,
            shares_requested=shares_count,
            full_name=form.full_name.data,
            phone=form.phone.data,
            national_id=form.national_id.data,
            address=form.address.data,
            date_of_birth=form.date_of_birth.data,
            nationality=form.nationality.data,
            occupation=form.occupation.data,
            id_document_front=front_filename,
            id_document_back=back_filename,
            proof_of_address=address_filename,
            status='pending',
            referred_by_user_id=referrer_tree.user_id if referrer_tree else None
        )
        
        db.session.add(inv_request)
        db.session.commit()
        
        # Clear referral from session
        session.pop('referral_code', None)
        session.pop('referral_apartment', None)
        
        flash('تم إرسال طلبك بنجاح! سنتواصل معك قريباً', 'success')
        return redirect(url_for('user_views.request_confirmation', request_id=inv_request.id))
    
    # If form has errors, flash them
    if form.errors:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field}: {error}', 'error')
    
    return render_template('user/investment_request.html',
                         form=form,
                         apartment=apartment,
                         shares_count=shares_count,
                         total_amount=total_amount,
                         referral_code=referral_code,
                         referrer=User.query.get(referrer_tree.user_id) if referrer_tree else None)


@bp.route('/car-investment-request/<int:car_id>', methods=['GET', 'POST'])
@login_required
def car_investment_request(car_id):
    """Submit car investment request with KYC documents"""
    car = Car.query.get_or_404(car_id)

    shares_count = int(request.args.get('shares', 1))
    total_amount = car.share_price * shares_count

    # Check for referral code in session
    referral_code = None
    referrer_tree = None
    if 'referral_code' in session and session.get('referral_car') == car_id:
        referral_code = session['referral_code']
        referrer_tree = CarReferralTree.query.filter_by(
            car_id=car_id,
            referral_code=referral_code
        ).first()

    form = InvestmentRequestForm()
    if referral_code and request.method == 'GET':
        form.referral_code.data = referral_code

    if form.validate_on_submit():
        manual_referral_code = form.referral_code.data
        if manual_referral_code:
            referrer_tree = CarReferralTree.query.filter_by(
                car_id=car_id,
                referral_code=manual_referral_code.strip()
            ).first()
            if not referrer_tree:
                flash('كود الإحالة غير صحيح أو غير موجود لهذه السيارة', 'error')
                return render_template('user/investment_request.html',
                                     form=form,
                                     car=car,
                                     shares_count=shares_count,
                                     total_amount=total_amount,
                                     referral_code=manual_referral_code,
                                     referrer=None)

        from flask import current_app
        upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'documents')
        os.makedirs(upload_dir, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        front_file = form.id_document_front.data
        front_filename = secure_filename(f"{timestamp}_front_{current_user.id}_{front_file.filename}")
        front_path = os.path.join(upload_dir, front_filename)
        front_file.save(front_path)

        back_file = form.id_document_back.data
        back_filename = secure_filename(f"{timestamp}_back_{current_user.id}_{back_file.filename}")
        back_path = os.path.join(upload_dir, back_filename)
        back_file.save(back_path)

        address_file = form.proof_of_address.data
        address_filename = secure_filename(f"{timestamp}_address_{current_user.id}_{address_file.filename}")
        address_path = os.path.join(upload_dir, address_filename)
        address_file.save(address_path)

        inv_request = CarInvestmentRequest(
            user_id=current_user.id,
            car_id=car_id,
            shares_requested=shares_count,
            full_name=form.full_name.data,
            phone=form.phone.data,
            national_id=form.national_id.data,
            address=form.address.data,
            date_of_birth=form.date_of_birth.data,
            nationality=form.nationality.data,
            occupation=form.occupation.data,
            id_document_front=front_filename,
            id_document_back=back_filename,
            proof_of_address=address_filename,
            status='pending',
            referred_by_user_id=referrer_tree.user_id if referrer_tree else None
        )

        db.session.add(inv_request)
        db.session.commit()

        session.pop('referral_code', None)
        session.pop('referral_car', None)

        flash('تم إرسال طلبك بنجاح! سنتواصل معك قريباً', 'success')
        return redirect(url_for('user_views.request_confirmation_car', request_id=inv_request.id))

    if form.errors:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field}: {error}', 'error')

    return render_template('user/investment_request.html',
                         form=form,
                         car=car,
                         shares_count=shares_count,
                         total_amount=total_amount,
                         referral_code=referral_code,
                         referrer=User.query.get(referrer_tree.user_id) if referrer_tree else None)


@bp.route('/car-request-confirmation/<int:request_id>')
@login_required
def request_confirmation_car(request_id):
    inv_request = CarInvestmentRequest.query.get_or_404(request_id)
    if inv_request.user_id != current_user.id:
        flash('غير مصرح لك بعرض هذا الطلب', 'error')
        return redirect(url_for('user_views.dashboard'))
    return render_template('user/request_confirmation.html', request_id=request_id)


@bp.route('/request-confirmation/<int:request_id>')
@login_required
def request_confirmation(request_id):
    """Show confirmation page after submitting investment request"""
    inv_request = InvestmentRequest.query.get_or_404(request_id)
    
    # Ensure user can only see their own requests
    if inv_request.user_id != current_user.id:
        flash('غير مصرح لك بعرض هذا الطلب', 'error')
        return redirect(url_for('user_views.dashboard'))
    
    return render_template('user/request_confirmation.html', request_id=request_id)


@bp.route('/my-investment-requests')
@login_required
def my_investment_requests():
    """Show user's investment requests"""
    requests = InvestmentRequest.query.filter_by(user_id=current_user.id)\
        .order_by(desc(InvestmentRequest.date_submitted)).all()
    
    return render_template('user/my_investment_requests.html', requests=requests)


# ============= REFERRAL SYSTEM =============

@bp.route('/my-referrals')
@login_required
def my_referrals():
    """Show user's referral trees for all apartments and cars they invested in"""
    from app.models import ReferralTree

    # Apartments where user has approved investments
    approved_requests = InvestmentRequest.query.filter_by(
        user_id=current_user.id,
        status='approved'
    ).all()

    trees = []
    for req in approved_requests:
        referral_code = current_user.get_or_create_referral_code(req.apartment_id)
        tree_node = ReferralTree.query.filter_by(
            user_id=current_user.id,
            apartment_id=req.apartment_id
        ).first()

        if tree_node:
            upline = tree_node.get_upline()
            downline = tree_node.get_downline()
            trees.append({
                'apartment': req.apartment,
                'referral_code': referral_code,
                'upline': upline,
                'downline': downline,
                'total_referrals': len(downline),
                'total_rewards': tree_node.total_rewards_earned
            })

    # Cars where user has approved investments
    car_approved_requests = CarInvestmentRequest.query.filter_by(
        user_id=current_user.id,
        status='approved'
    ).all()

    car_trees = []
    for req in car_approved_requests:
        node = CarReferralTree.query.filter_by(user_id=current_user.id, car_id=req.car_id).first()
        if not node:
            import secrets
            node = CarReferralTree(
                user_id=current_user.id,
                car_id=req.car_id,
                level=0,
                referral_code=f"REF{current_user.id}CAR{req.car_id}{secrets.token_hex(4).upper()}"
            )
            db.session.add(node)
            db.session.commit()

        if node:
            upline = node.get_upline()
            downline = node.get_downline()
            car_trees.append({
                'car': req.car,
                'referral_code': node.referral_code,
                'upline': upline,
                'downline': downline,
                'total_referrals': len(downline),
                'total_rewards': node.total_rewards_earned
            })

    return render_template('user/my_referrals.html', trees=trees, car_trees=car_trees)


@bp.route('/refer/<int:apartment_id>')
@login_required
def get_referral_link(apartment_id):
    """Generate and display referral link for an apartment"""
    from app.models import ReferralTree
    
    apartment = Apartment.query.get_or_404(apartment_id)
    
    # Check if user has approved investment in this apartment
    approved_request = InvestmentRequest.query.filter_by(
        user_id=current_user.id,
        apartment_id=apartment_id,
        status='approved'
    ).first()
    
    if not approved_request:
        flash('يجب أن يتم قبول استثمارك أولاً للحصول على رابط إحالة', 'error')
        return redirect(url_for('user_views.my_investments'))
    
    # Get or create referral code
    referral_code = current_user.get_or_create_referral_code(apartment_id)
    referral_link = url_for('main.referred_investment', 
                            apartment_id=apartment_id, 
                            ref=referral_code, 
                            _external=True)
    
    return render_template('user/referral_link.html',
                         apartment=apartment,
                         referral_code=referral_code,
                         referral_link=referral_link)


@bp.route('/refer-car/<int:car_id>')
@login_required
def get_referral_link_car(car_id):
    """Generate and display referral link for a car"""
    car = Car.query.get_or_404(car_id)

    approved_request = CarInvestmentRequest.query.filter_by(
        user_id=current_user.id,
        car_id=car_id,
        status='approved'
    ).first()

    if not approved_request:
        flash('يجب أن يتم قبول استثمارك أولاً للحصول على رابط إحالة', 'error')
        return redirect(url_for('user_views.my_investments'))

    # Get or create referral code for car
    node = CarReferralTree.query.filter_by(user_id=current_user.id, car_id=car_id).first()
    if not node:
        # Create a root node with a new referral code
        import secrets
        node = CarReferralTree(
            user_id=current_user.id,
            car_id=car_id,
            level=0,
            referral_code=f"REF{current_user.id}CAR{car_id}{secrets.token_hex(4).upper()}"
        )
        db.session.add(node)
        db.session.commit()

    referral_code = node.referral_code
    referral_link = url_for('main.referred_investment_car', car_id=car_id, ref=referral_code, _external=True)

    return render_template('user/referral_link_car.html',
                         car=car,
                         referral_code=referral_code,
                         referral_link=referral_link)


@bp.route('/delete-account', methods=['GET', 'POST'])
@login_required
def delete_account():
    """Delete user account permanently"""
    if request.method == 'POST':
        password = request.form.get('password')
        confirmation = request.form.get('confirmation') 
        reason = request.form.get('reason')
        understand = request.form.get('understand')
        
        # Verify password
        if not current_user.check_password(password):
            flash('كلمة المرور غير صحيحة', 'error')
            return render_template('user/delete_account.html')
        
        # Verify confirmation text
        if confirmation != 'حذف الحساب':
            flash('يجب كتابة "حذف الحساب" بالضبط للتأكيد', 'error')
            return render_template('user/delete_account.html')
        
        # Check if user has remaining balance
        if current_user.wallet_balance > 0 or current_user.rewards_balance > 0:
            flash('يجب سحب جميع الأموال من المحفظة قبل حذف الحساب', 'error')
            return render_template('user/delete_account.html')
        
        # Store user info for logging
        user_email = current_user.email
        user_name = current_user.name
        user_id = current_user.id
        
        try:
            # Delete related records in proper order to avoid foreign key constraints
            
            # Delete car referral trees
            CarReferralTree.query.filter_by(user_id=user_id).delete()
            CarReferralTree.query.filter_by(referred_by_user_id=user_id).delete()
            
            # Delete referral trees
            from app.models import ReferralTree
            ReferralTree.query.filter_by(user_id=user_id).delete()
            ReferralTree.query.filter_by(referred_by_user_id=user_id).delete()
            
            # Delete car investment requests
            CarInvestmentRequest.query.filter_by(user_id=user_id).delete()
            CarInvestmentRequest.query.filter_by(referred_by_user_id=user_id).update({CarInvestmentRequest.referred_by_user_id: None})
            
            # Delete investment requests
            InvestmentRequest.query.filter_by(user_id=user_id).delete()
            InvestmentRequest.query.filter_by(referred_by_user_id=user_id).update({InvestmentRequest.referred_by_user_id: None})
            
            # Delete car shares
            CarShare.query.filter_by(user_id=user_id).delete()
            
            # Delete apartment shares  
            Share.query.filter_by(user_id=user_id).delete()
            
            # Delete transactions
            Transaction.query.filter_by(user_id=user_id).delete()
            
            # Finally delete the user account
            db.session.delete(current_user)
            db.session.commit()
            
            # Log the account deletion
            print(f"Account deleted: {user_name} ({user_email}) - Reason: {reason}")
            
            # Logout the user
            from flask_login import logout_user
            logout_user()
            
            flash('تم حذف حسابك نهائياً. نتمنى لك التوفيق في رحلتك القادمة.', 'success')
            return redirect(url_for('main.index'))
            
        except Exception as e:
            db.session.rollback()
            print(f"Error deleting account for {user_email}: {str(e)}")
            flash('حدث خطأ أثناء حذف الحساب. يرجى المحاولة لاحقاً أو التواصل مع الدعم.', 'error')
            return render_template('user/delete_account.html')
    
    return render_template('user/delete_account.html')
