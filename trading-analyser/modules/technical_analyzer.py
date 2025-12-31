# -*- coding: utf-8 -*-
"""
Technical Analysis Module
Calculate technical indicators and analyze market data
"""

import pandas as pd
import numpy as np
import talib
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime

from config import Config
from utils.logger import setup_logger
from utils.helpers import cache_result

logger = setup_logger(__name__)

class TechnicalAnalyzer:
    """Technical analysis with various indicators"""
    
    def __init__(self):
        """Initialize technical analyzer"""
        self.config = Config.TECHNICAL
        logger.info("Technical Analyzer initialized")
    
    @cache_result(expiry_seconds=Config.CACHE.CACHE_EXPIRY['indicator_data'])
    def calculate_indicators(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate all technical indicators
        
        Parameters:
            df (pd.DataFrame): OHLCV data
        
        Returns:
            Dict[str, Any]: Dictionary of calculated indicators
        """
        try:
            if df is None or df.empty:
                logger.warning("Empty dataframe provided for indicator calculation")
                return {}
            
            # Ensure required columns exist
            required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
            for col in required_cols:
                if col not in df.columns:
                    logger.error(f"Missing required column: {col}")
                    return {}
            
            # Extract numpy arrays for TA-Lib
            open_prices = df['Open'].values.astype(float)
            high_prices = df['High'].values.astype(float)
            low_prices = df['Low'].values.astype(float)
            close_prices = df['Close'].values.astype(float)
            volume = df['Volume'].values.astype(float)
            
            indicators = {}
            
            # Trend Indicators
            indicators.update(self._calculate_trend_indicators(close_prices))
            
            # Momentum Indicators
            indicators.update(self._calculate_momentum_indicators(
                open_prices, high_prices, low_prices, close_prices))
            
            # Volatility Indicators
            indicators.update(self._calculate_volatility_indicators(
                high_prices, low_prices, close_prices))
            
            # Volume Indicators
            indicators.update(self._calculate_volume_indicators(
                close_prices, volume))
            
            # Moving Averages
            indicators.update(self._calculate_moving_averages(close_prices))
            
            # Support and Resistance
            indicators.update(self._calculate_support_resistance(df))
            
            # Market State
            indicators.update(self._analyze_market_state(indicators, df))
            
            logger.info(f"Calculated {len(indicators)} technical indicators")
            return indicators
            
        except Exception as e:
            logger.error(f"Error calculating indicators: {e}", exc_info=True)
            return {}
    
    def _calculate_trend_indicators(self, close_prices: np.ndarray) -> Dict[str, Any]:
        """Calculate trend indicators"""
        indicators = {}
        
        try:
            # ADX (Average Directional Index)
            adx = talib.ADX(self._get_valid_array(close_prices), 
                          self._get_valid_array(close_prices), 
                          self._get_valid_array(close_prices),
                          timeperiod=self.config.ADX_PERIOD)
            indicators['adx'] = float(adx[-1]) if len(adx) > 0 else 0
            
            # Plus and Minus Directional Indicators
            plus_di = talib.PLUS_DI(self._get_valid_array(close_prices), 
                                   self._get_valid_array(close_prices), 
                                   self._get_valid_array(close_prices),
                                   timeperiod=self.config.ADX_PERIOD)
            minus_di = talib.MINUS_DI(self._get_valid_array(close_prices), 
                                     self._get_valid_array(close_prices), 
                                     self._get_valid_array(close_prices),
                                     timeperiod=self.config.ADX_PERIOD)
            
            indicators['plus_di'] = float(plus_di[-1]) if len(plus_di) > 0 else 0
            indicators['minus_di'] = float(minus_di[-1]) if len(minus_di) > 0 else 0
            
            # Determine trend direction
            if indicators['adx'] > 25:
                if indicators['plus_di'] > indicators['minus_di']:
                    indicators['trend'] = 'UPTREND'
                else:
                    indicators['trend'] = 'DOWNTREND'
            else:
                indicators['trend'] = 'RANGING'
            
        except Exception as e:
            logger.warning(f"Error calculating trend indicators: {e}")
        
        return indicators
    
    def _calculate_momentum_indicators(self, open_prices: np.ndarray, 
                                      high_prices: np.ndarray, 
                                      low_prices: np.ndarray, 
                                      close_prices: np.ndarray) -> Dict[str, Any]:
        """Calculate momentum indicators"""
        indicators = {}
        
        try:
            # RSI (Relative Strength Index)
            rsi = talib.RSI(self._get_valid_array(close_prices), 
                           timeperiod=self.config.RSI_PERIOD)
            indicators['rsi'] = float(rsi[-1]) if len(rsi) > 0 else 50
            
            # MACD (Moving Average Convergence Divergence)
            macd, macd_signal, macd_hist = talib.MACD(
                self._get_valid_array(close_prices),
                fastperiod=self.config.MACD_FAST,
                slowperiod=self.config.MACD_SLOW,
                signalperiod=self.config.MACD_SIGNAL)
            
            indicators['macd'] = (
                float(macd[-1]) if len(macd) > 0 else 0,
                float(macd_signal[-1]) if len(macd_signal) > 0 else 0,
                float(macd_hist[-1]) if len(macd_hist) > 0 else 0
            )
            
            # Stochastic Oscillator
            slowk, slowd = talib.STOCH(
                self._get_valid_array(high_prices),
                self._get_valid_array(low_prices),
                self._get_valid_array(close_prices),
                fastk_period=self.config.STOCH_PERIOD,
                slowk_period=3,
                slowk_matype=0,
                slowd_period=3,
                slowd_matype=0)
            
            indicators['stochastic'] = (
                float(slowk[-1]) if len(slowk) > 0 else 50,
                float(slowd[-1]) if len(slowd) > 0 else 50
            )
            
            # Williams %R
            willr = talib.WILLR(self._get_valid_array(high_prices),
                               self._get_valid_array(low_prices),
                               self._get_valid_array(close_prices),
                               timeperiod=self.config.STOCH_PERIOD)
            indicators['williams_r'] = float(willr[-1]) if len(willr) > 0 else -50
            
            # CCI (Commodity Channel Index)
            cci = talib.CCI(self._get_valid_array(high_prices),
                           self._get_valid_array(low_prices),
                           self._get_valid_array(close_prices),
                           timeperiod=20)
            indicators['cci'] = float(cci[-1]) if len(cci) > 0 else 0
            
            # Momentum
            momentum = talib.MOM(self._get_valid_array(close_prices), timeperiod=10)
            indicators['momentum'] = float(momentum[-1]) if len(momentum) > 0 else 0
            
        except Exception as e:
            logger.warning(f"Error calculating momentum indicators: {e}")
        
        return indicators
    
    def _calculate_volatility_indicators(self, high_prices: np.ndarray,
                                        low_prices: np.ndarray,
                                        close_prices: np.ndarray) -> Dict[str, Any]:
        """Calculate volatility indicators"""
        indicators = {}
        
        try:
            # Bollinger Bands
            upper, middle, lower = talib.BBANDS(
                self._get_valid_array(close_prices),
                timeperiod=self.config.BB_PERIOD,
                nbdevup=self.config.BB_STD,
                nbdevdn=self.config.BB_STD,
                matype=0)
            
            indicators['bollinger_bands'] = {
                'upper': float(upper[-1]) if len(upper) > 0 else 0,
                'middle': float(middle[-1]) if len(middle) > 0 else 0,
                'lower': float(lower[-1]) if len(lower) > 0 else 0,
                'bandwidth': ((upper[-1] - lower[-1]) / middle[-1]) * 100 if len(middle) > 0 else 0
            }
            
            # ATR (Average True Range)
            atr = talib.ATR(self._get_valid_array(high_prices),
                           self._get_valid_array(low_prices),
                           self._get_valid_array(close_prices),
                           timeperiod=self.config.ATR_PERIOD)
            indicators['atr'] = float(atr[-1]) if len(atr) > 0 else 0
            indicators['atr_percent'] = (indicators['atr'] / close_prices[-1]) * 100 if close_prices[-1] > 0 else 0
            
            # Standard Deviation
            std_dev = talib.STDDEV(self._get_valid_array(close_prices), timeperiod=20)
            indicators['std_dev'] = float(std_dev[-1]) if len(std_dev) > 0 else 0
            
        except Exception as e:
            logger.warning(f"Error calculating volatility indicators: {e}")
        
        return indicators
    
    def _calculate_volume_indicators(self, close_prices: np.ndarray,
                                    volume: np.ndarray) -> Dict[str, Any]:
        """Calculate volume indicators"""
        indicators = {}
        
        try:
            # OBV (On-Balance Volume)
            obv = talib.OBV(self._get_valid_array(close_prices), self._get_valid_array(volume))
            indicators['obv'] = float(obv[-1]) if len(obv) > 0 else 0
            
            # Volume SMA
            volume_sma = talib.SMA(self._get_valid_array(volume), timeperiod=20)
            indicators['volume_sma'] = float(volume_sma[-1]) if len(volume_sma) > 0 else 0
            indicators['volume_ratio'] = (volume[-1] / indicators['volume_sma']) if indicators['volume_sma'] > 0 else 0
            
            # Money Flow Index
            mfi = talib.MFI(self._get_valid_array(close_prices),
                           self._get_valid_array(close_prices),
                           self._get_valid_array(close_prices),
                           self._get_valid_array(volume),
                           timeperiod=14)
            indicators['mfi'] = float(mfi[-1]) if len(mfi) > 0 else 50
            
        except Exception as e:
            logger.warning(f"Error calculating volume indicators: {e}")
        
        return indicators
    
    def _calculate_moving_averages(self, close_prices: np.ndarray) -> Dict[str, Any]:
        """Calculate moving averages"""
        indicators = {}
        
        try:
            # Simple Moving Averages
            moving_averages = {}
            for period in self.config.SMA_PERIODS:
                sma = talib.SMA(self._get_valid_array(close_prices), timeperiod=period)
                moving_averages[f'sma_{period}'] = float(sma[-1]) if len(sma) > 0 else 0
            
            # Exponential Moving Averages
            for period in self.config.EMA_PERIODS:
                ema = talib.EMA(self._get_valid_array(close_prices), timeperiod=period)
                moving_averages[f'ema_{period}'] = float(ema[-1]) if len(ema) > 0 else 0
            
            indicators['moving_averages'] = moving_averages
            
            # Determine MA alignment
            current_price = close_prices[-1]
            ma_20 = moving_averages.get('sma_20', 0)
            ma_50 = moving_averages.get('sma_50', 0)
            ma_200 = moving_averages.get('sma_200', 0)
            
            if all([ma_20, ma_50, ma_200]):
                if current_price > ma_20 > ma_50 > ma_200:
                    indicators['ma_alignment'] = 'STRONG_BULLISH'
                elif current_price < ma_20 < ma_50 < ma_200:
                    indicators['ma_alignment'] = 'STRONG_BEARISH'
                elif current_price > ma_20 and ma_20 > ma_50:
                    indicators['ma_alignment'] = 'BULLISH'
                elif current_price < ma_20 and ma_20 < ma_50:
                    indicators['ma_alignment'] = 'BEARISH'
                else:
                    indicators['ma_alignment'] = 'NEUTRAL'
            
        except Exception as e:
            logger.warning(f"Error calculating moving averages: {e}")
        
        return indicators
    
    def _calculate_support_resistance(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate support and resistance levels"""
        indicators = {}
        
        try:
            if len(df) < 20:
                return indicators
            
            recent_data = df.tail(50)
            
            # Pivot Points
            pivot = (recent_data['High'].max() + recent_data['Low'].min() + recent_data['Close'].iloc[-1]) / 3
            
            indicators['pivot_points'] = {
                'pivot': float(pivot),
                'r1': float(2 * pivot - recent_data['Low'].min()),
                'r2': float(pivot + (recent_data['High'].max() - recent_data['Low'].min())),
                's1': float(2 * pivot - recent_data['High'].max()),
                's2': float(pivot - (recent_data['High'].max() - recent_data['Low'].min()))
            }
            
            # Recent highs and lows
            indicators['recent_high'] = float(recent_data['High'].max())
            indicators['recent_low'] = float(recent_data['Low'].min())
            
            # Fibonacci levels
            high = recent_data['High'].max()
            low = recent_data['Low'].min()
            diff = high - low
            
            indicators['fibonacci'] = {
                '0.0': float(low),
                '0.236': float(high - diff * 0.236),
                '0.382': float(high - diff * 0.382),
                '0.5': float(high - diff * 0.5),
                '0.618': float(high - diff * 0.618),
                '0.786': float(high - diff * 0.786),
                '1.0': float(high)
            }
            
        except Exception as e:
            logger.warning(f"Error calculating support/resistance: {e}")
        
        return indicators
    
    def _analyze_market_state(self, indicators: Dict[str, Any], df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze overall market state"""
        analysis = {}
        
        try:
            current_price = df['Close'].iloc[-1]
            
            # Overbought/Oversold Analysis
            overbought_count = 0
            oversold_count = 0
            
            # RSI
            rsi = indicators.get('rsi', 50)
            if rsi > self.config.RSI_OVERBOUGHT:
                overbought_count += 1
                analysis['rsi_state'] = 'OVERBOUGHT'
            elif rsi < self.config.RSI_OVERSOLD:
                oversold_count += 1
                analysis['rsi_state'] = 'OVERSOLD'
            else:
                analysis['rsi_state'] = 'NEUTRAL'
            
            # Stochastic
            stochastic_k, stochastic_d = indicators.get('stochastic', (50, 50))
            if stochastic_k > self.config.STOCH_OVERBOUGHT:
                overbought_count += 1
                analysis['stochastic_state'] = 'OVERBOUGHT'
            elif stochastic_k < self.config.STOCH_OVERSOLD:
                oversold_count += 1
                analysis['stochastic_state'] = 'OVERSOLD'
            else:
                analysis['stochastic_state'] = 'NEUTRAL'
            
            # Williams %R
            williams_r = indicators.get('williams_r', -50)
            if williams_r > -20:
                overbought_count += 1
                analysis['williams_state'] = 'OVERBOUGHT'
            elif williams_r < -80:
                oversold_count += 1
                analysis['williams_state'] = 'OVERSOLD'
            else:
                analysis['williams_state'] = 'NEUTRAL'
            
            # Market State Summary
            if overbought_count >= 2:
                analysis['market_state'] = 'OVERBOUGHT'
            elif oversold_count >= 2:
                analysis['market_state'] = 'OVERSOLD'
            else:
                analysis['market_state'] = 'NEUTRAL'
            
            # Volatility State
            atr_percent = indicators.get('atr_percent', 0)
            if atr_percent > 3:
                analysis['volatility'] = 'HIGH'
            elif atr_percent < 1:
                analysis['volatility'] = 'LOW'
            else:
                analysis['volatility'] = 'MODERATE'
            
            # Trend Strength
            adx = indicators.get('adx', 0)
            if adx > 40:
                analysis['trend_strength'] = 'VERY_STRONG'
            elif adx > 25:
                analysis['trend_strength'] = 'STRONG'
            elif adx > 20:
                analysis['trend_strength'] = 'WEAK'
            else:
                analysis['trend_strength'] = 'NO_TREND'
            
        except Exception as e:
            logger.warning(f"Error analyzing market state: {e}")
        
        return analysis
    
    def detect_candlestick_patterns(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Detect Japanese candlestick patterns
        
        Parameters:
            df (pd.DataFrame): OHLCV data
        
        Returns:
            List[Dict[str, Any]]: List of detected patterns
        """
        patterns = []
        
        try:
            if len(df) < 3:
                return patterns
            
            # Extract last few candles for pattern detection
            recent_df = df.tail(10)
            
            open_prices = recent_df['Open'].values.astype(float)
            high_prices = recent_df['High'].values.astype(float)
            low_prices = recent_df['Low'].values.astype(float)
            close_prices = recent_df['Close'].values.astype(float)
            
            # Define pattern functions
            pattern_checks = [
                (talib.CDL2CROWS, "Two Crows", "bearish"),
                (talib.CDL3BLACKCROWS, "Three Black Crows", "bearish"),
                (talib.CDL3INSIDE, "Three Inside", "reversal"),
                (talib.CDL3LINESTRIKE, "Three Line Strike", "reversal"),
                (talib.CDL3OUTSIDE, "Three Outside", "reversal"),
                (talib.CDL3STARSINSOUTH, "Three Stars in South", "bullish"),
                (talib.CDL3WHITESOLDIERS, "Three White Soldiers", "bullish"),
                (talib.CDLABANDONEDBABY, "Abandoned Baby", "reversal"),
                (talib.CDLADVANCEBLOCK, "Advance Block", "bearish"),
                (talib.CDLBELTHOLD, "Belt Hold", "reversal"),
                (talib.CDLBREAKAWAY, "Breakaway", "reversal"),
                (talib.CDLCLOSINGMARUBOZU, "Closing Marubozu", "continuation"),
                (talib.CDLCONCEALBABYSWALL, "Concealing Baby Swallow", "bearish"),
                (talib.CDLCOUNTERATTACK, "Counterattack", "reversal"),
                (talib.CDLDARKCLOUDCOVER, "Dark Cloud Cover", "bearish"),
                (talib.CDLDOJI, "Doji", "neutral"),
                (talib.CDLDOJISTAR, "Doji Star", "reversal"),
                (talib.CDLDRAGONFLYDOJI, "Dragonfly Doji", "bullish"),
                (talib.CDLENGULFING, "Engulfing", "reversal"),
                (talib.CDLEVENINGDOJISTAR, "Evening Doji Star", "bearish"),
                (talib.CDLEVENINGSTAR, "Evening Star", "bearish"),
                (talib.CDLGAPSIDESIDEWHITE, "Gap Side By Side White", "continuation"),
                (talib.CDLGRAVESTONEDOJI, "Gravestone Doji", "bearish"),
                (talib.CDLHAMMER, "Hammer", "bullish"),
                (talib.CDLHANGINGMAN, "Hanging Man", "bearish"),
                (talib.CDLHARAMI, "Harami", "reversal"),
                (talib.CDLHARAMICROSS, "Harami Cross", "reversal"),
                (talib.CDLHIGHWAVE, "High Wave", "neutral"),
                (talib.CDLHIKKAKE, "Hikkake", "continuation"),
                (talib.CDLHIKKAKEMOD, "Modified Hikkake", "continuation"),
                (talib.CDLHOMINGPIGEON, "Homing Pigeon", "bullish"),
                (talib.CDLIDENTICAL3CROWS, "Identical Three Crows", "bearish"),
                (talib.CDLINNECK, "In Neck", "bearish"),
                (talib.CDLINVERTEDHAMMER, "Inverted Hammer", "bullish"),
                (talib.CDLKICKING, "Kicking", "reversal"),
                (talib.CDLKICKINGBYLENGTH, "Kicking by Length", "reversal"),
                (talib.CDLLADDERBOTTOM, "Ladder Bottom", "bullish"),
                (talib.CDLLONGLEGGEDDOJI, "Long Legged Doji", "neutral"),
                (talib.CDLLONGLINE, "Long Line", "continuation"),
                (talib.CDLMARUBOZU, "Marubozu", "continuation"),
                (talib.CDLMATCHINGLOW, "Matching Low", "bullish"),
                (talib.CDLMATHOLD, "Mat Hold", "bullish"),
                (talib.CDLMORNINGDOJISTAR, "Morning Doji Star", "bullish"),
                (talib.CDLMORNINGSTAR, "Morning Star", "bullish"),
                (talib.CDLONNECK, "On Neck", "bearish"),
                (talib.CDLPIERCING, "Piercing", "bullish"),
                (talib.CDLRICKSHAWMAN, "Rickshaw Man", "neutral"),
                (talib.CDLRISEFALL3METHODS, "Rising/Falling Three Methods", "continuation"),
                (talib.CDLSEPARATINGLINES, "Separating Lines", "continuation"),
                (talib.CDLSHOOTINGSTAR, "Shooting Star", "bearish"),
                (talib.CDLSHORTLINE, "Short Line", "continuation"),
                (talib.CDLSPINNINGTOP, "Spinning Top", "neutral"),
                (talib.CDLSTALLEDPATTERN, "Stalled Pattern", "bearish"),
                (talib.CDLSTICKSANDWICH, "Stick Sandwich", "bullish"),
                (talib.CDLTAKURI, "Takuri", "bullish"),
                (talib.CDLTASUKIGAP, "Tasuki Gap", "continuation"),
                (talib.CDLTHRUSTING, "Thrusting", "bearish"),
                (talib.CDLTRISTAR, "Tristar", "reversal"),
                (talib.CDLUNIQUE3RIVER, "Unique Three River", "bullish"),
                (talib.CDLUPSIDEGAP2CROWS, "Upside Gap Two Crows", "bearish"),
                (talib.CDLXSIDEGAP3METHODS, "Upside/Downside Gap Three Methods", "continuation"),
            ]
            
            # Check each pattern
            for pattern_func, pattern_name, pattern_type in pattern_checks:
                try:
                    pattern_result = pattern_func(open_prices, high_prices, low_prices, close_prices)
                    
                    # Check if pattern was detected in the last candle
                    if pattern_result[-1] != 0:
                        reliability = self._calculate_pattern_reliability(pattern_name, pattern_type)
                        
                        patterns.append({
                            'name': pattern_name,
                            'type': pattern_type,
                            'reliability': reliability,
                            'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            'strength': abs(pattern_result[-1])
                        })
                        
                except Exception as e:
                    # Some patterns might not be available or cause errors
                    continue
            
            # Sort patterns by strength
            patterns.sort(key=lambda x: x['strength'], reverse=True)
            
            logger.info(f"Detected {len(patterns)} candlestick patterns")
            
        except Exception as e:
            logger.error(f"Error detecting candlestick patterns: {e}")
        
        return patterns
    
    def _calculate_pattern_reliability(self, pattern_name: str, pattern_type: str) -> float:
        """
        Calculate pattern reliability based on historical accuracy
        
        Parameters:
            pattern_name (str): Pattern name
            pattern_type (str): Pattern type
        
        Returns:
            float: Reliability score (0-1)
        """
        # This is a simplified reliability calculation
        # In a real application, you would use historical data
        
        reliability_scores = {
            # High reliability patterns
            'Engulfing': 0.75,
            'Morning Star': 0.80,
            'Evening Star': 0.80,
            'Hammer': 0.70,
            'Shooting Star': 0.70,
            'Doji': 0.60,
            'Piercing': 0.65,
            'Dark Cloud Cover': 0.65,
            
            # Medium reliability patterns
            'Harami': 0.55,
            'Harami Cross': 0.55,
            'Spinning Top': 0.50,
            'Hanging Man': 0.55,
            'Inverted Hammer': 0.55,
            
            # Default for other patterns
            'default': 0.45
        }
        
        return reliability_scores.get(pattern_name, reliability_scores['default'])
    
    def _get_valid_array(self, arr: np.ndarray) -> np.ndarray:
        """Ensure array is valid for TA-Lib"""
        if arr is None or len(arr) == 0:
            return np.zeros(1)
        
        # Replace NaN values with previous values
        arr_valid = np.copy(arr)
        mask = np.isnan(arr_valid)
        
        if mask.any():
            # Forward fill
            idx = np.where(~mask, np.arange(len(mask)), 0)
            np.maximum.accumulate(idx, out=idx)
            arr_valid = arr_valid[idx]
        
        return arr_valid.astype(float)

def test_technical_analyzer():
    """Test technical analyzer"""
    import yfinance as yf
    
    analyzer = TechnicalAnalyzer()
    
    print("Testing Technical Analyzer...")
    
    # Get sample data
    ticker = yf.Ticker('AAPL')
    df = ticker.history(period='1mo', interval='1d')
    
    if not df.empty:
        # Calculate indicators
        indicators = analyzer.calculate_indicators(df)
        
        print(f"\nCalculated {len(indicators)} indicators")
        
        # Display some key indicators
        print(f"\nKey Indicators:")
        print(f"  RSI: {indicators.get('rsi', 0):.2f}")
        print(f"  MACD: {indicators.get('macd', (0,0,0))}")
        print(f"  ADX: {indicators.get('adx', 0):.2f}")
        print(f"  Trend: {indicators.get('trend', 'N/A')}")
        print(f"  Market State: {indicators.get('market_state', 'N/A')}")
        
        # Detect patterns
        patterns = analyzer.detect_candlestick_patterns(df)
        
        if patterns:
            print(f"\nDetected Patterns:")
            for pattern in patterns[:3]:  # Show first 3
                print(f"  {pattern['name']} ({pattern['type']}) - Reliability: {pattern['reliability']:.2f}")
        else:
            print("\nNo patterns detected")

if __name__ == "__main__":
    test_technical_analyzer()
