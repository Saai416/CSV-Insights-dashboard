import os
import json
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from models import db
from models.report import Report
from services.csv_service import CSVService
from services.llm_service import LLMService
from config import Config

upload_bp = Blueprint('upload', __name__)


def allowed_file(filename):
    """Check if file extension is allowed.
    
    Args:
        filename: Name of the file
        
    Returns:
        True if allowed, False otherwise
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS


@upload_bp.route('/upload', methods=['POST'])
def upload_file():
    """Upload and analyze CSV file.
    
    Defensive checks:
    - File presence validation
    - MIME type checking
    - Extension validation
    - Size limit (5MB via Flask config)
    - Uses secure_filename to prevent path traversal
    - Defensive CSV parsing
    - LLM error handling
    - Database insertion with error handling
    - Auto-cleanup of old reports
    
    Returns:
        JSON response with insights and report ID
    """
    # Check if file is present
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    # Check if file is selected
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Validate file type by extension
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Only CSV files are allowed'}), 400
    
    # Additional MIME type check
    if file.content_type and not file.content_type.startswith('text/'):
        # Be lenient with MIME types as they can vary
        # but reject obvious non-text types
        if not any(t in file.content_type for t in ['csv', 'plain', 'ms-excel']):
            return jsonify({'error': 'Invalid MIME type. Expected CSV file'}), 400
    
    try:
        # Use secure_filename to prevent path traversal
        filename = secure_filename(file.filename)
        
        # Ensure upload directory exists
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        
        # Save file temporarily
        filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # Check file size (additional check beyond Flask's MAX_CONTENT_LENGTH)
        file_size = os.path.getsize(filepath)
        if file_size > Config.MAX_CONTENT_LENGTH:
            os.remove(filepath)
            return jsonify({'error': f'File too large. Maximum size is {Config.MAX_CONTENT_LENGTH // (1024*1024)}MB'}), 400
        
        if file_size == 0:
            os.remove(filepath)
            return jsonify({'error': 'File is empty'}), 400
        
        
        # Parse CSV with defensive error handling
        csv_service = CSVService()
        success, summary, error_msg = csv_service.parse_csv(filepath)
        
        if not success:
            os.remove(filepath)
            return jsonify({'error': error_msg}), 400
        
        # Generate insights via LLM (returns structured dict)
        llm_service = LLMService()
        success, insights_dict, error_msg = llm_service.generate_insights(summary)
        
        if not success:
            os.remove(filepath)
            return jsonify({'error': f'Failed to generate insights: {error_msg}'}), 500
        
        # Generate chart data
        from services.chart_service import ChartService
        chart_data = ChartService.get_chart_data(summary)
        
        # Store in database
        try:
            report = Report(
                filename=filename,
                summary_data=json.dumps(summary),
                insights_json=json.dumps(insights_dict),
                chart_data=json.dumps(chart_data)
            )
            db.session.add(report)
            db.session.commit()
            
            # Auto-cleanup old reports (keep only 5)
            Report.cleanup_old_reports(Config.MAX_STORED_REPORTS)
            
            # Clean up temporary file
            os.remove(filepath)
            
            return jsonify({
                'success': True,
                'report_id': report.id,
                'filename': filename,
                'insights': insights_dict,  # Return structured dict
                'summary': summary,
                'chart_data': chart_data,
                'warning': summary.get('warning', '')  # Pass warning to frontend
            }), 200
            
        except Exception as e:
            db.session.rollback()
            # Clean up file on database error
            if os.path.exists(filepath):
                os.remove(filepath)
            return jsonify({'error': 'Database error while storing report'}), 500
            
    except Exception as e:
        # Catch-all for unexpected errors
        return jsonify({'error': 'Unexpected error during file processing'}), 500


@upload_bp.route('/ask', methods=['POST'])
def ask_question():
    """Answer follow-up question about a report.
    
    Request body:
        {
            "report_id": int,
            "question": str
        }
    
    Returns:
        JSON response with answer
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Request body must be JSON'}), 400
        
        report_id = data.get('report_id')
        question = data.get('question')
        
        if not report_id or not question:
            return jsonify({'error': 'report_id and question are required'}), 400
        
        # Retrieve report
        report = Report.query.get(report_id)
        if not report:
            return jsonify({'error': 'Report not found'}), 404
        
        # Parse summary
        try:
            summary = json.loads(report.summary_data)
            insights = json.loads(report.insights_json)
        except json.JSONDecodeError:
            return jsonify({'error': 'Invalid report data'}), 500
        
        # Get answer from LLM
        llm_service = LLMService()
        success, answer, error_msg = llm_service.answer_question(
            summary, insights, question
        )
        
        if not success:
            return jsonify({'error': f'Failed to answer question: {error_msg}'}), 500
        
        return jsonify({
            'success': True,
            'answer': answer
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500
