# -*- coding: utf-8 -*-
"""
Configuration settings for Trading Analysis Tool
Configuration file for Trading Analysis Tool
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
CACHE_DIR = BASE_DIR / "cache"

# Create directories
for directory in [DATA_DIR, LOGS_DIR, CACHE_DIR]:
    directory.mkdir(exist_ok=True)

# API Keys (loaded from .env file)
class APIConfig:
    """API Configuration"""
    
    # Yahoo Finance (no API key needed)
    YFINANCE_TIMEOUT = 10
    
    # Alpha Vantage (optional - for more detailed data)
    ALPHA_VANTAGE_API = os.getenv("ALPHA_VANTAGE_API", "")
    
    # Finnhub (optional - for real-time data)
    FINNHUB_API = os.getenv("FINNHUB_API", "")
    
    # CryptoCompare (optional - for crypto data)
    CRYPTO_COMPARE_API = os.getenv("CRYPTO_COMPARE_API", "")
    
    # Whale Alert (optional - for whale tracking)
    WHALE_ALERT_API = os.getenv("WHALE_ALERT_API", "")
    
    # Twitter API (optional - for sentiment analysis)
    TWITTER_API = {
        "consumer_key": os.getenv("TWITTER_CONSUMER_KEY", ""),
        "consumer_secret": os.getenv("TWITTER_CONSUMER_SECRET", ""),
        "access_token": os.getenv("TWITTER_ACCESS_TOKEN", ""),
        "access_token_secret": os.getenv("TWITTER_ACCESS_SECRET", "")
    }

# Technical Analysis Configuration
class TechnicalConfig:
    """Technical Analysis Configuration"""
    
    # Indicator periods
    RSI_PERIOD = 14
    MACD_FAST = 12
    MACD_SLOW = 26
    MACD_SIGNAL = 9
    BB_PERIOD = 20
    BB_STD = 2
    SMA_PERIODS = [20, 50, 200]
    EMA_PERIODS = [9, 21]
    STOCH_PERIOD = 14
    ATR_PERIOD = 14
    ADX_PERIOD = 14
    
    # Important levels
    RSI_OVERSOLD = 30
    RSI_OVERBOUGHT = 70
    STOCH_OVERSOLD = 20
    STOCH_OVERBOUGHT = 80

# AI Configuration
class AIConfig:
    """AI Configuration"""
    
    # Analysis weights
    TECHNICAL_WEIGHTS = {
        'rsi': 0.15,
        'macd': 0.20,
        'bollinger': 0.15,
        'moving_averages': 0.15,
        'stochastic': 0.10,
        'adx': 0.10,
        'volume': 0.10,
        'sentiment': 0.05
    }
    
    # Decision thresholds
    BUY_THRESHOLD = 10
    SELL_THRESHOLD = -10
    MIN_CONFIDENCE = 0.3
    MAX_CONFIDENCE = 0.95
    
    # Risk management
    RISK_PER_TRADE = 0.02  # 2% risk per trade
    STOP_LOSS_ATR_MULTIPLIER = 1.5
    TAKE_PROFIT_ATR_MULTIPLIERS = [1, 2, 3]

# Display Configuration
class DisplayConfig:
    """Display Configuration"""
    
    # Colors for terminal
    COLORS = {
        'GREEN': '\033[92m',
        'RED': '\033[91m',
        'YELLOW': '\033[93m',
        'BLUE': '\033[94m',
        'PURPLE': '\033[95m',
        'CYAN': '\033[96m',
        'WHITE': '\033[97m',
        'BOLD': '\033[1m',
        'UNDERLINE': '\033[4m',
        'END': '\033[0m'
    }
    
    # Table formatting
    TABLE_WIDTH = 80
    
    # Maximum items to display in lists
    MAX_DISPLAY_ITEMS = 10

# Cache Configuration
class CacheConfig:
    """Cache Configuration"""
    
    # Cache expiry times (seconds)
    CACHE_EXPIRY = {
        'asset_info': 300,      # 5 minutes
        'historical_data': 60,  # 1 minute
        'whale_data': 300,      # 5 minutes
        'indicator_data': 120   # 2 minutes
    }
    
    # Maximum cache size
    MAX_CACHE_SIZE = 1000

# Logging Configuration
class LogConfig:
    """Logging Configuration"""
    
    LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE = LOGS_DIR / "trading_tool.log"
    MAX_LOG_SIZE = 10 * 1024 * 1024  # 10 MB
    BACKUP_COUNT = 5

# Market Configuration
class MarketConfig:
    """Market Configuration"""
    
    # Default watchlists
    DEFAULT_WATCHLISTS = {
        'crypto': [
            ('BTC-USD', 'Bitcoin'),
            ('ETH-USD', 'Ethereum'),
            ('SOL-USD', 'Solana'),
            ('BNB-USD', 'Binance Coin'),
            ('XRP-USD', 'Ripple'),
            ('ADA-USD', 'Cardano'),
            ('AVAX-USD', 'Avalanche'),
            ('DOT-USD', 'Polkadot'),
            ('DOGE-USD', 'Dogecoin'),
            ('MATIC-USD', 'Polygon')
        ],
        'forex': [
            ('EURUSD=X', 'Euro/US Dollar'),
            ('GBPUSD=X', 'British Pound/US Dollar'),
            ('USDJPY=X', 'US Dollar/Japanese Yen'),
            ('USDCHF=X', 'US Dollar/Swiss Franc'),
            ('AUDUSD=X', 'Australian Dollar/US Dollar'),
            ('USDCAD=X', 'US Dollar/Canadian Dollar'),
            ('NZDUSD=X', 'New Zealand Dollar/US Dollar')
        ],
        'stock': [
            ('AAPL', 'Apple Inc.'),
            ('MSFT', 'Microsoft Corporation'),
            ('GOOGL', 'Alphabet Inc.'),
            ('AMZN', 'Amazon.com Inc.'),
            ('TSLA', 'Tesla Inc.'),
            ('NVDA', 'NVIDIA Corporation'),
            ('META', 'Meta Platforms Inc.'),
            ('BRK-B', 'Berkshire Hathaway Inc.'),
            ('JPM', 'JPMorgan Chase & Co.'),
            ('JNJ', 'Johnson & Johnson')
        ]
    }
    
    # Allowed timeframes
    ALLOWED_TIMEFRAMES = ['1m', '5m', '15m', '30m', '1h', '4h', '1d', '1wk', '1mo']
    
    # Data limits
    MAX_DATA_POINTS = 1000
    DEFAULT_LOOKBACK_DAYS = 365

# Main Configuration Class
class Config:
    """Main Configuration Class"""
    
    API = APIConfig()
    TECHNICAL = TechnicalConfig()
    AI = AIConfig()
    DISPLAY = DisplayConfig()
    CACHE = CacheConfig()
    LOG = LogConfig()
    MARKET = MarketConfig()
    
    @classmethod
    def print_config(cls):
        """Print current configuration"""
        print("\n🔧 Program Configuration:")
        print(f"   Data Path: {DATA_DIR}")
        print(f"   Logs Path: {LOGS_DIR}")
        print(f"   Log Level: {cls.LOG.LOG_LEVEL}")
        print(f"   Stocks in Watchlist: {len(cls.MARKET.DEFAULT_WATCHLISTS['stock'])}")
        print(f"   Cryptos in Watchlist: {len(cls.MARKET.DEFAULT_WATCHLISTS['crypto'])}")

# Test configuration
if __name__ == "__main__":
    Config.print_config()
