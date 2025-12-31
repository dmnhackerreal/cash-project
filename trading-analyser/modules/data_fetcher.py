# -*- coding: utf-8 -*-
"""
Data fetching module
Fetch market data from various sources
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
import requests
import time

from config import Config
from utils.logger import setup_logger
from utils.helpers import cache_result, validate_symbol, detect_market_type

logger = setup_logger(__name__)

class MarketDataFetcher:
    """Fetch market data from various sources"""
    
    def __init__(self):
        """Initialize data fetcher"""
        self.yfinance_timeout = Config.API.YFINANCE_TIMEOUT
        self.cache = {}
        logger.info("Market Data Fetcher initialized")
    
    @cache_result(expiry_seconds=Config.CACHE.CACHE_EXPIRY['historical_data'])
    def get_historical_data(self, symbol: str, interval: str = '1d', 
                           period: str = '1mo') -> Optional[pd.DataFrame]:
        """
        Get historical market data
        
        Parameters:
            symbol (str): Trading symbol
            interval (str): Data interval (1m, 5m, 15m, 30m, 1h, 1d, 1wk, 1mo)
            period (str): Data period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, max)
        
        Returns:
            Optional[pd.DataFrame]: Historical data or None
        """
        try:
            # Validate symbol
            if not validate_symbol(symbol):
                logger.warning(f"Invalid symbol: {symbol}")
                return None
            
            # Clean symbol for Yahoo Finance
            clean_symbol = self._clean_symbol(symbol)
            
            logger.info(f"Fetching historical data for {clean_symbol} ({interval}/{period})")
            
            # Fetch data
            ticker = yf.Ticker(clean_symbol)
            df = ticker.history(period=period, interval=interval)
            
            if df.empty:
                logger.warning(f"No data found for {clean_symbol}")
                return None
            
            # Clean and prepare data
            df = self._clean_dataframe(df)
            
            logger.info(f"Fetched {len(df)} data points for {clean_symbol}")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol}: {e}")
            return None
    
    @cache_result(expiry_seconds=Config.CACHE.CACHE_EXPIRY['asset_info'])
    def get_asset_info(self, symbol: str, market_type: str = 'auto') -> Optional[Dict[str, Any]]:
        """
        Get comprehensive asset information
        
        Parameters:
            symbol (str): Trading symbol
            market_type (str): Market type ('crypto', 'forex', 'stock', 'auto')
        
        Returns:
            Optional[Dict[str, Any]]: Asset information or None
        """
        try:
            # Auto-detect market type if needed
            if market_type == 'auto':
                market_type = detect_market_type(symbol)
            
            logger.info(f"Fetching info for {symbol} (market: {market_type})")
            
            # Clean symbol
            clean_symbol = self._clean_symbol(symbol, market_type)
            
            # Fetch from Yahoo Finance
            ticker = yf.Ticker(clean_symbol)
            info = ticker.info
            
            if not info:
                logger.warning(f"No info found for {clean_symbol}")
                return None
            
            # Extract relevant information
            asset_info = self._extract_asset_info(info, market_type, symbol)
            
            # Add additional data based on market type
            if market_type == 'crypto':
                asset_info.update(self._get_crypto_extra_info(symbol))
            elif market_type == 'stock':
                asset_info.update(self._get_stock_extra_info(symbol))
            
            logger.info(f"Fetched info for {symbol}")
            return asset_info
            
        except Exception as e:
            logger.error(f"Error fetching asset info for {symbol}: {e}")
            return None
    
    def get_real_time_price(self, symbol: str) -> Optional[float]:
        """
        Get real-time price
        
        Parameters:
            symbol (str): Trading symbol
        
        Returns:
            Optional[float]: Current price or None
        """
        try:
            clean_symbol = self._clean_symbol(symbol)
            ticker = yf.Ticker(clean_symbol)
            
            # Try to get real-time price
            price = ticker.info.get('regularMarketPrice', 0)
            
            if not price or price == 0:
                # Fallback to latest close
                history = ticker.history(period='1d', interval='1m')
                if not history.empty:
                    price = history['Close'].iloc[-1]
            
            return price if price else None
            
        except Exception as e:
            logger.error(f"Error fetching real-time price for {symbol}: {e}")
            return None
    
    def get_multiple_prices(self, symbols: list) -> Dict[str, float]:
        """
        Get prices for multiple symbols
        
        Parameters:
            symbols (list): List of symbols
        
        Returns:
            Dict[str, float]: Symbol-price mapping
        """
        prices = {}
        
        for symbol in symbols:
            try:
                price = self.get_real_time_price(symbol)
                if price:
                    prices[symbol] = price
            except Exception as e:
                logger.warning(f"Error getting price for {symbol}: {e}")
        
        return prices
    
    def get_volume_data(self, symbol: str, days: int = 30) -> Optional[pd.DataFrame]:
        """
        Get volume data
        
        Parameters:
            symbol (str): Trading symbol
            days (int): Number of days
        
        Returns:
            Optional[pd.DataFrame]: Volume data or None
        """
        try:
            period = f"{days}d"
            df = self.get_historical_data(symbol, interval='1d', period=period)
            
            if df is not None and 'Volume' in df.columns:
                volume_df = df[['Volume']].copy()
                volume_df['Volume_SMA'] = volume_df['Volume'].rolling(window=20).mean()
                volume_df['Volume_Ratio'] = volume_df['Volume'] / volume_df['Volume_SMA']
                
                return volume_df
            
        except Exception as e:
            logger.error(f"Error fetching volume data for {symbol}: {e}")
        
        return None
    
    def _clean_symbol(self, symbol: str, market_type: str = None) -> str:
        """
        Clean symbol for Yahoo Finance
        
        Parameters:
            symbol (str): Trading symbol
            market_type (str): Market type
        
        Returns:
            str: Cleaned symbol
        """
        # Remove spaces
        clean = symbol.strip().upper()
        
        # Handle forex pairs
        if market_type == 'forex' and '=X' not in clean:
            clean = f"{clean}=X"
        
        # Handle crypto
        if market_type == 'crypto' and '-USD' not in clean and '/USD' not in clean:
            # Check if it's already a pair
            if len(clean.split('-')) == 1 and len(clean.split('/')) == 1:
                clean = f"{clean}-USD"
        
        return clean
    
    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and prepare dataframe
        
        Parameters:
            df (pd.DataFrame): Raw dataframe
        
        Returns:
            pd.DataFrame: Cleaned dataframe
        """
        # Make a copy
        df_clean = df.copy()
        
        # Ensure required columns
        required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        for col in required_cols:
            if col not in df_clean.columns:
                df_clean[col] = np.nan
        
        # Remove NaN values
        df_clean = df_clean.dropna(subset=['Close'])
        
        # Convert to numeric
        for col in required_cols:
            df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
        
        # Sort by index
        df_clean = df_clean.sort_index()
        
        # Calculate returns
        df_clean['Returns'] = df_clean['Close'].pct_change()
        df_clean['Log_Returns'] = np.log(df_clean['Close'] / df_clean['Close'].shift(1))
        
        return df_clean
    
    def _extract_asset_info(self, info: Dict, market_type: str, symbol: str) -> Dict[str, Any]:
        """
        Extract asset information from Yahoo Finance data
        
        Parameters:
            info (Dict): Yahoo Finance info
            market_type (str): Market type
            symbol (str): Original symbol
        
        Returns:
            Dict[str, Any]: Extracted information
        """
        asset_info = {
            'symbol': symbol,
            'market_type': market_type,
            'name': info.get('shortName', symbol),
            'current_price': info.get('regularMarketPrice', 0),
            'previous_close': info.get('previousClose', 0),
            'open_price': info.get('open', 0),
            'day_high': info.get('dayHigh', 0),
            'day_low': info.get('dayLow', 0),
            'volume': info.get('volume', 0),
            'avg_volume': info.get('averageVolume', 0),
            'market_cap': info.get('marketCap', 0),
            'fifty_two_week_high': info.get('fiftyTwoWeekHigh', 0),
            'fifty_two_week_low': info.get('fiftyTwoWeekLow', 0),
            'dividend_yield': info.get('dividendYield', 0),
            'pe_ratio': info.get('trailingPE', 0),
            'beta': info.get('beta', 0),
            'currency': info.get('currency', 'USD'),
            'last_updated': datetime.now().isoformat()
        }
        
        # Calculate daily change
        if asset_info['current_price'] and asset_info['previous_close']:
            change = asset_info['current_price'] - asset_info['previous_close']
            change_percent = (change / asset_info['previous_close']) * 100
            asset_info['daily_change'] = change
            asset_info['daily_change_percent'] = change_percent
        
        return asset_info
    
    def _get_crypto_extra_info(self, symbol: str) -> Dict[str, Any]:
        """
        Get extra information for cryptocurrencies
        
        Parameters:
            symbol (str): Crypto symbol
        
        Returns:
            Dict[str, Any]: Extra crypto information
        """
        extra_info = {}
        
        try:
            # You can add crypto-specific APIs here
            # For example: CoinGecko, CryptoCompare, etc.
            
            # For now, return empty dict
            pass
            
        except Exception as e:
            logger.warning(f"Error getting crypto extra info for {symbol}: {e}")
        
        return extra_info
    
    def _get_stock_extra_info(self, symbol: str) -> Dict[str, Any]:
        """
        Get extra information for stocks
        
        Parameters:
            symbol (str): Stock symbol
        
        Returns:
            Dict[str, Any]: Extra stock information
        """
        extra_info = {}
        
        try:
            # You can add stock-specific APIs here
            # For example: Alpha Vantage, Finnhub, etc.
            
            # For now, return empty dict
            pass
            
        except Exception as e:
            logger.warning(f"Error getting stock extra info for {symbol}: {e}")
        
        return extra_info

def test_data_fetcher():
    """Test data fetcher"""
    fetcher = MarketDataFetcher()
    
    print("Testing Market Data Fetcher...")
    
    # Test historical data
    df = fetcher.get_historical_data('AAPL', interval='1d', period='1mo')
    if df is not None:
        print(f"\nAAPL data shape: {df.shape}")
        print(f"Latest close: ${df['Close'].iloc[-1]:.2f}")
    
    # Test asset info
    info = fetcher.get_asset_info('BTC-USD', 'crypto')
    if info:
        print(f"\nBTC Info:")
        print(f"  Name: {info.get('name')}")
        print(f"  Price: ${info.get('current_price', 0):.2f}")
        print(f"  Market Cap: ${info.get('market_cap', 0):,.0f}")
    
    # Test real-time price
    price = fetcher.get_real_time_price('AAPL')
    if price:
        print(f"\nAAPL real-time price: ${price:.2f}")

if __name__ == "__main__":
    test_data_fetcher()
