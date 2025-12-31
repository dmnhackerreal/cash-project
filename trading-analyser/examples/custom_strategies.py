#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Custom Strategies Examples
Examples showing how to create custom trading strategies
"""

import sys
import os
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
from abc import ABC, abstractmethod
import warnings

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from modules.data_fetcher import MarketDataFetcher
from modules.technical_analyzer import TechnicalAnalyzer
from utils.logger import setup_logger

logger = setup_logger(__name__)

class TradingStrategy(ABC):
    """Abstract base class for trading strategies"""
    
    def __init__(self, name: str, description: str = ""):
        """Initialize strategy"""
        self.name = name
        self.description = description
        self.fetcher = MarketDataFetcher()
        self.analyzer = TechnicalAnalyzer()
        self.parameters = {}
        
        logger.info(f"Initialized strategy: {name}")
    
    @abstractmethod
    def generate_signal(self, symbol: str, df: pd.DataFrame, 
                       indicators: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate trading signal
        
        Parameters:
            symbol (str): Trading symbol
            df (pd.DataFrame): Price data
            indicators (Dict[str, Any]): Technical indicators
        
        Returns:
            Dict[str, Any]: Trading signal
        """
        pass
    
    def backtest(self, symbol: str, start_date: str, end_date: str,
                initial_capital: float = 10000) -> Dict[str, Any]:
        """
        Backtest strategy
        
        Parameters:
            symbol (str): Trading symbol
            start_date (str): Start date (YYYY-MM-DD)
            end_date (str): End date (YYYY-MM-DD)
            initial_capital (float): Initial capital
        
        Returns:
            Dict[str, Any]: Backtest results
        """
        logger.info(f"Backtesting {self.name} on {symbol} from {start_date} to {end_date}")
        
        try:
            # Fetch historical data
            df = self.fetcher.get_historical_data(symbol, period='max')
            
            if df is None or df.empty:
                logger.warning(f"No data for {symbol}")
                return {}
            
            # Filter by date range
            mask = (df.index >= start_date) & (df.index <= end_date)
            df = df.loc[mask]
            
            if df.empty:
                logger.warning(f"No data in date range for {symbol}")
                return {}
            
            # Initialize backtest variables
            capital = initial_capital
            position = 0
            trades = []
            current_trade = None
            
            # Run backtest
            for i in range(1, len(df)):
                current_date = df.index[i]
                current_price = df['Close'].iloc[i]
                
                # Get data up to current point
                df_slice = df.iloc[:i+1]
                indicators = self.analyzer.calculate_indicators(df_slice)
                
                # Generate signal
                signal = self.generate_signal(symbol, df_slice, indicators)
                
                # Execute trades based on signal
                if signal['action'] == 'BUY' and position == 0:
                    # Enter long position
                    position_size = capital / current_price
                    position = position_size
                    capital = 0
                    
                    current_trade = {
                        'entry_date': current_date,
                        'entry_price': current_price,
                        'position_size': position_size,
                        'type': 'LONG'
                    }
                    
                elif signal['action'] == 'SELL' and position > 0:
                    # Exit long position
                    exit_value = position * current_price
                    capital = exit_value
                    
                    trades.append({
                        **current_trade,
                        'exit_date': current_date,
                        'exit_price': current_price,
                        'pnl': exit_value - (current_trade['position_size'] * current_trade['entry_price']),
                        'pnl_percent': ((current_price / current_trade['entry_price']) - 1) * 100
                    })
                    
                    position = 0
                    current_trade = None
            
            # Close any open position at the end
            if position > 0:
                exit_price = df['Close'].iloc[-1]
                exit_value = position * exit_price
                capital = exit_value
                
                trades.append({
                    **current_trade,
                    'exit_date': df.index[-1],
                    'exit_price': exit_price,
                    'pnl': exit_value - (current_trade['position_size'] * current_trade['entry_price']),
                    'pnl_percent': ((exit_price / current_trade['entry_price']) - 1) * 100
                })
            
            # Calculate performance metrics
            results = self._calculate_performance_metrics(trades, initial_capital, capital)
            
            logger.info(f"Backtest completed: {results.get('total_return_percent', 0):.1f}% return")
            return results
            
        except Exception as e:
            logger.error(f"Error in backtest: {e}")
            return {}
    
    def _calculate_performance_metrics(self, trades: List[Dict[str, Any]],
                                      initial_capital: float,
                                      final_capital: float) -> Dict[str, Any]:
        """Calculate performance metrics from trades"""
        if not trades:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0,
                'total_return': 0,
                'total_return_percent': 0,
                'avg_win': 0,
                'avg_loss': 0,
                'profit_factor': 0,
                'max_drawdown': 0
            }
        
        # Calculate metrics
        winning_trades = [t for t in trades if t['pnl'] > 0]
        losing_trades = [t for t in trades if t['pnl'] <= 0]
        
        total_return = final_capital - initial_capital
        total_return_percent = (total_return / initial_capital) * 100
        
        avg_win = np.mean([t['pnl'] for t in winning_trades]) if winning_trades else 0
        avg_loss = np.mean([t['pnl'] for t in losing_trades]) if losing_trades else 0
        
        gross_profit = sum(t['pnl'] for t in winning_trades)
        gross_loss = abs(sum(t['pnl'] for t in losing_trades))
        
        profit_factor = gross_profit / gross_loss if gross_loss != 0 else float('inf')
        
        # Calculate drawdown
        equity_curve = [initial_capital]
        for trade in trades:
            equity_curve.append(equity_curve[-1] + trade['pnl'])
        
        running_max = np.maximum.accumulate(equity_curve)
        drawdowns = (equity_curve - running_max) / running_max * 100
        max_drawdown = abs(drawdowns.min()) if len(drawdowns) > 0 else 0
        
        return {
            'strategy_name': self.name,
            'total_trades': len(trades),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': len(winning_trades) / len(trades) * 100,
            'total_return': total_return,
            'total_return_percent': total_return_percent,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'max_drawdown': max_drawdown,
            'initial_capital': initial_capital,
            'final_capital': final_capital,
            'trades': trades
        }
    
    def optimize_parameters(self, symbol: str, param_grid: Dict[str, List[Any]],
                          start_date: str, end_date: str) -> Dict[str, Any]:
        """
        Optimize strategy parameters using grid search
        
        Parameters:
            symbol (str): Trading symbol
            param_grid (Dict[str, List[Any]]): Parameter grid
            start_date (str): Start date for optimization
            end_date (str): End date for optimization
        
        Returns:
            Dict[str, Any]: Optimization results
        """
        logger.info(f"Optimizing {self.name} parameters on {symbol}")
        
        try:
            # Generate all parameter combinations
            from itertools import product
            
            param_names = list(param_grid.keys())
            param_values = list(product(*param_grid.values()))
            
            best_result = None
            best_score = -float('inf')
            all_results = []
            
            # Test each parameter combination
            for values in param_values:
                # Update strategy parameters
                params = dict(zip(param_names, values))
                self.parameters.update(params)
                
                # Run backtest
                result = self.backtest(symbol, start_date, end_date)
                
                if result:
                    # Use Sharpe ratio as score (simplified)
                    score = result.get('total_return_percent', 0) / (result.get('max_drawdown', 1) + 1)
                    
                    result['parameters'] = params
                    result['score'] = score
                    
                    all_results.append(result)
                    
                    if score > best_score:
                        best_score = score
                        best_result = result
            
            # Sort results by score
            all_results.sort(key=lambda x: x.get('score', 0), reverse=True)
            
            optimization_result = {
                'best_parameters': best_result.get('parameters', {}) if best_result else {},
                'best_score': best_score,
                'best_result': best_result,
                'all_results': all_results[:10]  # Top 10 results
            }
            
            logger.info(f"Optimization completed. Best score: {best_score:.3f}")
            return optimization_result
            
        except Exception as e:
            logger.error(f"Error optimizing parameters: {e}")
            return {}

