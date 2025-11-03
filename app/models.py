"""
Database models for the Apartment Sharing Platform
Defines User, Apartment, Share, and Transaction models
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

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
    password_hash = db.Column(db.String(200), nullable=False)
    wallet_balance = db.Column(db.Float, default=0.0)
    is_admin = db.Column(db.Boolean, default=False)
    date_joined = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    shares = db.relationship('Share', backref='investor', lazy='dynamic', cascade='all, delete-orphan')
    transactions = db.relationship('Transaction', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
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
    
    def __repr__(self):
        return f'<User {self.email}>'


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
