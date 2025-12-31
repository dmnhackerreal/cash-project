#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Basic Usage Examples
Examples showing how to use the Trading Analysis Tool
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from modules.watchlist_manager import WatchlistManager
from modules.data_fetcher import MarketDataFetcher
from modules.technical_analyzer import TechnicalAnalyzer
from modules.ai_signal_generator import AISignalGenerator
from modules.whale_tracker import WhaleTracker
from modules.price_action_analyzer import PriceActionAnalyzer
from modules.visualizer import MarketVisualizer

def example_watchlist():
    """Example: Using Watchlist Manager"""
    print("="*60)
    print("EXAMPLE 1: Watchlist Management")
    print("="*60)
    
    # Initialize watchlist manager
    watchlist = WatchlistManager()
    
    # Display crypto watchlist
    print("\n📋 Crypto Watchlist:")
    watchlist.display_watchlist('crypto')
    
    # Add a new crypto to watchlist
    watchlist.add_to_watchlist('LTC-USD', 'Litecoin', 'crypto')
    
    # Display updated watchlist
    print("\n📋 Updated Crypto Watchlist:")
    watchlist.display_watchlist('crypto')
    
    # Get watchlist as DataFrame
    df = watchlist.get_watchlist_dataframe('crypto')
    print(f"\n📊 Watchlist DataFrame shape: {df.shape}")

def example_data_fetching():
    """Example: Fetching Market Data"""
    print("\n" + "="*60)
    print("EXAMPLE 2: Market Data Fetching")
    print("="*60)
    
    # Initialize data fetcher
    fetcher = MarketDataFetcher()
    
    # Fetch historical data
    print("\n📈 Fetching AAPL historical data...")
    df = fetcher.get_historical_data('AAPL', interval='1d', period='1mo')
    
    if df is not None:
        print(f"   Fetched {len(df)} days of data")
        print(f"   Latest close: ${df['Close'].iloc[-1]:.2f}")
        print(f"   Data columns: {list(df.columns)}")
    
    # Fetch asset information
    print("\n🔍 Fetching BTC information...")
    info = fetcher.get_asset_info('BTC-USD', 'crypto')
    
    if info:
        print(f"   Name: {info.get('name')}")
        print(f"   Price: ${info.get('current_price', 0):.2f}")
        print(f"   Market Cap: ${info.get('market_cap', 0):,.0f}")
        print(f"   24h Volume: ${info.get('volume', 0):,.0f}")
    
    # Get real-time price
    print("\n⏰ Getting real-time price for ETH...")
    price = fetcher.get_real_time_price('ETH-USD')
    if price:
        print(f"   Current price: ${price:.2f}")

def example_technical_analysis():
    """Example: Technical Analysis"""
    print("\n" + "="*60)
    print("EXAMPLE 3: Technical Analysis")
    print("="*60)
    
    # Initialize modules
    fetcher = MarketDataFetcher()
    analyzer = TechnicalAnalyzer()
    
    # Fetch data
    print("\n📊 Analyzing TSLA...")
    df = fetcher.get_historical_data('TSLA', interval='1d', period='3mo')
    
    if df is not None:
        # Calculate indicators
        indicators = analyzer.calculate_indicators(df)
        
        print(f"   Calculated {len(indicators)} indicators")
        
        # Display key indicators
        print(f"\n   Key Indicators:")
        print(f"     RSI: {indicators.get('rsi', 0):.2f}")
        print(f"     MACD: {indicators.get('macd', (0,0,0))}")
        print(f"     ADX: {indicators.get('adx', 0):.2f}")
        print(f"     Trend: {indicators.get('trend', 'N/A')}")
        
        # Detect candlestick patterns
        print(f"\n   Candlestick Patterns:")
        patterns = analyzer.detect_candlestick_patterns(df)
        
        if patterns:
            for pattern in patterns[:3]:  # Show first 3
                print(f"     • {pattern['name']} ({pattern['type']})")
        else:
            print("     No significant patterns detected")