class RSIMACDStrategy(TradingStrategy):
    """RSI + MACD crossover strategy"""
    
    def __init__(self):
        """Initialize RSI MACD strategy"""
        super().__init__(
            name="RSI_MACD_Crossover",
            description="Combines RSI oversold/overbought with MACD crossover"
        )
        
        # Default parameters
        self.parameters = {
            'rsi_period': 14,
            'rsi_overbought': 70,
            'rsi_oversold': 30,
            'macd_fast': 12,
            'macd_slow': 26,
            'macd_signal': 9
        }
    
    def generate_signal(self, symbol: str, df: pd.DataFrame,
                       indicators: Dict[str, Any]) -> Dict[str, Any]:
        """Generate signal based on RSI and MACD"""
        signal = {
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'action': 'HOLD',
            'confidence': 0.5,
            'reasons': []
        }
        
        try:
            # Get indicators
            rsi = indicators.get('rsi', 50)
            macd_line, macd_signal, macd_hist = indicators.get('macd', (0, 0, 0))
            
            # Buy conditions
            buy_conditions = []
            
            if rsi < self.parameters['rsi_oversold']:
                buy_conditions.append(f"RSI oversold ({rsi:.1f})")
            
            if macd_hist > 0 and macd_line > macd_signal:
                buy_conditions.append("MACD bullish crossover")
            
            # Sell conditions
            sell_conditions = []
            
            if rsi > self.parameters['rsi_overbought']:
                sell_conditions.append(f"RSI overbought ({rsi:.1f})")
            
            if macd_hist < 0 and macd_line < macd_signal:
                sell_conditions.append("MACD bearish crossover")
            
            # Determine action
            if len(buy_conditions) >= 2:
                signal['action'] = 'BUY'
                signal['confidence'] = 0.7
                signal['reasons'] = buy_conditions
            
            elif len(sell_conditions) >= 2:
                signal['action'] = 'SELL'
                signal['confidence'] = 0.7
                signal['reasons'] = sell_conditions
            
            elif len(buy_conditions) == 1:
                signal['action'] = 'BUY'
                signal['confidence'] = 0.6
                signal['reasons'] = buy_conditions
            
            elif len(sell_conditions) == 1:
                signal['action'] = 'SELL'
                signal['confidence'] = 0.6
                signal['reasons'] = sell_conditions
            
        except Exception as e:
            logger.error(f"Error generating RSI MACD signal: {e}")
        
        return signal

