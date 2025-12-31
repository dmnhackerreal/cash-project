# -*- coding: utf-8 -*-
"""
Whale Tracking Module
Track whale activities and large wallet movements
"""

import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import time
import json

from config import Config
from utils.logger import setup_logger
from utils.helpers import cache_result

logger = setup_logger(__name__)

class WhaleTracker:
    """Track whale activities and large transactions"""
    
    def __init__(self):
        """Initialize whale tracker"""
        self.api_key = Config.API.WHALE_ALERT_API
        self.cache = {}
        logger.info("Whale Tracker initialized")
    
    @cache_result(expiry_seconds=Config.CACHE.CACHE_EXPIRY['whale_data'])
    def get_whale_activity(self, symbol: str, hours: int = 24) -> Optional[Dict[str, Any]]:
        """
        Get whale activity for a cryptocurrency
        
        Parameters:
            symbol (str): Cryptocurrency symbol (e.g., BTC, ETH)
            hours (int): Hours to look back
        
        Returns:
            Optional[Dict[str, Any]]: Whale activity data or None
        """
        try:
            # For BTC, ETH, etc., we can use various sources
            # This is a simplified implementation
            
            # Clean symbol
            clean_symbol = symbol.upper().replace('-USD', '').replace('/USD', '')
            
            logger.info(f"Fetching whale activity for {clean_symbol}")
            
            # Simulated data (replace with actual API calls)
            whale_data = self._get_simulated_whale_data(clean_symbol, hours)
            
            if whale_data:
                logger.info(f"Found {whale_data.get('transaction_count', 0)} whale transactions")
                return whale_data
            else:
                logger.warning(f"No whale data found for {clean_symbol}")
                return None
            
        except Exception as e:
            logger.error(f"Error fetching whale activity for {symbol}: {e}")
            return None
    
    def get_large_transactions(self, symbol: str, min_amount: float = 1000000, 
                              hours: int = 24) -> List[Dict[str, Any]]:
        """
        Get large transactions for a cryptocurrency
        
        Parameters:
            symbol (str): Cryptocurrency symbol
            min_amount (float): Minimum transaction amount in USD
            hours (int): Hours to look back
        
        Returns:
            List[Dict[str, Any]]: List of large transactions
        """
        transactions = []
        
        try:
            # Get whale activity
            whale_data = self.get_whale_activity(symbol, hours)
            
            if whale_data and 'transactions' in whale_data:
                # Filter by minimum amount
                for tx in whale_data['transactions']:
                    if tx.get('amount_usd', 0) >= min_amount:
                        transactions.append(tx)
            
            logger.info(f"Found {len(transactions)} large transactions for {symbol}")
            
        except Exception as e:
            logger.error(f"Error getting large transactions for {symbol}: {e}")
        
        return transactions
    
    def get_top_wallets(self, symbol: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get top wallets for a cryptocurrency
        
        Parameters:
            symbol (str): Cryptocurrency symbol
            limit (int): Number of wallets to return
        
        Returns:
            List[Dict[str, Any]]: List of top wallets
        """
        wallets = []
        
        try:
            # Clean symbol
            clean_symbol = symbol.upper().replace('-USD', '').replace('/USD', '')
            
            logger.info(f"Fetching top wallets for {clean_symbol}")
            
            # Simulated data (replace with blockchain explorer API)
            wallets = self._get_simulated_top_wallets(clean_symbol, limit)
            
            logger.info(f"Found {len(wallets)} top wallets for {clean_symbol}")
            
        except Exception as e:
            logger.error(f"Error getting top wallets for {symbol}: {e}")
        
        return wallets
    
    def get_exchange_flows(self, symbol: str, hours: int = 24) -> Dict[str, float]:
        """
        Get exchange inflows and outflows
        
        Parameters:
            symbol (str): Cryptocurrency symbol
            hours (int): Hours to look back
        
        Returns:
            Dict[str, float]: Exchange flow data
        """
        flows = {'inflow': 0, 'outflow': 0, 'net_flow': 0}
        
        try:
            # Get whale activity
            whale_data = self.get_whale_activity(symbol, hours)
            
            if whale_data:
                flows['inflow'] = whale_data.get('inflow_24h', 0)
                flows['outflow'] = whale_data.get('outflow_24h', 0)
                flows['net_flow'] = flows['inflow'] - flows['outflow']
            
            logger.info(f"Exchange flows for {symbol}: In=${flows['inflow']:,.0f}, "
                       f"Out=${flows['outflow']:,.0f}, Net=${flows['net_flow']:,.0f}")
            
        except Exception as e:
            logger.error(f"Error getting exchange flows for {symbol}: {e}")
        
        return flows
    
    def track_whale_clusters(self, symbol: str, cluster_size: int = 10) -> List[Dict[str, Any]]:
        """
        Track whale transaction clusters
        
        Parameters:
            symbol (str): Cryptocurrency symbol
            cluster_size (int): Minimum cluster size
        
        Returns:
            List[Dict[str, Any]]: Whale clusters
        """
        clusters = []
        
        try:
            # Get large transactions
            transactions = self.get_large_transactions(symbol, min_amount=500000, hours=48)
            
            if transactions:
                # Group by hour
                df = pd.DataFrame(transactions)
                df['hour'] = pd.to_datetime(df['timestamp']).dt.floor('H')
                
                # Find clusters (hours with multiple large transactions)
                hour_counts = df.groupby('hour').size()
                cluster_hours = hour_counts[hour_counts >= cluster_size].index
                
                for hour in cluster_hours:
                    hour_txs = df[df['hour'] == hour]
                    
                    cluster = {
                        'timestamp': hour.strftime("%Y-%m-%d %H:00"),
                        'transaction_count': len(hour_txs),
                        'total_volume': hour_txs['amount_usd'].sum(),
                        'average_size': hour_txs['amount_usd'].mean(),
                        'min_size': hour_txs['amount_usd'].min(),
                        'max_size': hour_txs['amount_usd'].max()
                    }
                    
                    clusters.append(cluster)
            
            logger.info(f"Found {len(clusters)} whale clusters for {symbol}")
            
        except Exception as e:
            logger.error(f"Error tracking whale clusters for {symbol}: {e}")
        
        return clusters
    
    def analyze_whale_sentiment(self, symbol: str, days: int = 7) -> Dict[str, Any]:
        """
        Analyze whale sentiment
        
        Parameters:
            symbol (str): Cryptocurrency symbol
            days (int): Days to analyze
        
        Returns:
            Dict[str, Any]: Whale sentiment analysis
        """
        sentiment = {
            'sentiment': 'NEUTRAL',
            'score': 0,
            'confidence': 0,
            'buying_pressure': 0,
            'selling_pressure': 0
        }
        
        try:
            # Get whale activity for multiple days
            all_transactions = []
            
            for day in range(days):
                hours_back = (day + 1) * 24
                whale_data = self.get_whale_activity(symbol, hours=hours_back)
                
                if whale_data and 'transactions' in whale_data:
                    # Get transactions for this specific day
                    day_transactions = []
                    for tx in whale_data['transactions']:
                        tx_time = datetime.fromisoformat(tx.get('timestamp', '').replace('Z', '+00:00'))
                        if tx_time.date() == (datetime.now() - timedelta(days=day)).date():
                            day_transactions.append(tx)
                    
                    all_transactions.extend(day_transactions)
            
            if all_transactions:
                # Calculate metrics
                df = pd.DataFrame(all_transactions)
                
                # Determine if transactions are buys or sells
                # In real implementation, you would check if going to/from exchanges
                
                # Simulate sentiment calculation
                total_volume = df['amount_usd'].sum() if 'amount_usd' in df.columns else 0
                transaction_count = len(df)
                
                # Simple sentiment based on volume and count
                if total_volume > 100000000:  # More than $100M
                    if transaction_count > 50:
                        sentiment['sentiment'] = 'STRONG_BUY'
                        sentiment['score'] = 85
                    else:
                        sentiment['sentiment'] = 'BUY'
                        sentiment['score'] = 70
                elif total_volume > 50000000:  # More than $50M
                    sentiment['sentiment'] = 'SLIGHT_BUY'
                    sentiment['score'] = 60
                elif total_volume < 10000000:  # Less than $10M
                    sentiment['sentiment'] = 'SELL'
                    sentiment['score'] = 40
                else:
                    sentiment['sentiment'] = 'NEUTRAL'
                    sentiment['score'] = 50
                
                # Calculate confidence based on data quality
                sentiment['confidence'] = min(0.9, transaction_count / 100)
                
                # Estimate buying/selling pressure
                # In real implementation, analyze transaction directions
                sentiment['buying_pressure'] = min(1.0, total_volume / 100000000)
                sentiment['selling_pressure'] = min(1.0, (50000000 - total_volume) / 50000000)
            
            logger.info(f"Whale sentiment for {symbol}: {sentiment['sentiment']} "
                       f"(score: {sentiment['score']}, confidence: {sentiment['confidence']:.1%})")
            
        except Exception as e:
            logger.error(f"Error analyzing whale sentiment for {symbol}: {e}")
        
        return sentiment
    
    def get_whale_alert_notifications(self, min_value: float = 1000000, 
                                     limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get whale alert notifications
        
        Parameters:
            min_value (float): Minimum transaction value
            limit (int): Maximum number of alerts
        
        Returns:
            List[Dict[str, Any]]: Whale alerts
        """
        alerts = []
        
        try:
            # This would integrate with Whale Alert API
            if self.api_key:
                url = f"https://api.whale-alert.io/v1/transactions"
                params = {
                    'api_key': self.api_key,
                    'min_value': min_value,
                    'limit': limit
                }
                
                response = requests.get(url, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    alerts = data.get('transactions', [])
                else:
                    logger.warning(f"Whale Alert API returned {response.status_code}")
            
            logger.info(f"Got {len(alerts)} whale alerts")
            
        except Exception as e:
            logger.warning(f"Error getting whale alerts: {e}")
            # Return simulated data if API fails
            alerts = self._get_simulated_alerts(min_value, limit)
        
        return alerts
    
    def _get_simulated_whale_data(self, symbol: str, hours: int) -> Dict[str, Any]:
        """Get simulated whale data (for testing)"""
        # Generate realistic simulated data
        import random
        
        base_transaction_count = random.randint(5, 50)
        transaction_count = base_transaction_count * (1 if symbol != 'BTC' else 3)
        
        transactions = []
        total_volume = 0
        
        for i in range(transaction_count):
            # Generate random transaction
            amount_usd = random.randint(100000, 5000000)
            if random.random() < 0.2:  # 20% chance of very large transaction
                amount_usd *= random.randint(5, 20)
            
            transaction = {
                'id': f"tx_{symbol}_{i}",
                'timestamp': (datetime.now() - timedelta(hours=random.randint(0, hours))).isoformat(),
                'amount_usd': amount_usd,
                'amount_crypto': amount_usd / random.randint(1000, 50000),
                'from_address': f"0x{''.join(random.choices('0123456789abcdef', k=40))}",
                'to_address': f"0x{''.join(random.choices('0123456789abcdef', k=40))}",
                'type': random.choice(['exchange_deposit', 'exchange_withdrawal', 'wallet_transfer']),
                'exchange': random.choice(['Binance', 'Coinbase', 'Kraken', 'FTX', 'Huobi']) 
                           if random.random() < 0.7 else None
            }
            
            transactions.append(transaction)
            total_volume += amount_usd
        
        # Calculate inflows and outflows
        inflow = sum(tx['amount_usd'] for tx in transactions if tx['type'] == 'exchange_deposit')
        outflow = sum(tx['amount_usd'] for tx in transactions if tx['type'] == 'exchange_withdrawal')
        
        # Generate top wallets
        top_wallets = self._get_simulated_top_wallets(symbol, 5)
        
        return {
            'symbol': symbol,
            'transaction_count': transaction_count,
            'total_volume': total_volume,
            'average_size': total_volume / transaction_count if transaction_count > 0 else 0,
            'inflow_24h': inflow,
            'outflow_24h': outflow,
            'net_flow': inflow - outflow,
            'top_wallets': top_wallets,
            'transactions': transactions[:10],  # Limit to 10 for response size
            'last_updated': datetime.now().isoformat()
        }
    
    def _get_simulated_top_wallets(self, symbol: str, limit: int) -> List[Dict[str, Any]]:
        """Get simulated top wallets (for testing)"""
        import random
        
        wallets = []
        
        # Base balances based on symbol
        base_balance = {
            'BTC': 1000,
            'ETH': 10000,
            'SOL': 100000,
            'ADA': 1000000,
            'DOT': 500000,
            'default': 100000
        }
        
        base = base_balance.get(symbol, base_balance['default'])
        
        for i in range(limit):
            # Generate decreasing balances
            balance = base * (limit - i) * random.uniform(0.8, 1.2)
            
            wallet = {
                'rank': i + 1,
                'address': f"0x{''.join(random.choices('0123456789abcdef', k=40))}",
                'balance': balance,
                'balance_usd': balance * random.randint(1000, 50000),
                'percentage': (balance / (base * limit * 10)) * 100,
                'type': random.choice(['exchange', 'whale', 'institution', 'miner'])
            }
            
            wallets.append(wallet)
        
        return wallets
    
    def _get_simulated_alerts(self, min_value: float, limit: int) -> List[Dict[str, Any]]:
        """Get simulated alerts (for testing)"""
        import random
        
        symbols = ['BTC', 'ETH', 'SOL', 'ADA', 'DOT', 'XRP', 'DOGE', 'MATIC', 'AVAX', 'LINK']
        alerts = []
        
        for i in range(min(limit, 20)):
            symbol = random.choice(symbols)
            amount_usd = random.randint(int(min_value), int(min_value * 10))
            
            alert = {
                'id': f"alert_{i}",
                'timestamp': (datetime.now() - timedelta(minutes=random.randint(0, 120))).isoformat(),
                'symbol': symbol,
                'amount_usd': amount_usd,
                'amount_crypto': amount_usd / random.randint(1000, 50000),
                'from': random.choice(['Unknown Wallet', 'Exchange', 'Institution']),
                'to': random.choice(['Exchange', 'Unknown Wallet']),
                'transaction_type': random.choice(['transfer', 'exchange']),
                'hash': f"0x{''.join(random.choices('0123456789abcdef', k=64))}"
            }
            
            alerts.append(alert)
        
        return alerts
    
    def save_whale_data(self, symbol: str, data: Dict[str, Any], filepath: str):
        """
        Save whale data to file
        
        Parameters:
            symbol (str): Cryptocurrency symbol
            data (Dict[str, Any]): Whale data
            filepath (str): File path
        """
        try:
            import json
            
            # Add metadata
            data_with_meta = {
                'symbol': symbol,
                'fetched_at': datetime.now().isoformat(),
                'data': data
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data_with_meta, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Whale data saved to {filepath}")
            
        except Exception as e:
            logger.error(f"Error saving whale data: {e}")
    
    def load_whale_data(self, filepath: str) -> Optional[Dict[str, Any]]:
        """
        Load whale data from file
        
        Parameters:
            filepath (str): File path
        
        Returns:
            Optional[Dict[str, Any]]: Whale data or None
        """
        try:
            import json
            
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            logger.info(f"Whale data loaded from {filepath}")
            return data.get('data', {})
            
        except Exception as e:
            logger.error(f"Error loading whale data: {e}")
            return None

def test_whale_tracker():
    """Test whale tracker"""
    tracker = WhaleTracker()
    
    print("Testing Whale Tracker...")
    
    # Test whale activity
    whale_data = tracker.get_whale_activity('BTC', hours=24)
    
    if whale_data:
        print(f"\nWhale Activity for BTC:")
        print(f"  Transactions: {whale_data.get('transaction_count', 0)}")
        print(f"  Total Volume: ${whale_data.get('total_volume', 0):,.0f}")
        print(f"  Average Size: ${whale_data.get('average_size', 0):,.0f}")
        print(f"  24h Inflow: ${whale_data.get('inflow_24h', 0):,.0f}")
        print(f"  24h Outflow: ${whale_data.get('outflow_24h', 0):,.0f}")
        
        if 'top_wallets' in whale_data:
            print(f"\nTop Wallets:")
            for wallet in whale_data['top_wallets'][:3]:
                print(f"  • {wallet.get('address', '')[:20]}... : "
                      f"{wallet.get('balance', 0):,.0f} BTC")
    
    # Test large transactions
    large_txs = tracker.get_large_transactions('ETH', min_amount=1000000)
    print(f"\nLarge ETH Transactions: {len(large_txs)}")
    
    # Test whale sentiment
    sentiment = tracker.analyze_whale_sentiment('SOL', days=3)
    print(f"\nWhale Sentiment for SOL: {sentiment['sentiment']} "
          f"(score: {sentiment['score']})")

if __name__ == "__main__":
    test_whale_tracker()
