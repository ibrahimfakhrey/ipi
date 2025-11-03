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
from app.models import db, Apartment, Share, Transaction, InvestmentRequest, User
from sqlalchemy import desc
import os
from datetime import datetime

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
    """User dashboard showing investments and statistics"""
    # Get user's shares grouped by apartment
    shares = Share.query.filter_by(user_id=current_user.id).all()
    
    # Group shares by apartment
    investments = {}
    for share in shares:
        apt_id = share.apartment_id
        if apt_id not in investments:
            apartment = share.apartment
            investments[apt_id] = {
                'apartment': apartment,
                'shares_count': 0,
                'total_invested': 0,
                'monthly_income': 0
            }
        investments[apt_id]['shares_count'] += 1
        investments[apt_id]['total_invested'] += share.share_price
        
        # Calculate monthly income
        apartment = share.apartment
        if apartment.total_shares > 0:
            share_percentage = 1 / apartment.total_shares
            investments[apt_id]['monthly_income'] += apartment.monthly_rent * share_percentage
    
    # Calculate totals
    total_invested = current_user.get_total_invested()
    expected_monthly = current_user.get_monthly_expected_income()
    
    # Get recent transactions
    recent_transactions = Transaction.query.filter_by(user_id=current_user.id)\
        .order_by(desc(Transaction.date)).limit(10).all()
    
    return render_template('user/dashboard.html',
                         investments=investments.values(),
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


@bp.route('/my-investments')
@login_required
def my_investments():
    """Detailed view of all user investments"""
    # Get user's shares grouped by apartment
    shares = Share.query.filter_by(user_id=current_user.id).all()
    
    # Group shares by apartment
    investments = {}
    for share in shares:
        apt_id = share.apartment_id
        if apt_id not in investments:
            apartment = share.apartment
            investments[apt_id] = {
                'apartment': apartment,
                'shares': [],
                'shares_count': 0,
                'total_invested': 0,
                'monthly_income': 0,
                'roi_percentage': 0
            }
        
        investments[apt_id]['shares'].append(share)
        investments[apt_id]['shares_count'] += 1
        investments[apt_id]['total_invested'] += share.share_price
        
        # Calculate monthly income
        apartment = share.apartment
        if apartment.total_shares > 0:
            share_percentage = 1 / apartment.total_shares
            monthly_per_share = apartment.monthly_rent * share_percentage
            investments[apt_id]['monthly_income'] += monthly_per_share
            
            # Calculate ROI
            if investments[apt_id]['total_invested'] > 0:
                yearly_income = monthly_per_share * 12 * investments[apt_id]['shares_count']
                investments[apt_id]['roi_percentage'] = (yearly_income / investments[apt_id]['total_invested']) * 100
    
    return render_template('user/my_investments.html',
                         investments=investments.values())


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
        
        # Save uploaded files
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
    """Show user's referral trees for all apartments they invested in"""
    from app.models import ReferralTree
    
    # Get all apartments where user has approved investments
    approved_requests = InvestmentRequest.query.filter_by(
        user_id=current_user.id,
        status='approved'
    ).all()
    
    trees = []
    for req in approved_requests:
        # Get or create referral code for this apartment
        referral_code = current_user.get_or_create_referral_code(req.apartment_id)
        
        # Get referral tree node
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
    
    return render_template('user/my_referrals.html', trees=trees)


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