class BollingerBandStrategy(TradingStrategy):
    """Bollinger Band mean reversion strategy"""
    
    def __init__(self):
        """Initialize Bollinger Band strategy"""
        super().__init__(
            name="Bollinger_Band_Reversion",
            description="Trades bounces from Bollinger Bands"
        )
        
        # Default parameters
        self.parameters = {
            'bb_period': 20,
            'bb_std': 2,
            'rsi_period': 14,
            'exit_threshold': 0.5
        }
    
    def generate_signal(self, symbol: str, df: pd.DataFrame,
                       indicators: Dict[str, Any]) -> Dict[str, Any]:
        """Generate signal based on Bollinger Bands"""
        signal = {
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'action': 'HOLD',
            'confidence': 0.5,
            'reasons': []
        }
        
        try:
            current_price = df['Close'].iloc[-1]
            
            # Get Bollinger Bands
            bb = indicators.get('bollinger_bands', {})
            if not bb:
                return signal
            
            bb_upper = bb.get('upper', 0)
            bb_middle = bb.get('middle', 0)
            bb_lower = bb.get('lower', 0)
            
            # Get RSI
            rsi = indicators.get('rsi', 50)
            
            # Calculate position within bands
            if bb_upper != bb_lower:
                bb_position = (current_price - bb_lower) / (bb_upper - bb_lower)
            else:
                bb_position = 0.5
            
            # Buy conditions (near lower band, oversold RSI)
            if bb_position < 0.2 and rsi < 30:
                signal['action'] = 'BUY'
                signal['confidence'] = 0.75
                signal['reasons'] = [
                    f"Price near lower Bollinger Band (position: {bb_position:.2f})",
                    f"RSI oversold ({rsi:.1f})"
                ]
            
            # Sell conditions (near upper band, overbought RSI)
            elif bb_position > 0.8 and rsi > 70:
                signal['action'] = 'SELL'
                signal['confidence'] = 0.75
                signal['reasons'] = [
                    f"Price near upper Bollinger Band (position: {bb_position:.2f})",
                    f"RSI overbought ({rsi:.1f})"
                ]
            
            # Exit conditions (return to middle band)
            elif signal['action'] == 'BUY' and bb_position > self.parameters['exit_threshold']:
                signal['action'] = 'SELL'  # Exit buy
                signal['confidence'] = 0.6
                signal['reasons'] = [f"Price returned to middle band (position: {bb_position:.2f})"]
            
            elif signal['action'] == 'SELL' and bb_position < self.parameters['exit_threshold']:
                signal['action'] = 'BUY'  # Exit sell (cover short)
                signal['confidence'] = 0.6
                signal['reasons'] = [f"Price returned to middle band (position: {bb_position:.2f})"]
            
        except Exception as e:
            logger.error(f"Error generating Bollinger Band signal: {e}")
        
        return signal

class TrendFollowingStrategy(TradingStrategy):
    """Trend following with moving averages"""
    
    def __init__(self):
        """Initialize trend following strategy"""
        super().__init__(
            name="Trend_Following_MA",
            description="Follows trends using multiple moving averages"
        )
        
        # Default parameters
        self.parameters = {
            'sma_fast': 20,
            'sma_slow': 50,
            'ema_fast': 9,
            'ema_slow': 21,
            'adx_threshold': 25
        }
    
    def generate_signal(self, symbol: str, df: pd.DataFrame,
                       indicators: Dict[str, Any]) -> Dict[str, Any]:
        """Generate signal based on trend following"""
        signal = {
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'action': 'HOLD',
            'confidence': 0.5,
            'reasons': []
        }
        
        try:
            current_price = df['Close'].iloc[-1]
            
            # Get moving averages
            ma_data = indicators.get('moving_averages', {})
            if not ma_data:
                return signal
            
            # Get specific MAs
            sma_fast = ma_data.get(f'sma_{self.parameters["sma_fast"]}', 0)
            sma_slow = ma_data.get(f'sma_{self.parameters["sma_slow"]}', 0)
            ema_fast = ma_data.get(f'ema_{self.parameters["ema_fast"]}', 0)
            ema_slow = ma_data.get(f'ema_{self.parameters["ema_slow"]}', 0)
            
            # Get ADX for trend strength
            adx = indicators.get('adx', 0)
            
            # Check if we have valid MA values
            if not all([sma_fast, sma_slow, ema_fast, ema_slow]):
                return signal
            
            # Bullish trend conditions
            bullish_conditions = []
            
            if current_price > sma_fast > sma_slow:
                bullish_conditions.append("Price above fast and slow SMA")
            
            if current_price > ema_fast > ema_slow:
                bullish_conditions.append("Price above fast and slow EMA")
            
            if adx > self.parameters['adx_threshold']:
                bullish_conditions.append(f"Strong trend (ADX: {adx:.1f})")
            
            # Bearish trend conditions
            bearish_conditions = []
            
            if current_price < sma_fast < sma_slow:
                bearish_conditions.append("Price below fast and slow SMA")
            
            if current_price < ema_fast < ema_slow:
                bearish_conditions.append("Price below fast and slow EMA")
            
            if adx > self.parameters['adx_threshold']:
                bearish_conditions.append(f"Strong trend (ADX: {adx:.1f})")
            
            # Determine action
            if len(bullish_conditions) >= 2:
                signal['action'] = 'BUY'
                signal['confidence'] = min(0.8, 0.5 + (len(bullish_conditions) * 0.1))
                signal['reasons'] = bullish_conditions
            
            elif len(bearish_conditions) >= 2:
                signal['action'] = 'SELL'
                signal['confidence'] = min(0.8, 0.5 + (len(bearish_conditions) * 0.1))
                signal['reasons'] = bearish_conditions
            
        except Exception as e:
            logger.error(f"Error generating trend following signal: {e}")
        
        return signal

