# -*- coding: utf-8 -*-
"""
Visualization Module
Create charts and visualizations for market data
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import mplfinance as mpf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import warnings

from config import Config
from utils.logger import setup_logger

logger = setup_logger(__name__)

class MarketVisualizer:
    """Create visualizations for market analysis"""
    
    def __init__(self):
        """Initialize market visualizer"""
        warnings.filterwarnings('ignore')
        plt.style.use('seaborn-v0_8-darkgrid')
        self.figsize = (14, 8)
        logger.info("Market Visualizer initialized")
    
    def plot_candlestick(self, df: pd.DataFrame, symbol: str, 
                        timeframe: str, save_path: str = None):
        """
        Plot candlestick chart
        
        Parameters:
            df (pd.DataFrame): OHLCV data
            symbol (str): Trading symbol
            timeframe (str): Timeframe
            save_path (str): Path to save the plot
        """
        try:
            if df is None or df.empty:
                logger.warning("No data to plot")
                return
            
            logger.info(f"Plotting candlestick chart for {symbol} ({timeframe})")
            
            # Create figure
            fig, axes = plt.subplots(2, 1, figsize=self.figsize, 
                                   gridspec_kw={'height_ratios': [3, 1]})
            
            # Plot candlesticks
            ax1 = axes[0]
            self._plot_candlesticks(ax1, df, symbol)
            
            # Plot volume
            ax2 = axes[1]
            self._plot_volume(ax2, df)
            
            # Add title and labels
            plt.suptitle(f'{symbol} - {timeframe} Chart', fontsize=16, fontweight='bold')
            
            # Adjust layout
            plt.tight_layout()
            
            # Save or show
            if save_path:
                plt.savefig(save_path, dpi=150, bbox_inches='tight')
                logger.info(f"Chart saved to {save_path}")
            else:
                plt.show()
            
            plt.close()
            
        except Exception as e:
            logger.error(f"Error plotting candlestick chart: {e}")
            plt.close()
    
    def plot_with_indicators(self, df: pd.DataFrame, symbol: str, 
                           timeframe: str, indicators: Dict[str, Any],
                           save_path: str = None):
        """
        Plot chart with technical indicators
        
        Parameters:
            df (pd.DataFrame): OHLCV data
            symbol (str): Trading symbol
            timeframe (str): Timeframe
            indicators (Dict[str, Any]): Technical indicators
            save_path (str): Path to save the plot
        """
        try:
            if df is None or df.empty:
                logger.warning("No data to plot")
                return
            
            logger.info(f"Plotting chart with indicators for {symbol}")
            
            # Create figure with subplots
            fig = plt.figure(figsize=(16, 12))
            gs = fig.add_gridspec(4, 1, hspace=0.05)
            
            # Main price chart
            ax1 = fig.add_subplot(gs[0:2, 0])
            self._plot_candlesticks(ax1, df, symbol, show_volume=False)
            
            # Add indicators to main chart
            self._add_indicators_to_chart(ax1, df, indicators)
            
            # RSI subplot
            ax2 = fig.add_subplot(gs[2, 0], sharex=ax1)
            self._plot_rsi(ax2, df, indicators)
            
            # Volume subplot
            ax3 = fig.add_subplot(gs[3, 0], sharex=ax1)
            self._plot_volume(ax3, df)
            
            # Add title
            plt.suptitle(f'{symbol} - Technical Analysis ({timeframe})', 
                        fontsize=16, fontweight='bold')
            
            # Adjust layout
            plt.tight_layout()
            
            # Save or show
            if save_path:
                plt.savefig(save_path, dpi=150, bbox_inches='tight')
                logger.info(f"Indicator chart saved to {save_path}")
            else:
                plt.show()
            
            plt.close()
            
        except Exception as e:
            logger.error(f"Error plotting indicator chart: {e}")
            plt.close()
    
    def plot_volume(self, df: pd.DataFrame, symbol: str, 
                   timeframe: str, save_path: str = None):
        """
        Plot volume chart
        
        Parameters:
            df (pd.DataFrame): OHLCV data
            symbol (str): Trading symbol
            timeframe (str): Timeframe
            save_path (str): Path to save the plot
        """
        try:
            if df is None or df.empty or 'Volume' not in df.columns:
                logger.warning("No volume data to plot")
                return
            
            logger.info(f"Plotting volume chart for {symbol}")
            
            fig, ax = plt.subplots(figsize=self.figsize)
            
            # Plot volume bars
            colors = ['green' if df['Close'].iloc[i] >= df['Open'].iloc[i] 
                     else 'red' for i in range(len(df))]
            
            ax.bar(df.index, df['Volume'], color=colors, alpha=0.7)
            
            # Add volume moving average
            if len(df) >= 20:
                volume_sma = df['Volume'].rolling(window=20).mean()
                ax.plot(df.index, volume_sma, color='blue', 
                       linewidth=2, label='20-period SMA')
            
            # Customize
            ax.set_title(f'{symbol} - Volume Analysis ({timeframe})', 
                        fontsize=14, fontweight='bold')
            ax.set_ylabel('Volume')
            ax.grid(True, alpha=0.3)
            ax.legend()
            
            # Format x-axis
            self._format_xaxis(ax, df)
            
            plt.tight_layout()
            
            # Save or show
            if save_path:
                plt.savefig(save_path, dpi=150, bbox_inches='tight')
                logger.info(f"Volume chart saved to {save_path}")
            else:
                plt.show()
            
            plt.close()
            
        except Exception as e:
            logger.error(f"Error plotting volume chart: {e}")
            plt.close()
    
    def plot_all(self, df: pd.DataFrame, symbol: str, 
                timeframe: str, indicators: Dict[str, Any],
                save_path: str = None):
        """
        Plot comprehensive analysis chart
        
        Parameters:
            df (pd.DataFrame): OHLCV data
            symbol (str): Trading symbol
            timeframe (str): Timeframe
            indicators (Dict[str, Any]): Technical indicators
            save_path (str): Path to save the plot
        """
        try:
            if df is None or df.empty:
                logger.warning("No data to plot")
                return
            
            logger.info(f"Plotting comprehensive chart for {symbol}")
            
            # Create figure with multiple subplots
            fig = plt.figure(figsize=(18, 16))
            gs = fig.add_gridspec(6, 1, hspace=0.05)
            
            # 1. Price with moving averages
            ax1 = fig.add_subplot(gs[0:2, 0])
            self._plot_price_with_mas(ax1, df, symbol, indicators)
            
            # 2. MACD
            ax2 = fig.add_subplot(gs[2, 0], sharex=ax1)
            self._plot_macd(ax2, df, indicators)
            
            # 3. RSI
            ax3 = fig.add_subplot(gs[3, 0], sharex=ax1)
            self._plot_rsi(ax3, df, indicators)
            
            # 4. Stochastic
            ax4 = fig.add_subplot(gs[4, 0], sharex=ax1)
            self._plot_stochastic(ax4, df, indicators)
            
            # 5. Volume
            ax5 = fig.add_subplot(gs[5, 0], sharex=ax1)
            self._plot_volume(ax5, df)
            
            # Add main title
            plt.suptitle(f'{symbol} - Comprehensive Analysis ({timeframe})', 
                        fontsize=18, fontweight='bold', y=0.98)
            
            # Adjust layout
            plt.tight_layout()
            
            # Save or show
            if save_path:
                plt.savefig(save_path, dpi=150, bbox_inches='tight')
                logger.info(f"Comprehensive chart saved to {save_path}")
            else:
                plt.show()
            
            plt.close()
            
        except Exception as e:
            logger.error(f"Error plotting comprehensive chart: {e}")
            plt.close()
    
    def plot_comparison(self, symbols: List[str], period: str = '1mo',
                       save_path: str = None):
        """
        Plot comparison of multiple symbols
        
        Parameters:
            symbols (List[str]): List of symbols
            period (str): Time period
            save_path (str): Path to save the plot
        """
        try:
            import yfinance as yf
            
            logger.info(f"Plotting comparison for {len(symbols)} symbols")
            
            fig, axes = plt.subplots(len(symbols), 1, 
                                   figsize=(14, 4 * len(symbols)),
                                   sharex=True)
            
            if len(symbols) == 1:
                axes = [axes]
            
            for idx, symbol in enumerate(symbols):
                ax = axes[idx]
                
                # Fetch data
                ticker = yf.Ticker(symbol)
                df = ticker.history(period=period)
                
                if not df.empty:
                    # Plot normalized returns
                    returns = (df['Close'] / df['Close'].iloc[0] - 1) * 100
                    
                    ax.plot(df.index, returns, linewidth=2, label=symbol)
                    ax.fill_between(df.index, returns, 0, 
                                   alpha=0.2, where=returns >= 0)
                    ax.fill_between(df.index, returns, 0, 
                                   alpha=0.2, where=returns < 0, color='red')
                    
                    # Add current return as text
                    current_return = returns.iloc[-1]
                    color = 'green' if current_return >= 0 else 'red'
                    ax.text(0.02, 0.95, f'{current_return:.1f}%', 
                           transform=ax.transAxes,
                           fontsize=12, fontweight='bold',
                           color=color, verticalalignment='top')
                
                # Customize subplot
                ax.set_ylabel('Return (%)')
                ax.grid(True, alpha=0.3)
                ax.legend(loc='upper left')
            
            # Add title
            plt.suptitle(f'Performance Comparison ({period})', 
                        fontsize=16, fontweight='bold')
            
            # Format x-axis
            self._format_xaxis(axes[-1], df)
            
            plt.tight_layout()
            
            # Save or show
            if save_path:
                plt.savefig(save_path, dpi=150, bbox_inches='tight')
                logger.info(f"Comparison chart saved to {save_path}")
            else:
                plt.show()
            
            plt.close()
            
        except Exception as e:
            logger.error(f"Error plotting comparison: {e}")
            plt.close()
    
    def plot_mplfinance(self, df: pd.DataFrame, symbol: str, 
                       timeframe: str, indicators: Dict[str, Any] = None,
                       save_path: str = None):
        """
        Plot using mplfinance library
        
        Parameters:
            df (pd.DataFrame): OHLCV data
            symbol (str): Trading symbol
            timeframe (str): Timeframe
            indicators (Dict[str, Any]): Technical indicators
            save_path (str): Path to save the plot
        """
        try:
            logger.info(f"Plotting mplfinance chart for {symbol}")
            
            # Create style
            mc = mpf.make_marketcolors(
                up='green', down='red',
                edge={'up': 'green', 'down': 'red'},
                wick={'up': 'green', 'down': 'red'},
                volume={'up': 'green', 'down': 'red'}
            )
            
            style = mpf.make_mpf_style(
                marketcolors=mc,
                gridstyle='--',
                gridcolor='gray',
                rc={'font.size': 10}
            )
            
            # Prepare additional plots
            add_plots = []
            
            # Add moving averages if available
            if indicators and 'moving_averages' in indicators:
                ma_data = indicators['moving_averages']
                
                # Add SMA 20
                if 'sma_20' in ma_data:
                    sma_20 = pd.Series([ma_data['sma_20']] * len(df), index=df.index)
                    ap_sma20 = mpf.make_addplot(sma_20, color='blue', width=1.5)
                    add_plots.append(ap_sma20)
                
                # Add SMA 50
                if 'sma_50' in ma_data:
                    sma_50 = pd.Series([ma_data['sma_50']] * len(df), index=df.index)
                    ap_sma50 = mpf.make_addplot(sma_50, color='orange', width=1.5)
                    add_plots.append(ap_sma50)
            
            # Plot
            fig, axes = mpf.plot(
                df,
                type='candle',
                style=style,
                title=f'{symbol} - {timeframe}',
                ylabel='Price ($)',
                volume=True,
                addplot=add_plots if add_plots else None,
                figsize=self.figsize,
                returnfig=True
            )
            
            # Save or show
            if save_path:
                plt.savefig(save_path, dpi=150, bbox_inches='tight')
                logger.info(f"mplfinance chart saved to {save_path}")
            else:
                plt.show()
            
            plt.close()
            
        except Exception as e:
            logger.error(f"Error plotting with mplfinance: {e}")
            plt.close()
    
    def _plot_candlesticks(self, ax, df: pd.DataFrame, symbol: str, 
                          show_volume: bool = False):
        """Plot candlestick chart"""
        # Calculate width based on timeframe
        if len(df) > 100:
            width = 0.8
        elif len(df) > 50:
            width = 1.0
        else:
            width = 1.5
        
        # Create OHLC arrays
        dates = mdates.date2num(df.index)
        opens = df['Open'].values
        highs = df['High'].values
        lows = df['Low'].values
        closes = df['Close'].values
        
        # Plot candlesticks
        for i in range(len(df)):
            color = 'green' if closes[i] >= opens[i] else 'red'
            
            # Plot body
            ax.bar(dates[i], abs(closes[i] - opens[i]), 
                  bottom=min(opens[i], closes[i]),
                  width=width, color=color, edgecolor=color)
            
            # Plot wicks
            ax.plot([dates[i], dates[i]], [lows[i], highs[i]], 
                   color=color, linewidth=1)
        
        # Add moving averages
        if len(df) >= 20:
            sma_20 = df['Close'].rolling(window=20).mean()
            ax.plot(dates, sma_20.values, color='blue', 
                   linewidth=2, label='SMA 20', alpha=0.8)
        
        if len(df) >= 50:
            sma_50 = df['Close'].rolling(window=50).mean()
            ax.plot(dates, sma_50.values, color='orange', 
                   linewidth=2, label='SMA 50', alpha=0.8)
        
        # Customize
        ax.set_ylabel('Price ($)', fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.legend(loc='upper left')
        
        # Format x-axis
        self._format_xaxis(ax, df)
    
    def _plot_volume(self, ax, df: pd.DataFrame):
        """Plot volume bars"""
        if 'Volume' not in df.columns:
            return
        
        # Colors based on price action
        colors = ['green' if df['Close'].iloc[i] >= df['Open'].iloc[i] 
                 else 'red' for i in range(len(df))]
        
        # Convert dates
        dates = mdates.date2num(df.index)
        
        # Plot volume bars
        ax.bar(dates, df['Volume'].values, color=colors, alpha=0.7)
        
        # Add volume moving average
        if len(df) >= 20:
            volume_sma = df['Volume'].rolling(window=20).mean()
            ax.plot(dates, volume_sma.values, color='blue', 
                   linewidth=2, label='Volume SMA 20')
        
        # Customize
        ax.set_ylabel('Volume', fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.legend(loc='upper left')
        
        # Hide x-axis labels for non-bottom subplots
        if ax.get_subplotspec().is_last_row():
            self._format_xaxis(ax, df)
        else:
            ax.set_xticklabels([])
    
    def _add_indicators_to_chart(self, ax, df: pd.DataFrame, 
                                indicators: Dict[str, Any]):
        """Add technical indicators to chart"""
        dates = mdates.date2num(df.index)
        
        # Add Bollinger Bands if available
        if 'bollinger_bands' in indicators:
            bb = indicators['bollinger_bands']
            
            # Create arrays for the entire period (simplified)
            upper = np.full(len(df), bb.get('upper', 0))
            middle = np.full(len(df), bb.get('middle', 0))
            lower = np.full(len(df), bb.get('lower', 0))
            
            ax.plot(dates, upper, color='purple', linewidth=1, 
                   alpha=0.7, label='BB Upper')
            ax.plot(dates, middle, color='purple', linewidth=1, 
                   alpha=0.7, label='BB Middle', linestyle='--')
            ax.plot(dates, lower, color='purple', linewidth=1, 
                   alpha=0.7, label='BB Lower')
        
        # Add support/resistance levels
        current_price = df['Close'].iloc[-1]
        
        # Simple support/resistance based on recent highs/lows
        if len(df) >= 20:
            recent_high = df['High'].tail(20).max()
            recent_low = df['Low'].tail(20).min()
            
            ax.axhline(y=recent_high, color='red', linestyle='--', 
                      alpha=0.5, label='Resistance')
            ax.axhline(y=recent_low, color='green', linestyle='--', 
                      alpha=0.5, label='Support')
        
        # Update legend
        handles, labels = ax.get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        ax.legend(by_label.values(), by_label.keys(), 
                 loc='upper left', fontsize=9)
    
    def _plot_rsi(self, ax, df: pd.DataFrame, indicators: Dict[str, Any]):
        """Plot RSI indicator"""
        # Calculate RSI if not in indicators
        rsi_values = None
        
        if 'rsi' in indicators:
            # Create array for the entire period (simplified)
            rsi_values = np.full(len(df), indicators['rsi'])
        else:
            # Calculate RSI
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi_values = 100 - (100 / (1 + rs))
        
        dates = mdates.date2num(df.index)
        
        # Plot RSI
        ax.plot(dates, rsi_values, color='blue', linewidth=2)
        
        # Add overbought/oversold lines
        ax.axhline(y=70, color='red', linestyle='--', alpha=0.7)
        ax.axhline(y=30, color='green', linestyle='--', alpha=0.7)
        
        # Fill between lines
        ax.fill_between(dates, 70, rsi_values, where=rsi_values >= 70,
                       color='red', alpha=0.2)
        ax.fill_between(dates, 30, rsi_values, where=rsi_values <= 30,
                       color='green', alpha=0.2)
        
        # Customize
        ax.set_ylabel('RSI', fontsize=12)
        ax.set_ylim(0, 100)
        ax.grid(True, alpha=0.3)
        
        # Hide x-axis labels for non-bottom subplots
        if not ax.get_subplotspec().is_last_row():
            ax.set_xticklabels([])
    
    def _plot_macd(self, ax, df: pd.DataFrame, indicators: Dict[str, Any]):
        """Plot MACD indicator"""
        # Calculate MACD if not in indicators
        macd_line = None
        signal_line = None
        histogram = None
        
        if 'macd' in indicators:
            macd_data = indicators['macd']
            if isinstance(macd_data, tuple) and len(macd_data) == 3:
                # Create arrays for the entire period (simplified)
                macd_line = np.full(len(df), macd_data[0])
                signal_line = np.full(len(df), macd_data[1])
                histogram = np.full(len(df), macd_data[2])
        
        if macd_line is None:
            # Calculate MACD
            exp1 = df['Close'].ewm(span=12, adjust=False).mean()
            exp2 = df['Close'].ewm(span=26, adjust=False).mean()
            macd_line = exp1 - exp2
            signal_line = macd_line.ewm(span=9, adjust=False).mean()
            histogram = macd_line - signal_line
        
        dates = mdates.date2num(df.index)
        
        # Plot MACD components
        ax.plot(dates, macd_line, color='blue', linewidth=1.5, label='MACD')
        ax.plot(dates, signal_line, color='red', linewidth=1.5, label='Signal')
        
        # Plot histogram
        colors = ['green' if h >= 0 else 'red' for h in histogram]
        ax.bar(dates, histogram, color=colors, alpha=0.5, width=1)
        
        # Zero line
        ax.axhline(y=0, color='black', linestyle='-', alpha=0.5)
        
        # Customize
        ax.set_ylabel('MACD', fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.legend(loc='upper left', fontsize=9)
        
        # Hide x-axis labels for non-bottom subplots
        if not ax.get_subplotspec().is_last_row():
            ax.set_xticklabels([])
    
    def _plot_stochastic(self, ax, df: pd.DataFrame, indicators: Dict[str, Any]):
        """Plot Stochastic oscillator"""
        # Calculate Stochastic if not in indicators
        k_values = None
        d_values = None
        
        if 'stochastic' in indicators:
            stochastic_data = indicators['stochastic']
            if isinstance(stochastic_data, tuple) and len(stochastic_data) == 2:
                # Create arrays for the entire period (simplified)
                k_values = np.full(len(df), stochastic_data[0])
                d_values = np.full(len(df), stochastic_data[1])
        
        if k_values is None:
            # Calculate Stochastic
            low_min = df['Low'].rolling(window=14).min()
            high_max = df['High'].rolling(window=14).max()
            k_values = 100 * ((df['Close'] - low_min) / (high_max - low_min))
            d_values = k_values.rolling(window=3).mean()
        
        dates = mdates.date2num(df.index)
        
        # Plot Stochastic
        ax.plot(dates, k_values, color='blue', linewidth=2, label='%K')
        ax.plot(dates, d_values, color='red', linewidth=2, label='%D', linestyle='--')
        
        # Add overbought/oversold lines
        ax.axhline(y=80, color='red', linestyle='--', alpha=0.7)
        ax.axhline(y=20, color='green', linestyle='--', alpha=0.7)
        
        # Fill between lines
        ax.fill_between(dates, 80, k_values, where=k_values >= 80,
                       color='red', alpha=0.2)
        ax.fill_between(dates, 20, k_values, where=k_values <= 20,
                       color='green', alpha=0.2)
        
        # Customize
        ax.set_ylabel('Stochastic', fontsize=12)
        ax.set_ylim(0, 100)
        ax.grid(True, alpha=0.3)
        ax.legend(loc='upper left', fontsize=9)
        
        # Hide x-axis labels for non-bottom subplots
        if not ax.get_subplotspec().is_last_row():
            ax.set_xticklabels([])
    
    def _plot_price_with_mas(self, ax, df: pd.DataFrame, symbol: str,
                            indicators: Dict[str, Any]):
        """Plot price with multiple moving averages"""
        # Plot candlesticks
        self._plot_candlesticks(ax, df, symbol, show_volume=False)
        
        # Add additional moving averages from indicators
        dates = mdates.date2num(df.index)
        
        if indicators and 'moving_averages' in indicators:
            ma_data = indicators['moving_averages']
            
            # Plot EMA 9
            if 'ema_9' in ma_data:
                ema_9 = np.full(len(df), ma_data['ema_9'])
                ax.plot(dates, ema_9, color='cyan', linewidth=2, 
                       label='EMA 9', alpha=0.8)
            
            # Plot EMA 21
            if 'ema_21' in ma_data:
                ema_21 = np.full(len(df), ma_data['ema_21'])
                ax.plot(dates, ema_21, color='magenta', linewidth=2, 
                       label='EMA 21', alpha=0.8)
            
            # Update legend
            handles, labels = ax.get_legend_handles_labels()
            by_label = dict(zip(labels, handles))
            ax.legend(by_label.values(), by_label.keys(), 
                     loc='upper left', fontsize=9)
    
    def _format_xaxis(self, ax, df: pd.DataFrame):
        """Format x-axis for time series"""
        if len(df) == 0:
            return
        
        # Determine date format based on timeframe
        date_range = (df.index[-1] - df.index[0]).days
        
        if date_range > 365:  # More than 1 year
            date_format = '%Y'
            locator = mdates.YearLocator()
        elif date_range > 30:  # More than 1 month
            date_format = '%b %Y'
            locator = mdates.MonthLocator()
        elif date_range > 7:  # More than 1 week
            date_format = '%d %b'
            locator = mdates.DayLocator(interval=max(1, date_range // 7))
        else:  # Less than 1 week
            date_format = '%d %b %H:%M'
            locator = mdates.DayLocator()
        
        # Apply formatting
        ax.xaxis.set_major_locator(locator)
        ax.xaxis.set_major_formatter(mdates.DateFormatter(date_format))
        
        # Rotate dates for readability
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
    
    def create_dashboard(self, analyses: Dict[str, Any], 
                        save_path: str = 'dashboard.png'):
        """
        Create a comprehensive dashboard
        
        Parameters:
            analyses (Dict[str, Any]): All analysis results
            save_path (str): Path to save the dashboard
        """
        try:
            logger.info("Creating comprehensive dashboard")
            
            # Create figure with multiple sections
            fig = plt.figure(figsize=(20, 24))
            
            # Title
            fig.suptitle('Trading Analysis Dashboard', fontsize=24, 
                        fontweight='bold', y=0.98)
            
            # Create grid for different sections
            gs = fig.add_gridspec(4, 3, hspace=0.3, wspace=0.3)
            
            # 1. Price Chart (top left, spans 2 columns)
            ax1 = fig.add_subplot(gs[0, 0:2])
            if 'price_data' in analyses:
                self._plot_candlesticks(ax1, analyses['price_data'], 
                                       analyses.get('symbol', ''))
            
            # 2. Key Metrics (top right)
            ax2 = fig.add_subplot(gs[0, 2])
            self._plot_metrics(ax2, analyses)
            
            # 3. Technical Indicators (middle left)
            ax3 = fig.add_subplot(gs[1, 0])
            self._plot_technical_summary(ax3, analyses)
            
            # 4. AI Signal (middle center)
            ax4 = fig.add_subplot(gs[1, 1])
            self._plot_ai_signal(ax4, analyses)
            
            # 5. Whale Activity (middle right)
            ax5 = fig.add_subplot(gs[1, 2])
            self._plot_whale_activity(ax5, analyses)
            
            # 6. Price Action Analysis (bottom left)
            ax6 = fig.add_subplot(gs[2, 0])
            self._plot_price_action(ax6, analyses)
            
            # 7. Risk Analysis (bottom center)
            ax7 = fig.add_subplot(gs[2, 1])
            self._plot_risk_analysis(ax7, analyses)
            
            # 8. Market Sentiment (bottom right)
            ax8 = fig.add_subplot(gs[2, 2])
            self._plot_market_sentiment(ax8, analyses)
            
            # 9. Recommendation (bottom row, spans 3 columns)
            ax9 = fig.add_subplot(gs[3, :])
            self._plot_recommendation(ax9, analyses)
            
            # Adjust layout
            plt.tight_layout()
            
            # Save dashboard
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            logger.info(f"Dashboard saved to {save_path}")
            
            plt.close()
            
        except Exception as e:
            logger.error(f"Error creating dashboard: {e}")
            plt.close()
    
    def _plot_metrics(self, ax, analyses: Dict[str, Any]):
        """Plot key metrics"""
        ax.axis('off')
        
        metrics = analyses.get('metrics', {})
        text = "KEY METRICS\n\n"
        
        for key, value in metrics.items():
            text += f"{key}: {value}\n"
        
        ax.text(0.05, 0.95, text, transform=ax.transAxes,
               fontsize=11, verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    def _plot_technical_summary(self, ax, analyses: Dict[str, Any]):
        """Plot technical summary"""
        ax.axis('off')
        
        indicators = analyses.get('indicators', {})
        text = "TECHNICAL SUMMARY\n\n"
        
        # Add key indicators
        key_indicators = ['rsi', 'macd', 'adx', 'trend']
        for indicator in key_indicators:
            if indicator in indicators:
                value = indicators[indicator]
                text += f"{indicator.upper()}: {value}\n"
        
        ax.text(0.05, 0.95, text, transform=ax.transAxes,
               fontsize=10, verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))
    
    def _plot_ai_signal(self, ax, analyses: Dict[str, Any]):
        """Plot AI signal"""
        ax.axis('off')
        
        signal = analyses.get('signal', {})
        action = signal.get('action', 'HOLD')
        confidence = signal.get('confidence', 0)
        
        # Color based on action
        if action == 'BUY':
            color = 'green'
        elif action == 'SELL':
            color = 'red'
        else:
            color = 'gray'
        
        text = f"AI SIGNAL\n\n{action}\n\nConfidence: {confidence:.1%}"
        
        ax.text(0.5, 0.5, text, transform=ax.transAxes,
               fontsize=14, fontweight='bold',
               color=color, ha='center', va='center',
               bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.5))
    
    def _plot_whale_activity(self, ax, analyses: Dict[str, Any]):
        """Plot whale activity"""
        ax.axis('off')
        
        whale_data = analyses.get('whale_data', {})
        text = "WHALE ACTIVITY\n\n"
        
        if whale_data:
            text += f"Transactions: {whale_data.get('transaction_count', 0)}\n"
            text += f"Total Volume: ${whale_data.get('total_volume', 0):,.0f}\n"
            text += f"Net Flow: ${whale_data.get('net_flow', 0):,.0f}"
        
        ax.text(0.05, 0.95, text, transform=ax.transAxes,
               fontsize=10, verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.5))
    
    def _plot_price_action(self, ax, analyses: Dict[str, Any]):
        """Plot price action analysis"""
        ax.axis('off')
        
        pa_analysis = analyses.get('price_action', {})
        text = "PRICE ACTION\n\n"
        
        if pa_analysis:
            text += f"Structure: {pa_analysis.get('market_structure', 'N/A')}\n"
            text += f"FVG Count: {len(pa_analysis.get('fair_value_gaps', []))}\n"
            text += f"OB Count: {len(pa_analysis.get('order_blocks', []))}"
        
        ax.text(0.05, 0.95, text, transform=ax.transAxes,
               fontsize=10, verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.5))
    
    def _plot_risk_analysis(self, ax, analyses: Dict[str, Any]):
        """Plot risk analysis"""
        ax.axis('off')
        
        signal = analyses.get('signal', {})
        text = "RISK ANALYSIS\n\n"
        
        if signal:
            text += f"Stop Loss: ${signal.get('stop_loss', 0):.2f}\n"
            text += f"Take Profit: ${signal.get('take_profit', [0])[0]:.2f}\n"
            text += f"Risk/Reward: 1:{signal.get('risk_reward', 0):.1f}"
        
        ax.text(0.05, 0.95, text, transform=ax.transAxes,
               fontsize=10, verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='lightcoral', alpha=0.5))
    
    def _plot_market_sentiment(self, ax, analyses: Dict[str, Any]):
        """Plot market sentiment"""
        ax.axis('off')
        
        indicators = analyses.get('indicators', {})
        text = "MARKET SENTIMENT\n\n"
        
        # Determine sentiment from indicators
        rsi = indicators.get('rsi', 50)
        
        if rsi > 70:
            sentiment = "OVERBOUGHT"
            color = "red"
        elif rsi < 30:
            sentiment = "OVERSOLD"
            color = "green"
        else:
            sentiment = "NEUTRAL"
            color = "gray"
        
        text += f"Sentiment: {sentiment}\n"
        text += f"RSI: {rsi:.1f}"
        
        ax.text(0.05, 0.95, text, transform=ax.transAxes,
               fontsize=10, verticalalignment='top', color=color,
               bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.5))
    
    def _plot_recommendation(self, ax, analyses: Dict[str, Any]):
        """Plot final recommendation"""
        ax.axis('off')
        
        signal = analyses.get('signal', {})
        text = "FINAL RECOMMENDATION\n\n"
        
        if signal:
            action = signal.get('action', 'HOLD')
            reasons = signal.get('reasons', [])
            
            text += f"ACTION: {action}\n\n"
            text += "REASONS:\n"
            
            for reason in reasons[:5]:  # Show first 5 reasons
                text += f"• {reason}\n"
        
        ax.text(0.05, 0.95, text, transform=ax.transAxes,
               fontsize=12, verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))

def test_visualizer():
    """Test visualizer"""
    import yfinance as yf
    from modules.technical_analyzer import TechnicalAnalyzer
    
    visualizer = MarketVisualizer()
    
    print("Testing Market Visualizer...")
    
    # Get sample data
    ticker = yf.Ticker('AAPL')
    df = ticker.history(period='1mo', interval='1d')
    
    if not df.empty:
        # Calculate indicators
        analyzer = TechnicalAnalyzer()
        indicators = analyzer.calculate_indicators(df)
        
        # Test different plots
        print("1. Testing candlestick chart...")
        visualizer.plot_candlestick(df, 'AAPL', '1d')
        
        print("2. Testing chart with indicators...")
        visualizer.plot_with_indicators(df, 'AAPL', '1d', indicators)
        
        print("3. Testing volume chart...")
        visualizer.plot_volume(df, 'AAPL', '1d')
        
        print("4. Testing mplfinance chart...")
        visualizer.plot_mplfinance(df, 'AAPL', '1d', indicators)
        
        print("5. Testing comparison chart...")
        visualizer.plot_comparison(['AAPL', 'MSFT', 'GOOGL'], period='1mo')

if __name__ == "__main__":
    test_visualizer()
