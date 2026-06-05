"""
Production-Grade Backend Utilities
Provides validation, pagination, rate limiting, and API response formatting
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from functools import wraps
from flask import request, jsonify
from collections import defaultdict
import time


# =====================================================
# LOGGING CONFIGURATION
# =====================================================

class Logger:
    """Production logging system"""
    
    _instances = {}
    
    def __new__(cls, name):
        if name not in cls._instances:
            cls._instances[name] = super(Logger, cls).__new__(cls)
        return cls._instances[name]
    
    def __init__(self, name):
        if not hasattr(self, 'logger'):
            import logging.handlers
            import os
            
            # Create logs directory
            os.makedirs('logs', exist_ok=True)
            
            self.logger = logging.getLogger(name)
            self.logger.setLevel(logging.DEBUG)
            
            # File handler
            file_handler = logging.handlers.RotatingFileHandler(
                f'logs/{name}.log',
                maxBytes=10485760,  # 10MB
                backupCount=5
            )
            file_handler.setLevel(logging.DEBUG)
            
            # Console handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            
            # Formatter
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
    
    def debug(self, msg):
        self.logger.debug(msg)
    
    def info(self, msg):
        self.logger.info(msg)
    
    def warning(self, msg):
        self.logger.warning(msg)
    
    def error(self, msg):
        self.logger.error(msg)
    
    def critical(self, msg):
        self.logger.critical(msg)


# =====================================================
# VALIDATION UTILITIES
# =====================================================

class Validator:
    """Input validation utilities"""
    
    @staticmethod
    def validate_username(username: str) -> Tuple[bool, str]:
        """Validate username"""
        if not username or len(username.strip()) < 3:
            return False, "Username must be at least 3 characters"
        
        if len(username) > 50:
            return False, "Username cannot exceed 50 characters"
        
        if not all(c.isalnum() or c in '_-' for c in username):
            return False, "Username can only contain alphanumeric characters, hyphens, and underscores"
        
        return True, ""
    
    @staticmethod
    def validate_email(email: str) -> Tuple[bool, str]:
        """Validate email"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not email or not re.match(pattern, email):
            return False, "Invalid email format"
        
        if len(email) > 120:
            return False, "Email cannot exceed 120 characters"
        
        return True, ""
    
    @staticmethod
    def validate_password(password: str) -> Tuple[bool, str]:
        """Validate password strength"""
        if not password or len(password) < 6:
            return False, "Password must be at least 6 characters"
        
        if len(password) > 128:
            return False, "Password cannot exceed 128 characters"
        
        return True, ""
    
    @staticmethod
    def validate_file_extension(filename: str, allowed: set) -> Tuple[bool, str]:
        """Validate file extension"""
        if '.' not in filename:
            return False, "File must have an extension"
        
        ext = filename.rsplit('.', 1)[1].lower()
        if ext not in allowed:
            return False, f"Invalid file type. Allowed: {', '.join(allowed)}"
        
        return True, ""
    
    @staticmethod
    def validate_crop(crop: str, valid_crops: list) -> Tuple[bool, str]:
        """Validate crop name"""
        if not crop or crop not in valid_crops:
            return False, f"Invalid crop. Supported: {', '.join(valid_crops)}"
        
        return True, ""


# =====================================================
# PAGINATION UTILITIES
# =====================================================

class Pagination:
    """Pagination utilities"""
    
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100
    
    @staticmethod
    def get_pagination_params(request_args) -> Tuple[int, int]:
        """Extract and validate pagination parameters"""
        page = request_args.get('page', 1, type=int)
        per_page = request_args.get('per_page', Pagination.DEFAULT_PAGE_SIZE, type=int)
        
        # Validate
        page = max(1, page)
        per_page = max(1, min(per_page, Pagination.MAX_PAGE_SIZE))
        
        return page, per_page
    
    @staticmethod
    def paginate_list(items: list, page: int, per_page: int) -> Dict:
        """Paginate a list of items"""
        total = len(items)
        pages = (total + per_page - 1) // per_page
        
        start = (page - 1) * per_page
        end = start + per_page
        
        return {
            'items': items[start:end],
            'page': page,
            'per_page': per_page,
            'total': total,
            'pages': pages,
            'has_next': page < pages,
            'has_prev': page > 1
        }


# =====================================================
# RATE LIMITING
# =====================================================

