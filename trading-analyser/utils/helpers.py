# -*- coding: utf-8 -*-
"""
Helper functions and utilities
Helper functions and utilities for Trading Tool
"""

import json
import hashlib
import pickle
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from functools import lru_cache, wraps
import pandas as pd
import numpy as np

from config import Config
from .logger import setup_logger

logger = setup_logger(__name__)

def color_text(text: str, color: str = 'white') -> str:
    """
    Color text for terminal
    
    Parameters:
        text (str): Input text
        color (str): Color ('green', 'red', 'yellow', 'blue', 'purple', 'cyan', 'white')
    
    Returns:
        str: Colored text
    """
    colors = Config.DISPLAY.COLORS
    color_code = colors.get(color.upper(), colors['WHITE'])
    return f"{color_code}{text}{colors['END']}"

def print_table(data: List[List[str]], headers: List[str] = None, 
                title: str = None, align: str = 'left') -> None:
    """
    Print beautiful table in terminal
    
    Parameters:
        data (List[List[str]]): Table data
        headers (List[str]): Column headers
        title (str): Table title
        align (str): Alignment ('left', 'center', 'right')
    """
    if not data:
        print("⚠️ No data to display")
        return
    
    # Calculate column widths
    if headers:
        col_widths = [len(str(h)) for h in headers]
    else:
        col_widths = [0] * len(data[0])
    
    for row in data:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))
    
    # Add padding
    col_widths = [w + 2 for w in col_widths]
    total_width = sum(col_widths) + len(col_widths) + 1
    
    # Print title
    if title:
        print(f"\n{title}")
        print("=" * total_width)
    
    # Print headers
    if headers:
        header_row = "|"
        for i, header in enumerate(headers):
            if align == 'center':
                header_row += f" {header.center(col_widths[i]-2)} |"
            elif align == 'right':
                header_row += f" {header.rjust(col_widths[i]-2)} |"
            else:
                header_row += f" {header.ljust(col_widths[i]-2)} |"
        print(header_row)
        print("-" * total_width)
    
    # Print data
    for row in data:
        row_str = "|"
        for i, cell in enumerate(row):
            cell_str = str(cell)
            if align == 'center':
                row_str += f" {cell_str.center(col_widths[i]-2)} |"
            elif align == 'right':
                row_str += f" {cell_str.rjust(col_widths[i]-2)} |"
            else:
                row_str += f" {cell_str.ljust(col_widths[i]-2)} |"
        print(row_str)
    
    if title:
        print("=" * total_width)

def format_number(number: float, decimals: int = 2) -> str:
    """
    Format number with commas and decimal places
    
    Parameters:
        number (float): Number to format
        decimals (int): Decimal places
    
    Returns:
        str: Formatted number
    """
    if pd.isna(number):
        return "N/A"
    
    # Format with commas
    formatted = f"{number:,.{decimals}f}"
    
    # Add symbol for large numbers
    if abs(number) >= 1_000_000_000:
        return f"${formatted}B"
    elif abs(number) >= 1_000_000:
        return f"${formatted}M"
    elif abs(number) >= 1_000:
        return f"${formatted}K"
    else:
        return f"${formatted}"

def calculate_percentage_change(old_value: float, new_value: float) -> float:
    """
    Calculate percentage change
    
    Parameters:
        old_value (float): Old value
        new_value (float): New value
    
    Returns:
        float: Percentage change
    """
    if old_value == 0:
        return 0
    return ((new_value - old_value) / old_value) * 100

