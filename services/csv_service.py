import pandas as pd
from typing import Dict, Any, Tuple


class CSVService:
    """Service for defensive CSV parsing and analysis."""
    
    @staticmethod
    def parse_csv(file_path: str) -> Tuple[bool, Dict[str, Any], str]:
        """Parse CSV file with defensive error handling.
        
        Handles:
        - Empty files (0 bytes)
        - Encoding errors (utf-8 fallback to latin-1, ISO-8859-1)
        - Empty dataframes
        - Headers-only files
        - Duplicate column names
        - Malformed CSV structure
        - Missing columns
        - Pandas parsing exceptions
        
        Args:
            file_path: Path to CSV file
            
        Returns:
            Tuple of (success: bool, summary: dict, error_message: str)
        """
        import os
        
        # Check file size (0 bytes check)
        if os.path.getsize(file_path) == 0:
            return False, {}, "Uploaded file is empty"
        
        encodings = ['utf-8', 'latin-1', 'ISO-8859-1', 'cp1252']
        df = None
        last_error = None
        
        # Try multiple encodings
        for encoding in encodings:
            try:
                df = pd.read_csv(file_path, encoding=encoding, on_bad_lines='error')
                break
            except UnicodeDecodeError as e:
                last_error = e
                continue
            except pd.errors.ParserError as e:
                return False, {}, "Malformed CSV file. Please check formatting"
            except Exception as e:
                # Catch pandas parsing errors
                error_str = str(e).lower()
                if any(keyword in error_str for keyword in ['parse', 'tokeniz', 'delimiter', 'quote']):
                    return False, {}, "Malformed CSV file. Please check formatting"
                return False, {}, f"CSV parsing error: {str(e)}"
        
        if df is None:
            return False, {}, "Failed to read CSV. Please check file encoding"
        
        # Check for duplicate headers (before pandas renaming)
        warning_msg = ""
        try:
            # We use the successful encoding from above
            import csv
            
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                # Read first line only
                header_line = f.readline()
                # Parse csv
                reader = csv.reader([header_line])
                headers = next(reader)
                
                if len(headers) != len(set(headers)):
                    duplicates = [col for col in headers if headers.count(col) > 1]
                    unique_duplicates = list(set(duplicates))
                    warning_msg = f"Note: Duplicate column names detected ({', '.join(unique_duplicates)}) and were automatically renamed."
        except Exception:
            pass
            
        if df is None:
            return False, {}, "Failed to read CSV. Please check file encoding"
            
        # Post-pandas check (just in case) - REMOVED strict check as per user request
        # if len(df.columns) != len(set(df.columns)):
        #     duplicates = [col for col in df.columns if list(df.columns).count(col) > 1]
        #     unique_duplicates = list(set(duplicates))
        #     return False, {}, f"Duplicate column names detected: {', '.join(unique_duplicates)}"
        
        # Validate dataframe has columns
        if len(df.columns) == 0:
            return False, {}, "CSV file has no columns"
        
        # Check for headers-only (no data rows)
        if len(df) == 0:
            return False, {}, "Dataset contains headers but no data rows"
        
        # Generate summary
        try:
            summary = CSVService._generate_summary(df)
            # Add warning to summary so it can be passed to frontend
            if warning_msg:
                summary['warning'] = warning_msg
                
            return True, summary, ""
        except Exception as e:
            return False, {}, f"Error analyzing CSV: {str(e)}"
    
    @staticmethod
    def _generate_summary(df: pd.DataFrame) -> Dict[str, Any]:
        """Generate comprehensive CSV summary.
        
        Args:
            df: Pandas DataFrame
            
        Returns:
            Dictionary with summary statistics
        """
        summary = {
            'row_count': len(df),
            'column_count': len(df.columns),
            'columns': list(df.columns),
            'data_types': {},
            'missing_values': {},
            'sample_data': {}
        }
        
        # Data types and missing values
        for col in df.columns:
            summary['data_types'][col] = str(df[col].dtype)
            summary['missing_values'][col] = int(df[col].isna().sum())
            
            # Sample data (first 50 non-null values for preview)
            non_null_values = df[col].dropna().head(50).tolist()
            # Convert to JSON-serializable format
            summary['sample_data'][col] = [
                None if pd.isna(v) else (int(v) if isinstance(v, (int, float)) and not pd.isna(v) and v == int(v) else (float(v) if isinstance(v, (int, float)) else str(v)))
                for v in non_null_values
            ]
        
        # Numeric column statistics
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            summary['numeric_stats'] = {}
            for col in numeric_cols:
                if not df[col].isna().all():
                    summary['numeric_stats'][col] = {
                        'mean': float(df[col].mean()),
                        'min': float(df[col].min()),
                        'max': float(df[col].max()),
                    }
        
        return summary
    
    @staticmethod
    def validate_summary(summary: Dict[str, Any]) -> bool:
        """Validate that summary object is well-formed before sending to LLM.
        
        Args:
            summary: Summary dictionary
            
        Returns:
            True if valid, False otherwise
        """
        required_keys = ['row_count', 'column_count', 'columns', 'data_types']
        
        try:
            # Check required keys
            for key in required_keys:
                if key not in summary:
                    return False
            
            # Check that counts are positive
            if summary['row_count'] <= 0 or summary['column_count'] <= 0:
                return False
            
            # Check that columns list is not empty
            if len(summary['columns']) == 0:
                return False
            
            return True
            
        except Exception:
            return False