class MeanReversionStrategy(TradingStrategy):
    """Mean reversion strategy using statistical measures"""
    
    def __init__(self):
        """Initialize mean reversion strategy"""
        super().__init__(
            name="Statistical_Mean_Reversion",
            description="Trades mean reversion using statistical measures"
        )
        
        # Default parameters
        self.parameters = {
            'lookback_period': 20,
            'std_dev_multiplier': 2,
            'rsi_period': 14,
            'holding_period': 5
        }
    
    def generate_signal(self, symbol: str, df: pd.DataFrame,
                       indicators: Dict[str, Any]) -> Dict[str, Any]:
        """Generate signal based on mean reversion"""
        signal = {
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'action': 'HOLD',
            'confidence': 0.5,
            'reasons': []
        }
        
        try:
            if len(df) < self.parameters['lookback_period']:
                return signal
            
            current_price = df['Close'].iloc[-1]
            
            # Calculate mean and standard deviation
            lookback_data = df['Close'].tail(self.parameters['lookback_period'])
            mean_price = lookback_data.mean()
            std_price = lookback_data.std()
            
            # Calculate z-score
            z_score = (current_price - mean_price) / std_price if std_price > 0 else 0
            
            # Get RSI
            rsi = indicators.get('rsi', 50)
            
            # Buy conditions (oversold, below mean)
            if (z_score < -self.parameters['std_dev_multiplier'] and 
                rsi < 30):
                signal['action'] = 'BUY'
                signal['confidence'] = 0.8
                signal['reasons'] = [
                    f"Price {abs(z_score):.1f} standard deviations below mean",
                    f"RSI oversold ({rsi:.1f})"
                ]
            
            # Sell conditions (overbought, above mean)
            elif (z_score > self.parameters['std_dev_multiplier'] and 
                  rsi > 70):
                signal['action'] = 'SELL'
                signal['confidence'] = 0.8
                signal['reasons'] = [
                    f"Price {abs(z_score):.1f} standard deviations above mean",
                    f"RSI overbought ({rsi:.1f})"
                ]
            
            # Exit conditions (return to mean)
            elif abs(z_score) < 0.5:
                if signal.get('previous_action') == 'BUY':
                    signal['action'] = 'SELL'  # Exit buy
                    signal['confidence'] = 0.6
                    signal['reasons'] = [f"Price returned to mean (z-score: {z_score:.2f})"]
                elif signal.get('previous_action') == 'SELL':
                    signal['action'] = 'BUY'  # Exit sell
                    signal['confidence'] = 0.6
                    signal['reasons'] = [f"Price returned to mean (z-score: {z_score:.2f})"]
            
        except Exception as e:
            logger.error(f"Error generating mean reversion signal: {e}")
        
        return signal

