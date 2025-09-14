from flask import Flask, render_template, redirect, flash, url_for
from flask_login import LoginManager, login_required, current_user
from app.models import User, ReviewResult
from app.db import db

def create_app():
    app = Flask(__name__)

    # 📌 Gizli anahtar (oturum, güvenlik için)
    app.config['SECRET_KEY'] = '321312312312'

    # ✅ MySQL bağlantısı
    app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:bugra123@localhost/hotel_system"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # 📌 Veritabanını başlat
    db.init_app(app)

    # 🔐 Flask-Login yapılandırması
    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # 📁 Blueprint route'ları
    from app.routes.auth import auth
    from app.routes.gpt import gpt
    from app.routes.admin import admin_bp
    from app.routes.chat_bot import chat_bot_bp
    from app.routes.gpt_owner import gpt_owner
    from app.routes.analytics import analytics_bp

    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(gpt, url_prefix='/gpt')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(chat_bot_bp, url_prefix='/chat_bot')
    app.register_blueprint(gpt_owner, url_prefix='/gpt_owner')
    app.register_blueprint(analytics_bp)

    # 🌐 Ana sayfa yönlendirmesi
    @app.route('/')
    def home():
        return redirect('/auth/')

    # Hakkımızda sayfası
    @app.route('/about_us')
    def about_us():
        return render_template('about_us.html')

    # Platform sayfası
    @app.route('/platform')
    def platform():
        return render_template('platform.html')
    
    # Otel sahibi için analiz geçmişi
    @app.route("/owner_reviews")
    @login_required
    def owner_reviews():
        if current_user.role != 'owner':
            flash("You do not have permission to access this page.", "danger")
            return redirect(url_for('auth.login'))

        results = ReviewResult.query.filter_by(user_id=current_user.id).order_by(ReviewResult.created_at.desc()).all()
        return render_template("owner_reviews.html", results=results)

    # 📌 Tabloları oluştur
    with app.app_context():
        db.create_all()

    return app
