"""
Performance analyzer for new tokens with advanced metrics
"""
import asyncio
import aiohttp
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import json
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """Performance metrics for tokens"""
    token_address: str
    symbol: str
    win_rate_30d: float
    pnl_30d: float
    transaction_count_7d: int
    volume_7d_usd: float
    price_change_24h: float
    holder_count: int
    liquidity_usd: float
    creation_timestamp: datetime
    composite_score: float
    passes_filters: bool
    filter_violations: List[str]
    
    def to_dict(self) -> Dict:
        return {
            "token_address": self.token_address,
            "symbol": self.symbol,
            "win_rate_30d": self.win_rate_30d,
            "pnl_30d": self.pnl_30d,
            "transaction_count_7d": self.transaction_count_7d,
            "volume_7d_usd": self.volume_7d_usd,
            "price_change_24h": self.price_change_24h,
            "holder_count": self.holder_count,
            "liquidity_usd": self.liquidity_usd,
            "creation_timestamp": self.creation_timestamp.isoformat(),
            "composite_score": self.composite_score,
            "passes_filters": self.passes_filters,
            "filter_violations": self.filter_violations
        }


class NewTokenPerformanceAnalyzer:
    """Main analyzer for new tokens with performance filters"""
    
    def __init__(self, config_path: str = "config/performance_config.yaml"):
        import yaml
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        self.session = aiohttp.ClientSession()
    
    async def analyze_token(self, token_address: str, symbol: str = "") -> Optional[PerformanceMetrics]:
        """
        Analyze a single token against performance filters
        """
        try:
            # Fetch token data
            token_data = await self._fetch_token_data(token_address)
            
            if not token_data:
                return None
            
            # Calculate metrics
            win_rate = await self._calculate_win_rate(token_data)
            pnl_30d = await self._calculate_pnl_30d(token_data)
            
            # Get transaction count (simplified)
            tx_count = token_data.get('transaction_count_7d', 0)
            
            # Check filter compliance
            passes_filters, violations = await self._check_performance_filters(
                win_rate, pnl_30d, tx_count, token_data
            )
            
            # Calculate composite score
            composite_score = await self._calculate_composite_score(
                win_rate, pnl_30d, tx_count, token_data
            )
            
            # Create performance metrics
            metrics = PerformanceMetrics(
                token_address=token_address,
                symbol=symbol or token_data.get('symbol', 'UNKNOWN'),
                win_rate_30d=win_rate,
                pnl_30d=pnl_30d,
                transaction_count_7d=tx_count,
                volume_7d_usd=token_data.get('volume_7d_usd', 0),
                price_change_24h=token_data.get('price_change_24h', 0),
                holder_count=token_data.get('holder_count', 0),
                liquidity_usd=token_data.get('liquidity_usd', 0),
                creation_timestamp=datetime.fromisoformat(
                    token_data.get('creation_time', datetime.utcnow().isoformat())
                ),
                composite_score=composite_score,
                passes_filters=passes_filters,
                filter_violations=violations
            )
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error analyzing token {token_address}: {e}")
            return None
    
    async def _fetch_token_data(self, token_address: str) -> Optional[Dict]:
        """Fetch token data from DexScreener"""
        try:
            async with self.session.get(
                f"https://api.dexscreener.com/latest/dex/tokens/{token_address}"
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    pairs = data.get('pairs', [])
                    
                    if pairs:
                        pair = pairs[0]
                        return {
                            'symbol': pair.get('baseToken', {}).get('symbol', 'UNKNOWN'),
                            'price': float(pair.get('priceUsd', 0)),
                            'liquidity_usd': float(pair.get('liquidity', {}).get('usd', 0)),
                            'volume_24h_usd': float(pair.get('volume', {}).get('h24', 0)),
                            'volume_7d_usd': float(pair.get('volume', {}).get('h24', 0)) * 7,  # Approximation
                            'price_change_24h': float(pair.get('priceChange', {}).get('h24', 0)),
                            'transaction_count_7d': 100,  # Placeholder
                            'holder_count': 500,  # Placeholder
                            'creation_time': datetime.utcnow().isoformat()
                        }
        except Exception as e:
            logger.error(f"Error fetching data for {token_address}: {e}")
        
        return None
    
    async def _calculate_win_rate(self, token_data: Dict) -> float:
        """Calculate win rate (simplified for now)"""
        # Placeholder calculation - can be enhanced with historical data
        price_change = token_data.get('price_change_24h', 0)
        
        if price_change > 5:
            return 75.0  # High win rate for tokens with >5% gain
        elif price_change > 0:
            return 50.0  # Medium win rate
        else:
            return 25.0  # Low win rate
    
    async def _calculate_pnl_30d(self, token_data: Dict) -> float:
        """Calculate 30-day PnL (simplified)"""
        # Placeholder calculation
        price_change = token_data.get('price_change_24h', 0)
        
        # Extrapolate 24h change to 30 days (simplified)
        return price_change * 30
    
    async def _check_performance_filters(self, win_rate: float, pnl_30d: float,
                                        transaction_count_7d: int, 
                                        token_data: Dict) -> Tuple[bool, List[str]]:
        """
        Check if token meets all performance filters
        """
        filters_config = self.config['performance_filters']
        violations = []
        
        # 1. Win rate filter (25%+)
        if win_rate < filters_config['win_rate']['minimum']:
            violations.append(f"Win rate too low: {win_rate:.1f}%")
        
        # 2. 30D PnL filter (40%+)
        if pnl_30d < filters_config['pnl_30d']['minimum']:
            violations.append(f"30D PnL too low: {pnl_30d:.1f}%")
        
        # 3. 7D Transaction count filter (<150)
        if transaction_count_7d >= filters_config['transaction_7d']['maximum']:
            violations.append(f"7D transactions too high: {transaction_count_7d}")
        
        # 4. Volume requirements
        volume_7d = token_data.get('volume_7d_usd', 0)
        min_daily = filters_config['volume_requirements']['min_daily_volume_usd']
        
        if volume_7d < min_daily * 7:
            violations.append(f"7D volume too low: ${volume_7d:,.0f}")
        
        # 5. Holder metrics
        holder_count = token_data.get('holder_count', 0)
        min_holders = filters_config['holder_metrics']['min_unique_holders']
        
        if holder_count < min_holders:
            violations.append(f"Holder count too low: {holder_count}")
        
        passes = len(violations) == 0
        
        return passes, violations
    
    async def _calculate_composite_score(self, win_rate: float, pnl_30d: float,
                                        tx_metrics: int, token_data: Dict) -> float:
        """Calculate composite score (0-100)"""
        weights = self.config['scoring']['weights']
        
        # Normalize win rate (0-100 scale)
        win_rate_score = min(win_rate, 100)
        
        # Normalize PnL (cap at 1000% for scoring)
        pnl_score = min(pnl_30d, 1000) / 10
        
        # Transaction count score (inverse - fewer transactions is better)
        max_tx = self.config['performance_filters']['transaction_7d']['maximum']
        tx_score = 100 * (1 - min(tx_metrics / max_tx, 1))
        
        # Calculate weighted composite score
        composite = (
            win_rate_score * weights['win_rate'] +
            pnl_score * weights['pnl_30d'] +
            tx_score * weights['transaction_count']
        )
        
        return min(composite, 100)
    
    async def close(self):
        """Close session"""
        await self.session.close()
