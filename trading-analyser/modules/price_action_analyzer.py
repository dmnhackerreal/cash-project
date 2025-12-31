# -*- coding: utf-8 -*-
"""
Price Action Analysis Module
Analyze price action using ICT, SMC, and traditional methods
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
import warnings

from config import Config
from utils.logger import setup_logger

logger = setup_logger(__name__)

class PriceActionAnalyzer:
    """Analyze price action using various methodologies"""
    
    def __init__(self):
        """Initialize price action analyzer"""
        warnings.filterwarnings('ignore')
        logger.info("Price Action Analyzer initialized")
    
    def analyze_ict_concepts(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze ICT (Inner Circle Trader) concepts
        
        Parameters:
            df (pd.DataFrame): OHLCV data
        
        Returns:
            Dict[str, Any]: ICT analysis results
        """
        analysis = {
            'market_structure': '',
            'fair_value_gaps': [],
            'order_blocks': [],
            'liquidity_pools': {},
            'breaker_blocks': [],
            'mitigation_blocks': [],
            'displacement': False,
            'liquidity_grab': False
        }
        
        try:
            if len(df) < 20:
                logger.warning("Insufficient data for ICT analysis")
                return analysis
            
            # Market Structure Analysis
            analysis['market_structure'] = self._analyze_market_structure(df)
            
            # Fair Value Gaps (FVG)
            analysis['fair_value_gaps'] = self._find_fair_value_gaps(df)
            
            # Order Blocks
            analysis['order_blocks'] = self._find_order_blocks(df)
            
            # Liquidity Pools
            analysis['liquidity_pools'] = self._find_liquidity_pools(df)
            
            # Breaker Blocks
            analysis['breaker_blocks'] = self._find_breaker_blocks(df)
            
            # Mitigation Blocks
            analysis['mitigation_blocks'] = self._find_mitigation_blocks(df)
            
            # Displacement
            analysis['displacement'] = self._check_displacement(df)
            
            # Liquidity Grab
            analysis['liquidity_grab'] = self._check_liquidity_grab(df)
            
            logger.info(f"ICT analysis completed: {analysis['market_structure']}")
            
        except Exception as e:
            logger.error(f"Error in ICT analysis: {e}", exc_info=True)
        
        return analysis
    
    def analyze_smc_concepts(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze SMC (Smart Money Concepts)
        
        Parameters:
            df (pd.DataFrame): OHLCV data
        
        Returns:
            Dict[str, Any]: SMC analysis results
        """
        analysis = {
            'market_structure': '',
            'supply_demand_zones': [],
            'bos_choch': [],
            'equal_highs_lows': [],
            'mitigation_blocks': [],
            'liquidity_zones': []
        }
        
        try:
            if len(df) < 20:
                logger.warning("Insufficient data for SMC analysis")
                return analysis
            
            # Market Structure
            analysis['market_structure'] = self._analyze_smc_market_structure(df)
            
            # Supply and Demand Zones
            analysis['supply_demand_zones'] = self._find_supply_demand_zones(df)
            
            # BOS (Break of Structure) and CHoCH (Change of Character)
            analysis['bos_choch'] = self._find_bos_choch(df)
            
            # Equal Highs and Lows
            analysis['equal_highs_lows'] = self._find_equal_highs_lows(df)
            
            # Mitigation Blocks (for SMC)
            analysis['mitigation_blocks'] = self._find_smc_mitigation_blocks(df)
            
            # Liquidity Zones
            analysis['liquidity_zones'] = self._find_liquidity_zones(df)
            
            logger.info(f"SMC analysis completed: {analysis['market_structure']}")
            
        except Exception as e:
            logger.error(f"Error in SMC analysis: {e}", exc_info=True)
        
        return analysis
    
    def analyze_traditional_pa(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze traditional price action
        
        Parameters:
            df (pd.DataFrame): OHLCV data
        
        Returns:
            Dict[str, Any]: Traditional PA analysis
        """
        analysis = {
            'support_resistance': {},
            'trend_lines': [],
            'chart_patterns': [],
            'candlestick_clusters': [],
            'volume_profile': {},
            'market_condition': ''
        }
        
        try:
            if len(df) < 20:
                logger.warning("Insufficient data for traditional PA analysis")
                return analysis
            
            # Support and Resistance
            analysis['support_resistance'] = self._find_support_resistance(df)
            
            # Trend Lines
            analysis['trend_lines'] = self._draw_trend_lines(df)
            
            # Chart Patterns
            analysis['chart_patterns'] = self._identify_chart_patterns(df)
            
            # Candlestick Clusters
            analysis['candlestick_clusters'] = self._analyze_candlestick_clusters(df)
            
            # Volume Profile
            analysis['volume_profile'] = self._calculate_volume_profile(df)
            
            # Market Condition
            analysis['market_condition'] = self._determine_market_condition(df)
            
            logger.info(f"Traditional PA analysis completed: {analysis['market_condition']}")
            
        except Exception as e:
            logger.error(f"Error in traditional PA analysis: {e}", exc_info=True)
        
        return analysis
    
    def _analyze_market_structure(self, df: pd.DataFrame) -> str:
        """Analyze market structure (ICT)"""
        if len(df) < 30:
            return "INSUFFICIENT_DATA"
        
        # Get recent highs and lows
        recent_data = df.tail(30)
        
        # Find swing highs and lows
        swing_highs = self._find_swing_highs(recent_data, window=5)
        swing_lows = self._find_swing_lows(recent_data, window=5)
        
        if len(swing_highs) < 2 or len(swing_lows) < 2:
            return "CONSOLIDATION"
        
        # Check for higher highs and higher lows (Uptrend)
        if (swing_highs[-1] > swing_highs[-2] and 
            swing_lows[-1] > swing_lows[-2]):
            return "UPTREND"
        
        # Check for lower highs and lower lows (Downtrend)
        elif (swing_highs[-1] < swing_highs[-2] and 
              swing_lows[-1] < swing_lows[-2]):
            return "DOWNTREND"
        
        # Check for equal highs/lows (Range)
        elif (abs(swing_highs[-1] - swing_highs[-2]) / swing_highs[-2] < 0.01 and
              abs(swing_lows[-1] - swing_lows[-2]) / swing_lows[-2] < 0.01):
            return "RANGE"
        
        else:
            return "CONSOLIDATION"
    
    def _find_fair_value_gaps(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Find Fair Value Gaps (FVG)"""
        fvgs = []
        
        try:
            # Need at least 3 candles for FVG detection
            for i in range(2, len(df)):
                # Bullish FVG: Low of current candle > High of candle-2
                if (df['Low'].iloc[i] > df['High'].iloc[i-2] and
                    df['High'].iloc[i-1] < df['Low'].iloc[i]):  # Candle-1 doesn't fill the gap
                    
                    fvg = {
                        'type': 'BULLISH_FVG',
                        'start_time': df.index[i-2],
                        'end_time': df.index[i],
                        'price_range': (df['High'].iloc[i-2], df['Low'].iloc[i]),
                        'gap_size': df['Low'].iloc[i] - df['High'].iloc[i-2],
                        'filled': False
                    }
                    
                    # Check if FVG has been filled
                    for j in range(i+1, min(i+20, len(df))):
                        if df['Low'].iloc[j] <= fvg['price_range'][0]:
                            fvg['filled'] = True
                            fvg['filled_time'] = df.index[j]
                            break
                    
                    fvgs.append(fvg)
                
                # Bearish FVG: High of current candle < Low of candle-2
                elif (df['High'].iloc[i] < df['Low'].iloc[i-2] and
                      df['Low'].iloc[i-1] > df['High'].iloc[i]):  # Candle-1 doesn't fill the gap
                    
                    fvg = {
                        'type': 'BEARISH_FVG',
                        'start_time': df.index[i-2],
                        'end_time': df.index[i],
                        'price_range': (df['Low'].iloc[i-2], df['High'].iloc[i]),
                        'gap_size': df['Low'].iloc[i-2] - df['High'].iloc[i],
                        'filled': False
                    }
                    
                    # Check if FVG has been filled
                    for j in range(i+1, min(i+20, len(df))):
                        if df['High'].iloc[j] >= fvg['price_range'][1]:
                            fvg['filled'] = True
                            fvg['filled_time'] = df.index[j]
                            break
                    
                    fvgs.append(fvg)
        
        except Exception as e:
            logger.warning(f"Error finding FVGs: {e}")
        
        # Return recent FVGs (last 10)
        return fvgs[-10:] if fvgs else []
    
    def _find_order_blocks(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Find Order Blocks"""
        order_blocks = []
        
        try:
            for i in range(1, len(df)-1):
                current_candle = df.iloc[i]
                next_candle = df.iloc[i+1]
                
                # Bearish Order Block: Strong bearish candle followed by bullish candle
                if (current_candle['Close'] < current_candle['Open'] and  # Bearish candle
                    abs(current_candle['Close'] - current_candle['Open']) > 
                    (current_candle['High'] - current_candle['Low']) * 0.7 and  # Strong candle
                    next_candle['Close'] > next_candle['Open']):  # Followed by bullish
                    
                    ob = {
                        'type': 'BEARISH_OB',
                        'time': df.index[i],
                        'price_range': (current_candle['Low'], current_candle['High']),
                        'strength': abs(current_candle['Close'] - current_candle['Open']) / 
                                   (current_candle['High'] - current_candle['Low']),
                        'tested': False
                    }
                    
                    # Check if OB has been tested
                    for j in range(i+2, min(i+50, len(df))):
                        if df['High'].iloc[j] >= ob['price_range'][0]:
                            ob['tested'] = True
                            ob['test_time'] = df.index[j]
                            break
                    
                    order_blocks.append(ob)
                
                # Bullish Order Block: Strong bullish candle followed by bearish candle
                elif (current_candle['Close'] > current_candle['Open'] and  # Bullish candle
                      abs(current_candle['Close'] - current_candle['Open']) > 
                      (current_candle['High'] - current_candle['Low']) * 0.7 and  # Strong candle
                      next_candle['Close'] < next_candle['Open']):  # Followed by bearish
                    
                    ob = {
                        'type': 'BULLISH_OB',
                        'time': df.index[i],
                        'price_range': (current_candle['Low'], current_candle['High']),
                        'strength': abs(current_candle['Close'] - current_candle['Open']) / 
                                   (current_candle['High'] - current_candle['Low']),
                        'tested': False
                    }
                    
                    # Check if OB has been tested
                    for j in range(i+2, min(i+50, len(df))):
                        if df['Low'].iloc[j] <= ob['price_range'][1]:
                            ob['tested'] = True
                            ob['test_time'] = df.index[j]
                            break
                    
                    order_blocks.append(ob)
        
        except Exception as e:
            logger.warning(f"Error finding order blocks: {e}")
        
        # Return recent order blocks (last 10)
        return order_blocks[-10:] if order_blocks else []
    
    def _find_liquidity_pools(self, df: pd.DataFrame) -> Dict[str, float]:
        """Find Liquidity Pools"""
        pools = {}
        
        try:
            if len(df) < 50:
                return pools
            
            recent_data = df.tail(100)
            
            # Previous High Liquidity
            pools['previous_high'] = recent_data['High'].max()
            
            # Previous Low Liquidity
            pools['previous_low'] = recent_data['Low'].min()
            
            # Recent High (Stop Hunts above)
            pools['recent_high'] = recent_data['High'].tail(20).max()
            
            # Recent Low (Stop Hunts below)
            pools['recent_low'] = recent_data['Low'].tail(20).min()
            
            # Equal Highs/Lows (Liquidity pools)
            high_counts = {}
            low_counts = {}
            
            # Find price levels with multiple touches
            for i in range(len(recent_data)):
                high = round(recent_data['High'].iloc[i], 2)
                low = round(recent_data['Low'].iloc[i], 2)
                
                high_counts[high] = high_counts.get(high, 0) + 1
                low_counts[low] = low_counts.get(low, 0) + 1
            
            # Find levels with at least 3 touches
            for price, count in high_counts.items():
                if count >= 3:
                    pools[f'high_liquidity_{price}'] = price
            
            for price, count in low_counts.items():
                if count >= 3:
                    pools[f'low_liquidity_{price}'] = price
        
        except Exception as e:
            logger.warning(f"Error finding liquidity pools: {e}")
        
        return pools
    
    def _find_breaker_blocks(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Find Breaker Blocks"""
        breaker_blocks = []
        
        try:
            for i in range(2, len(df)):
                # Breaker block after a displacement
                if self._is_displacement_candle(df.iloc[i-1]):
                    bb = {
                        'type': 'BULLISH_BREAKER' if df['Close'].iloc[i-1] > df['Open'].iloc[i-1] else 'BEARISH_BREAKER',
                        'time': df.index[i],
                        'price': df['Close'].iloc[i],
                        'displacement_candle': df.index[i-1]
                    }
                    breaker_blocks.append(bb)
        
        except Exception as e:
            logger.warning(f"Error finding breaker blocks: {e}")
        
        return breaker_blocks
    
    def _find_mitigation_blocks(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Find Mitigation Blocks (ICT)"""
        mitigation_blocks = []
        
        try:
            for i in range(1, len(df)):
                # Mitigation block: candle that closes into a FVG or OB
                current_candle = df.iloc[i]
                
                # Check if this candle closes into a previously identified level
                # This is simplified - would need integration with FVG/OB detection
                
                # Simple heuristic: candle closing near a recent swing point
                if i > 10:
                    recent_high = df['High'].iloc[i-10:i].max()
                    recent_low = df['Low'].iloc[i-10:i].min()
                    
                    if abs(current_candle['Close'] - recent_high) / recent_high < 0.01:
                        mb = {
                            'type': 'HIGH_MITIGATION',
                            'time': df.index[i],
                            'price': current_candle['Close'],
                            'target': recent_high
                        }
                        mitigation_blocks.append(mb)
                    
                    elif abs(current_candle['Close'] - recent_low) / recent_low < 0.01:
                        mb = {
                            'type': 'LOW_MITIGATION',
                            'time': df.index[i],
                            'price': current_candle['Close'],
                            'target': recent_low
                        }
                        mitigation_blocks.append(mb)
        
        except Exception as e:
            logger.warning(f"Error finding mitigation blocks: {e}")
        
        return mitigation_blocks
    
    def _check_displacement(self, df: pd.DataFrame) -> bool:
        """Check for displacement (strong momentum candle)"""
        if len(df) < 2:
            return False
        
        last_candle = df.iloc[-1]
        
        # Displacement: strong candle with small wicks
        body_size = abs(last_candle['Close'] - last_candle['Open'])
        total_range = last_candle['High'] - last_candle['Low']
        
        if total_range > 0:
            body_ratio = body_size / total_range
            
            # Strong displacement candle: body > 70% of total range
            return body_ratio > 0.7
        
        return False
    
    def _check_liquidity_grab(self, df: pd.DataFrame) -> bool:
        """Check for liquidity grab (wick above/below recent range)"""
        if len(df) < 20:
            return False
        
        last_candle = df.iloc[-1]
        recent_data = df.tail(20)
        
        recent_high = recent_data['High'].max()
        recent_low = recent_data['Low'].min()
        
        # Liquidity grab: long wick beyond recent range that gets rejected
        upper_wick = last_candle['High'] - max(last_candle['Open'], last_candle['Close'])
        lower_wick = min(last_candle['Open'], last_candle['Close']) - last_candle['Low']
        
        # Check for upper liquidity grab
        if (last_candle['High'] > recent_high * 1.005 and  # 0.5% above recent high
            upper_wick > (last_candle['High'] - last_candle['Low']) * 0.3 and  # Significant wick
            last_candle['Close'] < recent_high):  # Closes below the high
            return True
        
        # Check for lower liquidity grab
        if (last_candle['Low'] < recent_low * 0.995 and  # 0.5% below recent low
            lower_wick > (last_candle['High'] - last_candle['Low']) * 0.3 and  # Significant wick
            last_candle['Close'] > recent_low):  # Closes above the low
            return True
        
        return False
    
    def _analyze_smc_market_structure(self, df: pd.DataFrame) -> str:
        """Analyze market structure (SMC)"""
        # Similar to ICT but with different terminology
        return self._analyze_market_structure(df)
    
    def _find_supply_demand_zones(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Find Supply and Demand Zones (SMC)"""
        zones = []
        
        try:
            # Look for consolidation zones followed by strong moves
            for i in range(10, len(df)-5):
                # Check for consolidation (small range candles)
                consolidation_range = df.iloc[i-5:i]
                range_sizes = consolidation_range['High'] - consolidation_range['Low']
                avg_range = range_sizes.mean()
                
                # Check for breakout candle
                breakout_candle = df.iloc[i]
                breakout_range = breakout_candle['High'] - breakout_candle['Low']
                
                if breakout_range > avg_range * 2:  # Strong breakout
                    # Determine zone type based on breakout direction
                    if breakout_candle['Close'] > breakout_candle['Open']:  # Bullish breakout
                        zone = {
                            'type': 'DEMAND_ZONE',
                            'time': df.index[i-5],
                            'price_range': (consolidation_range['Low'].min(), 
                                          consolidation_range['High'].max()),
                            'breakout_time': df.index[i],
                            'breakout_direction': 'BULLISH'
                        }
                    else:  # Bearish breakout
                        zone = {
                            'type': 'SUPPLY_ZONE',
                            'time': df.index[i-5],
                            'price_range': (consolidation_range['Low'].min(), 
                                          consolidation_range['High'].max()),
                            'breakout_time': df.index[i],
                            'breakout_direction': 'BEARISH'
                        }
                    
                    zones.append(zone)
        
        except Exception as e:
            logger.warning(f"Error finding supply/demand zones: {e}")
        
        return zones[-5:] if zones else []  # Return last 5 zones
    
    def _find_bos_choch(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Find BOS (Break of Structure) and CHoCH (Change of Character)"""
        bos_choch = []
        
        try:
            # Find swing points
            swing_highs = self._find_swing_highs(df, window=3)
            swing_lows = self._find_swing_lows(df, window=3)
            
            for i in range(1, len(swing_highs)):
                # BOS: Break of previous swing high/low
                if swing_highs[i] > swing_highs[i-1]:
                    bos_choch.append({
                        'type': 'BOS',
                        'time': df.index[df['High'] == swing_highs[i]].max(),
                        'price': swing_highs[i],
                        'direction': 'BULLISH'
                    })
                
                elif swing_lows[i] < swing_lows[i-1]:
                    bos_choch.append({
                        'type': 'BOS',
                        'time': df.index[df['Low'] == swing_lows[i]].max(),
                        'price': swing_lows[i],
                        'direction': 'BEARISH'
                    })
            
            # CHoCH: Change from higher highs to lower highs or vice versa
            if len(swing_highs) >= 3:
                if (swing_highs[-1] < swing_highs[-2] and 
                    swing_highs[-2] > swing_highs[-3]):
                    bos_choch.append({
                        'type': 'CHOCH',
                        'time': df.index[df['High'] == swing_highs[-1]].max(),
                        'price': swing_highs[-1],
                        'direction': 'BEARISH_REVERSAL'
                    })
                
                elif (swing_lows[-1] > swing_lows[-2] and 
                      swing_lows[-2] < swing_lows[-3]):
                    bos_choch.append({
                        'type': 'CHOCH',
                        'time': df.index[df['Low'] == swing_lows[-1]].max(),
                        'price': swing_lows[-1],
                        'direction': 'BULLISH_REVERSAL'
                    })
        
        except Exception as e:
            logger.warning(f"Error finding BOS/CHoCH: {e}")
        
        return bos_choch
    
    def _find_equal_highs_lows(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Find Equal Highs and Lows"""
        equal_levels = []
        
        try:
            # Find swing highs and lows
            swing_highs = self._find_swing_highs(df, window=3)
            swing_lows = self._find_swing_lows(df, window=3)
            
            # Group similar highs/lows
            tolerance = 0.005  # 0.5% tolerance
            
            # Equal highs
            for i in range(len(swing_highs)):
                for j in range(i+1, len(swing_highs)):
                    if abs(swing_highs[i] - swing_highs[j]) / swing_highs[i] < tolerance:
                        equal_levels.append({
                            'type': 'EQUAL_HIGHS',
                            'price': (swing_highs[i] + swing_highs[j]) / 2,
                            'first_time': df.index[df['High'] == swing_highs[i]].max(),
                            'second_time': df.index[df['High'] == swing_highs[j]].max()
                        })
            
            # Equal lows
            for i in range(len(swing_lows)):
                for j in range(i+1, len(swing_lows)):
                    if abs(swing_lows[i] - swing_lows[j]) / swing_lows[i] < tolerance:
                        equal_levels.append({
                            'type': 'EQUAL_LOWS',
                            'price': (swing_lows[i] + swing_lows[j]) / 2,
                            'first_time': df.index[df['Low'] == swing_lows[i]].max(),
                            'second_time': df.index[df['Low'] == swing_lows[j]].max()
                        })
        
        except Exception as e:
            logger.warning(f"Error finding equal highs/lows: {e}")
        
        return equal_levels
    
    def _find_smc_mitigation_blocks(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Find Mitigation Blocks (SMC)"""
        # Similar to ICT mitigation blocks
        return self._find_mitigation_blocks(df)
    
    def _find_liquidity_zones(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Find Liquidity Zones (SMC)"""
        # Similar to ICT liquidity pools
        pools = self._find_liquidity_pools(df)
        
        liquidity_zones = []
        for key, price in pools.items():
            if 'high' in key or 'low' in key:
                liquidity_zones.append({
                    'type': 'HIGH_LIQUIDITY' if 'high' in key else 'LOW_LIQUIDITY',
                    'price': price,
                    'description': key
                })
        
        return liquidity_zones
    
    def _find_support_resistance(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Find traditional support and resistance levels"""
        levels = {}
        
        try:
            if len(df) < 50:
                return levels
            
            recent_data = df.tail(100)
            
            # Pivot Points
            pivot = (recent_data['High'].max() + recent_data['Low'].min() + 
                    recent_data['Close'].iloc[-1]) / 3
            
            levels['pivot'] = pivot
            levels['r1'] = 2 * pivot - recent_data['Low'].min()
            levels['r2'] = pivot + (recent_data['High'].max() - recent_data['Low'].min())
            levels['s1'] = 2 * pivot - recent_data['High'].max()
            levels['s2'] = pivot - (recent_data['High'].max() - recent_data['Low'].min())
            
            # Recent highs and lows
            levels['recent_high'] = recent_data['High'].tail(20).max()
            levels['recent_low'] = recent_data['Low'].tail(20).min()
            
            # Psychological levels (round numbers)
            current_price = df['Close'].iloc[-1]
            nearest_round = round(current_price / 10) * 10
            levels['psychological'] = {
                'below': nearest_round - 10,
                'current': nearest_round,
                'above': nearest_round + 10
            }
        
        except Exception as e:
            logger.warning(f"Error finding support/resistance: {e}")
        
        return levels
    
    def _draw_trend_lines(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Draw trend lines"""
        trend_lines = []
        
        try:
            # Find swing points for trend lines
            swing_highs = self._find_swing_highs(df, window=5)
            swing_lows = self._find_swing_lows(df, window=5)
            
            # Draw uptrend lines (connect higher lows)
            if len(swing_lows) >= 2:
                for i in range(len(swing_lows)-1):
                    if swing_lows[i+1] > swing_lows[i]:
                        trend_lines.append({
                            'type': 'UPTREND_LINE',
                            'start_price': swing_lows[i],
                            'end_price': swing_lows[i+1],
                            'slope': (swing_lows[i+1] - swing_lows[i]) / (i+1 - i),
                            'valid': True
                        })
            
            # Draw downtrend lines (connect lower highs)
            if len(swing_highs) >= 2:
                for i in range(len(swing_highs)-1):
                    if swing_highs[i+1] < swing_highs[i]:
                        trend_lines.append({
                            'type': 'DOWNTREND_LINE',
                            'start_price': swing_highs[i],
                            'end_price': swing_highs[i+1],
                            'slope': (swing_highs[i+1] - swing_highs[i]) / (i+1 - i),
                            'valid': True
                        })
        
        except Exception as e:
            logger.warning(f"Error drawing trend lines: {e}")
        
        return trend_lines[-5:] if trend_lines else []  # Return last 5 trend lines
    
    def _identify_chart_patterns(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Identify traditional chart patterns"""
        patterns = []
        
        try:
            # Simplified pattern detection
            # In real implementation, use more sophisticated algorithms
            
            # Head and Shoulders
            patterns.extend(self._detect_head_shoulders(df))
            
            # Double Top/Bottom
            patterns.extend(self._detect_double_patterns(df))
            
            # Triangle Patterns
            patterns.extend(self._detect_triangle_patterns(df))
            
            # Flag/Pennant
            patterns.extend(self._detect_flag_patterns(df))
        
        except Exception as e:
            logger.warning(f"Error identifying chart patterns: {e}")
        
        return patterns
    
    def _analyze_candlestick_clusters(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Analyze candlestick clusters"""
        clusters = []
        
        try:
            # Look for areas with similar open/close prices
            for i in range(5, len(df), 5):
                cluster_data = df.iloc[i-5:i]
                
                # Check if candles are clustering
                price_range = cluster_data['High'].max() - cluster_data['Low'].min()
                avg_body = abs(cluster_data['Close'] - cluster_data['Open']).mean()
                
                if price_range < avg_body * 3:  # Tight clustering
                    clusters.append({
                        'time': df.index[i-5],
                        'price_range': (cluster_data['Low'].min(), cluster_data['High'].max()),
                        'type': 'CONSOLIDATION_CLUSTER',
                        'density': len(cluster_data) / price_range if price_range > 0 else 0
                    })
        
        except Exception as e:
            logger.warning(f"Error analyzing candlestick clusters: {e}")
        
        return clusters
    
    def _calculate_volume_profile(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate volume profile"""
        profile = {}
        
        try:
            if 'Volume' not in df.columns:
                return profile
            
            # Simplified volume profile
            recent_data = df.tail(50)
            
            # Price levels
            min_price = recent_data['Low'].min()
            max_price = recent_data['High'].max()
            price_range = max_price - min_price
            
            if price_range > 0:
                # Create bins
                num_bins = 20
                bin_size = price_range / num_bins
                
                volume_by_price = {}
                for i in range(num_bins):
                    price_level = min_price + (i * bin_size) + (bin_size / 2)
                    volume_by_price[price_level] = 0
                
                # Accumulate volume by price
                for idx, row in recent_data.iterrows():
                    price_bin = round((row['Close'] - min_price) / bin_size)
                    price_level = min_price + (price_bin * bin_size) + (bin_size / 2)
                    
                    if price_level in volume_by_price:
                        volume_by_price[price_level] += row['Volume']
                
                profile = volume_by_price
        
        except Exception as e:
            logger.warning(f"Error calculating volume profile: {e}")
        
        return profile
    
    def _determine_market_condition(self, df: pd.DataFrame) -> str:
        """Determine overall market condition"""
        # Use multiple indicators
        volatility = df['Close'].pct_change().std() * 100
        
        if volatility > 3:
            return "HIGH_VOLATILITY"
        elif volatility < 1:
            return "LOW_VOLATILITY"
        
        trend = self._analyze_market_structure(df)
        
        if trend == "UPTREND":
            return "TRENDING_UP"
        elif trend == "DOWNTREND":
            return "TRENDING_DOWN"
        else:
            return "RANGING"
    
    def _find_swing_highs(self, df: pd.DataFrame, window: int = 3) -> List[float]:
        """Find swing highs"""
        swing_highs = []
        
        for i in range(window, len(df) - window):
            if (df['High'].iloc[i] == df['High'].iloc[i-window:i+window+1].max() and
                df['High'].iloc[i] > df['High'].iloc[i-1] and
                df['High'].iloc[i] > df['High'].iloc[i+1]):
                swing_highs.append(df['High'].iloc[i])
        
        return swing_highs
    
    def _find_swing_lows(self, df: pd.DataFrame, window: int = 3) -> List[float]:
        """Find swing lows"""
        swing_lows = []
        
        for i in range(window, len(df) - window):
            if (df['Low'].iloc[i] == df['Low'].iloc[i-window:i+window+1].min() and
                df['Low'].iloc[i] < df['Low'].iloc[i-1] and
                df['Low'].iloc[i] < df['Low'].iloc[i+1]):
                swing_lows.append(df['Low'].iloc[i])
        
        return swing_lows
    
    def _is_displacement_candle(self, candle: pd.Series) -> bool:
        """Check if candle is a displacement candle"""
        body_size = abs(candle['Close'] - candle['Open'])
        total_range = candle['High'] - candle['Low']
        
        if total_range > 0:
            return body_size / total_range > 0.7
        
        return False
    
    def _detect_head_shoulders(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect Head and Shoulders patterns"""
        patterns = []
        
        try:
            swing_highs = self._find_swing_highs(df, window=3)
            
            if len(swing_highs) >= 5:
                # Look for H&S pattern: middle high (head) higher than two surrounding highs (shoulders)
                for i in range(2, len(swing_highs)-2):
                    if (swing_highs[i] > swing_highs[i-1] and
                        swing_highs[i] > swing_highs[i+1] and
                        abs(swing_highs[i-1] - swing_highs[i+1]) / swing_highs[i-1] < 0.05):  # Shoulders roughly equal
                        
                        patterns.append({
                            'type': 'HEAD_SHOULDERS',
                            'completion': i + 2 < len(swing_highs),
                            'neckline_break': False  # Would need to check price action
                        })
        
        except Exception as e:
            logger.warning(f"Error detecting head and shoulders: {e}")
        
        return patterns
    
    def _detect_double_patterns(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect Double Top/Bottom patterns"""
        patterns = []
        
        try:
            swing_highs = self._find_swing_highs(df, window=3)
            swing_lows = self._find_swing_lows(df, window=3)
            
            # Double Top
            if len(swing_highs) >= 2:
                for i in range(1, len(swing_highs)):
                    if abs(swing_highs[i] - swing_highs[i-1]) / swing_highs[i-1] < 0.02:  # Within 2%
                        patterns.append({
                            'type': 'DOUBLE_TOP',
                            'price': (swing_highs[i] + swing_highs[i-1]) / 2
                        })
            
            # Double Bottom
            if len(swing_lows) >= 2:
                for i in range(1, len(swing_lows)):
                    if abs(swing_lows[i] - swing_lows[i-1]) / swing_lows[i-1] < 0.02:  # Within 2%
                        patterns.append({
                            'type': 'DOUBLE_BOTTOM',
                            'price': (swing_lows[i] + swing_lows[i-1]) / 2
                        })
        
        except Exception as e:
            logger.warning(f"Error detecting double patterns: {e}")
        
        return patterns
    
    def _detect_triangle_patterns(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect Triangle patterns"""
        patterns = []
        
        try:
            # Simplified triangle detection
            # Look for converging highs and lows
            if len(df) >= 20:
                first_half = df.head(10)
                second_half = df.tail(10)
                
                high_range_first = first_half['High'].max() - first_half['High'].min()
                high_range_second = second_half['High'].max() - second_half['High'].min()
                low_range_first = first_half['Low'].max() - first_half['Low'].min()
                low_range_second = second_half['Low'].max() - second_half['Low'].min()
                
                # Check for convergence
                if (high_range_second < high_range_first * 0.7 and
                    low_range_second < low_range_first * 0.7):
                    
                    patterns.append({
                        'type': 'TRIANGLE',
                        'subtype': 'SYMMETRICAL',
                        'converging': True
                    })
        
        except Exception as e:
            logger.warning(f"Error detecting triangle patterns: {e}")
        
        return patterns
    
    def _detect_flag_patterns(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect Flag/Pennant patterns"""
        patterns = []
        
        # Simplified detection
        # Look for strong move followed by consolidation
        if len(df) >= 15:
            first_5 = df.head(5)
            middle_5 = df.iloc[5:10]
            last_5 = df.tail(5)
            
            # Check for flag (small consolidation after strong move)
            first_move = abs(first_5['Close'].iloc[-1] - first_5['Open'].iloc[0])
            consolidation_range = middle_5['High'].max() - middle_5['Low'].min()
            
            if first_move > consolidation_range * 3:
                patterns.append({
                    'type': 'FLAG',
                    'pole': first_move,
                    'flag': consolidation_range
                })
        
        return patterns

def test_price_action():
    """Test price action analyzer"""
    import yfinance as yf
    
    analyzer = PriceActionAnalyzer()
    
    print("Testing Price Action Analyzer...")
    
    # Get sample data
    ticker = yf.Ticker('AAPL')
    df = ticker.history(period='3mo', interval='1d')
    
    if not df.empty:
        # ICT Analysis
        ict_analysis = analyzer.analyze_ict_concepts(df)
        print(f"\nICT Analysis:")
        print(f"  Market Structure: {ict_analysis.get('market_structure', 'N/A')}")
        print(f"  FVGs Found: {len(ict_analysis.get('fair_value_gaps', []))}")
        print(f"  Order Blocks: {len(ict_analysis.get('order_blocks', []))}")
        
        # SMC Analysis
        smc_analysis = analyzer.analyze_smc_concepts(df)
        print(f"\nSMC Analysis:")
        print(f"  Market Structure: {smc_analysis.get('market_structure', 'N/A')}")
        print(f"  Supply/Demand Zones: {len(smc_analysis.get('supply_demand_zones', []))}")
        print(f"  BOS/CHoCH: {len(smc_analysis.get('bos_choch', []))}")
        
        # Traditional PA
        traditional_pa = analyzer.analyze_traditional_pa(df)
        print(f"\nTraditional PA:")
        print(f"  Market Condition: {traditional_pa.get('market_condition', 'N/A')}")
        print(f"  Support/Resistance Levels: {len(traditional_pa.get('support_resistance', {}))}")
        print(f"  Chart Patterns: {len(traditional_pa.get('chart_patterns', []))}")

if __name__ == "__main__":
    test_price_action()