class RateLimiter:
    """Simple rate limiter implementation"""
    
    def __init__(self, max_requests=100, window_seconds=3600):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = defaultdict(list)
    
    def is_rate_limited(self, identifier: str) -> bool:
        """Check if identifier has exceeded rate limit"""
        now = time.time()
        cutoff = now - self.window_seconds
        
        # Clean old requests
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier]
            if req_time > cutoff
        ]
        
        if len(self.requests[identifier]) >= self.max_requests:
            return True
        
        self.requests[identifier].append(now)
        return False
    
    def get_remaining(self, identifier: str) -> int:
        """Get remaining requests for identifier"""
        now = time.time()
        cutoff = now - self.window_seconds
        
        valid_requests = [
            req_time for req_time in self.requests[identifier]
            if req_time > cutoff
        ]
        
        return max(0, self.max_requests - len(valid_requests))


# Global rate limiters
API_LIMITER = RateLimiter(max_requests=100, window_seconds=3600)  # 100/hour
UPLOAD_LIMITER = RateLimiter(max_requests=20, window_seconds=3600)  # 20/hour


def rate_limit(limiter: RateLimiter, get_key=None):
    """Rate limiting decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if get_key:
                key = get_key()
            else:
                key = request.remote_addr
            
            if limiter.is_rate_limited(key):
                remaining = limiter.get_remaining(key)
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'remaining': remaining
                }), 429
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# =====================================================
# API RESPONSE FORMATTING
# =====================================================

class APIResponse:
    """Standard API response formatter"""
    
    @staticmethod
    def success(data: Any = None, message: str = "Success", code: int = 200) -> Tuple[Dict, int]:
        """Format successful response"""
        response = {
            'success': True,
            'message': message,
            'data': data,
            'timestamp': datetime.utcnow().isoformat()
        }
        return response, code
    
    @staticmethod
    def error(error: str, code: int = 400, details: Any = None) -> Tuple[Dict, int]:
        """Format error response"""
        response = {
            'success': False,
            'error': error,
            'code': code,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        if details:
            response['details'] = details
        
        return response, code
    
    @staticmethod
    def paginated(items: list, pagination: Dict, message: str = "Success") -> Tuple[Dict, int]:
        """Format paginated response"""
        response = {
            'success': True,
            'message': message,
            'data': items,
            'pagination': {
                'page': pagination['page'],
                'per_page': pagination['per_page'],
                'total': pagination['total'],
                'pages': pagination['pages'],
                'has_next': pagination['has_next'],
                'has_prev': pagination['has_prev']
            },
            'timestamp': datetime.utcnow().isoformat()
        }
        return response, 200


# =====================================================
# DATA SANITIZATION
# =====================================================

class Sanitizer:
    """Input sanitization utilities"""
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Remove dangerous characters from filename"""
        import re
        # Remove path separators and null bytes
        filename = filename.replace('\\', '').replace('/', '').replace('\x00', '')
        # Keep only alphanumeric, dots, hyphens, and underscores
        filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
        return filename[:255]  # Max filename length
    
    @staticmethod
    def sanitize_string(text: str, max_length: int = None) -> str:
        """Sanitize text input"""
        if not isinstance(text, str):
            return ""
        
        # Remove null bytes and control characters
        text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\t\r')
        text = text.strip()
        
        if max_length:
            text = text[:max_length]
        
        return text


# =====================================================
# QUERY OPTIMIZATION
# =====================================================

class QueryCache:
    """Simple query cache for frequently accessed data"""
    
    def __init__(self, ttl_seconds=300):
        self.cache = {}
        self.ttl = ttl_seconds
    
    def get(self, key: str) -> Any:
        """Get cached value if not expired"""
        if key in self.cache:
            timestamp, value = self.cache[key]
            if time.time() - timestamp < self.ttl:
                return value
            else:
                del self.cache[key]
        return None
    
    def set(self, key: str, value: Any):
        """Cache a value"""
        self.cache[key] = (time.time(), value)
    
    def clear(self, key: str = None):
        """Clear cache"""
        if key:
            self.cache.pop(key, None)
        else:
            self.cache.clear()


# Global cache instance
QUERY_CACHE = QueryCache(ttl_seconds=300)


# =====================================================
# TIMING UTILITIES
# =====================================================

def get_time_range(time_range: str) -> Tuple[datetime, datetime]:
    """Get date range based on string"""
    now = datetime.utcnow()
    
    if time_range == 'today':
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = now
    elif time_range == 'week':
        start = now - timedelta(days=7)
        end = now
    elif time_range == 'month':
        start = now - timedelta(days=30)
        end = now
    elif time_range == 'year':
        start = now - timedelta(days=365)
        end = now
    else:
        start = now - timedelta(days=30)
        end = now
    
    return start, end
