from flask import Blueprint, jsonify, render_template_string
from services.health_service import HealthService

status_bp = Blueprint('status', __name__)


@status_bp.route('/status', methods=['GET'])
def get_status():
    """Health check endpoint - returns JSON.
    
    Never crashes. All checks wrapped in try/except.
    Returns valid JSON even if DB and LLM fail.
    
    Returns:
        JSON response with system health status
    """
    try:
        status = HealthService.get_full_status()
        return jsonify(status), 200
    except Exception as e:
        # Fail-safe: return degraded status even if health service fails
        return jsonify({
            'overall_status': 'unhealthy',
            'services': {
                'backend': {'status': 'down', 'response_time_ms': 0, 'error': 'System error'},
                'database': {'status': 'down', 'response_time_ms': 0, 'error': 'Unknown'},
                'llm': {'status': 'down', 'response_time_ms': 0, 'error': 'Unknown'}
            },
            'timestamp': 'N/A'
        }), 200


@status_bp.route('/status/ui', methods=['GET'])
def get_status_ui():
    """Health check UI - returns HTML page.
    
    Returns:
        HTML page with color-coded status display
    """
    try:
        status = HealthService.get_full_status()
        
        # Determine overall status color and icon
        overall = status['overall_status']
        if overall == 'healthy':
            overall_color = '#10b981'  # Green
            overall_icon = '✅'
        elif overall == 'degraded':
            overall_color = '#f59e0b'  # Yellow/Orange
            overall_icon = '⚠️'
        else:
            overall_color = '#ef4444'  # Red
            overall_icon = '❌'
        
        # Generate service status rows
        services_html = ''
        for service_name, service_data in status['services'].items():
            service_status = service_data.get('status', 'down')
            response_time = service_data.get('response_time_ms', 0)
            error = service_data.get('error', '')
            
            if service_status == 'up':
                status_icon = '✅'
                status_color = '#10b981'
            else:
                status_icon = '❌'
                status_color = '#ef4444'
            
            error_display = f'<br><small style="color: #ef4444;">Error: {error}</small>' if error else ''
            
            services_html += f'''
            <tr>
                <td style="padding: 12px; border-bottom: 1px solid #e5e7eb;">
                    <strong>{service_name.capitalize()}</strong>
                </td>
                <td style="padding: 12px; border-bottom: 1px solid #e5e7eb; color: {status_color};">
                    {status_icon} {service_status.upper()}
                </td>
                <td style="padding: 12px; border-bottom: 1px solid #e5e7eb;">
                    {response_time} ms{error_display}
                </td>
            </tr>
            '''
        
        html = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>System Health Status</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                    max-width: 800px;
                    margin: 50px auto;
                    padding: 20px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                }}
                .container {{
                    background: white;
                    border-radius: 12px;
                    box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                    padding: 30px;
                }}
                h1 {{
                    color: #1f2937;
                    margin-bottom: 10px;
                }}
                .status-badge {{
                    display: inline-block;
                    padding: 8px 16px;
                    border-radius: 20px;
                    font-weight: bold;
                    font-size: 18px;
                    margin: 20px 0;
                    background-color: {overall_color};
                    color: white;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                    background: white;
                    border-radius: 8px;
                    overflow: hidden;
                }}
                th {{
                    background: #f3f4f6;
                    padding: 12px;
                    text-align: left;
                    font-weight: 600;
                    color: #374151;
                }}
                .timestamp {{
                    color: #6b7280;
                    font-size: 14px;
                    margin-top: 20px;
                }}
                .refresh-info {{
                    background: #eff6ff;
                    padding: 12px;
                    border-radius: 8px;
                    border-left: 4px solid #3b82f6;
                    margin-top: 20px;
                    color: #1e40af;
                }}
            </style>
            <script>
                // Auto-refresh every 10 seconds
                setTimeout(function() {{
                    location.reload();
                }}, 10000);
            </script>
        </head>
        <body>
            <div class="container">
                <h1>🏥 System Health Status</h1>
                
                <div class="status-badge">
                    {overall_icon} Overall Status: {overall.upper()}
                </div>
                
                <table>
                    <thead>
                        <tr>
                            <th>Service</th>
                            <th>Status</th>
                            <th>Response Time</th>
                        </tr>
                    </thead>
                    <tbody>
                        {services_html}
                    </tbody>
                </table>
                
                <div class="refresh-info">
                    ℹ️ This page auto-refreshes every 10 seconds
                </div>
                
                <div class="timestamp">
                    Last updated: {status['timestamp']}
                </div>
            </div>
        </body>
        </html>
        '''
        
        return html, 200
        
    except Exception as e:
        # Fail-safe HTML
        return f'''
        <!DOCTYPE html>
        <html>
        <head><title>System Health Status - Error</title></head>
        <body style="font-family: sans-serif; padding: 50px;">
            <h1>❌ Health Check System Error</h1>
            <p>Unable to retrieve system status.</p>
        </body>
        </html>
        ''', 200
