"""
Database models for the Apartment Sharing Platform
Defines User, Apartment, Share, and Transaction models
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import secrets

# Initialize SQLAlchemy
db = SQLAlchemy()


class User(UserMixin, db.Model):
    """
    User model for both regular users and admins
    Stores user information and wallet balance
    """
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(200), nullable=True)  # Nullable for social auth users
    wallet_balance = db.Column(db.Float, default=0.0)
    rewards_balance = db.Column(db.Float, default=0.0)  # Separate balance for referral rewards
    is_admin = db.Column(db.Boolean, default=False)
    
    # Social Authentication Fields
    auth_provider = db.Column(db.String(20), default='email', index=True)  # 'email', 'google', 'apple'
    provider_user_id = db.Column(db.String(255), index=True)  # Unique ID from provider
    provider_email = db.Column(db.String(255))  # Email from provider
    date_joined = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Simple Referral System
    referral_number = db.Column(db.String(20), unique=True, index=True)  # Simple referral number like IPI000123
    
    # KYC Information
    phone = db.Column(db.String(20))
    national_id = db.Column(db.String(50))
    address = db.Column(db.Text)
    date_of_birth = db.Column(db.String(20))
    nationality = db.Column(db.String(50))
    occupation = db.Column(db.String(100))
    id_document_path = db.Column(db.String(300))  # Path to uploaded ID document
    
    # Relationships
    shares = db.relationship('Share', backref='investor', lazy='dynamic', cascade='all, delete-orphan')
    transactions = db.relationship('Transaction', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    investment_requests = db.relationship('InvestmentRequest', 
                                         foreign_keys='InvestmentRequest.user_id',
                                         backref='user', 
                                         lazy='dynamic', 
                                         cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set user password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify user password"""
        return check_password_hash(self.password_hash, password)
    
    def add_to_wallet(self, amount, transaction_type='rental_income'):
        """Add amount to user wallet and create transaction record"""
        self.wallet_balance += amount
        transaction = Transaction(
            user_id=self.id,
            amount=amount,
            transaction_type=transaction_type
        )
        db.session.add(transaction)
    
    def deduct_from_wallet(self, amount, transaction_type='share_purchase'):
        """Deduct amount from wallet and create transaction record"""
        if self.wallet_balance >= amount:
            self.wallet_balance -= amount
            transaction = Transaction(
                user_id=self.id,
                amount=-amount,
                transaction_type=transaction_type
            )
            db.session.add(transaction)
            return True
        return False
    
    def get_total_invested(self):
        """Calculate total amount invested by user"""
        return sum([share.share_price for share in self.shares])
    
    def get_monthly_expected_income(self):
        """Calculate expected monthly income from all investments"""
        total = 0
        for share in self.shares:
            apartment = share.apartment
            if apartment and apartment.total_shares > 0:
                share_percentage = 1 / apartment.total_shares
                total += apartment.monthly_rent * share_percentage
        return total
    
    def get_or_create_referral_code(self, apartment_id):
        """Get or create referral code for a specific apartment"""
        # Import here to avoid circular import
        from app.models import ReferralTree
        
        # Check if user already has a referral node for this apartment
        referral_node = ReferralTree.query.filter_by(
            user_id=self.id,
            apartment_id=apartment_id
        ).first()
        
        if referral_node:
            return referral_node.referral_code
        
        # Create new referral code
        referral_code = f"REF{self.id}APT{apartment_id}{secrets.token_hex(4).upper()}"
        
        # Create referral tree node
        new_node = ReferralTree(
            user_id=self.id,
            apartment_id=apartment_id,
            referral_code=referral_code,
            level=0  # Root level (will be updated if they were referred)
        )
        db.session.add(new_node)
        db.session.commit()
        
        return referral_code
    
    def add_rewards(self, amount, description='referral_reward'):
        """Add amount to rewards balance and create transaction"""
        self.rewards_balance += amount
        transaction = Transaction(
            user_id=self.id,
            amount=amount,
            transaction_type='reward',
            description=description
        )
        db.session.add(transaction)
    
    def generate_referral_number(self):
        """Generate unique referral number like 'IPI000123'"""
        if not self.referral_number:
            self.referral_number = f"IPI{str(self.id).zfill(6)}"
        return self.referral_number
    
    def link_social_account(self, provider, provider_user_id, provider_email):
        """Link social authentication account to existing user"""
        self.auth_provider = provider
        self.provider_user_id = provider_user_id
        self.provider_email = provider_email
    
    def __repr__(self):
        return f'<User {self.email}>'


