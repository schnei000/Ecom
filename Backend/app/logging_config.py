"""
Logging configuration module.
Provides structured logging with security considerations (masking sensitive data).
"""

import logging
import logging.handlers
import json
import os
from datetime import datetime, timezone


class SensitiveDataFilter(logging.Filter):
    """Filter to mask sensitive data in logs."""
    
    SENSITIVE_KEYS = [
        'password', 'passwd', 'token', 'access_token', 'refresh_token',
        'secret', 'api_key', 'apikey', 'authorization', 'auth',
        'jwt', 'credit_card', 'creditcard', 'ssn', 'social_security'
    ]
    
    def filter(self, record):
        """Mask sensitive data in log records."""
        if hasattr(record, 'msg') and isinstance(record.msg, str):
            for key in self.SENSITIVE_KEYS:
                # Simple pattern: key=value or key: value
                patterns = [
                    f'{key}="[^"]*"',
                    f'{key}=\'[^\']*\'',
                    f'{key}=[^ ,}}]*',
                    f'{key}: [^ ,}}]*'
                ]
                
                import re
                for pattern in patterns:
                    record.msg = re.sub(pattern, f'{key}=***MASKED***', record.msg, flags=re.IGNORECASE)
        
        return True


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging."""
    
    def format(self, record):
        """Format log record as JSON."""
        log_data = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'message': record.getMessage(),
        }
        
        # Add extra fields if present
        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id
        if hasattr(record, 'request_id'):
            log_data['request_id'] = record.request_id
        if hasattr(record, 'ip_address'):
            log_data['ip_address'] = record.ip_address
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)


def setup_logging(app):
    """
    Configure logging for Flask application.
    
    Args:
        app: Flask application instance
    """
    log_level = os.environ.get('LOG_LEVEL', 'INFO').upper()
    logs_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
    
    # Créer le répertoire de logs avec permissions restreintes (owner rw, group r, autres rien)
    os.makedirs(logs_dir, mode=0o750, exist_ok=True)
    
    # Remove default Flask logger handlers
    app.logger.handlers.clear()
    
    logger = logging.getLogger('ecommerce_api')
    logger.setLevel(getattr(logging, log_level))
    logger.handlers.clear()
    logger.propagate = False
    
    sensitive_filter = SensitiveDataFilter()
    
    # Console Handler (development/human-readable)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, log_level))
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    console_handler.addFilter(sensitive_filter)
    
    # File Handler (JSON format for production)
    log_file = os.path.join(logs_dir, 'app.log')
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    file_handler.setLevel(logging.INFO)
    file_formatter = JSONFormatter()
    file_handler.setFormatter(file_formatter)
    file_handler.addFilter(sensitive_filter)
    
    # Error File Handler
    error_log_file = os.path.join(logs_dir, 'error.log')
    error_handler = logging.handlers.RotatingFileHandler(
        error_log_file,
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_formatter)
    error_handler.addFilter(sensitive_filter)
    
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.addHandler(error_handler)
    
    # Also configure Flask's logger
    app.logger.addHandler(console_handler)
    app.logger.addHandler(file_handler)
    
    return logger


def log_security_event(logger, event_type: str, **kwargs):
    """
    Log security-related events.
    
    Args:
        logger: Logger instance
        event_type: Type of security event (e.g., 'FAILED_LOGIN', 'ADMIN_ACTION')
        **kwargs: Additional context to log
    """
    message = f"SECURITY_EVENT: {event_type}"
    for key, value in kwargs.items():
        message += f" | {key}={value}"
    
    logger.warning(message)
