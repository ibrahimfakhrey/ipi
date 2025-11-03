"""
User-facing view routes
Dashboard, wallet, and share purchase functionality
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.models import db, Apartment, Share, Transaction
from sqlalchemy import desc

bp = Blueprint('user_views', __name__, url_prefix='/user')


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
    """Buy shares page and processing"""
    apartment = Apartment.query.get_or_404(apartment_id)
    
    if request.method == 'POST':
        num_shares = int(request.form.get('num_shares', 1))
        
        if num_shares < 1:
            flash('يجب شراء حصة واحدة على الأقل', 'error')
            return render_template('user/buy_shares.html', apartment=apartment)
        
        # Process purchase
        success, message = apartment.purchase_shares(current_user, num_shares)
        
        if success:
            db.session.commit()
            flash(message, 'success')
            return redirect(url_for('user_views.dashboard'))
        else:
            flash(message, 'error')
    
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
