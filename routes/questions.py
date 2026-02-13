from flask import Blueprint, request, jsonify
from models import db
from models.report import Report
from models.question import ReportQuestion
from services.llm_service import LLMService

questions_bp = Blueprint('questions', __name__)

@questions_bp.route('/api/questions/<int:report_id>', methods=['GET'])
def get_questions(report_id):
    """Get Q&A history for a report."""
    try:
        report = Report.query.get(report_id)
        if not report:
            return jsonify({'error': 'Report not found'}), 404
            
        questions = ReportQuestion.query.filter_by(report_id=report_id)\
            .order_by(ReportQuestion.created_at.asc()).all()
            
        return jsonify([q.to_dict() for q in questions]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@questions_bp.route('/api/questions/<int:report_id>', methods=['POST'])
def ask_question(report_id):
    """Ask a follow-up question with context."""
    try:
        data = request.json
        question_text = data.get('question')
        
        if not question_text or len(question_text) < 3:
            return jsonify({'error': 'Question must be at least 3 characters'}), 400
            
        if len(question_text) > 300:
            return jsonify({'error': 'Question too long (max 300 chars)'}), 400
            
        # Fetch report context
        report = Report.query.get(report_id)
        if not report:
            return jsonify({'error': 'Report not found'}), 404
            
        # Fetch last 5 questions for context
        history = ReportQuestion.query.filter_by(report_id=report_id)\
            .order_by(ReportQuestion.created_at.desc()).limit(5).all()
        history.reverse() # Chronological order
        
        # Prepare context for LLM
        context = {
            'summary': report.summary_data,
            'insights': report.insights_json,
            # Format history as strictly 'Q: ... A: ...' text
            'history': "\n".join([f"Q: {q.question}\nA: {q.answer}" for q in history])
        }
        
        try:
            # Call LLM
            llm_service = LLMService()
            # We reuse the existing answer_question method but we might need to modify it or the prompt
            # The current LLMService.answer_question takes (question, context_str)
            # We need to construct a rich context string
            
            full_context_str = f"""
Dataset Summary:
{context['summary']}

Key Insights:
{context['insights']}

Previous Q&A:
{context['history']}
"""
            # Call new robust method
            success, answer, error = llm_service.answer_with_context(question_text, full_context_str)
            
            if not success:
               return jsonify({'error': error}), 500
            
            # Save to DB
            new_q = ReportQuestion(
                report_id=report.id,
                question=question_text,
                answer=answer
            )
            db.session.add(new_q)
            db.session.commit()
            
            return jsonify(new_q.to_dict()), 201
            
        except Exception as e:
            return jsonify({'error': f"LLM Error: {str(e)}"}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500
