import os
from flask import Flask, jsonify, render_template
from flask_cors import CORS
from models import db
from models.report import Report
from models.question import ReportQuestion
from routes.status import status_bp
from routes.upload import upload_bp
from routes.reports import reports_bp
from routes.export import export_bp
from config import Config


def create_app():
    """Create and configure Flask application."""
    app = Flask(__name__, 
                static_folder='static',
                template_folder='templates')
    
    # Load configuration
    app.config.from_object(Config)
    Config.validate()
    
    # Enable CORS
    CORS(app)
    
    # Initialize database
    db.init_app(app)
    
    # Ensure data directory exists
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    from routes.questions import questions_bp
    
    # Register blueprints
    app.register_blueprint(status_bp)
    app.register_blueprint(upload_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(export_bp)
    app.register_blueprint(questions_bp)
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Endpoint not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500
    
    @app.errorhandler(413)
    def request_entity_too_large(error):
        return jsonify({'error': 'File too large. Maximum size is 5MB'}), 413
    
    # Homepage
    @app.route('/')
    def index():
        return render_template('index.html')
    
    return app


if __name__ == '__main__':
    app = create_app()
    
    # Ensure upload directory exists
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    
    print("\n" + "="*60)
    print("CSV INSIGHTS APPLICATION")
    print("="*60)
    print(f"Server starting on http://localhost:5000")
    print(f"Health Check: http://localhost:5000/status")
    print(f"Health UI: http://localhost:5000/status/ui")
    print("="*60 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=Config.DEBUG)
