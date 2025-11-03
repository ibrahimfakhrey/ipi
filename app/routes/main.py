"""
Main public routes
Landing page and market listings
"""
from flask import Blueprint, render_template, request
from app.models import Apartment, User
from sqlalchemy import desc

bp = Blueprint('main', __name__)


@bp.route('/')
def index():
    """Landing page with hero section and featured apartments"""
    # Get statistics for counters
    total_users = User.query.count()
    total_apartments = Apartment.query.count()
    total_invested = sum([apt.total_price - (apt.shares_available * apt.share_price) 
                         for apt in Apartment.query.all()])
    
    # Get featured apartments (newest and available)
    featured_apartments = Apartment.query.filter_by(is_closed=False)\
        .order_by(desc(Apartment.date_created)).limit(6).all()
    
    stats = {
        'users': total_users,
        'apartments': total_apartments,
        'invested': total_invested
    }
    
    return render_template('user/landing.html', 
                         stats=stats, 
                         featured_apartments=featured_apartments)


@bp.route('/market')
def market():
    """Market page showing all available apartments"""
    # Get filter parameters
    status_filter = request.args.get('status', 'all')
    location_filter = request.args.get('location', '')
    sort_by = request.args.get('sort', 'newest')
    
    # Base query
    query = Apartment.query
    
    # Apply filters
    if status_filter == 'available':
        query = query.filter(Apartment.is_closed == False, Apartment.shares_available > 0)
    elif status_filter == 'closed':
        query = query.filter(Apartment.is_closed == True)
    elif status_filter == 'new':
        query = query.filter(Apartment.shares_available == Apartment.total_shares)
    
    if location_filter:
        query = query.filter(Apartment.location.contains(location_filter))
    
    # Apply sorting
    if sort_by == 'newest':
        query = query.order_by(desc(Apartment.date_created))
    elif sort_by == 'price_low':
        query = query.order_by(Apartment.total_price)
    elif sort_by == 'price_high':
        query = query.order_by(desc(Apartment.total_price))
    elif sort_by == 'completion':
        query = query.order_by(Apartment.shares_available)
    
    apartments = query.all()
    
    # Get unique locations for filter dropdown
    locations = db.session.query(Apartment.location).distinct().all()
    locations = [loc[0] for loc in locations]
    
    return render_template('user/market.html', 
                         apartments=apartments,
                         locations=locations,
                         current_status=status_filter,
                         current_location=location_filter,
                         current_sort=sort_by)


@bp.route('/apartment/<int:apartment_id>')
def apartment_detail(apartment_id):
    """Apartment detail page"""
    apartment = Apartment.query.get_or_404(apartment_id)
    
    # Get investors count
    investors_count = db.session.query(db.func.count(db.distinct(Share.user_id)))\
        .filter(Share.apartment_id == apartment_id).scalar()
    
    return render_template('user/apartment_detail.html', 
                         apartment=apartment,
                         investors_count=investors_count)


@bp.route('/about')
def about():
    """About page"""
    return render_template('user/about.html')


@bp.route('/faq')
def faq():
    """FAQ page in Arabic"""
    faqs = [
        {
            'question': 'ما هي المنصة؟',
            'answer': 'منصة استثمار عقاري تتيح لك شراء حصص في العقارات والحصول على دخل شهري من الإيجار'
        },
        {
            'question': 'كيف أبدأ الاستثمار؟',
            'answer': 'سجل حسابك، اختر العقار المناسب، واشترِ الحصص التي تناسب ميزانيتك'
        },
        {
            'question': 'متى أحصل على العائد؟',
            'answer': 'يتم توزيع الإيجار الشهري على المستثمرين في أول كل شهر تلقائياً'
        },
        {
            'question': 'ما هو الحد الأدنى للاستثمار؟',
            'answer': 'يمكنك شراء حصة واحدة من أي عقار، والحد الأدنى يبدأ من 5,000 جنيه'
        },
        {
            'question': 'هل يمكنني بيع حصصي؟',
            'answer': 'حالياً، الاستثمار طويل الأجل مع عوائد شهرية ثابتة'
        }
    ]
    return render_template('user/faq.html', faqs=faqs)


# Import db and Share for apartment_detail route
from app.models import db, Share