class BreakoutStrategy(TradingStrategy):
    """Breakout trading strategy"""
    
    def __init__(self):
        """Initialize breakout strategy"""
        super().__init__(
            name="Breakout_Trading",
            description="Trades breakouts from consolidation patterns"
        )
        
        # Default parameters
        self.parameters = {
            'consolidation_period': 10,
            'breakout_multiplier': 1.5,
            'volume_multiplier': 1.5,
            'stop_loss_atr_multiplier': 1.5
        }
    
    def generate_signal(self, symbol: str, df: pd.DataFrame,
                       indicators: Dict[str, Any]) -> Dict[str, Any]:
        """Generate signal based on breakouts"""
        signal = {
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'action': 'HOLD',
            'confidence': 0.5,
            'reasons': []
        }
        
        try:
            if len(df) < self.parameters['consolidation_period'] + 1:
                return signal
            
            current_price = df['Close'].iloc[-1]
            current_volume = df['Volume'].iloc[-1]
            
            # Analyze consolidation period
            consolidation_data = df.tail(self.parameters['consolidation_period'] + 1)
            consolidation_range = consolidation_data.iloc[:-1]  # Exclude current candle
            
            # Calculate consolidation metrics
            consolidation_high = consolidation_range['High'].max()
            consolidation_low = consolidation_range['Low'].min()
            consolidation_range_size = consolidation_high - consolidation_low
            avg_consolidation_volume = consolidation_range['Volume'].mean()
            
            # Check for breakout
            is_breakout = False
            breakout_direction = None
            
            # Upside breakout
            if current_price > consolidation_high:
                price_move = current_price - consolidation_high
                
                if (price_move > consolidation_range_size * 0.5 and  # Significant move
                    current_volume > avg_consolidation_volume * self.parameters['volume_multiplier']):
                    
                    is_breakout = True
                    breakout_direction = 'UP'
            
            # Downside breakout
            elif current_price < consolidation_low:
                price_move = consolidation_low - current_price
                
                if (price_move > consolidation_range_size * 0.5 and  # Significant move
                    current_volume > avg_consolidation_volume * self.parameters['volume_multiplier']):
                    
                    is_breakout = True
                    breakout_direction = 'DOWN'
            
            # Generate signal based on breakout
            if is_breakout:
                if breakout_direction == 'UP':
                    signal['action'] = 'BUY'
                    signal['confidence'] = 0.7
                    signal['reasons'] = [
                        f"Upside breakout from {self.parameters['consolidation_period']}-period consolidation",
                        f"Volume {current_volume/avg_consolidation_volume:.1f}x average"
                    ]
                
                elif breakout_direction == 'DOWN':
                    signal['action'] = 'SELL'
                    signal['confidence'] = 0.7
                    signal['reasons'] = [
                        f"Downside breakout from {self.parameters['consolidation_period']}-period consolidation",
                        f"Volume {current_volume/avg_consolidation_volume:.1f}x average"
                    ]
            
        except Exception as e:
            logger.error(f"Error generating breakout signal: {e}")
        
        return signal

class StrategyTester:
    """Test and compare multiple strategies"""
    
    def __init__(self):
        """Initialize strategy tester"""
        self.strategies = {}
        self.results = {}
        
        logger.info("Strategy Tester initialized")
    
    def add_strategy(self, strategy: TradingStrategy):
        """Add strategy to tester"""
        self.strategies[strategy.name] = strategy
        logger.info(f"Added strategy: {strategy.name}")
    
    def test_strategies(self, symbol: str, start_date: str, 
                       end_date: str) -> Dict[str, Any]:
        """
        Test all strategies on a symbol
        
        Parameters:
            symbol (str): Trading symbol
            start_date (str): Start date
            end_date (str): End date
        
        Returns:
            Dict[str, Any]: Test results
        """
        logger.info(f"Testing strategies on {symbol} from {start_date} to {end_date}")
        
        results = {}
        
        for name, strategy in self.strategies.items():
            try:
                print(f"\n🔍 Testing {name}...")
                result = strategy.backtest(symbol, start_date, end_date)
                
                if result:
                    results[name] = result
                    print(f"   ✅ Completed: {result.get('total_return_percent', 0):.1f}% return")
                else:
                    print(f"   ❌ Failed")
                    
            except Exception as e:
                logger.error(f"Error testing strategy {name}: {e}")
                print(f"   ❌ Error: {str(e)}")
        
        # Compare results
        comparison = self._compare_results(results)
        
        self.results[symbol] = {
            'individual_results': results,
            'comparison': comparison
        }
        
        return self.results[symbol]
    
    def _compare_results(self, results: Dict[str, Dict[str, Any]]) -> pd.DataFrame:
        """Compare strategy results"""
        if not results:
            return pd.DataFrame()
        
        comparison_data = []
        
        for strategy_name, result in results.items():
            comparison_data.append({
                'Strategy': strategy_name,
                'Total Return %': result.get('total_return_percent', 0),
                'Win Rate %': result.get('win_rate', 0),
                'Total Trades': result.get('total_trades', 0),
                'Avg Win': result.get('avg_win', 0),
                'Avg Loss': result.get('avg_loss', 0),
                'Profit Factor': result.get('profit_factor', 0),
                'Max Drawdown %': result.get('max_drawdown', 0)
            })
        
        df_comparison = pd.DataFrame(comparison_data)
        df_comparison = df_comparison.sort_values('Total Return %', ascending=False)
        
        return df_comparison
    
    def plot_comparison(self, symbol: str):
        """Plot strategy comparison"""
        try:
            import matplotlib.pyplot as plt
            
            if symbol not in self.results:
                logger.warning(f"No results for {symbol}")
                return
            
            comparison = self.results[symbol]['comparison']
            
            if comparison.empty:
                logger.warning("No comparison data to plot")
                return
            
            fig, axes = plt.subplots(2, 2, figsize=(14, 10))
            
            # 1. Total Return
            ax1 = axes[0, 0]
            ax1.bar(comparison['Strategy'], comparison['Total Return %'])
            ax1.set_title('Total Return %')
            ax1.set_ylabel('Return %')
            ax1.tick_params(axis='x', rotation=45)
            
            # 2. Win Rate
            ax2 = axes[0, 1]
            ax2.bar(comparison['Strategy'], comparison['Win Rate %'])
            ax2.set_title('Win Rate %')
            ax2.set_ylabel('Win Rate %')
            ax2.tick_params(axis='x', rotation=45)
            
            # 3. Profit Factor
            ax3 = axes[1, 0]
            ax3.bar(comparison['Strategy'], comparison['Profit Factor'])
            ax3.set_title('Profit Factor')
            ax3.set_ylabel('Ratio')
            ax3.tick_params(axis='x', rotation=45)
            
            # 4. Max Drawdown
            ax4 = axes[1, 1]
            ax4.bar(comparison['Strategy'], comparison['Max Drawdown %'])
            ax4.set_title('Maximum Drawdown %')
            ax4.set_ylabel('Drawdown %')
            ax4.tick_params(axis='x', rotation=45)
            
            plt.suptitle(f'Strategy Comparison - {symbol}', fontsize=16, fontweight='bold')
            plt.tight_layout()
            plt.show()
            
        except Exception as e:
            logger.error(f"Error plotting comparison: {e}")

