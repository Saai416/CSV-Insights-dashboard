"""Export routes for downloading reports."""
from flask import Blueprint, jsonify, request, send_file
from models.report import Report
from services.export_service import ExportService
from io import BytesIO
import json


export_bp = Blueprint('export', __name__, url_prefix='/export')


@export_bp.route('/text', methods=['POST'])
def export_text():
    """Export report as formatted text.
    
    Request JSON:
        {report_id: int}
    
    Returns:
        JSON with formatted_text field
    """
    try:
        data = request.get_json()
        report_id = data.get('report_id')
        
        if not report_id:
            return jsonify({'error': 'report_id required'}), 400
        
        # Get report from database
        report = Report.query.get(report_id)
        if not report:
            return jsonify({'error': 'Report not found'}), 404
        
        # Generate formatted text
        report_data = {
            'filename': report.filename,
            'summary_data': report.summary_data,
            'insights_json': report.insights_json
        }
        
        formatted_text = ExportService.generate_text_report(report_data)
        
        return jsonify({
            'success': True,
            'formatted_text': formatted_text
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Export failed: {str(e)}'}), 500


@export_bp.route('/download', methods=['POST'])
def export_download():
    """Download report as text file.
    
    Request JSON:
        {report_id: int}
    
    Returns:
        Text file attachment
    """
    try:
        data = request.get_json()
        report_id = data.get('report_id')
        
        if not report_id:
            return jsonify({'error': 'report_id required'}), 400
        
        # Get report from database
        report = Report.query.get(report_id)
        if not report:
            return jsonify({'error': 'Report not found'}), 404
        
        # Generate formatted text
        report_data = {
            'filename': report.filename,
            'summary_data': report.summary_data,
            'insights_json': report.insights_json
        }
        
        formatted_text = ExportService.generate_text_report(report_data)
        
        # Create in-memory file
        file_buffer = BytesIO(formatted_text.encode('utf-8'))
        file_buffer.seek(0)
        
        # Generate filename
        safe_filename = report.filename.replace('.csv', '_report.txt')
        
        return send_file(
            file_buffer,
            mimetype='text/plain',
            as_attachment=True,
            download_name=safe_filename
        )
        
    except Exception as e:
        return jsonify({'error': f'Download failed: {str(e)}'}), 500