def example_ai_signal():
    """Example: AI Signal Generation"""
    print("\n" + "="*60)
    print("EXAMPLE 4: AI Signal Generation")
    print("="*60)
    
    # Initialize modules
    fetcher = MarketDataFetcher()
    analyzer = TechnicalAnalyzer()
    ai = AISignalGenerator()
    
    # Generate signal for NVDA
    print("\n🤖 Generating AI signal for NVDA...")
    df = fetcher.get_historical_data('NVDA', interval='1d', period='1mo')
    
    if df is not None:
        indicators = analyzer.calculate_indicators(df)
        signal = ai.generate_signal('NVDA', df, indicators)
        
        print(f"\n   Signal Details:")
        print(f"     Action: {signal.get('action')}")
        print(f"     Confidence: {signal.get('confidence'):.1%}")
        print(f"     Current Price: ${signal.get('current_price', 0):.2f}")
        print(f"     Stop Loss: ${signal.get('stop_loss', 0):.2f}")
        print(f"     Take Profit: {[f'${tp:.2f}' for tp in signal.get('take_profit', [])]}")
        print(f"     Risk/Reward: 1:{signal.get('risk_reward', 0):.1f}")
        
        print(f"\n   Top Reasons:")
        for reason in signal.get('reasons', [])[:3]:
            print(f"     • {reason}")

def example_whale_tracking():
    """Example: Whale Tracking"""
    print("\n" + "="*60)
    print("EXAMPLE 5: Whale Tracking")
    print("="*60)
    
    # Initialize whale tracker
    tracker = WhaleTracker()
    
    # Track whale activity for SOL
    print("\n🐋 Tracking whale activity for SOL...")
    whale_data = tracker.get_whale_activity('SOL', hours=24)
    
    if whale_data:
        print(f"\n   Whale Activity Summary:")
        print(f"     Transactions (24h): {whale_data.get('transaction_count', 0)}")
        print(f"     Total Volume: ${whale_data.get('total_volume', 0):,.0f}")
        print(f"     Average Size: ${whale_data.get('average_size', 0):,.0f}")
        print(f"     24h Inflow: ${whale_data.get('inflow_24h', 0):,.0f}")
        print(f"     24h Outflow: ${whale_data.get('outflow_24h', 0):,.0f}")
    
    # Analyze whale sentiment
    print("\n📊 Analyzing whale sentiment for ETH...")
    sentiment = tracker.analyze_whale_sentiment('ETH', days=3)
    
    print(f"\n   Whale Sentiment:")
    print(f"     Sentiment: {sentiment.get('sentiment', 'N/A')}")
    print(f"     Score: {sentiment.get('score', 0)}")
    print(f"     Confidence: {sentiment.get('confidence', 0):.1%}")

def example_price_action():
    """Example: Price Action Analysis"""
    print("\n" + "="*60)
    print("EXAMPLE 6: Price Action Analysis")
    print("="*60)
    
    # Initialize modules
    fetcher = MarketDataFetcher()
    analyzer = PriceActionAnalyzer()
    
    # Analyze price action for EUR/USD
    print("\n🎯 Analyzing price action for EUR/USD...")
    df = fetcher.get_historical_data('EURUSD=X', interval='4h', period='1mo')
    
    if df is not None:
        # ICT Analysis
        ict_analysis = analyzer.analyze_ict_concepts(df)
        
        print(f"\n   ICT Analysis:")
        print(f"     Market Structure: {ict_analysis.get('market_structure', 'N/A')}")
        print(f"     FVGs Found: {len(ict_analysis.get('fair_value_gaps', []))}")
        print(f"     Order Blocks: {len(ict_analysis.get('order_blocks', []))}")
        
        # SMC Analysis
        smc_analysis = analyzer.analyze_smc_concepts(df)
        
        print(f"\n   SMC Analysis:")
        print(f"     Market Structure: {smc_analysis.get('market_structure', 'N/A')}")
        print(f"     Supply/Demand Zones: {len(smc_analysis.get('supply_demand_zones', []))}")

