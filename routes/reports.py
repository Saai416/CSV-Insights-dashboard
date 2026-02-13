from flask import Blueprint, jsonify
from models.report import Report

reports_bp = Blueprint('reports', __name__)


@reports_bp.route('/reports', methods=['GET'])
def get_all_reports():
    """Get all reports.
    
    Returns:
        JSON list of all reports
    """
    try:
        reports = Report.query.order_by(Report.created_at.desc()).all()
        return jsonify({
            'success': True,
            'count': len(reports),
            'reports': [{
                'id': r.id,
                'filename': r.filename,
                'created_at': r.created_at.isoformat()
            } for r in reports]
        }), 200
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve reports'}), 500


@reports_bp.route('/reports/<int:report_id>', methods=['GET'])
def get_report(report_id):
    """Get specific report by ID.
    
    Args:
        report_id: Report ID
        
    Returns:
        JSON report data
    """
    try:
        report = Report.query.get(report_id)
        
        if not report:
            return jsonify({'error': 'Report not found'}), 404
        
        return jsonify({
            'success': True,
            'report': report.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve report'}), 500


@reports_bp.route('/reports/<int:report_id>/export', methods=['GET'])
def export_report(report_id):
    """Export report as JSON.
    
    Args:
        report_id: Report ID
        
    Returns:
        Complete report JSON for export
    """
    try:
        report = Report.query.get(report_id)
        
        if not report:
            return jsonify({'error': 'Report not found'}), 404
        
        # Return complete report data
        export_data = report.to_dict()
        
        return jsonify(export_data), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to export report'}), 500
