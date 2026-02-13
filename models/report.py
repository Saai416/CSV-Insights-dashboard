from datetime import datetime
from models import db


class Report(db.Model):
    """Report model for storing CSV analysis results with structured data."""
    
    __tablename__ = 'reports'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    summary_data = db.Column(db.Text, nullable=False)  # JSON string of CSV summary stats
    insights_json = db.Column(db.Text, nullable=False)  # Structured JSON insights from LLM
    chart_data = db.Column(db.Text, nullable=True)  # JSON chart data
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    # Relationship to Questions
    questions = db.relationship('ReportQuestion', backref='report', lazy=True, cascade="all, delete-orphan")
    
    def to_dict(self):

        """Convert report to dictionary."""
        import json
        
        return {
            'id': self.id,
            'filename': self.filename,
            'summary_data': self.summary_data,
            'insights_json': json.loads(self.insights_json) if self.insights_json else {},
            'chart_data': json.loads(self.chart_data) if self.chart_data else {},
            'created_at': self.created_at.isoformat()
        }
    
    @staticmethod
    def cleanup_old_reports(max_reports=5):
        """Delete old reports, keeping only the most recent ones.
        
        Args:
            max_reports: Maximum number of reports to keep
        """
        try:
            total_reports = Report.query.count()
            
            if total_reports > max_reports:
                # Get reports to delete (oldest ones)
                reports_to_delete = Report.query.order_by(
                    Report.created_at.asc()
                ).limit(total_reports - max_reports).all()
                
                for report in reports_to_delete:
                    db.session.delete(report)
                
                db.session.commit()
                return len(reports_to_delete)
            
            return 0
            
        except Exception as e:
            db.session.rollback()
            print(f"Error during cleanup: {str(e)}")
            return 0