def get_timestamp() -> str:
    """
    Get current timestamp
    
    Returns:
        str: Current timestamp
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def cache_result(expiry_seconds: int = 300):
    """
    Cache function results with expiry
    
    Parameters:
        expiry_seconds (int): Cache expiry in seconds
    """
    def decorator(func):
        cache = {}
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key
            key = hashlib.md5(
                f"{func.__name__}{args}{kwargs}".encode()
            ).hexdigest()
            
            # Check cache
            current_time = time.time()
            if key in cache:
                result, timestamp = cache[key]
                if current_time - timestamp < expiry_seconds:
                    logger.debug(f"Cache hit for {func.__name__}")
                    return result
            
            # Call function
            result = func(*args, **kwargs)
            
            # Update cache
            cache[key] = (result, current_time)
            
            # Clean old cache entries
            for k in list(cache.keys()):
                if current_time - cache[k][1] > expiry_seconds * 2:
                    del cache[k]
            
            return result
        
        return wrapper
    
    return decorator

def validate_symbol(symbol: str) -> bool:
    """
    Validate trading symbol
    
    Parameters:
        symbol (str): Trading symbol
    
    Returns:
        bool: True if valid
    """
    if not symbol or len(symbol) > 20:
        return False
    
    # Basic validation
    valid_chars = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-=./")
    return all(char in valid_chars for char in symbol.upper())

def detect_market_type(symbol: str) -> str:
    """
    Detect market type from symbol
    
    Parameters:
        symbol (str): Trading symbol
    
    Returns:
        str: Market type ('crypto', 'forex', 'stock')
    """
    symbol_upper = symbol.upper()
    
    if any(x in symbol_upper for x in ['-USD', '/USD', 'USDT']):
        return 'crypto'
    elif '=X' in symbol_upper or any(x in symbol_upper for x in ['EUR', 'GBP', 'JPY', 'CHF', 'AUD', 'CAD', 'NZD']):
        return 'forex'
    else:
        return 'stock'

def calculate_support_resistance(df: pd.DataFrame, window: int = 20) -> Dict[str, float]:
    """
    Calculate support and resistance levels
    
    Parameters:
        df (pd.DataFrame): Price data
        window (int): Lookback window
    
    Returns:
        Dict[str, float]: Support and resistance levels
    """
    if len(df) < window:
        return {}
    
    recent_data = df.tail(window)
    
    support = recent_data['Low'].min()
    resistance = recent_data['High'].max()
    pivot = (support + resistance) / 2
    
    return {
        'support': support,
        'resistance': resistance,
        'pivot': pivot,
        'r1': (2 * pivot) - support,
        'r2': pivot + (resistance - support),
        's1': (2 * pivot) - resistance,
        's2': pivot - (resistance - support)
    }

def calculate_volatility(df: pd.DataFrame, period: int = 20) -> float:
    """
    Calculate price volatility
    
    Parameters:
        df (pd.DataFrame): Price data
        period (int): Period for calculation
    
    Returns:
        float: Volatility percentage
    """
    if len(df) < period:
        return 0
    
    returns = df['Close'].pct_change().dropna()
    if len(returns) < period:
        return 0
    
    volatility = returns.tail(period).std() * np.sqrt(252)  # Annualized
    return volatility * 100  # As percentage

def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and prepare dataframe
    
    Parameters:
        df (pd.DataFrame): Raw dataframe
    
    Returns:
        pd.DataFrame: Cleaned dataframe
    """
    # Make a copy
    df_clean = df.copy()
    
    # Remove NaN values
    df_clean = df_clean.dropna()
    
    # Ensure numeric columns
    numeric_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
    for col in numeric_cols:
        if col in df_clean.columns:
            df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
    
    # Remove duplicates
    df_clean = df_clean[~df_clean.index.duplicated(keep='first')]
    
    # Sort by index
    df_clean = df_clean.sort_index()
    
    return df_clean

def save_to_json(data: Any, filepath: Path) -> bool:
    """
    Save data to JSON file
    
    Parameters:
        data (Any): Data to save
        filepath (Path): File path
    
    Returns:
        bool: Success status
    """
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
        return True
    except Exception as e:
        logger.error(f"Error saving to JSON: {e}")
        return False

def load_from_json(filepath: Path) -> Optional[Any]:
    """
    Load data from JSON file
    
    Parameters:
        filepath (Path): File path
    
    Returns:
        Optional[Any]: Loaded data or None
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading from JSON: {e}")
        return None

def test_helpers():
    """Test helper functions"""
    print("Testing helper functions...")
    
    # Test color_text
    print(color_text("Green text", "green"))
    print(color_text("Red text", "red"))
    
    # Test print_table
    data = [
        ["AAPL", "150.25", "+2.5%"],
        ["GOOGL", "2800.50", "+1.2%"],
        ["TSLA", "750.80", "-0.5%"]
    ]
    headers = ["Symbol", "Price", "Change"]
    print_table(data, headers, title="Stock Prices")
    
    # Test format_number
    print(f"Formatted: {format_number(1234567.89)}")
    print(f"Formatted: {format_number(1234.56)}")
    
    # Test calculate_percentage_change
    change = calculate_percentage_change(100, 120)
    print(f"Percentage change: {change:.2f}%")

if __name__ == "__main__":
    test_helpers()