class ApartmentImage(db.Model):
    """Stores additional images for apartments."""
    __tablename__ = 'apartment_images'

    id = db.Column(db.Integer, primary_key=True)
    apartment_id = db.Column(db.Integer, db.ForeignKey('apartments.id'), nullable=False, index=True)
    filename = db.Column(db.String(300), nullable=False)
    alt = db.Column(db.String(300))
    sort_order = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f'<ApartmentImage {self.filename} for Apt:{self.apartment_id}>'


class Apartment(db.Model):
    """
    Apartment model representing investment properties
    Each apartment can be divided into shares
    """
    __tablename__ = 'apartments'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(300), default='default_apartment.jpg')
    total_price = db.Column(db.Float, nullable=False)
    total_shares = db.Column(db.Integer, nullable=False)
    shares_available = db.Column(db.Integer, nullable=False)
    monthly_rent = db.Column(db.Float, nullable=False)
    location = db.Column(db.String(200), nullable=False)
    is_closed = db.Column(db.Boolean, default=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    last_payout_date = db.Column(db.DateTime)
    
    # Relationships
    shares = db.relationship('Share', backref='apartment', lazy='dynamic', cascade='all, delete-orphan')
    images_rel = db.relationship('ApartmentImage', backref='apartment', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def images(self):
        """Return ordered list of image filenames for this apartment."""
        return [img.filename for img in self.images_rel.order_by(ApartmentImage.sort_order).all()]
    
    @property
    def share_price(self):
        """Calculate price per share"""
        if self.total_shares > 0:
            return self.total_price / self.total_shares
        return 0
    
    @property
    def shares_sold(self):
        """Calculate number of shares sold"""
        return self.total_shares - self.shares_available
    
    @property
    def completion_percentage(self):
        """Calculate percentage of shares sold"""
        if self.total_shares > 0:
            return (self.shares_sold / self.total_shares) * 100
        return 0
    
    @property
    def investors_count(self):
        """Calculate number of unique investors"""
        return db.session.query(db.func.count(db.func.distinct(Share.user_id)))\
            .filter(Share.apartment_id == self.id).scalar() or 0
    
    @property
    def status(self):
        """Get apartment status in Arabic"""
        if self.is_closed or self.shares_available == 0:
            return 'مغلق'
        elif self.shares_available == self.total_shares:
            return 'جديد'
        else:
            return 'متاح'
    
    def can_purchase_shares(self, num_shares):
        """Check if specified number of shares can be purchased"""
        return not self.is_closed and self.shares_available >= num_shares
    
    def purchase_shares(self, user, num_shares):
        """Process share purchase for a user"""
        if not self.can_purchase_shares(num_shares):
            return False, "عدد الحصص غير متاح"
        
        total_cost = self.share_price * num_shares
        
        # Check if user has sufficient balance
        if user.wallet_balance < total_cost:
            return False, "رصيد المحفظة غير كافي"
        
        # Deduct from wallet
        user.deduct_from_wallet(total_cost, 'share_purchase')
        
        # Create share records
        for _ in range(num_shares):
            share = Share(
                user_id=user.id,
                apartment_id=self.id,
                share_price=self.share_price
            )
            db.session.add(share)
        
        # Update available shares
        self.shares_available -= num_shares
        
        # Close apartment if all shares sold
        if self.shares_available == 0:
            self.is_closed = True
        
        return True, "تم شراء الحصص بنجاح"
    
    def distribute_monthly_rent(self):
        """Distribute monthly rent to all shareholders"""
        if self.shares.count() == 0:
            return 0
        
        rent_per_share = self.monthly_rent / self.total_shares
        payouts = 0
        
        for share in self.shares:
            share.investor.add_to_wallet(rent_per_share, 'rental_income')
            payouts += 1
        
        self.last_payout_date = datetime.utcnow()
        return payouts
    
    def __repr__(self):
        return f'<Apartment {self.title}>'


class Share(db.Model):
    """
    Share model representing individual investment shares
    Links users to apartments
    """
    __tablename__ = 'shares'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    apartment_id = db.Column(db.Integer, db.ForeignKey('apartments.id'), nullable=False)
    share_price = db.Column(db.Float, nullable=False)
    date_purchased = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Share User:{self.user_id} Apartment:{self.apartment_id}>'


class Transaction(db.Model):
    """
    Transaction model for tracking all financial activities
    Includes deposits, withdrawals, purchases, and rental income
    """
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    transaction_type = db.Column(db.String(50), nullable=False)  # rental_income, share_purchase, deposit, withdrawal
    date = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.String(200))
    
    @property
    def type_arabic(self):
        """Get transaction type in Arabic"""
        types = {
            'rental_income': 'دخل إيجار',
            'share_purchase': 'شراء حصة',
            'deposit': 'إيداع',
            'withdrawal': 'سحب'
        }
        return types.get(self.transaction_type, self.transaction_type)
    
    def __repr__(self):
        return f'<Transaction {self.transaction_type}: {self.amount}>'


class InvestmentRequest(db.Model):
    """
    Investment Request model for KYC and investment approval process
    Stores user documents and admin approval workflow
    """
    __tablename__ = 'investment_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    apartment_id = db.Column(db.Integer, db.ForeignKey('apartments.id'), nullable=False)
    shares_requested = db.Column(db.Integer, nullable=False)
    referred_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # Who referred this user
    
    # KYC Documents
    full_name = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    national_id = db.Column(db.String(50), nullable=False)
    address = db.Column(db.Text, nullable=False)
    date_of_birth = db.Column(db.String(20), nullable=False)
    nationality = db.Column(db.String(50), nullable=False)
    occupation = db.Column(db.String(100), nullable=False)
    id_document_front = db.Column(db.String(300))  # Front of ID
    id_document_back = db.Column(db.String(300))   # Back of ID
    proof_of_address = db.Column(db.String(300))   # Utility bill, etc.
    
    # Request Status
    status = db.Column(db.String(50), default='pending')  # pending, under_review, approved, rejected, documents_missing
    admin_notes = db.Column(db.Text)
    missing_documents = db.Column(db.Text)  # Comma-separated list of missing docs
    contract_pdf = db.Column(db.String(300))  # Admin uploaded contract
    
    # Timestamps
    date_submitted = db.Column(db.DateTime, default=datetime.utcnow)
    date_reviewed = db.Column(db.DateTime)
    reviewed_by = db.Column(db.Integer, db.ForeignKey('users.id'))  # Admin who reviewed
    
    # Relationships
    apartment = db.relationship('Apartment', backref='investment_requests')
    reviewer = db.relationship('User', foreign_keys=[reviewed_by])
    referrer = db.relationship('User', foreign_keys=[referred_by_user_id], backref='referred_investments')
    
    @property
    def status_arabic(self):
        """Get status in Arabic"""
        statuses = {
            'pending': 'قيد الانتظار',
            'under_review': 'قيد المراجعة',
            'approved': 'تمت الموافقة',
            'rejected': 'مرفوض',
            'documents_missing': 'مستندات ناقصة'
        }
        return statuses.get(self.status, self.status)
    
    @property
    def total_amount(self):
        """Calculate total investment amount"""
        if self.apartment:
            return self.apartment.share_price * self.shares_requested
        return 0
    
    def __repr__(self):
        return f'<InvestmentRequest User:{self.user_id} Apartment:{self.apartment_id} Status:{self.status}>'


class ReferralTree(db.Model):
    """
    Referral Tree model to track multi-level referrals per apartment
    Each user can have multiple trees (one per apartment they invest in)
    """
    __tablename__ = 'referral_trees'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    apartment_id = db.Column(db.Integer, db.ForeignKey('apartments.id'), nullable=False)
    referred_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # Parent in the tree
    referral_code = db.Column(db.String(100), unique=True, nullable=False, index=True)  # Unique code for this user-apartment
    level = db.Column(db.Integer, default=0)  # 0 = root, 1 = direct referral, 2 = second level, etc.
    date_joined_tree = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Track total rewards earned from this tree branch
    total_rewards_earned = db.Column(db.Float, default=0.0)
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id], backref='referral_nodes')
    apartment = db.relationship('Apartment', backref='referral_tree_nodes')
    referred_by = db.relationship('User', foreign_keys=[referred_by_user_id])
    
    # Unique constraint: one entry per user per apartment
    __table_args__ = (db.UniqueConstraint('user_id', 'apartment_id', name='_user_apartment_uc'),)
    
    def get_upline(self, max_levels=10):
        """Get all users above this user in the tree"""
        upline = []
        current = self
        level = 0
        
        while current.referred_by_user_id and level < max_levels:
            parent = ReferralTree.query.filter_by(
                user_id=current.referred_by_user_id,
                apartment_id=current.apartment_id
            ).first()
            
            if parent:
                upline.append({
                    'user': parent.user,
                    'level': parent.level,
                    'referral_code': parent.referral_code,
                    'total_rewards_earned': parent.total_rewards_earned
                })
                current = parent
                level += 1
            else:
                break
        
        return upline
    
    def get_downline(self, max_levels=10):
        """Get all users below this user in the tree (recursive)"""
        def get_children(node, current_level=1):
            if current_level > max_levels:
                return []
            
            children = ReferralTree.query.filter_by(
                referred_by_user_id=node.user_id,
                apartment_id=node.apartment_id
            ).all()
            
            result = []
            for child in children:
                result.append({
                    'user': child.user,
                    'level': child.level,
                    'referral_code': child.referral_code,
                    'date_joined': child.date_joined_tree
                })
                # Recursively get children's children
                result.extend(get_children(child, current_level + 1))
            
            return result
        
        return get_children(self)
    
    def __repr__(self):
        return f'<ReferralTree User:{self.user_id} Apartment:{self.apartment_id} Level:{self.level}>'


