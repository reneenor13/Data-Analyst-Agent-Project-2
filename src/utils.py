import re
import logging
import hashlib
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse
import requests
from datetime import datetime
import os

logger = logging.getLogger(__name__)

class Utils:
    @staticmethod
    def extract_urls(text: str) -> List[str]:
        """Extract URLs from text"""
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        urls = re.findall(url_pattern, text)
        return urls
    
    @staticmethod
    def extract_questions(text: str) -> List[str]:
        """Extract individual questions from text"""
        # Split by numbers (1., 2., etc.) or dashes
        patterns = [
            r'\d+\.\s*',  # 1. 2. 3.
            r'\d+\)\s*',  # 1) 2) 3)
            r'-\s*',      # - question
            r'\*\s*',     # * question
        ]
        
        questions = []
        for pattern in patterns:
            parts = re.split(pattern, text)
            if len(parts) > 1:
                questions = [part.strip() for part in parts[1:] if part.strip()]
                break
        
        # If no pattern found, split by lines
        if not questions:
            lines = text.strip().split('\n')
            questions = [line.strip() for line in lines if line.strip()]
        
        return questions
    
    @staticmethod
    def identify_analysis_type(question: str) -> str:
        """Identify what type of analysis is needed"""
        question_lower = question.lower()
        
        keywords = {
            'correlation': ['correlation', 'correlate', 'relationship', 'association'],
            'counting': ['how many', 'count', 'number of', 'total'],
            'plotting': ['plot', 'chart', 'graph', 'visualize', 'draw', 'scatterplot', 'histogram'],
            'statistical': ['average', 'mean', 'median', 'std', 'variance', 'statistics'],
            'filtering': ['filter', 'where', 'select', 'subset'],
            'scraping': ['scrape', 'extract', 'wikipedia', 'website', 'url'],
            'aggregation': ['sum', 'group by', 'aggregate', 'summarize'],
            'comparison': ['compare', 'versus', 'vs', 'difference', 'between']
        }
        
        for analysis_type, words in keywords.items():
            if any(word in question_lower for word in words):
                return analysis_type
        
        return 'general'
    
    @staticmethod
    def extract_column_names(question: str, available_columns: List[str]) -> List[str]:
        """Extract relevant column names from question"""
        question_lower = question.lower()
        relevant_columns = []
        
        for col in available_columns:
            col_lower = col.lower()
            # Direct match
            if col_lower in question_lower:
                relevant_columns.append(col)
            # Partial match for common variations
            elif any(word in col_lower for word in question_lower.split()):
                relevant_columns.append(col)
        
        return relevant_columns
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """Validate if URL is properly formatted"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    @staticmethod
    def safe_request(url: str, timeout: int = 30) -> Optional[requests.Response]:
        """Make a safe HTTP request with proper headers"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
            }
            
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()
            return response
        except Exception as e:
            logger.error(f"Request to {url} failed: {e}")
            return None
    
    @staticmethod
    def generate_cache_key(*args) -> str:
        """Generate a cache key from arguments"""
        combined = ''.join(str(arg) for arg in args)
        return hashlib.md5(combined.encode()).hexdigest()
    
    @staticmethod
    def format_number(num: float, precision: int = 6) -> str:
        """Format numbers consistently"""
        if abs(num) < 0.001:
            return f"{num:.2e}"
        elif abs(num) >= 1000:
            return f"{num:,.0f}"
        else:
            return f"{num:.{precision}f}".rstrip('0').rstrip('.')
    
    @staticmethod
    def parse_date_columns(df, date_columns: List[str] = None):
        """Parse potential date columns in DataFrame"""
        import pandas as pd
        
        if date_columns is None:
            # Try to identify date columns
            date_columns = []
            for col in df.columns:
                if any(word in col.lower() for word in ['date', 'time', 'created', 'updated', 'year', 'month']):
                    date_columns.append(col)
        
        for col in date_columns:
            if col in df.columns:
                try:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
                    logger.info(f"Parsed {col} as datetime")
                except Exception as e:
                    logger.warning(f"Failed to parse {col} as datetime: {e}")
        
        return df
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean text for processing"""
        if not isinstance(text, str):
            return str(text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\.,!?-]', '', text)
        
        return text
    
    @staticmethod
    def calculate_processing_time(start_time: datetime) -> float:
        """Calculate processing time in seconds"""
        return (datetime.now() - start_time).total_seconds()
    
    @staticmethod
    def truncate_text(text: str, max_length: int = 1000) -> str:
        """Truncate text to maximum length"""
        if len(text) <= max_length:
            return text
        return text[:max_length-3] + "..."
    
    @staticmethod
    def get_file_size_mb(file_path: str) -> float:
        """Get file size in MB"""
        try:
            size_bytes = os.path.getsize(file_path)
            return size_bytes / (1024 * 1024)
        except:
            return 0.0
    
    @staticmethod
    def is_numeric_column(series) -> bool:
        """Check if a pandas series is numeric"""
        try:
            pd.to_numeric(series, errors='coerce')
            return True
        except:
            return False
    
    @staticmethod
    def detect_encoding(file_content: bytes) -> str:
        """Detect file encoding"""
        import chardet
        
        try:
            result = chardet.detect(file_content)
            return result['encoding'] or 'utf-8'
        except:
            return 'utf-8'

# Helper functions for common operations
def safe_divide(a, b, default=0):
    """Safe division with default value"""
    try:
        return a / b if b != 0 else default
    except:
        return default

def safe_float(value, default=0.0):
    """Safely convert to float"""
    try:
        return float(value)
    except:
        return default

def safe_int(value, default=0):
    """Safely convert to integer"""
    try:
        return int(value)
    except:
        return default

def chunks(lst, n):
    """Yield successive n-sized chunks from list"""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def merge_dicts(dict1, dict2):
    """Safely merge two dictionaries"""
    result = dict1.copy()
    result.update(dict2)
    return result