def example_rsi_macd_strategy():
    """Example: RSI MACD Strategy"""
    print("="*60)
    print("EXAMPLE 1: RSI + MACD Strategy")
    print("="*60)
    
    # Initialize strategy
    strategy = RSIMACDStrategy()
    
    # Test on AAPL
    print("\n🔍 Testing RSI+MACD strategy on AAPL...")
    results = strategy.backtest('AAPL', '2023-01-01', '2023-12-31')
    
    if results:
        print(f"\n📊 Strategy Performance:")
        print(f"   Total Return: {results.get('total_return_percent', 0):.1f}%")
        print(f"   Total Trades: {results.get('total_trades', 0)}")
        print(f"   Win Rate: {results.get('win_rate', 0):.1f}%")
        print(f"   Profit Factor: {results.get('profit_factor', 0):.2f}")
        print(f"   Max Drawdown: {results.get('max_drawdown', 0):.1f}%")
    else:
        print("❌ No results from backtest")

def example_bollinger_band_strategy():
    """Example: Bollinger Band Strategy"""
    print("\n" + "="*60)
    print("EXAMPLE 2: Bollinger Band Strategy")
    print("="*60)
    
    # Initialize strategy
    strategy = BollingerBandStrategy()
    
    # Test on BTC
    print("\n🔍 Testing Bollinger Band strategy on BTC...")
    results = strategy.backtest('BTC-USD', '2023-01-01', '2023-12-31')
    
    if results:
        print(f"\n📊 Strategy Performance:")
        print(f"   Total Return: {results.get('total_return_percent', 0):.1f}%")
        print(f"   Total Trades: {results.get('total_trades', 0)}")
        print(f"   Win Rate: {results.get('win_rate', 0):.1f}%")
        
        # Show some trades
        trades = results.get('trades', [])
        if trades:
            print(f"\n💼 Sample Trades:")
            for i, trade in enumerate(trades[:3]):  # First 3 trades
                print(f"   Trade {i+1}: {trade['type']} at ${trade['entry_price']:.2f}, "
                      f"Exit at ${trade['exit_price']:.2f}, P&L: {trade['pnl_percent']:.1f}%")
    else:
        print("❌ No results from backtest")

def example_strategy_comparison():
    """Example: Strategy Comparison"""
    print("\n" + "="*60)
    print("EXAMPLE 3: Strategy Comparison")
    print("="*60)
    
    # Initialize tester
    tester = StrategyTester()
    
    # Add strategies
    tester.add_strategy(RSIMACDStrategy())
    tester.add_strategy(BollingerBandStrategy())
    tester.add_strategy(TrendFollowingStrategy())
    tester.add_strategy(MeanReversionStrategy())
    tester.add_strategy(BreakoutStrategy())
    
    # Test all strategies on MSFT
    print("\n🔍 Comparing strategies on MSFT...")
    results = tester.test_strategies('MSFT', '2023-01-01', '2023-12-31')
    
    if results and 'comparison' in results:
        comparison = results['comparison']
        
        print(f"\n🏆 Strategy Ranking:")
        for idx, row in comparison.iterrows():
            print(f"   {idx+1}. {row['Strategy']}: {row['Total Return %']:.1f}% return, "
                  f"{row['Win Rate %']:.1f}% win rate")
    
    # Plot comparison
    print("\n📈 Generating comparison charts...")
    tester.plot_comparison('MSFT')