# ===================== CARS DOMAIN MODELS =====================

class Car(db.Model):
    """
    Car model representing investable vehicles
    Mirrors Apartment model fields for consistency
    """
    __tablename__ = 'cars'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(300), default='default_car.jpg')
    total_price = db.Column(db.Float, nullable=False)
    total_shares = db.Column(db.Integer, nullable=False)
    shares_available = db.Column(db.Integer, nullable=False)
    monthly_rent = db.Column(db.Float, nullable=False)  # leasing/operations income
    location = db.Column(db.String(200), nullable=False)
    is_closed = db.Column(db.Boolean, default=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    last_payout_date = db.Column(db.DateTime)

    # Optional car-specific metadata
    brand = db.Column(db.String(100))
    model = db.Column(db.String(100))
    year = db.Column(db.String(10))

    # Relationships
    shares = db.relationship('CarShare', backref='car', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def share_price(self):
        if self.total_shares > 0:
            return self.total_price / self.total_shares
        return 0

    @property
    def shares_sold(self):
        return self.total_shares - self.shares_available

    @property
    def completion_percentage(self):
        if self.total_shares > 0:
            return (self.shares_sold / self.total_shares) * 100
        return 0

    @property
    def investors_count(self):
        return db.session.query(db.func.count(db.func.distinct(CarShare.user_id)))\
            .filter(CarShare.car_id == self.id).scalar() or 0

    @property
    def status(self):
        if self.is_closed or self.shares_available == 0:
            return 'مغلق'
        elif self.shares_available == self.total_shares:
            return 'جديد'
        else:
            return 'متاح'

    def can_purchase_shares(self, num_shares):
        return not self.is_closed and self.shares_available >= num_shares

    def purchase_shares(self, user, num_shares):
        if not self.can_purchase_shares(num_shares):
            return False, "عدد الحصص غير متاح"

        total_cost = self.share_price * num_shares
        if user.wallet_balance < total_cost:
            return False, "رصيد المحفظة غير كافي"

        user.deduct_from_wallet(total_cost, 'share_purchase')

        for _ in range(num_shares):
            share = CarShare(
                user_id=user.id,
                car_id=self.id,
                share_price=self.share_price
            )
            db.session.add(share)

        self.shares_available -= num_shares
        if self.shares_available == 0:
            self.is_closed = True

        return True, "تم شراء الحصص بنجاح"

    def distribute_monthly_rent(self):
        if self.shares.count() == 0:
            return 0

        rent_per_share = self.monthly_rent / self.total_shares
        payouts = 0

        for share in self.shares:
            share.investor.add_to_wallet(rent_per_share, 'rental_income')
            payouts += 1

        self.last_payout_date = datetime.utcnow()
        return payouts

    def __repr__(self):
        return f'<Car {self.title}>'


class CarShare(db.Model):
    """
    CarShare model linking users to cars via individual shares
    """
    __tablename__ = 'car_shares'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    car_id = db.Column(db.Integer, db.ForeignKey('cars.id'), nullable=False)
    share_price = db.Column(db.Float, nullable=False)
    date_purchased = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship back to user
    investor = db.relationship('User', backref=db.backref('car_shares', lazy='dynamic', cascade='all, delete-orphan'))

    def __repr__(self):
        return f'<CarShare User:{self.user_id} Car:{self.car_id}>'


class CarInvestmentRequest(db.Model):
    """
    Investment Request model for cars (mirrors InvestmentRequest)
    """
    __tablename__ = 'car_investment_requests'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    car_id = db.Column(db.Integer, db.ForeignKey('cars.id'), nullable=False)
    shares_requested = db.Column(db.Integer, nullable=False)
    referred_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    # KYC Documents
    full_name = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    national_id = db.Column(db.String(50), nullable=False)
    address = db.Column(db.Text, nullable=False)
    date_of_birth = db.Column(db.String(20), nullable=False)
    nationality = db.Column(db.String(50), nullable=False)
    occupation = db.Column(db.String(100), nullable=False)
    id_document_front = db.Column(db.String(300))
    id_document_back = db.Column(db.String(300))
    proof_of_address = db.Column(db.String(300))

    # Request Status
    status = db.Column(db.String(50), default='pending')
    admin_notes = db.Column(db.Text)
    missing_documents = db.Column(db.Text)
    contract_pdf = db.Column(db.String(300))

    # Timestamps
    date_submitted = db.Column(db.DateTime, default=datetime.utcnow)
    date_reviewed = db.Column(db.DateTime)
    reviewed_by = db.Column(db.Integer, db.ForeignKey('users.id'))

    # Relationships
    car = db.relationship('Car', backref='investment_requests')
    reviewer = db.relationship('User', foreign_keys=[reviewed_by])
    referrer = db.relationship('User', foreign_keys=[referred_by_user_id], backref='referred_car_investments')

    @property
    def status_arabic(self):
        statuses = {
            'pending': 'قيد الانتظار',
            'under_review': 'قيد المراجعة',
            'approved': 'تمت الموافقة',
            'rejected': 'مرفوض',
            'documents_missing': 'مستندات ناقصة'
        }
        return statuses.get(self.status, self.status)

    @property
    def total_amount(self):
        if self.car:
            return self.car.share_price * self.shares_requested
        return 0

    def __repr__(self):
        return f'<CarInvestmentRequest User:{self.user_id} Car:{self.car_id} Status:{self.status}>'


class CarReferralTree(db.Model):
    """
    Referral tree per car (mirrors ReferralTree)
    """
    __tablename__ = 'car_referral_trees'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    car_id = db.Column(db.Integer, db.ForeignKey('cars.id'), nullable=False)
    referred_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    referral_code = db.Column(db.String(100), unique=True, nullable=False, index=True)
    level = db.Column(db.Integer, default=0)
    date_joined_tree = db.Column(db.DateTime, default=datetime.utcnow)

    total_rewards_earned = db.Column(db.Float, default=0.0)

    # Relationships
    user = db.relationship('User', foreign_keys=[user_id], backref='car_referral_nodes')
    car = db.relationship('Car', backref='referral_tree_nodes')
    referred_by = db.relationship('User', foreign_keys=[referred_by_user_id])

    __table_args__ = (db.UniqueConstraint('user_id', 'car_id', name='_user_car_uc'),)

    def get_upline(self, max_levels=10):
        upline = []
        current = self
        level = 0

        while current.referred_by_user_id and level < max_levels:
            parent = CarReferralTree.query.filter_by(
                user_id=current.referred_by_user_id,
                car_id=current.car_id
            ).first()

            if parent:
                upline.append({
                    'user': parent.user,
                    'level': parent.level,
                    'referral_code': parent.referral_code,
                    'total_rewards_earned': parent.total_rewards_earned
                })
                current = parent
                level += 1
            else:
                break

        return upline

    def get_downline(self, max_levels=10):
        def get_children(node, current_level=1):
            if current_level > max_levels:
                return []

            children = CarReferralTree.query.filter_by(
                referred_by_user_id=node.user_id,
                car_id=node.car_id
            ).all()

            result = []
            for child in children:
                result.append({
                    'user': child.user,
                    'level': child.level,
                    'referral_code': child.referral_code,
                    'date_joined': child.date_joined_tree
                })
                result.extend(get_children(child, current_level + 1))

            return result

        return get_children(self)

    def __repr__(self):
        return f'<CarReferralTree User:{self.user_id} Car:{self.car_id} Level:{self.level}>'


class ReferralUsage(db.Model):
    """
    Simple referral tracking - records when someone uses a referral number
    Replaces complex MLM tree system with straightforward tracking
    """
    __tablename__ = 'referral_usages'
    
    id = db.Column(db.Integer, primary_key=True)
    referrer_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)  # Who's number was used
    referee_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)   # Who used the number
    asset_type = db.Column(db.String(20), nullable=False)  # 'apartment' or 'car'
    asset_id = db.Column(db.Integer, nullable=False)  # Which apartment/car ID
    investment_amount = db.Column(db.Float, nullable=False)  # How much they invested
    shares_purchased = db.Column(db.Integer, nullable=False)  # How many shares
    date_used = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    referrer = db.relationship('User', foreign_keys=[referrer_user_id], backref='referrals_given')
    referee = db.relationship('User', foreign_keys=[referee_user_id], backref='referrals_used')
    
    def __repr__(self):
        return f'<ReferralUsage Referrer:{self.referrer_user_id} Referee:{self.referee_user_id} Asset:{self.asset_type}:{self.asset_id}>'
