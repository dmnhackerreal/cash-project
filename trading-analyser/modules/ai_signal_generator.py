# -*- coding: utf-8 -*-
"""
AI Signal Generator Module
Generate trading signals using AI and machine learning
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
import random

from config import Config
from utils.logger import setup_logger
from utils.helpers import calculate_percentage_change

logger = setup_logger(__name__)

class AISignalGenerator:
    """Generate trading signals using AI techniques"""
    
    def __init__(self):
        """Initialize AI signal generator"""
        self.config = Config.AI
        logger.info("AI Signal Generator initialized")
    
    def generate_signal(self, symbol: str, df: pd.DataFrame, 
                       indicators: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate trading signal using AI
        
        Parameters:
            symbol (str): Trading symbol
            df (pd.DataFrame): Price data
            indicators (Dict[str, Any]): Technical indicators
        
        Returns:
            Dict[str, Any]: Trading signal with recommendations
        """
        try:
            if df is None or df.empty or not indicators:
                logger.warning("Insufficient data for signal generation")
                return self._get_default_signal(symbol, df)
            
            current_price = df['Close'].iloc[-1]
            
            # Calculate signal score
            score, reasons = self._calculate_signal_score(indicators, df)
            
            # Determine action based on score
            action, confidence = self._determine_action(score)
            
            # Calculate risk management levels
            risk_levels = self._calculate_risk_levels(current_price, indicators, action)
            
            # Generate signal
            signal = {
                'symbol': symbol,
                'timestamp': datetime.now().isoformat(),
                'action': action,
                'confidence': confidence,
                'score': score,
                'current_price': current_price,
                'reasons': reasons,
                'entry_price': current_price,
                'stop_loss': risk_levels['stop_loss'],
                'take_profit': risk_levels['take_profit'],
                'risk_reward': risk_levels['risk_reward'],
                'position_size': risk_levels['position_size']
            }
            
            logger.info(f"Generated {action} signal for {symbol} with confidence {confidence:.1%}")
            return signal
            
        except Exception as e:
            logger.error(f"Error generating signal for {symbol}: {e}")
            return self._get_default_signal(symbol, df)
    
    def _calculate_signal_score(self, indicators: Dict[str, Any], 
                               df: pd.DataFrame) -> Tuple[float, List[str]]:
        """
        Calculate overall signal score
        
        Parameters:
            indicators (Dict[str, Any]): Technical indicators
            df (pd.DataFrame): Price data
        
        Returns:
            Tuple[float, List[str]]: Score and reasons
        """
        score = 0
        reasons = []
        
        # 1. Trend Analysis (25%)
        trend_score, trend_reasons = self._analyze_trend(indicators)
        score += trend_score * 0.25
        reasons.extend(trend_reasons)
        
        # 2. Momentum Analysis (25%)
        momentum_score, momentum_reasons = self._analyze_momentum(indicators)
        score += momentum_score * 0.25
        reasons.extend(momentum_reasons)
        
        # 3. Volatility Analysis (15%)
        volatility_score, volatility_reasons = self._analyze_volatility(indicators)
        score += volatility_score * 0.15
        reasons.extend(volatility_reasons)
        
        # 4. Volume Analysis (15%)
        volume_score, volume_reasons = self._analyze_volume(indicators, df)
        score += volume_score * 0.15
        reasons.extend(volume_reasons)
        
        # 5. Price Action Analysis (20%)
        price_action_score, price_action_reasons = self._analyze_price_action(indicators, df)
        score += price_action_score * 0.20
        reasons.extend(price_action_reasons)
        
        return score, reasons
    
    def _analyze_trend(self, indicators: Dict[str, Any]) -> Tuple[float, List[str]]:
        """Analyze trend strength and direction"""
        score = 0
        reasons = []
        
        try:
            # ADX Trend Strength
            adx = indicators.get('adx', 0)
            if adx > 40:
                score += 20
                reasons.append("Very strong trend (ADX > 40)")
            elif adx > 25:
                score += 15
                reasons.append("Strong trend (ADX > 25)")
            elif adx > 20:
                score += 5
                reasons.append("Weak trend (ADX > 20)")
            else:
                score -= 5
                reasons.append("No clear trend (ADX < 20)")
            
            # Trend Direction
            trend = indicators.get('trend', 'RANGING')
            if trend == 'UPTREND':
                score += 10
                reasons.append("Uptrend confirmed")
            elif trend == 'DOWNTREND':
                score -= 10
                reasons.append("Downtrend confirmed")
            
            # Moving Average Alignment
            ma_alignment = indicators.get('ma_alignment', 'NEUTRAL')
            if ma_alignment == 'STRONG_BULLISH':
                score += 15
                reasons.append("Strong bullish MA alignment")
            elif ma_alignment == 'BULLISH':
                score += 10
                reasons.append("Bullish MA alignment")
            elif ma_alignment == 'STRONG_BEARISH':
                score -= 15
                reasons.append("Strong bearish MA alignment")
            elif ma_alignment == 'BEARISH':
                score -= 10
                reasons.append("Bearish MA alignment")
            
        except Exception as e:
            logger.warning(f"Error analyzing trend: {e}")
        
        return score, reasons
    
    def _analyze_momentum(self, indicators: Dict[str, Any]) -> Tuple[float, List[str]]:
        """Analyze momentum indicators"""
        score = 0
        reasons = []
        
        try:
            # RSI Analysis
            rsi = indicators.get('rsi', 50)
            if rsi < self.config.TECHNICAL.RSI_OVERSOLD:
                score += 15
                reasons.append(f"RSI oversold ({rsi:.1f})")
            elif rsi > self.config.TECHNICAL.RSI_OVERBOUGHT:
                score -= 15
                reasons.append(f"RSI overbought ({rsi:.1f})")
            elif 40 < rsi < 60:
                score += 5
                reasons.append(f"RSI neutral ({rsi:.1f})")
            
            # MACD Analysis
            macd_line, macd_signal, macd_hist = indicators.get('macd', (0, 0, 0))
            if macd_hist > 0 and macd_line > macd_signal:
                score += 10
                reasons.append("MACD bullish crossover")
            elif macd_hist < 0 and macd_line < macd_signal:
                score -= 10
                reasons.append("MACD bearish crossover")
            
            # Stochastic Analysis
            stochastic_k,
