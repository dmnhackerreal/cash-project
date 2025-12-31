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
            stochastic_k, stochastic_d = indicators.get('stochastic', (50, 50))
            if stochastic_k < self.config.TECHNICAL.STOCH_OVERSOLD:
                score += 10
                reasons.append(f"Stochastic oversold ({stochastic_k:.1f})")
            elif stochastic_k > self.config.TECHNICAL.STOCH_OVERBOUGHT:
                score -= 10
                reasons.append(f"Stochastic overbought ({stochastic_k:.1f})")
            
            # Williams %R
            williams_r = indicators.get('williams_r', -50)
            if williams_r < -80:
                score += 8
                reasons.append(f"Williams %R oversold ({williams_r:.1f})")
            elif williams_r > -20:
                score -= 8
                reasons.append(f"Williams %R overbought ({williams_r:.1f})")
            
        except Exception as e:
            logger.warning(f"Error analyzing momentum: {e}")
        
        return score, reasons
    
    def _analyze_volatility(self, indicators: Dict[str, Any]) -> Tuple[float, List[str]]:
        """Analyze volatility indicators"""
        score = 0
        reasons = []
        
        try:
            # Bollinger Bands Position
            bb = indicators.get('bollinger_bands', {})
            if bb:
                current_price = indicators.get('current_price', 0)
                bb_lower = bb.get('lower', 0)
                bb_upper = bb.get('upper', 0)
                bb_middle = bb.get('middle', 0)
                
                if current_price and bb_lower and bb_upper:
                    # Calculate position within bands
                    bb_position = (current_price - bb_lower) / (bb_upper - bb_lower) if bb_upper != bb_lower else 0.5
                    
                    if bb_position < 0.2:
                        score += 12
                        reasons.append("Price near lower Bollinger Band")
                    elif bb_position > 0.8:
                        score -= 12
                        reasons.append("Price near upper Bollinger Band")
                    elif 0.4 < bb_position < 0.6:
                        score += 5
                        reasons.append("Price in middle of Bollinger Bands")
            
            # ATR Analysis
            atr_percent = indicators.get('atr_percent', 0)
            if atr_percent > 3:
                score -= 5
                reasons.append(f"High volatility ({atr_percent:.1f}% ATR)")
            elif atr_percent < 1:
                score += 3
                reasons.append(f"Low volatility ({atr_percent:.1f}% ATR)")
            
            # Bollinger Bandwidth
            bb_bandwidth = bb.get('bandwidth', 0) if bb else 0
            if bb_bandwidth > 10:
                score -= 3
                reasons.append(f"Wide Bollinger Bands ({bb_bandwidth:.1f}%)")
            elif bb_bandwidth < 5:
                score += 2
                reasons.append(f"Narrow Bollinger Bands ({bb_bandwidth:.1f}%)")
            
        except Exception as e:
            logger.warning(f"Error analyzing volatility: {e}")
        
        return score, reasons
    
    def _analyze_volume(self, indicators: Dict[str, Any], df: pd.DataFrame) -> Tuple[float, List[str]]:
        """Analyze volume indicators"""
        score = 0
        reasons = []
        
        try:
            # Volume Ratio
            volume_ratio = indicators.get('volume_ratio', 0)
            if volume_ratio > 1.5:
                score += 8
                reasons.append(f"High volume ({(volume_ratio-1)*100:.0f}% above average)")
            elif volume_ratio < 0.5:
                score -= 3
                reasons.append(f"Low volume ({(1-volume_ratio)*100:.0f}% below average)")
            
            # OBV Trend
            obv = indicators.get('obv', 0)
            if len(df) > 10:
                # Check if OBV is making higher highs
                recent_obv = obv  # This would need actual OBV values from dataframe
                # Simplified version
                if volume_ratio > 1.2 and df['Close'].iloc[-1] > df['Close'].iloc[-2]:
                    score += 5
                    reasons.append("Volume confirming price movement")
            
            # Money Flow Index
            mfi = indicators.get('mfi', 50)
            if mfi > 80:
                score -= 8
                reasons.append(f"MFI overbought ({mfi:.1f})")
            elif mfi < 20:
                score += 8
                reasons.append(f"MFI oversold ({mfi:.1f})")
            
        except Exception as e:
            logger.warning(f"Error analyzing volume: {e}")
        
        return score, reasons
    
    def _analyze_price_action(self, indicators: Dict[str, Any], 
                             df: pd.DataFrame) -> Tuple[float, List[str]]:
        """Analyze price action and patterns"""
        score = 0
        reasons = []
        
        try:
            if len(df) < 5:
                return score, reasons
            
            # Recent price movement
            current_price = df['Close'].iloc[-1]
            prev_close = df['Close'].iloc[-2]
            
            price_change = ((current_price - prev_close) / prev_close) * 100
            
            # Analyze candlestick patterns
            patterns = indicators.get('patterns', [])
            for pattern in patterns[:3]:  # Check top 3 patterns
                pattern_name = pattern.get('name', '')
                pattern_type = pattern.get('type', '')
                reliability = pattern.get('reliability', 0.5)
                
                if pattern_type == 'bullish':
                    score += reliability * 10
                    reasons.append(f"Bullish pattern: {pattern_name}")
                elif pattern_type == 'bearish':
                    score -= reliability * 10
                    reasons.append(f"Bearish pattern: {pattern_name}")
                elif pattern_type == 'reversal':
                    if price_change > 0:  # If price went up, bearish reversal
                        score -= reliability * 8
                        reasons.append(f"Bearish reversal pattern: {pattern_name}")
                    else:  # If price went down, bullish reversal
                        score += reliability * 8
                        reasons.append(f"Bullish reversal pattern: {pattern_name}")
            
            # Support and Resistance
            recent_high = indicators.get('recent_high', 0)
            recent_low = indicators.get('recent_low', 0)
            
            if current_price > recent_high * 0.95:
                score -= 5
                reasons.append("Price near recent resistance")
            elif current_price < recent_low * 1.05:
                score += 5
                reasons.append("Price near recent support")
            
            # Price relative to moving averages
            ma_20 = indicators.get('moving_averages', {}).get('sma_20', 0)
            ma_50 = indicators.get('moving_averages', {}).get('sma_50', 0)
            
            if ma_20 and ma_50:
                if current_price > ma_20 > ma_50:
                    score += 8
                    reasons.append("Price above key moving averages")
                elif current_price < ma_20 < ma_50:
                    score -= 8
                    reasons.append("Price below key moving averages")
            
        except Exception as e:
            logger.warning(f"Error analyzing price action: {e}")
        
        return score, reasons
    
    def _determine_action(self, score: float) -> Tuple[str, float]:
        """
        Determine trading action based on score
        
        Parameters:
            score (float): Signal score
        
        Returns:
            Tuple[str, float]: Action and confidence
        """
        # Normalize score to -100 to 100 range
        normalized_score = max(-100, min(100, score))
        
        # Determine action
        if normalized_score >= self.config.BUY_THRESHOLD:
            action = "BUY"
            confidence = min(self.config.MAX_CONFIDENCE, 
                           self.config.MIN_CONFIDENCE + 
                           (normalized_score - self.config.BUY_THRESHOLD) / 
                           (100 - self.config.BUY_THRESHOLD) * 
                           (self.config.MAX_CONFIDENCE - self.config.MIN_CONFIDENCE))
        
        elif normalized_score <= self.config.SELL_THRESHOLD:
            action = "SELL"
            confidence = min(self.config.MAX_CONFIDENCE,
                           self.config.MIN_CONFIDENCE + 
                           (abs(normalized_score) - abs(self.config.SELL_THRESHOLD)) / 
                           (100 - abs(self.config.SELL_THRESHOLD)) * 
                           (self.config.MAX_CONFIDENCE - self.config.MIN_CONFIDENCE))
        
        else:
            action = "HOLD"
            confidence = self.config.MIN_CONFIDENCE
        
        return action, confidence
    
    def _calculate_risk_levels(self, current_price: float, 
                              indicators: Dict[str, Any], 
                              action: str) -> Dict[str, Any]:
        """
        Calculate risk management levels
        
        Parameters:
            current_price (float): Current price
            indicators (Dict[str, Any]): Technical indicators
            action (str): Trading action
        
        Returns:
            Dict[str, Any]: Risk management levels
        """
        risk_levels = {
            'stop_loss': 0,
            'take_profit': [],
            'risk_reward': 0,
            'position_size': 0
        }
        
        try:
            atr = indicators.get('atr', 0)
            
            if action == "BUY":
                # For BUY signals
                stop_loss = current_price - (atr * self.config.STOP_LOSS_ATR_MULTIPLIER)
                
                take_profit = []
                for multiplier in self.config.TAKE_PROFIT_ATR_MULTIPLIERS:
                    tp = current_price + (atr * multiplier)
                    take_profit.append(tp)
                
                risk = current_price - stop_loss
                reward = take_profit[0] - current_price
                
                risk_reward = reward / risk if risk > 0 else 1
            
            elif action == "SELL":
                # For SELL signals (short)
                stop_loss = current_price + (atr * self.config.STOP_LOSS_ATR_MULTIPLIER)
                
                take_profit = []
                for multiplier in self.config.TAKE_PROFIT_ATR_MULTIPLIERS:
                    tp = current_price - (atr * multiplier)
                    take_profit.append(tp)
                
                risk = stop_loss - current_price
                reward = current_price - take_profit[0]
                
                risk_reward = reward / risk if risk > 0 else 1
            
            else:
                # For HOLD signals
                stop_loss = current_price * 0.95  # 5% stop loss
                take_profit = [current_price * 1.05, current_price * 1.10, current_price * 1.15]
                risk_reward = 1
            
            # Calculate position size (simplified)
            # In real trading, this would consider account size, risk per trade, etc.
            position_size = self._calculate_position_size(current_price, stop_loss)
            
            risk_levels.update({
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'risk_reward': risk_reward,
                'position_size': position_size
            })
            
        except Exception as e:
            logger.warning(f"Error calculating risk levels: {e}")
        
        return risk_levels
    
    def _calculate_position_size(self, entry_price: float, stop_loss: float) -> float:
        """
        Calculate position size based on risk
        
        Parameters:
            entry_price (float): Entry price
            stop_loss (float): Stop loss price
        
        Returns:
            float: Position size
        """
        # Simplified position sizing
        # In real trading: Position Size = (Account Risk %) / (Entry - Stop Loss)
        
        risk_per_trade = self.config.RISK_PER_TRADE  # 2% risk per trade
        account_size = 10000  # Example account size
        
        risk_amount = account_size * risk_per_trade
        risk_per_share = abs(entry_price - stop_loss)
        
        if risk_per_share > 0:
            position_size = risk_amount / risk_per_share
        else:
            position_size = account_size / entry_price * 0.1  # 10% of account
        
        return position_size
    
    def _get_default_signal(self, symbol: str, df: pd.DataFrame) -> Dict[str, Any]:
        """Get default signal when analysis fails"""
        current_price = df['Close'].iloc[-1] if df is not None and not df.empty else 0
        
        return {
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'action': 'HOLD',
            'confidence': 0.3,
            'score': 0,
            'current_price': current_price,
            'reasons': ['Insufficient data for analysis'],
            'entry_price': current_price,
            'stop_loss': current_price * 0.95,
            'take_profit': [current_price * 1.05, current_price * 1.10, current_price * 1.15],
            'risk_reward': 1,
            'position_size': 0
        }
    
    def generate_multi_timeframe_signal(self, symbol: str, 
                                       timeframe_data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """
        Generate signal using multiple timeframes
        
        Parameters:
            symbol (str): Trading symbol
            timeframe_data (Dict[str, pd.DataFrame]): Data for different timeframes
        
        Returns:
            Dict[str, Any]: Multi-timeframe signal
        """
        signals = {}
        
        for timeframe, df in timeframe_data.items():
            if df is not None and not df.empty:
                # In a real implementation, you would calculate indicators for each timeframe
                signal = self.generate_signal(symbol, df, {})
                signals[timeframe] = signal
        
        # Combine signals from different timeframes
        combined_signal = self._combine_multi_timeframe_signals(signals)
        
        return combined_signal
    
    def _combine_multi_timeframe_signals(self, signals: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Combine signals from multiple timeframes"""
        if not signals:
            return self._get_default_signal('', None)
        
        # Count actions
        action_counts = {'BUY': 0, 'SELL': 0, 'HOLD': 0}
        total_confidence = 0
        
        for timeframe, signal in signals.items():
            action = signal.get('action', 'HOLD')
            confidence = signal.get('confidence', 0)
            
            if action in action_counts:
                action_counts[action] += 1
                total_confidence += confidence
        
        # Determine combined action
        if action_counts['BUY'] > action_counts['SELL'] and action_counts['BUY'] > action_counts['HOLD']:
            combined_action = 'BUY'
        elif action_counts['SELL'] > action_counts['BUY'] and action_counts['SELL'] > action_counts['HOLD']:
            combined_action = 'SELL'
        else:
            combined_action = 'HOLD'
        
        # Calculate average confidence
        avg_confidence = total_confidence / len(signals) if signals else 0.3
        
        # Create combined signal (using first signal's data as base)
        base_signal = next(iter(signals.values()))
        
        combined_signal = {
            'symbol': base_signal.get('symbol', ''),
            'timestamp': datetime.now().isoformat(),
            'action': combined_action,
            'confidence': avg_confidence,
            'score': base_signal.get('score', 0),
            'current_price': base_signal.get('current_price', 0),
            'reasons': [f"Multi-timeframe analysis: {combined_action} based on {len(signals)} timeframes"],
            'entry_price': base_signal.get('entry_price', 0),
            'stop_loss': base_signal.get('stop_loss', 0),
            'take_profit': base_signal.get('take_profit', []),
            'risk_reward': base_signal.get('risk_reward', 1),
            'position_size': base_signal.get('position_size', 0),
            'timeframe_signals': signals
        }
        
        return combined_signal

def test_ai_signal():
    """Test AI signal generator"""
    import yfinance as yf
    from modules.technical_analyzer import TechnicalAnalyzer
    
    print("Testing AI Signal Generator...")
    
    # Get sample data
    ticker = yf.Ticker('AAPL')
    df = ticker.history(period='1mo', interval='1d')
    
    if not df.empty:
        # Calculate indicators
        analyzer = TechnicalAnalyzer()
        indicators = analyzer.calculate_indicators(df)
        
        # Generate signal
        ai = AISignalGenerator()
        signal = ai.generate_signal('AAPL', df, indicators)
        
        print(f"\nSignal for AAPL:")
        print(f"  Action: {signal.get('action')}")
        print(f"  Confidence: {signal.get('confidence'):.1%}")
        print(f"  Score: {signal.get('score'):.1f}")
        print(f"  Current Price: ${signal.get('current_price', 0):.2f}")
        print(f"  Stop Loss: ${signal.get('stop_loss', 0):.2f}")
        print(f"  Take Profit: {[f'${tp:.2f}' for tp in signal.get('take_profit', [])]}")
        print(f"  Risk/Reward: 1:{signal.get('risk_reward', 0):.1f}")
        
        print(f"\nReasons:")
        for reason in signal.get('reasons', []):
            print(f"  • {reason}")

if __name__ == "__main__":
    test_ai_signal()