def example_visualization():
    """Example: Visualization"""
    print("\n" + "="*60)
    print("EXAMPLE 7: Visualization")
    print("="*60)
    
    # Initialize modules
    fetcher = MarketDataFetcher()
    analyzer = TechnicalAnalyzer()
    visualizer = MarketVisualizer()
    
    # Create charts for GOOGL
    print("\n📉 Creating charts for GOOGL...")
    df = fetcher.get_historical_data('GOOGL', interval='1d', period='3mo')
    
    if df is not None:
        indicators = analyzer.calculate_indicators(df)
        
        print("   1. Creating candlestick chart...")
        # visualizer.plot_candlestick(df, 'GOOGL', '1d')
        
        print("   2. Creating chart with indicators...")
        # visualizer.plot_with_indicators(df, 'GOOGL', '1d', indicators)
        
        print("   3. Creating comprehensive chart...")
        # visualizer.plot_all(df, 'GOOGL', '1d', indicators)
        
        print("   4. Creating comparison chart...")
        # visualizer.plot_comparison(['GOOGL', 'AMZN', 'META'], period='1mo')
        
        print("\n   ✓ Charts created successfully!")
        print("   Note: Charts are commented out to prevent display during testing")

def example_comprehensive_analysis():
    """Example: Comprehensive Analysis"""
    print("\n" + "="*60)
    print("EXAMPLE 8: Comprehensive Analysis")
    print("="*60)
    
    # Initialize all modules
    fetcher = MarketDataFetcher()
    ta_analyzer = TechnicalAnalyzer()
    ai_signal = AISignalGenerator()
    whale_tracker = WhaleTracker()
    pa_analyzer = PriceActionAnalyzer()
    visualizer = MarketVisualizer()
    
    symbol = 'BTC-USD'
    timeframe = '1d'
    
    print(f"\n🔍 Running comprehensive analysis for {symbol}...")
    
    # 1. Fetch data
    print("   1. 📈 Fetching market data...")
    df = fetcher.get_historical_data(symbol, interval=timeframe, period='3mo')
    
    if df is None:
        print("   ❌ Failed to fetch data!")
        return
    
    # 2. Technical Analysis
    print("   2. 📊 Performing technical analysis...")
    indicators = ta_analyzer.calculate_indicators(df)
    
    # 3. AI Signal
    print("   3. 🤖 Generating AI signal...")
    signal = ai_signal.generate_signal(symbol, df, indicators)
    
    # 4. Whale Tracking
    print("   4. 🐋 Tracking whale activity...")
    whale_data = whale_tracker.get_whale_activity('BTC', hours=24)
    
    # 5. Price Action Analysis
    print("   5. 🎯 Analyzing price action...")
    pa_analysis = pa_analyzer.analyze_ict_concepts(df)
    
    # 6. Display Results
    print("\n" + "="*60)
    print("COMPREHENSIVE ANALYSIS RESULTS")
    print("="*60)
    
    print(f"\n📌 Symbol: {symbol}")
    print(f"📅 Timeframe: {timeframe}")
    print(f"💰 Current Price: ${df['Close'].iloc[-1]:.2f}")
    
    print(f"\n🤖 AI Signal: {signal.get('action')} ({signal.get('confidence'):.1%})")
    
    print(f"\n📊 Technical Overview:")
    print(f"   RSI: {indicators.get('rsi', 0):.2f}")
    print(f"   Trend: {indicators.get('trend', 'N/A')}")
    print(f"   Market State: {indicators.get('market_state', 'N/A')}")
    
    if whale_data:
        print(f"\n🐋 Whale Activity:")
        print(f"   24h Volume: ${whale_data.get('total_volume', 0):,.0f}")
        print(f"   Net Flow: ${whale_data.get('net_flow', 0):,.0f}")
    
    print(f"\n🎯 Price Action:")
    print(f"   Market Structure: {pa_analysis.get('market_structure', 'N/A')}")
    print(f"   Order Blocks: {len(pa_analysis.get('order_blocks', []))}")
    
    print(f"\n⚠️ Risk Management:")
    print(f"   Stop Loss: ${signal.get('stop_loss', 0):.2f}")
    print(f"   Take Profit Targets: {[f'${tp:.2f}' for tp in signal.get('take_profit', [])]}")
    print(f"   Risk/Reward: 1:{signal.get('risk_reward', 0):.1f}")
    
    print("\n" + "="*60)

def main():
    """Run all examples"""
    print("🚀 TRADING ANALYSIS TOOL - BASIC USAGE EXAMPLES")
    print("="*60)
    
    try:
        # Run each example
        example_watchlist()
        example_data_fetching()
        example_technical_analysis()
        example_ai_signal()
        example_whale_tracking()
        example_price_action()
        example_visualization()
        example_comprehensive_analysis()
        
        print("\n" + "="*60)
        print("✅ All examples completed successfully!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
