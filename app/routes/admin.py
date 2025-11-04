"""
Admin dashboard routes
Full CRUD operations for apartments, users, and system management
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, TextAreaField, SelectField
from wtforms.validators import Optional
from werkzeug.utils import secure_filename
from app.models import db, Apartment, User, Share, Transaction, InvestmentRequest
from datetime import datetime
import os

bp = Blueprint('admin', __name__, url_prefix='/admin')


# Admin Forms
class UpdateStatusForm(FlaskForm):
    status = SelectField('الحالة', choices=[
        ('pending', 'قيد الانتظار'),
        ('under_review', 'قيد المراجعة'),
        ('approved', 'تمت الموافقة'),
        ('rejected', 'مرفوض'),
        ('documents_missing', 'مستندات ناقصة')
    ])
    admin_notes = TextAreaField('ملاحظات الإدارة', validators=[Optional()])
    missing_documents = TextAreaField('المستندات الناقصة', validators=[Optional()])


class UploadContractForm(FlaskForm):
    contract_file = FileField('ملف العقد', validators=[
        FileRequired(message='مطلوب'),
        FileAllowed(['pdf'], 'PDF فقط')
    ])


def admin_required(f):
    """Decorator to require admin access"""
    from functools import wraps
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash('الوصول مرفوض - صلاحيات المسؤول مطلوبة', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function


@bp.route('/dashboard')
@admin_required
def dashboard():
    """Admin dashboard with statistics"""
    # Calculate statistics
    total_users = User.query.filter_by(is_admin=False).count()
    total_apartments = Apartment.query.count()
    total_shares_sold = db.session.query(db.func.count(Share.id)).scalar()
    total_revenue = db.session.query(db.func.sum(Share.share_price)).scalar() or 0
    
    # Investment request statistics
    pending_requests = InvestmentRequest.query.filter_by(status='pending').count()
    under_review_requests = InvestmentRequest.query.filter_by(status='under_review').count()
    
    # Referral rewards statistics
    users_with_rewards = User.query.filter(User.rewards_balance > 0).count()
    
    # Recent activity
    recent_transactions = Transaction.query.order_by(db.desc(Transaction.date)).limit(10).all()
    recent_users = User.query.filter_by(is_admin=False).order_by(db.desc(User.date_joined)).limit(5).all()
    
    # Apartment statistics
    apartments = Apartment.query.all()
    active_apartments = [apt for apt in apartments if not apt.is_closed]
    closed_apartments = [apt for apt in apartments if apt.is_closed]
    
    stats = {
        'total_users': total_users,
        'total_apartments': total_apartments,
        'active_apartments': len(active_apartments),
        'closed_apartments': len(closed_apartments),
        'total_shares_sold': total_shares_sold,
        'total_revenue': total_revenue,
        'pending_requests': pending_requests,
        'under_review_requests': under_review_requests,
        'users_with_rewards': users_with_rewards
    }
    
    return render_template('admin/dashboard.html',
                         stats=stats,
                         recent_transactions=recent_transactions,
                         recent_users=recent_users)


# ============= APARTMENT MANAGEMENT =============

@bp.route('/apartments')
@admin_required
def apartments():
    """List all apartments"""
    apartments = Apartment.query.order_by(db.desc(Apartment.date_created)).all()
    return render_template('admin/apartments.html', apartments=apartments)


@bp.route('/apartments/add', methods=['GET', 'POST'])
@admin_required
def add_apartment():
    """Add new apartment"""
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        total_price = float(request.form.get('total_price'))
        total_shares = int(request.form.get('total_shares'))
        monthly_rent = float(request.form.get('monthly_rent'))
        location = request.form.get('location')
        
        # Handle image upload
        image_filename = 'default_apartment.jpg'
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                image_filename = f"{timestamp}_{filename}"
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], image_filename))
        
        apartment = Apartment(
            title=title,
            description=description,
            image=image_filename,
            total_price=total_price,
            total_shares=total_shares,
            shares_available=total_shares,
            monthly_rent=monthly_rent,
            location=location
        )
        
        db.session.add(apartment)
        db.session.commit()
        
        flash('تم إضافة الشقة بنجاح', 'success')
        return redirect(url_for('admin.apartments'))
    
    return render_template('admin/apartment_form.html', apartment=None)


@bp.route('/apartments/edit/<int:apartment_id>', methods=['GET', 'POST'])
@admin_required
def edit_apartment(apartment_id):
    """Edit existing apartment"""
    apartment = Apartment.query.get_or_404(apartment_id)
    
    if request.method == 'POST':
        apartment.title = request.form.get('title')
        apartment.description = request.form.get('description')
        apartment.total_price = float(request.form.get('total_price'))
        apartment.total_shares = int(request.form.get('total_shares'))
        apartment.monthly_rent = float(request.form.get('monthly_rent'))
        apartment.location = request.form.get('location')
        
        # Handle image upload
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                image_filename = f"{timestamp}_{filename}"
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], image_filename))
                apartment.image = image_filename
        
        db.session.commit()
        flash('تم تحديث الشقة بنجاح', 'success')
        return redirect(url_for('admin.apartments'))
    
    return render_template('admin/apartment_form.html', apartment=apartment)


@bp.route('/apartments/delete/<int:apartment_id>', methods=['POST'])
@admin_required
def delete_apartment(apartment_id):
    """Delete apartment"""
    apartment = Apartment.query.get_or_404(apartment_id)
    
    # Check if apartment has shares sold
    if apartment.shares.count() > 0:
        flash('لا يمكن حذف شقة تم بيع حصص فيها', 'error')
        return redirect(url_for('admin.apartments'))
    
    db.session.delete(apartment)
    db.session.commit()
    
    flash('تم حذف الشقة بنجاح', 'success')
    return redirect(url_for('admin.apartments'))


@bp.route('/apartments/close/<int:apartment_id>', methods=['POST'])
@admin_required
def close_apartment(apartment_id):
    """Manually close an apartment"""
    apartment = Apartment.query.get_or_404(apartment_id)
    apartment.is_closed = True
    db.session.commit()
    
    flash(f'تم إغلاق الشقة: {apartment.title}', 'success')
    return redirect(url_for('admin.apartments'))


@bp.route('/apartments/reopen/<int:apartment_id>', methods=['POST'])
@admin_required
def reopen_apartment(apartment_id):
    """Reopen a closed apartment"""
    apartment = Apartment.query.get_or_404(apartment_id)
    if apartment.shares_available > 0:
        apartment.is_closed = False
        db.session.commit()
        flash(f'تم إعادة فتح الشقة: {apartment.title}', 'success')
    else:
        flash('لا يمكن فتح شقة ليس بها حصص متاحة', 'error')
    
    return redirect(url_for('admin.apartments'))


# ============= USER MANAGEMENT =============

@bp.route('/users')
@admin_required
def users():
    """List all users"""
    users = User.query.filter_by(is_admin=False).order_by(db.desc(User.date_joined)).all()
    return render_template('admin/users.html', users=users)


@bp.route('/users/<int:user_id>')
@admin_required
def user_detail(user_id):
    """View user details and investments"""
    user = User.query.get_or_404(user_id)
    
    # Get user's investments
    shares = Share.query.filter_by(user_id=user_id).all()
    transactions = Transaction.query.filter_by(user_id=user_id).order_by(db.desc(Transaction.date)).all()
    
    # Group shares by apartment
    investments = {}
    for share in shares:
        apt_id = share.apartment_id
        if apt_id not in investments:
            investments[apt_id] = {
                'apartment': share.apartment,
                'shares_count': 0,
                'total_invested': 0
            }
        investments[apt_id]['shares_count'] += 1
        investments[apt_id]['total_invested'] += share.share_price
    
    return render_template('admin/user_detail.html',
                         user=user,
                         investments=investments.values(),
                         transactions=transactions)


@bp.route('/users/delete/<int:user_id>', methods=['POST'])
@admin_required
def delete_user(user_id):
    """Delete user (only if no investments)"""
    user = User.query.get_or_404(user_id)
    
    if user.is_admin:
        flash('لا يمكن حذف حساب المسؤول', 'error')
        return redirect(url_for('admin.users'))
    
    if user.shares.count() > 0:
        flash('لا يمكن حذف مستخدم لديه استثمارات', 'error')
        return redirect(url_for('admin.users'))
    
    db.session.delete(user)
    db.session.commit()
    
    flash('تم حذف المستخدم بنجاح', 'success')
    return redirect(url_for('admin.users'))


# ============= TRANSACTION MANAGEMENT =============

@bp.route('/transactions')
@admin_required
def transactions():
    """View all transactions"""
    page = request.args.get('page', 1, type=int)
    transactions = Transaction.query.order_by(db.desc(Transaction.date)).paginate(
        page=page, per_page=50, error_out=False
    )
    return render_template('admin/transactions.html', transactions=transactions)


# ============= PAYOUT MANAGEMENT =============

@bp.route('/payouts')
@admin_required
def payouts():
    """Payout management page"""
    # Closed apartments (fully sold)
    closed_apartments = Apartment.query.filter_by(is_closed=True).all()
    # Eligible active apartments (partially sold but with investors)
    eligible_apartments = Apartment.query.filter(
        Apartment.is_closed == False,
        Apartment.shares_available < Apartment.total_shares
    ).all()

    return render_template('admin/payouts.html', 
                         closed_apartments=closed_apartments,
                         eligible_apartments=eligible_apartments)


@bp.route('/payouts/distribute/<int:apartment_id>', methods=['POST'])
@admin_required
def distribute_payout(apartment_id):
    """Manually trigger payout for specific apartment"""
    apartment = Apartment.query.get_or_404(apartment_id)
    # Allow payouts for any apartment with investors (shares sold)
    if apartment.shares.count() == 0:
        flash('لا يمكن توزيع الإيجار على شقة بدون مستثمرين', 'error')
        return redirect(url_for('admin.payouts'))

    payouts = apartment.distribute_monthly_rent()
    db.session.commit()
    
    flash(f'تم توزيع {payouts} دفعة بنجاح للشقة: {apartment.title}', 'success')
    return redirect(url_for('admin.payouts'))


@bp.route('/payouts/distribute-all', methods=['POST'])
@admin_required
def distribute_all_payouts():
    """Distribute payouts to all closed apartments"""
    # Distribute to all apartments that have investors (shares sold), whether closed or active
    apartments = Apartment.query.filter(
        Apartment.shares_available < Apartment.total_shares
    ).all()
    total_payouts = 0
    
    for apartment in apartments:
        if apartment.shares.count() > 0:
            payouts = apartment.distribute_monthly_rent()
            total_payouts += payouts
    
    db.session.commit()
    
    flash(f'تم توزيع {total_payouts} دفعة بنجاح على جميع الشقق', 'success')
    return redirect(url_for('admin.payouts'))


# Investment Requests Management

@bp.route('/investment-requests')
@admin_required
def investment_requests():
    """List all investment requests with filters"""
    status_filter = request.args.get('status', 'all')
    page = request.args.get('page', 1, type=int)
    
    query = InvestmentRequest.query
    
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    
    pagination = query.order_by(db.desc(InvestmentRequest.date_submitted))\
        .paginate(page=page, per_page=20, error_out=False)
    
    # Get counts for each status
    all_count = InvestmentRequest.query.count()
    pending_count = InvestmentRequest.query.filter_by(status='pending').count()
    under_review_count = InvestmentRequest.query.filter_by(status='under_review').count()
    approved_count = InvestmentRequest.query.filter_by(status='approved').count()
    rejected_count = InvestmentRequest.query.filter_by(status='rejected').count()
    
    return render_template('admin/investment_requests.html',
                         requests=pagination.items,
                         pagination=pagination,
                         status_filter=status_filter,
                         all_count=all_count,
                         pending_count=pending_count,
                         under_review_count=under_review_count,
                         approved_count=approved_count,
                         rejected_count=rejected_count)


@bp.route('/investment-request/<int:request_id>')
@admin_required
def review_investment_request(request_id):
    """Review specific investment request"""
    inv_request = InvestmentRequest.query.get_or_404(request_id)
    status_form = UpdateStatusForm(obj=inv_request)
    contract_form = UploadContractForm()
    
    return render_template('admin/review_investment_request.html',
                         request=inv_request,
                         status_form=status_form,
                         contract_form=contract_form)


@bp.route('/investment-request/<int:request_id>/update-status', methods=['POST'])
@admin_required
def update_investment_request_status(request_id):
    """Update investment request status"""
    inv_request = InvestmentRequest.query.get_or_404(request_id)
    form = UpdateStatusForm()
    
    if form.validate_on_submit():
        inv_request.status = form.status.data
        inv_request.admin_notes = form.admin_notes.data
        inv_request.missing_documents = form.missing_documents.data
        inv_request.date_reviewed = datetime.utcnow()
        inv_request.reviewed_by = current_user.id
        
        db.session.commit()
        
        flash('تم تحديث حالة الطلب بنجاح', 'success')
    else:
        flash('حدث خطأ في تحديث الحالة', 'error')
    
    return redirect(url_for('admin.review_investment_request', request_id=request_id))


@bp.route('/investment-request/<int:request_id>/upload-contract', methods=['POST'])
@admin_required
def upload_contract(request_id):
    """Upload contract PDF for investment request"""
    inv_request = InvestmentRequest.query.get_or_404(request_id)
    form = UploadContractForm()
    
    if form.validate_on_submit():
        # Create contracts directory if it doesn't exist - use absolute path
        contracts_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'contracts')
        os.makedirs(contracts_dir, exist_ok=True)
        
        # Save contract file
        contract_file = form.contract_file.data
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = secure_filename(f"contract_{request_id}_{timestamp}_{contract_file.filename}")
        filepath = os.path.join(contracts_dir, filename)
        contract_file.save(filepath)
        
        # Update request
        inv_request.contract_pdf = filename
        db.session.commit()
        
        flash('تم رفع العقد بنجاح', 'success')
    else:
        flash('حدث خطأ في رفع العقد', 'error')
    
    return redirect(url_for('admin.review_investment_request', request_id=request_id))


@bp.route('/investment-request/<int:request_id>/approve', methods=['POST'])
@admin_required
def approve_investment_request(request_id):
    """Quick approve investment request"""
    from app.models import ReferralTree, Share
    
    inv_request = InvestmentRequest.query.get_or_404(request_id)
    
    inv_request.status = 'approved'
    inv_request.date_reviewed = datetime.utcnow()
    inv_request.reviewed_by = current_user.id
    
    # Calculate investment amount
    apartment = inv_request.apartment
    investment_amount = apartment.share_price * inv_request.shares_requested
    
    # Create Share records for the approved investment
    for _ in range(inv_request.shares_requested):
        share = Share(
            user_id=inv_request.user_id,
            apartment_id=inv_request.apartment_id,
            share_price=apartment.share_price
        )
        db.session.add(share)
    
    # Update available shares
    apartment.shares_available -= inv_request.shares_requested
    
    # Close apartment if all shares sold
    if apartment.shares_available <= 0:
        apartment.is_closed = True
    
    # Add investor to referral tree if referred
    if inv_request.referred_by_user_id:
        # Get referrer's tree node
        referrer_tree = ReferralTree.query.filter_by(
            user_id=inv_request.referred_by_user_id,
            apartment_id=inv_request.apartment_id
        ).first()
        
        if referrer_tree:
            # Use session.no_autoflush to avoid premature flush and UNIQUE constraint error
            with db.session.no_autoflush:
                # Check if investor already has a tree node for this apartment
                investor_tree = ReferralTree.query.filter_by(
                    user_id=inv_request.user_id,
                    apartment_id=inv_request.apartment_id
                ).first()
                
                if investor_tree:
                    # User already has a tree node - update it with referral info
                    investor_tree.referred_by_user_id = inv_request.referred_by_user_id
                    investor_tree.level = referrer_tree.level + 1
                else:
                    # Create new tree node for investor
                    investor_tree = ReferralTree(
                        user_id=inv_request.user_id,
                        apartment_id=inv_request.apartment_id,
                        referred_by_user_id=inv_request.referred_by_user_id,
                        level=referrer_tree.level + 1
                    )
                    investor_tree.referral_code = inv_request.user.get_or_create_referral_code(investor_tree.apartment_id)
                    db.session.add(investor_tree)

            # Distribute rewards up the referral tree
            upline = referrer_tree.get_upline(max_levels=10)
            upline.insert(0, referrer_tree)  # Include direct referrer

            for level, node in enumerate(upline):
                # Calculate reward: 0.05% for level 0, 0.005% for level 1, etc.
                reward_percentage = 0.05 * (0.1 ** level)  # 0.05%, 0.005%, 0.0005%, etc.
                reward_amount = investment_amount * (reward_percentage / 100)

                if reward_amount > 0:
                    # Add reward to user's rewards balance
                    upline_user = User.query.get(node.user_id)
                    upline_user.add_rewards(
                        reward_amount, 
                        f'إحالة من {inv_request.user.name} - {apartment.title}'
                    )

                    # Update tree node's total rewards
                    node.total_rewards_earned += reward_amount
    
    db.session.commit()
    
    flash(f'تمت الموافقة على الطلب #{request_id}', 'success')
    if inv_request.referred_by_user_id:
        flash(f'تم توزيع مكافآت الإحالة على السلسلة', 'info')
    
    return redirect(url_for('admin.review_investment_request', request_id=request_id))


@bp.route('/investment-request/<int:request_id>/reject', methods=['POST'])
@admin_required
def reject_investment_request(request_id):
    """Quick reject investment request"""
    inv_request = InvestmentRequest.query.get_or_404(request_id)
    
    inv_request.status = 'rejected'
    inv_request.date_reviewed = datetime.utcnow()
    inv_request.reviewed_by = current_user.id
    
    db.session.commit()
    
    flash(f'تم رفض الطلب #{request_id}', 'success')
    return redirect(url_for('admin.review_investment_request', request_id=request_id))


# ============= REFERRAL REWARDS MANAGEMENT =============

@bp.route('/users-with-rewards')
@admin_required
def users_with_rewards():
    """List all users with pending referral rewards"""
    users = User.query.filter(User.rewards_balance > 0).order_by(User.rewards_balance.desc()).all()
    
    return render_template('admin/users_rewards.html', users=users)


@bp.route('/payout-rewards/<int:user_id>', methods=['POST'])
@admin_required
def payout_rewards(user_id):
    """Transfer rewards from rewards_balance to wallet_balance"""
    user = User.query.get_or_404(user_id)
    
    if user.rewards_balance <= 0:
        flash('لا توجد مكافآت متاحة للدفع', 'error')
        return redirect(url_for('admin.users_with_rewards'))
    
    amount = user.rewards_balance
    
    # Transfer from rewards to wallet
    user.wallet_balance += amount
    user.rewards_balance = 0
    
    # Create transaction record
    transaction = Transaction(
        user_id=user.id,
        transaction_type='reward_payout',
        amount=amount,
        description=f'صرف مكافآت الإحالة - {amount:.2f} جنيه'
    )
    db.session.add(transaction)
    db.session.commit()
    
    flash(f'تم صرف {amount:.2f} جنيه من مكافآت الإحالة إلى محفظة {user.name}', 'success')
    return redirect(url_for('admin.users_with_rewards'))


@bp.route('/payout-partial-rewards/<int:user_id>', methods=['POST'])
@admin_required
def payout_partial_rewards(user_id):
    """Transfer partial amount from rewards_balance to wallet_balance"""
    user = User.query.get_or_404(user_id)
    
    amount = float(request.form.get('amount', 0))
    
    if amount <= 0:
        flash('المبلغ يجب أن يكون أكبر من صفر', 'error')
        return redirect(url_for('admin.users_with_rewards'))
    
    if amount > user.rewards_balance:
        flash('المبلغ أكبر من رصيد المكافآت المتاح', 'error')
        return redirect(url_for('admin.users_with_rewards'))
    
    # Transfer from rewards to wallet
    user.wallet_balance += amount
    user.rewards_balance -= amount
    
    # Create transaction record
    transaction = Transaction(
        user_id=user.id,
        transaction_type='reward_payout',
        amount=amount,
        description=f'صرف جزئي لمكافآت الإحالة - {amount:.2f} جنيه'
    )
    db.session.add(transaction)
    db.session.commit()
    
    flash(f'تم صرف {amount:.2f} جنيه من مكافآت الإحالة إلى محفظة {user.name}', 'success')
    return redirect(url_for('admin.users_with_rewards'))
