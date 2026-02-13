"""Export service for generating downloadable reports."""
import json
from typing import Dict, Any


class ExportService:
    """Service for exporting reports in various formats."""
    
    @staticmethod
    def generate_text_report(report_data: Dict[str, Any]) -> str:
        """Generate plain text report from structured data.
        
        Args:
            report_data: Dict containing filename, summary_data, insights_json
            
        Returns:
            Formatted text report
        """
        try:
            filename = report_data.get('filename', 'Unknown')
            insights = report_data.get('insights_json', {})
            
            # Handle both dict and JSON string
            if isinstance(insights, str):
                insights = json.loads(insights)
            
            report_lines = []
            report_lines.append("=" * 60)
            report_lines.append("CSV INSIGHTS REPORT")
            report_lines.append("=" * 60)
            report_lines.append(f"File: {filename}")
            report_lines.append("")
            
            # Summary
            if insights.get('summary'):
                report_lines.append("EXECUTIVE SUMMARY")
                report_lines.append("-" * 60)
                report_lines.append(insights['summary'])
                report_lines.append("")
            
            # Key Trends
            if insights.get('key_trends'):
                report_lines.append("KEY TRENDS")
                report_lines.append("-" * 60)
                for i, trend in enumerate(insights['key_trends'], 1):
                    report_lines.append(f"{i}. {trend}")
                report_lines.append("")
            
            # Outliers
            if insights.get('outliers') and len(insights['outliers']) > 0:
                report_lines.append("OUTLIERS DETECTED")
                report_lines.append("-" * 60)
                for i, outlier in enumerate(insights['outliers'], 1):
                    report_lines.append(f"{i}. {outlier}")
                report_lines.append("")
            
            # Risks
            if insights.get('risks') and len(insights['risks']) > 0:
                report_lines.append("RISKS")
                report_lines.append("-" * 60)
                for i, risk in enumerate(insights['risks'], 1):
                    report_lines.append(f"{i}. {risk}")
                report_lines.append("")
            
            # Recommendations
            if insights.get('recommendations'):
                report_lines.append("RECOMMENDATIONS")
                report_lines.append("-" * 60)
                for i, rec in enumerate(insights['recommendations'], 1):
                    report_lines.append(f"{i}. {rec}")
                report_lines.append("")
            
            report_lines.append("=" * 60)
            report_lines.append("End of Report")
            report_lines.append("=" * 60)
            
            return "\n".join(report_lines)
            
        except Exception as e:
            return f"Error generating report: {str(e)}"
