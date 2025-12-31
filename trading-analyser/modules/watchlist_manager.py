# -*- coding: utf-8 -*-
"""
Watchlist management module
Watchlist management for Crypto, Forex, and US Stocks
"""

import yfinance as yf
from datetime import datetime
from typing import List, Dict, Optional
import pandas as pd

from config import Config
from utils.logger import setup_logger
from utils.helpers import color_text, print_table, format_number

logger = setup_logger(__name__)

class WatchlistManager:
    """Manage watchlists for different markets"""
    
    def __init__(self):
        """Initialize watchlist manager"""
        self.watchlists = Config.MARKET.DEFAULT_WATCHLISTS
        self.cache = {}
        logger.info("Watchlist Manager initialized")
    
    def get_live_prices(self, symbols: List[str]) -> Dict[str, float]:
        """
        Get live prices for symbols
        
        Parameters:
            symbols (List[str]): List of symbols
        
        Returns:
            Dict[str, float]: Symbol-price mapping
        """
        prices = {}
        
        try:
            # Fetch prices in batches
            for symbol in symbols:
                try:
                    ticker = yf.Ticker(symbol)
                    price = ticker.info.get('regularMarketPrice', 0)
                    
                    # Fallback to history if needed
                    if not price or price == 0:
                        history = ticker.history(period='1d', interval='1m')
                        if not history.empty:
                            price = history['Close'].iloc[-1]
                    
                    prices[symbol] = price
                    
                except Exception as e:
                    logger.warning(f"Failed to get price for {symbol}: {e}")
                    prices[symbol] = 0
        
        except Exception as e:
            logger.error(f"Error fetching live prices: {e}")
        
        return prices
    
    def display_watchlist(self, market_type: str = 'all'):
        """
        Display watchlist
        
        Parameters:
            market_type (str): Market type ('crypto', 'forex', 'stock', 'all')
        """
        print(f"\n📋 {'ALL MARKETS' if market_type == 'all' else market_type.upper()} WATCHLIST")
        print("=" * Config.DISPLAY.TABLE_WIDTH)
        
        if market_type == 'all':
            for market in ['crypto', 'forex', 'stock']:
                self._display_single_watchlist(market)
        elif market_type in self.watchlists:
            self._display_single_watchlist(market_type)
        else:
            print(f"❌ Invalid market type: {market_type}")
    
    def _display_single_watchlist(self, market_type: str):
        """
        Display single market watchlist
        
        Parameters:
            market_type (str): Market type
        """
        if market_type not in self.watchlists:
            logger.error(f"Invalid market type: {market_type}")
            return
        
        symbols = [item[0] for item in self.watchlists[market_type]]
        names = [item[1] for item in self.watchlists[market_type]]
        
        # Get live prices
        prices = self.get_live_prices(symbols)
        
        # Prepare table data
        table_data = []
        for i, (symbol, name) in enumerate(self.watchlists[market_type]):
            price = prices.get(symbol, 0)
            price_str = format_number(price, 2)
            
            # Add color based on market type
            if market_type == 'crypto':
                symbol_display = color_text(symbol, 'cyan')
            elif market_type == 'forex':
                symbol_display = color_text(symbol, 'purple')
            else:
                symbol_display = color_text(symbol, 'green')
            
            table_data.append([
                str(i + 1),
                symbol_display,
                name[:25],  # Truncate long names
                price_str
            ])
        
        # Display table
        headers = ["#", "Symbol", "Name", "Current Price"]
        print(f"\n{market_type.upper()}")
        print("-" * 50)
        print_table(table_data, headers, align='left')
        
        # Display summary
        self._display_summary(market_type, prices)
    
    def _display_summary(self, market_type: str, prices: Dict[str, float]):
        """
        Display watchlist summary
        
        Parameters:
            market_type (str): Market type
            prices (Dict[str, float]): Price data
        """
        valid_prices = [p for p in prices.values() if p > 0]
        
        if valid_prices:
            avg_price = sum(valid_prices) / len(valid_prices)
            max_price = max(valid_prices)
            min_price = min(valid_prices)
            
            print(f"\n📊 Summary:")
            print(f"   Total Assets: {len(self.watchlists[market_type])}")
            print(f"   Average Price: {format_number(avg_price)}")
            print(f"   Highest: {format_number(max_price)}")
            print(f"   Lowest: {format_number(min_price)}")
            
            # Market sentiment
            rising = sum(1 for p in valid_prices if p > avg_price)
            falling = len(valid_prices) - rising
            
            sentiment = "🟢 Bullish" if rising > falling else "🔴 Bearish" if falling > rising else "🟡 Neutral"
            print(f"   Sentiment: {sentiment} ({rising}↑ / {falling}↓)")
    
    def add_to_watchlist(self, symbol: str, name: str, market_type: str):
        """
        Add symbol to watchlist
        
        Parameters:
            symbol (str): Trading symbol
            name (str): Asset name
            market_type (str): Market type
        """
        if market_type not in self.watchlists:
            logger.error(f"Cannot add to non-existent market: {market_type}")
            return False
        
        # Check if already exists
        existing_symbols = [item[0] for item in self.watchlists[market_type]]
        if symbol in existing_symbols:
            logger.warning(f"Symbol {symbol} already in watchlist")
            return False
        
        self.watchlists[market_type].append((symbol, name))
        logger.info(f"Added {symbol} ({name}) to {market_type} watchlist")
        return True
    
    def remove_from_watchlist(self, symbol: str, market_type: str):
        """
        Remove symbol from watchlist
        
        Parameters:
            symbol (str): Trading symbol
            market_type (str): Market type
        """
        if market_type not in self.watchlists:
            logger.error(f"Cannot remove from non-existent market: {market_type}")
            return False
        
        # Find and remove
        for i, (sym, name) in enumerate(self.watchlists[market_type]):
            if sym == symbol:
                del self.watchlists[market_type][i]
                logger.info(f"Removed {symbol} from {market_type} watchlist")
                return True
        
        logger.warning(f"Symbol {symbol} not found in {market_type} watchlist")
        return False
    
    def get_watchlist_dataframe(self, market_type: str = 'all') -> pd.DataFrame:
        """
        Get watchlist as DataFrame
        
        Parameters:
            market_type (str): Market type
        
        Returns:
            pd.DataFrame: Watchlist data
        """
        data = []
        
        if market_type == 'all':
            markets = self.watchlists.keys()
        else:
            markets = [market_type]
        
        for market in markets:
            if market in self.watchlists:
                for symbol, name in self.watchlists[market]:
                    data.append({
                        'market': market,
                        'symbol': symbol,
                        'name': name
                    })
        
        return pd.DataFrame(data)
    
    def save_watchlist(self, filepath: str):
        """
        Save watchlist to file
        
        Parameters:
            filepath (str): File path
        """
        import json
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.watchlists, f, indent=2, ensure_ascii=False)
            logger.info(f"Watchlist saved to {filepath}")
        except Exception as e:
            logger.error(f"Error saving watchlist: {e}")
    
    def load_watchlist(self, filepath: str):
        """
        Load watchlist from file
        
        Parameters:
            filepath (str): File path
        """
        import json
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                self.watchlists = json.load(f)
            logger.info(f"Watchlist loaded from {filepath}")
        except Exception as e:
            logger.error(f"Error loading watchlist: {e}")

def test_watchlist():
    """Test watchlist manager"""
    manager = WatchlistManager()
    
    print("Testing watchlist manager...")
    
    # Display all watchlists
    manager.display_watchlist('crypto')
    
    # Add new symbol
    manager.add_to_watchlist('LTC-USD', 'Litecoin', 'crypto')
    
    # Display again
    manager.display_watchlist('crypto')
    
    # Get DataFrame
    df = manager.get_watchlist_dataframe('crypto')
    print(f"\nDataFrame shape: {df.shape}")

if __name__ == "__main__":
    test_watchlist()
