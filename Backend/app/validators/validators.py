"""
Input validation and sanitization utilities.
Provides centralized validation for user inputs, ensuring security and data integrity.
"""

import re
import html
from decimal import Decimal, ROUND_DOWN, InvalidOperation
from typing import Optional


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


def sanitize_string(value: str, max_length: int = 255) -> str:
    """
    Sanitize string input by trimming whitespace and encoding HTML entities.
    
    Args:
        value: String to sanitize
        max_length: Maximum allowed length (default 255)
        
    Returns:
        Sanitized string
        
    Raises:
        ValidationError: If input is invalid
    """
    if not isinstance(value, str):
        raise ValidationError("Input must be a string")
    
    sanitized = value.strip()

    if len(sanitized) > max_length:
        raise ValidationError(f"Input exceeds maximum length of {max_length}")
    
    if len(sanitized) == 0:
        raise ValidationError("Input cannot be empty")
    
    # Encode HTML entities to prevent XSS
    sanitized = html.escape(sanitized)
    
    return sanitized


def validate_email(email: str) -> str:
    """
    Validate email format.
    
    Args:
        email: Email address to validate
        
    Returns:
        Cleaned email (lowercase)
        
    Raises:
        ValidationError: If email format is invalid
    """
    if not isinstance(email, str):
        raise ValidationError("Email must be a string")
    
    email = email.strip().lower()
    
    # RFC 5322 simplified regex (practical for most emails)
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(email_regex, email):
        raise ValidationError("Invalid email format")
    
    if len(email) > 120:
        raise ValidationError("Email too long (max 120 characters)")
    
    return email


def validate_username(username: str) -> str:
    """
    Validate username format.
    Requirements: 3-80 characters, alphanumeric + underscore, no leading/trailing underscore.
    
    Args:
        username: Username to validate
        
    Returns:
        Cleaned username
        
    Raises:
        ValidationError: If username format is invalid
    """
    if not isinstance(username, str):
        raise ValidationError("Username must be a string")
    
    username = username.strip()
    
    if len(username) < 3:
        raise ValidationError("Username must be at least 3 characters")
    if len(username) > 80:
        raise ValidationError("Username must not exceed 80 characters")
    
    username_regex = r'^[a-zA-Z0-9_]+$'
    if not re.match(username_regex, username):
        raise ValidationError("Username can only contain letters, numbers, and underscores")
    
    if username.startswith('_') or username.endswith('_'):
        raise ValidationError("Username cannot start or end with underscore")
    
    if '__' in username:
        raise ValidationError("Username cannot contain consecutive underscores")
    
    return username


def validate_password(password: str, min_length: int = 8) -> str:
    """
    Validate password strength.
    Requirements: 
    - Minimum length (default 8)
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character (!@#$%^&*)
    
    Args:
        password: Password to validate
        min_length: Minimum password length (default 8)
        
    Returns:
        The password (unchanged)
        
    Raises:
        ValidationError: If password doesn't meet requirements
    """
    if not isinstance(password, str):
        raise ValidationError("Password must be a string")
    
    if len(password) < min_length:
        raise ValidationError(f"Password must be at least {min_length} characters")
    
    if len(password) > 128:
        raise ValidationError("Password must not exceed 128 characters")
    
    if not re.search(r'[A-Z]', password):
        raise ValidationError("Password must contain at least one uppercase letter")

    if not re.search(r'[a-z]', password):
        raise ValidationError("Password must contain at least one lowercase letter")

    if not re.search(r'\d', password):
        raise ValidationError("Password must contain at least one digit")

    special_chars = r'!@#$%^&*()_+-=\[\]{};:\'",.<>?/\\|`~'
    if not re.search(f'[{re.escape(special_chars)}]', password):
        raise ValidationError("Password must contain at least one special character (!@#$%^&*)")
    
    return password


def validate_quantity(quantity: any, max_quantity: int = 10000) -> int:
    """
    Validate product quantity.
    Requirements:
    - Must be a positive integer
    - Must not exceed max_quantity
    
    Args:
        quantity: Quantity to validate
        max_quantity: Maximum allowed quantity (default 10000)
        
    Returns:
        Validated quantity as integer
        
    Raises:
        ValidationError: If quantity is invalid
    """
    try:
        qty = int(quantity)
    except (ValueError, TypeError):
        raise ValidationError("Quantity must be an integer")
    
    if qty <= 0:
        raise ValidationError("Quantity must be greater than 0")
    
    if qty > max_quantity:
        raise ValidationError(f"Quantity must not exceed {max_quantity}")
    
    return qty


def validate_price(price: any, min_price: float = 0.0, max_price: float = 999999.99) -> float:
    """
    Validate product price.
    Requirements:
    - Must be a positive number
    - Must be within price range
    
    Args:
        price: Price to validate
        min_price: Minimum allowed price (default 0.0)
        max_price: Maximum allowed price (default 999999.99)
        
    Returns:
        Validated price as float
        
    Raises:
        ValidationError: If price is invalid
    """
    try:
        p = float(price)
    except (ValueError, TypeError):
        raise ValidationError("Price must be a number")
    
    if p < min_price:
        raise ValidationError(f"Price must be at least {min_price}")
    
    if p > max_price:
        raise ValidationError(f"Price must not exceed {max_price}")
    
    # Vérification de la précision décimale via Decimal (évite les erreurs d'arrondi float)
    try:
        d = Decimal(str(price))
        if d.as_tuple().exponent < -2:
            raise ValidationError("Le prix ne peut pas avoir plus de 2 décimales")
    except InvalidOperation:
        raise ValidationError("Price must be a number")

    return round(p, 2)


def validate_stock(stock: any, max_stock: int = 1000000) -> int:
    """
    Validate product stock.
    Requirements:
    - Must be a non-negative integer
    - Must not exceed max_stock
    
    Args:
        stock: Stock to validate
        max_stock: Maximum allowed stock (default 1000000)
        
    Returns:
        Validated stock as integer
        
    Raises:
        ValidationError: If stock is invalid
    """
    try:
        s = int(stock)
    except (ValueError, TypeError):
        raise ValidationError("Stock must be an integer")
    
    if s < 0:
        raise ValidationError("Stock cannot be negative")
    
    if s > max_stock:
        raise ValidationError(f"Stock must not exceed {max_stock}")
    
    return s
