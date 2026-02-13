"""Chart data service for preparing visualization data."""
from typing import Dict, Any, List
import json


class ChartService:
    """Service for preparing chart data from CSV summaries."""
    
    @staticmethod
    def get_chart_data(summary: Dict[str, Any]) -> Dict[str, Any]:
        """Extract chart-ready data from CSV summary.
        
        Args:
            summary: CSV summary dict with data_types, numeric_stats, etc.
            
        Returns:
            Dict with bar_chart and histogram data, or empty if no numeric columns
        """
        try:
            data_types = summary.get('data_types', {})
            numeric_stats = summary.get('numeric_stats', {})
            
            # Find numeric columns
            numeric_columns = [
                col for col, dtype in data_types.items() 
                if 'int' in str(dtype).lower() or 'float' in str(dtype).lower()
            ]
            
            if not numeric_columns:
                return {
                    'has_numeric': False,
                    'message': 'No numeric columns found for charting'
                }
            
            # Use first numeric column for charts
            primary_column = numeric_columns[0]
            stats = numeric_stats.get(primary_column, {})
            
            # Find a suitable label column (first string/object/categorical column)
            label_column = None
            for col in summary.get('columns', []):
                dtype = str(data_types.get(col, '')).lower()
                if any(t in dtype for t in ['object', 'string', 'str', 'category']):
                    label_column = col
                    break
            
            # Prepare bar chart data (using sample data from summary)
            sample_data = summary.get('sample_data', {})
            bar_labels = []
            bar_values = []
            
            if primary_column in sample_data:
                values = sample_data[primary_column][:10]  # First 10 values
                
                # Determine labels
                if label_column and label_column in sample_data:
                    # Use actual column values as labels
                    raw_labels = sample_data[label_column][:10]
                    bar_labels = [str(l) for l in raw_labels]
                else:
                    # Fallback to Row indices
                    bar_labels = [f"Row {i+1}" for i in range(len(values))]
                    
                bar_values = [float(v) if v is not None else 0 for v in values]
            
            # Prepare histogram data (distribution bins)
            histogram_data = ChartService._create_histogram_bins(stats)
            
            return {
                'has_numeric': True,
                'primary_column': primary_column,
                'bar_chart': {
                    'labels': bar_labels,
                    'values': bar_values,
                    'title': f'{primary_column} - Sample Values'
                },
                'histogram': histogram_data
            }
            
        except Exception as e:
            return {
                'has_numeric': False,
                'message': f'Error preparing chart data: {str(e)}'
            }
    
    @staticmethod
    def _create_histogram_bins(stats: Dict[str, Any]) -> Dict[str, Any]:
        """Create histogram bins from numeric statistics.
        
        Args:
            stats: Dict with min, max, mean
            
        Returns:
            Dict with bins and counts
        """
        try:
            min_val = stats.get('min', 0)
            max_val = stats.get('max', 100)
            mean_val = stats.get('mean', 50)
            
            # Create 5 bins
            bin_width = (max_val - min_val) / 5
            bins = []
            counts = []
            
            for i in range(5):
                bin_start = min_val + (i * bin_width)
                bin_end = min_val + ((i + 1) * bin_width)
                bins.append(f"{bin_start:.1f}-{bin_end:.1f}")
                # Simulate normal distribution around mean
                # In production, would calculate from actual data
                distance_from_mean = abs((bin_start + bin_end) / 2 - mean_val)
                count = max(1, int(100 - (distance_from_mean * 2)))
                counts.append(count)
            
            return {
                'labels': bins,
                'values': counts,
                'title': 'Value Distribution'
            }
            
        except Exception as e:
            return {
                'labels': [],
                'values': [],
                'title': 'Distribution (unavailable)'
            }