def example_strategy_optimization():
    """Example: Strategy Optimization"""
    print("\n" + "="*60)
    print("EXAMPLE 4: Strategy Optimization")
    print("="*60)
    
    # Initialize strategy
    strategy = RSIMACDStrategy()
    
    # Define parameter grid for optimization
    param_grid = {
        'rsi_period': [10, 14, 20],
        'rsi_overbought': [65, 70, 75],
        'rsi_oversold': [25, 30, 35],
        'macd_fast': [8, 12, 16],
        'macd_slow': [20, 26, 32]
    }
    
    print("\n⚙️ Optimizing RSI+MACD strategy parameters...")
    optimization_results = strategy.optimize_parameters(
        'GOOGL',
        param_grid,
        '2023-01-01',
        '2023-06-30'  # Use first half for optimization
    )
    
    if optimization_results:
        best_params = optimization_results.get('best_parameters', {})
        best_score = optimization_results.get('best_score', 0)
        
        print(f"\n✅ Optimization Completed")
        print(f"   Best Score: {best_score:.3f}")
        print(f"\n🎯 Best Parameters:")
        for param, value in best_params.items():
            print(f"   {param}: {value}")
        
        # Test optimized strategy on second half
        print(f"\n🔍 Testing optimized strategy on out-of-sample data...")
        strategy.parameters.update(best_params)
        
        test_results = strategy.backtest('GOOGL', '2023-07-01', '2023-12-31')
        
        if test_results:
            print(f"\n📊 Optimized Strategy Performance:")
            print(f"   Total Return: {test_results.get('total_return_percent', 0):.1f}%")
            print(f"   Win Rate: {test_results.get('win_rate', 0):.1f}%")
            print(f"   Profit Factor: {test_results.get('profit_factor', 0):.2f}")
    else:
        print("❌ No optimization results")

def example_custom_strategy_creation():
    """Example: Creating Custom Strategy"""
    print("\n" + "="*60)
    print("EXAMPLE 5: Creating Custom Strategy")
    print("="*60)
    
    class MyCustomStrategy(TradingStrategy):
        """Custom strategy combining multiple indicators"""
        
        def __init__(self):
            super().__init__(
                name="My_Custom_Strategy",
                description="Combines multiple indicators for high-probability trades"
            )
            
            self.parameters = {
                'rsi_buy': 35,
                'rsi_sell': 65,
                'stoch_buy': 20,
                'stoch_sell': 80,
                'volume_multiplier': 1.5
            }
        
        def generate_signal(self, symbol: str, df: pd.DataFrame,
                           indicators: Dict[str, Any]) -> Dict[str, Any]:
            signal = {
                'symbol': symbol,
                'timestamp': datetime.now().isoformat(),
                'action': 'HOLD',
                'confidence': 0.5,
                'reasons': []
            }
            
            try:
                # Get indicators
                rsi = indicators.get('rsi', 50)
                stochastic_k, stochastic_d = indicators.get('stochastic', (50, 50))
                volume_ratio = indicators.get('volume_ratio', 1)
                
                # Strong buy conditions
                if (rsi < self.parameters['rsi_buy'] and
                    stochastic_k < self.parameters['stoch_buy'] and
                    volume_ratio > self.parameters['volume_multiplier']):
                    
                    signal['action'] = 'BUY'
                    signal['confidence'] = 0.85
                    signal['reasons'] = [
                        f"RSI deeply oversold ({rsi:.1f})",
                        f"Stochastic oversold ({stochastic_k:.1f})",
                        f"High volume ({volume_ratio:.1f}x average)"
                    ]
                
                # Strong sell conditions
                elif (rsi > self.parameters['rsi_sell'] and
                      stochastic_k > self.parameters['stoch_sell'] and
                      volume_ratio > self.parameters['volume_multiplier']):
                    
                    signal['action'] = 'SELL'
                    signal['confidence'] = 0.85
                    signal['reasons'] = [
                        f"RSI deeply overbought ({rsi:.1f})",
                        f"Stochastic overbought ({stochastic_k:.1f})",
                        f"High volume ({volume_ratio:.1f}x average)"
                    ]
                
                # Moderate buy conditions
                elif (rsi < 40 and stochastic_k < 30):
                    signal['action'] = 'BUY'
                    signal['confidence'] = 0.65
                    signal['reasons'] = [
                        f"RSI oversold ({rsi:.1f})",
                        f"Stochastic oversold ({stochastic_k:.1f})"
                    ]
                
                # Moderate sell conditions
                elif (rsi > 60 and stochastic_k > 70):
                    signal['action'] = 'SELL'
                    signal['confidence'] = 0.65
                    signal['reasons'] = [
                        f"RSI overbought ({rsi:.1f})",
                        f"Stochastic overbought ({stochastic_k:.1f})"
                    ]
                
            except Exception as e:
                logger.error(f"Error in custom strategy: {e}")
            
            return signal
    
    # Test custom strategy
    print("\n🔍 Testing custom strategy on TSLA...")
    strategy = MyCustomStrategy()
    results = strategy.backtest('TSLA', '2023-01-01', '2023-12-31')
    
    if results:
        print(f"\n✅ Custom Strategy Performance:")
        print(f"   Total Return: {results.get('total_return_percent', 0):.1f}%")
        print(f"   Total Trades: {results.get('total_trades', 0)}")
        print(f"   Win Rate: {results.get('win_rate', 0):.1f}%")
        print(f"   Profit Factor: {results.get('profit_factor', 0):.2f}")
        
        # Show strategy logic
        print(f"\n🎯 Strategy Logic:")
        print(f"   Buy when: RSI < {strategy.parameters['rsi_buy']} AND "
              f"Stochastic < {strategy.parameters['stoch_buy']} AND Volume > "
              f"{strategy.parameters['volume_multiplier']}x average")
        print(f"   Sell when: RSI > {strategy.parameters['rsi_sell']} AND "
              f"Stochastic > {strategy.parameters['stoch_sell']} AND Volume > "
              f"{strategy.parameters['volume_multiplier']}x average")
    else:
        print("❌ No results from custom strategy")

