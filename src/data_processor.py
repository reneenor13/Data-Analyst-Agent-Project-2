import pandas as pd
import numpy as np
import json
import io
from typing import Dict, Any, Union
import logging

logger = logging.getLogger(__name__)

class DataProcessor:
    def __init__(self):
        self.supported_formats = ['csv', 'xlsx', 'xls', 'json', 'txt', 'parquet']
    
    def process_file(self, file) -> pd.DataFrame:
        """Process uploaded file and return DataFrame"""
        try:
            filename = file.filename.lower()
            file_extension = filename.split('.')[-1]
            
            if file_extension not in self.supported_formats:
                raise ValueError(f"Unsupported file format: {file_extension}")
            
            # Read file content
            file_content = file.read()
            file.seek(0)  # Reset file pointer
            
            # Process based on file type
            if file_extension == 'csv':
                return self._process_csv(file_content)
            elif file_extension in ['xlsx', 'xls']:
                return self._process_excel(file_content)
            elif file_extension == 'json':
                return self._process_json(file_content)
            elif file_extension == 'txt':
                return self._process_text(file_content)
            elif file_extension == 'parquet':
                return self._process_parquet(file_content)
            else:
                raise ValueError(f"Processing not implemented for {file_extension}")
                
        except Exception as e:
            logger.error(f"File processing failed: {e}")
            raise Exception(f"File processing failed: {str(e)}")
    
    def _process_csv(self, content: bytes) -> pd.DataFrame:
        """Process CSV files"""
        try:
            # Try different encodings
            encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
            
            for encoding in encodings:
                try:
                    df = pd.read_csv(io.BytesIO(content), encoding=encoding)
                    break
                except UnicodeDecodeError:
                    continue
            else:
                raise ValueError("Could not decode CSV file with any supported encoding")
            
            # Clean column names
            df.columns = df.columns.str.strip()
            
            # Try to infer data types
            df = self._infer_types(df)
            
            logger.info(f"CSV processed: {df.shape[0]} rows, {df.shape[1]} columns")
            return df
            
        except Exception as e:
            raise Exception(f"CSV processing failed: {str(e)}")
    
    def _process_excel(self, content: bytes) -> pd.DataFrame:
        """Process Excel files"""
        try:
            df = pd.read_excel(io.BytesIO(content), engine='openpyxl')
            
            # Clean column names
            df.columns = df.columns.str.strip()
            
            # Try to infer data types
            df = self._infer_types(df)
            
            logger.info(f"Excel processed: {df.shape[0]} rows, {df.shape[1]} columns")
            return df
            
        except Exception as e:
            raise Exception(f"Excel processing failed: {str(e)}")
    
    def _process_json(self, content: bytes) -> pd.DataFrame:
        """Process JSON files"""
        try:
            json_data = json.loads(content.decode('utf-8'))
            
            # Handle different JSON structures
            if isinstance(json_data, list):
                df = pd.DataFrame(json_data)
            elif isinstance(json_data, dict):
                if 'data' in json_data:
                    df = pd.DataFrame(json_data['data'])
                else:
                    df = pd.DataFrame([json_data])
            else:
                raise ValueError("Unsupported JSON structure")
            
            df = self._infer_types(df)
            
            logger.info(f"JSON processed: {df.shape[0]} rows, {df.shape[1]} columns")
            return df
            
        except Exception as e:
            raise Exception(f"JSON processing failed: {str(e)}")
    
    def _process_text(self, content: bytes) -> pd.DataFrame:
        """Process text files (assume CSV-like format)"""
        try:
            text_content = content.decode('utf-8')
            
            # Try different delimiters
            delimiters = [',', '\t', ';', '|']
            
            for delimiter in delimiters:
                try:
                    df = pd.read_csv(io.StringIO(text_content), sep=delimiter)
                    if df.shape[1] > 1:  # Multiple columns found
                        break
                except:
                    continue
            else:
                # If no delimiter works, treat as single column
                lines = text_content.strip().split('\n')
                df = pd.DataFrame({'text': lines})
            
            df = self._infer_types(df)
            
            logger.info(f"Text processed: {df.shape[0]} rows, {df.shape[1]} columns")
            return df
            
        except Exception as e:
            raise Exception(f"Text processing failed: {str(e)}")
    
    def _process_parquet(self, content: bytes) -> pd.DataFrame:
        """Process Parquet files"""
        try:
            df = pd.read_parquet(io.BytesIO(content))
            
            logger.info(f"Parquet processed: {df.shape[0]} rows, {df.shape[1]} columns")
            return df
            
        except Exception as e:
            raise Exception(f"Parquet processing failed: {str(e)}")
    
    def _infer_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """Infer and convert appropriate data types"""
        try:
            # Convert numeric columns
            for col in df.columns:
                if df[col].dtype == 'object':
                    # Try to convert to numeric
                    numeric_series = pd.to_numeric(df[col], errors='coerce')
                    if not numeric_series.isna().all():
                        df[col] = numeric_series
                    else:
                        # Try to convert to datetime
                        try:
                            df[col] = pd.to_datetime(df[col], errors='coerce')
                        except:
                            pass  # Keep as object
            
            return df
            
        except Exception as e:
            logger.warning(f"Type inference failed: {e}")
            return df
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Basic data cleaning operations"""
        try:
            # Remove completely empty rows and columns
            df = df.dropna(how='all').dropna(axis=1, how='all')
            
            # Handle duplicate columns
            df = df.loc[:, ~df.columns.duplicated()]
            
            # Basic string cleaning for object columns
            for col in df.select_dtypes(include=['object']).columns:
                df[col] = df[col].astype(str).str.strip()
                df[col] = df[col].replace('', np.nan)
            
            logger.info(f"Data cleaned: {df.shape[0]} rows, {df.shape[1]} columns")
            return df
            
        except Exception as e:
            logger.warning(f"Data cleaning failed: {e}")
            return df
    
    def get_data_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get summary statistics and info about the data"""
        try:
            summary = {
                'shape': df.shape,
                'columns': df.columns.tolist(),
                'dtypes': df.dtypes.to_dict(),
                'missing_values': df.isnull().sum().to_dict(),
                'memory_usage': df.memory_usage(deep=True).sum(),
            }
            
            # Numeric summary
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                summary['numeric_summary'] = df[numeric_cols].describe().to_dict()
            
            # Categorical summary
            cat_cols = df.select_dtypes(include=['object']).columns
            if len(cat_cols) > 0:
                summary['categorical_summary'] = {}
                for col in cat_cols:
                    summary['categorical_summary'][col] = {
                        'unique_count': df[col].nunique(),
                        'top_values': df[col].value_counts().head().to_dict()
                    }
            
            return summary
            
        except Exception as e:
            logger.error(f"Summary generation failed: {e}")
            return {'error': str(e)}
    
    def filter_data(self, df: pd.DataFrame, filters: Dict[str, Any]) -> pd.DataFrame:
        """Apply filters to the data"""
        try:
            filtered_df = df.copy()
            
            for column, condition in filters.items():
                if column not in df.columns:
                    continue
                    
                if isinstance(condition, dict):
                    if 'min' in condition:
                        filtered_df = filtered_df[filtered_df[column] >= condition['min']]
                    if 'max' in condition:
                        filtered_df = filtered_df[filtered_df[column] <= condition['max']]
                    if 'equals' in condition:
                        filtered_df = filtered_df[filtered_df[column] == condition['equals']]
                    if 'contains' in condition:
                        filtered_df = filtered_df[filtered_df[column].str.contains(
                            condition['contains'], case=False, na=False)]
                
            logger.info(f"Data filtered: {len(filtered_df)} rows remaining")
            return filtered_df
            
        except Exception as e:
            logger.error(f"Data filtering failed: {e}")
            return df
