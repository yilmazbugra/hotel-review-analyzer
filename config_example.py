# Example Configuration File
# Copy this file to config.py and update with your actual values

class Config:
    # Secret key for Flask sessions and security
    SECRET_KEY = 'your-secret-key-here'
    
    # MySQL Database Configuration
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'your-username'
    MYSQL_PASSWORD = 'your-password'
    MYSQL_DB = 'hotel_system'
    
    # Flask-SQLAlchemy Configuration
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://your-username:your-password@localhost/hotel_system'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Email Configuration (if needed)
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'your-email@gmail.com'
    MAIL_PASSWORD = 'your-email-password'
    
    # API Keys (if needed)
    OPENAI_API_KEY = 'your-openai-api-key'
    
    # Debug mode (set to False in production)
    DEBUG = True