def example_multi_timeframe_strategy():
    """Example: Multi-Timeframe Strategy"""
    print("\n" + "="*60)
    print("EXAMPLE 6: Multi-Timeframe Strategy")
    print("="*60)
    
    class MultiTimeframeStrategy(TradingStrategy):
        """Strategy using multiple timeframes"""
        
        def __init__(self):
            super().__init__(
                name="Multi_Timeframe_Strategy",
                description="Uses higher timeframe for trend, lower for entries"
            )
            
            self.parameters = {
                'higher_tf': '1d',
                'lower_tf': '4h',
                'trend_sma': 50,
                'entry_sma': 20
            }
            
            self.fetcher = MarketDataFetcher()
            self.analyzer = TechnicalAnalyzer()
        
        def generate_signal(self, symbol: str, df: pd.DataFrame,
                           indicators: Dict[str, Any]) -> Dict[str, Any]:
            # This is a simplified version
            # In full implementation, you would fetch both timeframes
            
            signal = {
                'symbol': symbol,
                'timestamp': datetime.now().isoformat(),
                'action': 'HOLD',
                'confidence': 0.5,
                'reasons': []
            }
            
            # Simplified logic using current timeframe only
            current_price = df['Close'].iloc[-1]
            ma_data = indicators.get('moving_averages', {})
            
            sma_fast = ma_data.get(f'sma_{self.parameters["entry_sma"]}', 0)
            sma_slow = ma_data.get(f'sma_{self.parameters["trend_sma"]}', 0)
            
            if sma_fast and sma_slow:
                # Higher timeframe trend (simplified)
                if current_price > sma_slow:
                    # Uptrend
                    if current_price > sma_fast:
                        signal['action'] = 'BUY'
                        signal['confidence'] = 0.7
                        signal['reasons'] = [
                            f"Price above {self.parameters['entry_sma']}-period SMA",
                            f"In uptrend (above {self.parameters['trend_sma']}-period SMA)"
                        ]
                
                else:
                    # Downtrend
                    if current_price < sma_fast:
                        signal['action'] = 'SELL'
                        signal['confidence'] = 0.7
                        signal['reasons'] = [
                            f"Price below {self.parameters['entry_sma']}-period SMA",
                            f"In downtrend (below {self.parameters['trend_sma']}-period SMA)"
                        ]
            
            return signal
    
    # Test multi-timeframe strategy
    print("\n🔍 Testing multi-timeframe strategy on EUR/USD...")
    strategy = MultiTimeframeStrategy()
    results = strategy.backtest('EURUSD=X', '2023-01-01', '2023-12-31')
    
    if results:
        print(f"\n📊 Multi-Timeframe Strategy Performance:")
        print(f"   Total Return: {results.get('total_return_percent', 0):.1f}%")
        print(f"   Total Trades: {results.get('total_trades', 0)}")
        print(f"   Win Rate: {results.get('win_rate', 0):.1f}%")
        
        print(f"\n🎯 Strategy Logic:")
        print(f"   Uses {strategy.parameters['higher_tf']} for trend direction")
        print(f"   Uses {strategy.parameters['lower_tf']} for entry signals")
        print(f"   Trend SMA: {strategy.parameters['trend_sma']} periods")
        print(f"   Entry SMA: {strategy.parameters['entry_sma']} periods")
    else:
        print("❌ No results from multi-timeframe strategy")

def main():
    """Run all custom strategy examples"""
    print("🚀 TRADING ANALYSIS TOOL - CUSTOM STRATEGIES EXAMPLES")
    print("="*60)
    
    try:
        # Run each example
        example_rsi_macd_strategy()
        example_bollinger_band_strategy()
        example_strategy_comparison()
        example_strategy_optimization()
        example_custom_strategy_creation()
        example_multi_timeframe_strategy()
        
        print("\n" + "="*60)
        print("✅ All custom strategy examples completed!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Error running strategy examples: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
