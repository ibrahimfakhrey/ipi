"""
Admin dashboard routes
Full CRUD operations for apartments, users, and system management
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.models import db, Apartment, User, Share, Transaction
from datetime import datetime
import os

bp = Blueprint('admin', __name__, url_prefix='/admin')


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
        'total_revenue': total_revenue
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
    closed_apartments = Apartment.query.filter_by(is_closed=True).all()
    return render_template('admin/payouts.html', apartments=closed_apartments)


@bp.route('/payouts/distribute/<int:apartment_id>', methods=['POST'])
@admin_required
def distribute_payout(apartment_id):
    """Manually trigger payout for specific apartment"""
    apartment = Apartment.query.get_or_404(apartment_id)
    
    if not apartment.is_closed:
        flash('يمكن توزيع الإيجار فقط على الشقق المغلقة', 'error')
        return redirect(url_for('admin.payouts'))
    
    payouts = apartment.distribute_monthly_rent()
    db.session.commit()
    
    flash(f'تم توزيع {payouts} دفعة بنجاح للشقة: {apartment.title}', 'success')
    return redirect(url_for('admin.payouts'))


@bp.route('/payouts/distribute-all', methods=['POST'])
@admin_required
def distribute_all_payouts():
    """Distribute payouts to all closed apartments"""
    apartments = Apartment.query.filter_by(is_closed=True).all()
    total_payouts = 0
    
    for apartment in apartments:
        payouts = apartment.distribute_monthly_rent()
        total_payouts += payouts
    
    db.session.commit()
    
    flash(f'تم توزيع {total_payouts} دفعة بنجاح على جميع الشقق', 'success')
    return redirect(url_for('admin.payouts'))
