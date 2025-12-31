#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main execution file for Trading Analysis Tool
Advanced Trading Analysis Tool - Main File
"""

import sys
import os
from pathlib import Path

# Add module paths to sys.path
sys.path.append(str(Path(__file__).parent))

from modules.watchlist_manager import WatchlistManager
from modules.data_fetcher import MarketDataFetcher
from modules.technical_analyzer import TechnicalAnalyzer
from modules.ai_signal_generator import AISignalGenerator
from modules.whale_tracker import WhaleTracker
from modules.price_action_analyzer import PriceActionAnalyzer
from modules.visualizer import MarketVisualizer
from utils.logger import setup_logger

logger = setup_logger(__name__)

class AdvancedTradingTool:
    """Main Trading Analysis Tool Class"""
    
    def __init__(self):
        """Initialize all modules"""
        logger.info("Initializing Advanced Trading Tool...")
        
        self.watchlist_manager = WatchlistManager()
        self.data_fetcher = MarketDataFetcher()
        self.technical_analyzer = TechnicalAnalyzer()
        self.ai_signal = AISignalGenerator()
        self.whale_tracker = WhaleTracker()
        self.price_action = PriceActionAnalyzer()
        self.visualizer = MarketVisualizer()
        
        self.market_types = {
            '1': 'crypto',
            '2': 'forex', 
            '3': 'stock',
            '4': 'all'
        }
        
        logger.info("Trading Tool initialized successfully!")
    
    def display_menu(self):
        """Display main menu"""
        print("\n" + "="*80)
        print("🛠️  ADVANCED TRADING ANALYSIS TOOL")
        print("="*80)
        print("📊 Features:")
        print("  1. 📋 Display Watchlists (Crypto, Forex, US Stocks)")
        print("  2. 🔍 Extract Complete Asset Information")
        print("  3. 🤖 Generate Trading Signals with AI")
        print("  4. 📈 Technical Analysis with Indicators")
        print("  5. 🕯️ Detect Candlestick Patterns")
        print("  6. 🐋 Track Whale & Wallet Activity")
        print("  7. 🎯 Price Action Analysis (ICT/SMC)")
        print("  8. 📊 Comprehensive Analysis Report")
        print("  9. 📉 Display Charts")
        print("  0. ❌ Exit")
        print("="*80)
    
    def run(self):
        """Main execution loop"""
        logger.info("Starting Advanced Trading Tool...")
        
        while True:
            try:
                self.display_menu()
                choice = input("\n🎯 Select option (0-9): ").strip()
                
                if choice == "0":
                    logger.info("User exited the application")
                    print("\n👋 Thank you! Program terminated.")
                    break
                
                elif choice == "1":
                    self._handle_watchlist()
                
                elif choice == "2":
                    self._handle_asset_info()
                
                elif choice == "3":
                    self._handle_trading_signal()
                
                elif choice == "4":
                    self._handle_technical_analysis()
                
                elif choice == "5":
                    self._handle_candlestick_patterns()
                
                elif choice == "6":
                    self._handle_whale_tracking()
                
                elif choice == "7":
                    self._handle_price_action()
                
                elif choice == "8":
                    self._handle_comprehensive_report()
                
                elif choice == "9":
                    self._handle_visualization()
                
                else:
                    print("⚠️  Invalid option! Please enter a number between 0-9.")
                    
            except KeyboardInterrupt:
                print("\n\n⚠️  Interrupted by user.")
                logger.warning("Program interrupted by user")
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}", exc_info=True)
                print(f"❌ Error: {str(e)}")
    
    def _handle_watchlist(self):
        """Handle watchlist display"""
        print("\n" + "="*60)
        print("📋 Display Watchlists")
        print("="*60)
        print("  1. Cryptocurrencies")
        print("  2. Forex Pairs")
        print("  3. US Stocks")
        print("  4. All")
        
        choice = input("\nSelect market type: ").strip()
        market = self.market_types.get(choice, 'all')
        
        self.watchlist_manager.display_watchlist(market)
    
    def _handle_asset_info(self):
        """Handle asset information extraction"""
        print("\n" + "="*60)
        print("🔍 Extract Asset Information")
        print("="*60)
        
        symbol = input("📌 Enter symbol (e.g., BTC-USD, EURUSD=X, AAPL): ").upper()
        
        # Detect market type
        if any(x in symbol for x in ['-USD', 'BTC', 'ETH', 'USDT']):
            market_type = 'crypto'
        elif '=X' in symbol or any(x in symbol for x in ['EUR', 'GBP', 'JPY', 'USD']):
            market_type = 'forex'
        else:
            market_type = 'stock'
        
        asset_info = self.data_fetcher.get_asset_info(symbol, market_type)
        
        if asset_info:
            print(f"\n✅ Information for {symbol}:")
            for key, value in asset_info.items():
                print(f"   {key}: {value}")
        else:
            print(f"❌ No information found for {symbol}!")
    
    def _handle_trading_signal(self):
        """Handle trading signal generation"""
        print("\n" + "="*60)
        print("🤖 Generate Trading Signal with AI")
        print("="*60)
        
        symbol = input("📌 Symbol: ").upper()
        timeframe = input("⏰ Timeframe (1d, 4h, 1h, 15m): ").lower() or "1d"
        
        # Get historical data
        df = self.data_fetcher.get_historical_data(symbol, timeframe)
        
        if df is None or df.empty:
            print(f"❌ Failed to get data for {symbol}!")
            return
        
        # Technical analysis
        indicators = self.technical_analyzer.calculate_indicators(df)
        
        # Generate signal
        signal = self.ai_signal.generate_signal(symbol, df, indicators)
        
        # Display results
        print(f"\n🎯 Signal for {symbol} ({timeframe}):")
        print(f"   Action: {signal['action']}")
        print(f"   Confidence: {signal['confidence']:.1%}")
        print(f"   Entry Price: ${signal['entry_price']:.2f}")
        print(f"   Stop Loss: ${signal['stop_loss']:.2f}")
        print(f"   Take Profit: {', '.join([f'${tp:.2f}' for tp in signal['take_profit']])}")
        print(f"   Risk/Reward Ratio: 1:{signal['risk_reward']:.1f}")
        
        if signal['reasons']:
            print(f"\n📋 Reasons:")
            for reason in signal['reasons']:
                print(f"   • {reason}")
    
    def _handle_technical_analysis(self):
        """Handle technical analysis"""
        print("\n" + "="*60)
        print("📈 Technical Analysis")
        print("="*60)
        
        symbol = input("📌 Symbol: ").upper()
        timeframe = input("⏰ Timeframe (1d, 4h, 1h): ").lower() or "1d"
        
        df = self.data_fetcher.get_historical_data(symbol, timeframe)
        
        if df is None or df.empty:
            print(f"❌ Failed to get data for {symbol}!")
            return
        
        indicators = self.technical_analyzer.calculate_indicators(df)
        
        print(f"\n📊 Indicators for {symbol}:")
        for indicator, value in indicators.items():
            if isinstance(value, dict):
                print(f"\n   {indicator}:")
                for k, v in value.items():
                    print(f"     {k}: {v}")
            elif isinstance(value, tuple):
                print(f"   {indicator}: {value}")
            else:
                print(f"   {indicator}: {value:.4f}")
    
    def _handle_candlestick_patterns(self):
        """Handle candlestick pattern detection"""
        print("\n" + "="*60)
        print("🕯️ Detect Candlestick Patterns")
        print("="*60)
        
        symbol = input("📌 Symbol: ").upper()
        timeframe = input("⏰ Timeframe (1d, 4h, 1h): ").lower() or "1d"
        
        df = self.data_fetcher.get_historical_data(symbol, timeframe)
        
        if df is None or df.empty:
            print(f"❌ Failed to get data for {symbol}!")
            return
        
        patterns = self.technical_analyzer.detect_candlestick_patterns(df)
        
        if patterns:
            print(f"\n🔍 Patterns detected for {symbol}:")
            for pattern in patterns:
                print(f"\n   Pattern: {pattern['name']}")
                print(f"   Type: {pattern['type']}")
                print(f"   Reliability: {pattern['reliability']}")
                print(f"   Detection Time: {pattern['time']}")
        else:
            print(f"\n⚠️ No significant candlestick patterns found.")
    
    def _handle_whale_tracking(self):
        """Handle whale activity tracking"""
        print("\n" + "="*60)
        print("🐋 Track Whale & Wallet Activity")
        print("="*60)
        
        symbol = input("📌 Crypto symbol (e.g., BTC, ETH, SOL): ").upper()
        
        whale_data = self.whale_tracker.get_whale_activity(symbol)
        
        if whale_data:
            print(f"\n🐋 Whale activity for {symbol}:")
            print(f"   Transactions (24h): {whale_data.get('transaction_count', 0)}")
            print(f"   Total Volume: ${whale_data.get('total_volume', 0):,.0f}")
            print(f"   Average Size: ${whale_data.get('average_size', 0):,.0f}")
            print(f"   24h Inflow: ${whale_data.get('inflow_24h', 0):,.0f}")
            print(f"   24h Outflow: ${whale_data.get('outflow_24h', 0):,.0f}")
            
            if 'top_wallets' in whale_data:
                print(f"\n💰 Top Wallets:")
                for i, wallet in enumerate(whale_data['top_wallets'][:3], 1):
                    print(f"   {i}. {wallet.get('address', '')[:20]}... : {wallet.get('balance', 0)} {symbol}")
        else:
            print(f"❌ No whale data found for {symbol}!")
    
    def _handle_price_action(self):
        """Handle price action analysis"""
        print("\n" + "="*60)
        print("🎯 Price Action Analysis (ICT/SMC)")
        print("="*60)
        
        symbol = input("📌 Symbol: ").upper()
        timeframe = input("⏰ Timeframe (4h, 1h, 15m): ").lower() or "4h"
        
        df = self.data_fetcher.get_historical_data(symbol, timeframe)
        
        if df is None or df.empty:
            print(f"❌ Failed to get data for {symbol}!")
            return
        
        analysis = self.price_action.analyze_ict_concepts(df)
        
        print(f"\n🎯 ICT/SMC Analysis for {symbol}:")
        
        if analysis.get('market_structure'):
            print(f"\n   Market Structure: {analysis['market_structure']}")
        
        if analysis.get('order_blocks'):
            print(f"\n   Order Blocks:")
            for ob in analysis['order_blocks'][:3]:
                print(f"     • {ob['type']} at {ob['time']}")
        
        if analysis.get('fvg'):
            print(f"\n   Fair Value Gaps:")
            for fvg in analysis['fvg'][:2]:
                print(f"     • Range: {fvg['gap_range']}")
        
        if analysis.get('liquidity_pools'):
            print(f"\n   Liquidity Pools:")
            for key, value in analysis['liquidity_pools'].items():
                print(f"     • {key}: ${value:.2f}")
    
    def _handle_comprehensive_report(self):
        """Handle comprehensive analysis report"""
        print("\n" + "="*60)
        print("📊 Comprehensive Analysis Report")
        print("="*60)
        
        symbol = input("📌 Symbol: ").upper()
        timeframe = input("⏰ Timeframe: ").lower() or "1d"
        
        print(f"\n⏳ Preparing comprehensive report for {symbol}...")
        
        # Gather all data
        df = self.data_fetcher.get_historical_data(symbol, timeframe)
        
        if df is None or df.empty:
            print(f"❌ Failed to get data for {symbol}!")
            return
        
        # Various analyses
        asset_info = self.data_fetcher.get_asset_info(symbol, 'auto')
        indicators = self.technical_analyzer.calculate_indicators(df)
        signal = self.ai_signal.generate_signal(symbol, df, indicators)
        patterns = self.technical_analyzer.detect_candlestick_patterns(df)
        ict_analysis = self.price_action.analyze_ict_concepts(df)
        
        # Display report
        print("\n" + "="*80)
        print(f"📊 Comprehensive Analysis Report - {symbol}")
        print("="*80)
        
        # Basic information
        if asset_info:
            print("\n📌 Basic Information:")
            print(f"   Current Price: ${asset_info.get('current_price', 0):.2f}")
            if 'market_cap' in asset_info:
                print(f"   Market Cap: ${asset_info.get('market_cap', 0):,.0f}")
        
        # AI Signal
        print(f"\n🤖 AI Signal:")
        print(f"   Decision: {signal.get('action', 'N/A')}")
        print(f"   Confidence: {signal.get('confidence', 0):.1%}")
        
        # Technical Analysis
        print(f"\n📈 Technical Analysis:")
        print(f"   RSI: {indicators.get('rsi', 0):.2f}")
        print(f"   MACD: {indicators.get('macd', (0,0,0))[0]:.4f}")
        
        # Candlestick Patterns
        if patterns:
            print(f"\n🕯️ Candlestick Patterns:")
            for pattern in patterns[:2]:
                print(f"   • {pattern['name']} ({pattern['type']})")
        
        # ICT Analysis
        if ict_analysis.get('market_structure'):
            print(f"\n🎯 Price Action Analysis:")
            print(f"   Structure: {ict_analysis['market_structure']}")
        
        print("\n" + "="*80)
    
    def _handle_visualization(self):
        """Handle chart visualization"""
        print("\n" + "="*60)
        print("📉 Display Charts")
        print("="*60)
        
        symbol = input("📌 Symbol: ").upper()
        timeframe = input("⏰ Timeframe (1d, 4h, 1h): ").lower() or "1d"
        
        df = self.data_fetcher.get_historical_data(symbol, timeframe)
        
        if df is None or df.empty:
            print(f"❌ Failed to get data for {symbol}!")
            return
        
        print("\n📊 Chart Types:")
        print("  1. Candlestick Chart")
        print("  2. Chart with Indicators")
        print("  3. Volume Chart")
        print("  4. All Charts")
        
        choice = input("\nSelect chart type: ").strip()
        
        if choice == "1":
            self.visualizer.plot_candlestick(df, symbol, timeframe)
        elif choice == "2":
            indicators = self.technical_analyzer.calculate_indicators(df)
            self.visualizer.plot_with_indicators(df, symbol, timeframe, indicators)
        elif choice == "3":
            self.visualizer.plot_volume(df, symbol, timeframe)
        elif choice == "4":
            indicators = self.technical_analyzer.calculate_indicators(df)
            self.visualizer.plot_all(df, symbol, timeframe, indicators)
        else:
            print("⚠️  Invalid option!")

def main():
    """Main execution function"""
    print("\n" + "="*80)
    print("🚀 Advanced Trading Analysis Tool v1.0")
    print("📅 " + __import__('datetime').datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("="*80)
    
    try:
        tool = AdvancedTradingTool()
        tool.run()
    except Exception as e:
        logger.error(f"Critical error in main: {e}", exc_info=True)
        print(f"\n❌ Critical error: {str(e)}")
        print("Please restart or contact developer.")

if __name__ == "__main__":
    main()
