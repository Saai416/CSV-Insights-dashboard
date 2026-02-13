from datetime import datetime
from models import db

class ReportQuestion(db.Model):
    """Model for storing follow-up questions and AI answers."""
    
    __tablename__ = 'report_questions'
    
    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.Integer, db.ForeignKey('reports.id', ondelete='CASCADE'), nullable=False)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    # Relationship to Report (optional backref can be defined here or in Report)
    # report = db.relationship('Report', backref=db.backref('questions', lazy=True, cascade="all, delete-orphan"))
    
    def to_dict(self):
        """Convert question to dictionary."""
        return {
            'id': self.id,
            'report_id': self.report_id,
            'question': self.question,
            'answer': self.answer,
            'created_at': self.created_at.isoformat()
        }
