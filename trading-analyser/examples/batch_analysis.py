#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Batch Analysis Examples
Examples showing batch processing and analysis
"""

import sys
import os
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any
import concurrent.futures
import json

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from modules.watchlist_manager import WatchlistManager
from modules.data_fetcher import MarketDataFetcher
from modules.technical_analyzer import TechnicalAnalyzer
from modules.ai_signal_generator import AISignalGenerator
from utils.logger import setup_logger

logger = setup_logger(__name__)

class BatchAnalyzer:
    """Perform batch analysis on multiple symbols"""
    
    def __init__(self):
        """Initialize batch analyzer"""
        self.fetcher = MarketDataFetcher()
        self.analyzer = TechnicalAnalyzer()
        self.ai = AISignalGenerator()
        self.results_cache = {}
        
        logger.info("Batch Analyzer initialized")
    
    def analyze_watchlist(self, market_type: str = 'crypto', 
                         timeframe: str = '1d',
                         save_results: bool = True) -> pd.DataFrame:
        """
        Analyze entire watchlist
        
        Parameters:
            market_type (str): Market type ('crypto', 'forex', 'stock')
            timeframe (str): Timeframe for analysis
            save_results (bool): Whether to save results to file
        
        Returns:
            pd.DataFrame: Analysis results
        """
        logger.info(f"Starting batch analysis for {market_type} watchlist")
        
        # Get watchlist
        watchlist_manager = WatchlistManager()
        watchlist = watchlist_manager.watchlists.get(market_type, [])
        
        if not watchlist:
            logger.warning(f"No symbols found in {market_type} watchlist")
            return pd.DataFrame()
        
        # Extract symbols
        symbols = [item[0] for item in watchlist]
        
        # Analyze each symbol
        results = []
        
        for symbol in symbols:
            try:
                logger.info(f"Analyzing {symbol}...")
                
                result = self.analyze_symbol(symbol, timeframe)
                
                if result:
                    results.append(result)
                    logger.info(f"Completed analysis for {symbol}")
                else:
                    logger.warning(f"Analysis failed for {symbol}")
                    
            except Exception as e:
                logger.error(f"Error analyzing {symbol}: {e}")
        
        # Create DataFrame
        if results:
            df_results = pd.DataFrame(results)
            
            # Sort by score (descending)
            df_results = df_results.sort_values('score', ascending=False)
            
            # Save results if requested
            if save_results:
                self._save_results(df_results, market_type, timeframe)
            
            logger.info(f"Batch analysis completed: {len(results)}/{len(symbols)} symbols analyzed")
            return df_results
        
        else:
            logger.warning("No successful analyses")
            return pd.DataFrame()
    
    def analyze_symbol(self, symbol: str, timeframe: str = '1d') -> Dict[str, Any]:
        """
        Analyze single symbol
        
        Parameters:
            symbol (str): Trading symbol
            timeframe (str): Timeframe for analysis
        
        Returns:
            Dict[str, Any]: Analysis results
        """
        try:
            # Fetch data
            df = self.fetcher.get_historical_data(symbol, interval=timeframe, period='3mo')
            
            if df is None or df.empty:
                logger.warning(f"No data for {symbol}")
                return None
            
            # Calculate indicators
            indicators = self.analyzer.calculate_indicators(df)
            
            if not indicators:
                logger.warning(f"No indicators for {symbol}")
                return None
            
            # Generate signal
            signal = self.ai.generate_signal(symbol, df, indicators)
            
            # Prepare result
            result = {
                'symbol': symbol,
                'timestamp': datetime.now().isoformat(),
                'timeframe': timeframe,
                'current_price': df['Close'].iloc[-1],
                'action': signal.get('action', 'HOLD'),
                'confidence': signal.get('confidence', 0),
                'score': signal.get('score', 0),
                'rsi': indicators.get('rsi', 0),
                'macd': indicators.get('macd', (0, 0, 0))[0],
                'adx': indicators.get('adx', 0),
                'trend': indicators.get('trend', 'N/A'),
                'market_state': indicators.get('market_state', 'N/A'),
                'stop_loss': signal.get('stop_loss', 0),
                'take_profit_1': signal.get('take_profit', [0])[0],
                'risk_reward': signal.get('risk_reward', 0),
                'volume_ratio': indicators.get('volume_ratio', 0),
                'atr_percent': indicators.get('atr_percent', 0)
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing {symbol}: {e}")
            return None
    
    def analyze_parallel(self, symbols: List[str], timeframe: str = '1d',
                        max_workers: int = 5) -> List[Dict[str, Any]]:
        """
        Analyze symbols in parallel
        
        Parameters:
            symbols (List[str]): List of symbols to analyze
            timeframe (str): Timeframe for analysis
            max_workers (int): Maximum number of parallel workers
        
        Returns:
            List[Dict[str, Any]]: Analysis results
        """
        logger.info(f"Starting parallel analysis for {len(symbols)} symbols")
        
        results = []
        
        # Use ThreadPoolExecutor for parallel processing
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Create futures
            future_to_symbol = {
                executor.submit(self.analyze_symbol, symbol, timeframe): symbol
                for symbol in symbols
            }
            
            # Process results as they complete
            for future in concurrent.futures.as_completed(future_to_symbol):
                symbol = future_to_symbol[future]
                
                try:
                    result = future.result(timeout=30)  # 30 second timeout
                    
                    if result:
                        results.append(result)
                        logger.info(f"Completed parallel analysis for {symbol}")
                    else:
                        logger.warning(f"Parallel analysis failed for {symbol}")
                        
                except concurrent.futures.TimeoutError:
                    logger.error(f"Timeout analyzing {symbol}")
                except Exception as e:
                    logger.error(f"Error in parallel analysis for {symbol}: {e}")
        
        logger.info(f"Parallel analysis completed: {len(results)}/{len(symbols)} successful")
        return results
    
    def analyze_sector(self, sector: str, symbols: List[str] = None,
                      timeframe: str = '1d') -> pd.DataFrame:
        """
        Analyze a sector (e.g., tech stocks, DeFi tokens)
        
        Parameters:
            sector (str): Sector name
            symbols (List[str]): List of symbols (optional)
            timeframe (str): Timeframe for analysis
        
        Returns:
            pd.DataFrame: Sector analysis
        """
        logger.info(f"Starting sector analysis for {sector}")
        
        # Define sector symbols if not provided
        if symbols is None:
            sectors = {
                'tech': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'TSLA'],
                'defi': ['UNI-USD', 'AAVE-USD', 'COMP-USD', 'MKR-USD', 'SNX-USD'],
                'layer1': ['ETH-USD', 'SOL-USD', 'AVAX-USD', 'ADA-USD', 'DOT-USD'],
                'financials': ['JPM', 'BAC', 'GS', 'MS', 'C'],
                'healthcare': ['JNJ', 'PFE', 'MRK', 'ABT', 'UNH']
            }
            
            symbols = sectors.get(sector.lower(), [])
        
        if not symbols:
            logger.warning(f"No symbols defined for sector {sector}")
            return pd.DataFrame()
        
        # Analyze symbols
        results = self.analyze_parallel(symbols, timeframe)
        
        if not results:
            logger.warning(f"No results for sector {sector}")
            return pd.DataFrame()
        
        # Create DataFrame
        df_results = pd.DataFrame(results)
        
        # Calculate sector metrics
        sector_metrics = self._calculate_sector_metrics(df_results)
        
        # Add sector information
        df_results['sector'] = sector
        df_results['sector_sentiment'] = sector_metrics.get('sentiment', 'NEUTRAL')
        df_results['sector_score'] = sector_metrics.get('score', 0)
        
        # Sort by score
        df_results = df_results.sort_values('score', ascending=False)
        
        # Save results
        self._save_sector_results(df_results, sector, timeframe)
        
        logger.info(f"Sector analysis completed for {sector}: {len(results)} symbols")
        return df_results
    
    def analyze_correlation(self, symbols: List[str], 
                          period: str = '1mo') -> pd.DataFrame:
        """
        Analyze correlation between symbols
        
        Parameters:
            symbols (List[str]): List of symbols
            period (str): Time period
        
        Returns:
            pd.DataFrame: Correlation matrix
        """
        logger.info(f"Analyzing correlation for {len(symbols)} symbols")
        
        # Fetch price data for all symbols
        price_data = {}
        
        for symbol in symbols:
            try:
                df = self.fetcher.get_historical_data(symbol, interval='1d', period=period)
                
                if df is not None and not df.empty:
                    price_data[symbol] = df['Close']
                    logger.debug(f"Fetched data for {symbol}")
                else:
                    logger.warning(f"No data for {symbol}")
                    
            except Exception as e:
                logger.error(f"Error fetching data for {symbol}: {e}")
        
        if len(price_data) < 2:
            logger.warning("Insufficient data for correlation analysis")
            return pd.DataFrame()
        
        # Create DataFrame with all price series
        df_prices = pd.DataFrame(price_data)
        
        # Calculate returns
        df_returns = df_prices.pct_change().dropna()
        
        # Calculate correlation matrix
        correlation_matrix = df_returns.corr()
        
        # Calculate average correlation
        avg_correlation = correlation_matrix.values[np.triu_indices_from(correlation_matrix.values, k=1)].mean()
        
        logger.info(f"Correlation analysis completed. Average correlation: {avg_correlation:.3f}")
        
        return correlation_matrix
    
    def generate_daily_report(self, market_types: List[str] = None,
                             save_path: str = None) -> Dict[str, Any]:
        """
        Generate daily analysis report
        
        Parameters:
            market_types (List[str]): Market types to include
            save_path (str): Path to save report
        
        Returns:
            Dict[str, Any]: Daily report
        """
        logger.info("Generating daily report")
        
        if market_types is None:
            market_types = ['crypto', 'stock', 'forex']
        
        report = {
            'date': datetime.now().isoformat(),
            'summary': {},
            'market_analyses': {},
            'top_picks': [],
            'risk_assessment': {}
        }
        
        # Analyze each market
        for market in market_types:
            try:
                logger.info(f"Analyzing {market} market...")
                
                analysis = self.analyze_watchlist(market, '1d', save_results=False)
                
                if not analysis.empty:
                    # Add to report
                    report['market_analyses'][market] = analysis.to_dict('records')
                    
                    # Calculate market summary
                    market_summary = self._calculate_market_summary(analysis)
                    report['summary'][market] = market_summary
                    
                    # Get top picks
                    top_picks = analysis.nlargest(3, 'score')
                    for _, pick in top_picks.iterrows():
                        report['top_picks'].append({
                            'symbol': pick['symbol'],
                            'market': market,
                            'action': pick['action'],
                            'confidence': pick['confidence'],
                            'score': pick['score'],
                            'current_price': pick['current_price']
                        })
                    
                    logger.info(f"Completed {market} market analysis")
                    
            except Exception as e:
                logger.error(f"Error analyzing {market} market: {e}")
        
        # Calculate overall risk assessment
        report['risk_assessment'] = self._calculate_risk_assessment(report)
        
        # Sort top picks by score
        report['top_picks'] = sorted(report['top_picks'], 
                                    key=lambda x: x['score'], 
                                    reverse=True)[:5]  # Top 5
        
        # Save report
        if save_path:
            self._save_report(report, save_path)
        
        logger.info("Daily report generated successfully")
        return report
    
    def _calculate_sector_metrics(self, df_results: pd.DataFrame) -> Dict[str, Any]:
        """Calculate sector metrics"""
        if df_results.empty:
            return {'sentiment': 'NEUTRAL', 'score': 0}
        
        # Calculate average scores
        avg_score = df_results['score'].mean()
        avg_confidence = df_results['confidence'].mean()
        
        # Count actions
        buy_count = (df_results['action'] == 'BUY').sum()
        sell_count = (df_results['action'] == 'SELL').sum()
        hold_count = (df_results['action'] == 'HOLD').sum()
        
        # Determine sentiment
        if buy_count > sell_count and buy_count > hold_count:
            sentiment = 'BULLISH'
        elif sell_count > buy_count and sell_count > hold_count:
            sentiment = 'BEARISH'
        else:
            sentiment = 'NEUTRAL'
        
        return {
            'sentiment': sentiment,
            'score': avg_score,
            'confidence': avg_confidence,
            'buy_count': buy_count,
            'sell_count': sell_count,
            'hold_count': hold_count,
            'total_symbols': len(df_results)
        }
    
    def _calculate_market_summary(self, analysis: pd.DataFrame) -> Dict[str, Any]:
        """Calculate market summary"""
        if analysis.empty:
            return {'sentiment': 'NEUTRAL', 'score': 0}
        
        # Calculate metrics
        metrics = {
            'total_symbols': len(analysis),
            'average_score': analysis['score'].mean(),
            'average_confidence': analysis['confidence'].mean(),
            'average_rsi': analysis['rsi'].mean(),
            'bullish_percentage': (analysis['action'] == 'BUY').mean() * 100,
            'bearish_percentage': (analysis['action'] == 'SELL').mean() * 100,
            'top_symbol': analysis.iloc[0]['symbol'] if len(analysis) > 0 else 'N/A',
            'top_score': analysis['score'].max() if len(analysis) > 0 else 0
        }
        
        # Determine overall sentiment
        buy_pct = metrics['bullish_percentage']
        sell_pct = metrics['bearish_percentage']
        
        if buy_pct > 60:
            metrics['sentiment'] = 'STRONG_BULLISH'
        elif buy_pct > 40:
            metrics['sentiment'] = 'BULLISH'
        elif sell_pct > 60:
            metrics['sentiment'] = 'STRONG_BEARISH'
        elif sell_pct > 40:
            metrics['sentiment'] = 'BEARISH'
        else:
            metrics['sentiment'] = 'NEUTRAL'
        
        return metrics
    
    def _calculate_risk_assessment(self, report: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall risk assessment"""
        risk_assessment = {
            'overall_risk': 'MEDIUM',
            'market_risks': {},
            'recommendations': []
        }
        
        # Analyze each market
        for market, summary in report.get('summary', {}).items():
            sentiment = summary.get('sentiment', 'NEUTRAL')
            avg_rsi = summary.get('average_rsi', 50)
            
            # Determine market risk
            if sentiment in ['STRONG_BULLISH', 'STRONG_BEARISH']:
                risk = 'HIGH'
            elif sentiment in ['BULLISH', 'BEARISH']:
                risk = 'MEDIUM'
            else:
                risk = 'LOW'
            
            # Adjust based on RSI
            if avg_rsi > 70 or avg_rsi < 30:
                risk = 'HIGH'
            elif avg_rsi > 60 or avg_rsi < 40:
                risk = max(risk, 'MEDIUM')  # Don't lower risk
            
            risk_assessment['market_risks'][market] = {
                'risk_level': risk,
                'sentiment': sentiment,
                'avg_rsi': avg_rsi
            }
        
        # Determine overall risk
        market_risks = [data['risk_level'] for data in risk_assessment['market_risks'].values()]
        
        if 'HIGH' in market_risks:
            risk_assessment['overall_risk'] = 'HIGH'
        elif all(r == 'LOW' for r in market_risks):
            risk_assessment['overall_risk'] = 'LOW'
        else:
            risk_assessment['overall_risk'] = 'MEDIUM'
        
        # Generate recommendations
        if risk_assessment['overall_risk'] == 'HIGH':
            risk_assessment['recommendations'].extend([
                "Consider reducing position sizes",
                "Implement strict stop losses",
                "Avoid opening new positions in high-risk markets"
            ])
        elif risk_assessment['overall_risk'] == 'MEDIUM':
            risk_assessment['recommendations'].extend([
                "Maintain normal position sizing",
                "Use standard risk management",
                "Focus on high-conviction trades"
            ])
        else:
            risk_assessment['recommendations'].extend([
                "Can consider increasing position sizes",
                "Look for high-probability setups",
                "Consider longer-term investments"
            ])
        
        return risk_assessment
    
    def _save_results(self, df_results: pd.DataFrame, market_type: str, 
                     timeframe: str):
        """Save analysis results to file"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"analysis_{market_type}_{timeframe}_{timestamp}.csv"
            filepath = Path(__file__).parent.parent / "data" / filename
            
            df_results.to_csv(filepath, index=False)
            logger.info(f"Results saved to {filepath}")
            
        except Exception as e:
            logger.error(f"Error saving results: {e}")
    
    def _save_sector_results(self, df_results: pd.DataFrame, sector: str,
                           timeframe: str):
        """Save sector analysis results"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"sector_{sector}_{timeframe}_{timestamp}.csv"
            filepath = Path(__file__).parent.parent / "data" / filename
            
            df_results.to_csv(filepath, index=False)
            logger.info(f"Sector results saved to {filepath}")
            
        except Exception as e:
            logger.error(f"Error saving sector results: {e}")
    
    def _save_report(self, report: Dict[str, Any], save_path: str):
        """Save daily report"""
        try:
            if not save_path:
                timestamp = datetime.now().strftime("%Y%m%d")
                save_path = Path(__file__).parent.parent / "reports" / f"daily_report_{timestamp}.json"
            
            # Create directory if it doesn't exist
            save_path = Path(save_path)
            save_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"Daily report saved to {save_path}")
            
        except Exception as e:
            logger.error(f"Error saving daily report: {e}")

def example_batch_watchlist():
    """Example: Batch analyze watchlist"""
    print("="*60)
    print("EXAMPLE 1: Batch Watchlist Analysis")
    print("="*60)
    
    analyzer = BatchAnalyzer()
    
    # Analyze crypto watchlist
    print("\n📊 Analyzing crypto watchlist...")
    results = analyzer.analyze_watchlist('crypto', '1d', save_results=False)
    
    if not results.empty:
        print(f"\n📈 Analysis completed for {len(results)} cryptocurrencies")
        
        # Show top 5
        print("\n🏆 Top 5 Cryptocurrencies:")
        top_5 = results.head(5)
        
        for idx, row in top_5.iterrows():
            print(f"   {idx+1}. {row['symbol']}: {row['action']} "
                  f"(Score: {row['score']:.1f}, Confidence: {row['confidence']:.1%})")
        
        # Show statistics
        print(f"\n📊 Statistics:")
        print(f"   Average Score: {results['score'].mean():.1f}")
        print(f"   Average Confidence: {results['confidence'].mean():.1%}")
        print(f"   Bullish: {(results['action'] == 'BUY').sum()} symbols")
        print(f"   Bearish: {(results['action'] == 'SELL').sum()} symbols")
        print(f"   Neutral: {(results['action'] == 'HOLD').sum()} symbols")
    else:
        print("❌ No results obtained")

def example_parallel_analysis():
    """Example: Parallel analysis"""
    print("\n" + "="*60)
    print("EXAMPLE 2: Parallel Analysis")
    print("="*60)
    
    analyzer = BatchAnalyzer()
    
    # Define symbols for parallel analysis
    symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'NFLX']
    
    print(f"\n⚡ Analyzing {len(symbols)} symbols in parallel...")
    results = analyzer.analyze_parallel(symbols, '1d', max_workers=4)
    
    if results:
        print(f"\n✅ Parallel analysis completed: {len(results)}/{len(symbols)} successful")
        
        # Create DataFrame
        df_results = pd.DataFrame(results)
        df_results = df_results.sort_values('score', ascending=False)
        
        print("\n📊 Results:")
        for idx, row in df_results.head(3).iterrows():
            print(f"   • {row['symbol']}: {row['action']} "
                  f"(Score: {row['score']:.1f}, RSI: {row['rsi']:.1f})")
    else:
        print("❌ No results from parallel analysis")

def example_sector_analysis():
    """Example: Sector analysis"""
    print("\n" + "="*60)
    print("EXAMPLE 3: Sector Analysis")
    print("="*60)
    
    analyzer = BatchAnalyzer()
    
    # Analyze tech sector
    print("\n💻 Analyzing technology sector...")
    tech_results = analyzer.analyze_sector('tech')
    
    if not tech_results.empty:
        print(f"\n📈 Tech Sector Analysis:")
        print(f"   Total Symbols: {len(tech_results)}")
        print(f"   Sector Sentiment: {tech_results['sector_sentiment'].iloc[0]}")
        print(f"   Sector Score: {tech_results['sector_score'].iloc[0]:.1f}")
        
        print("\n🏆 Top Tech Stocks:")
        top_tech = tech_results.head(3)
        for idx, row in top_tech.iterrows():
            print(f"   {idx+1}. {row['symbol']}: {row['action']} "
                  f"(Score: {row['score']:.1f})")
    
    # Analyze DeFi sector
    print("\n🔗 Analyzing DeFi sector...")
    defi_results = analyzer.analyze_sector('defi')
    
    if not defi_results.empty:
        print(f"\n📈 DeFi Sector Analysis:")
        print(f"   Total Symbols: {len(defi_results)}")
        print(f"   Sector Sentiment: {defi_results['sector_sentiment'].iloc[0]}")
        
        print("\n🏆 Top DeFi Tokens:")
        top_defi = defi_results.head(3)
        for idx, row in top_defi.iterrows():
            print(f"   {idx+1}. {row['symbol']}: {row['action']} "
                  f"(Score: {row['score']:.1f})")

def example_correlation_analysis():
    """Example: Correlation analysis"""
    print("\n" + "="*60)
    print("EXAMPLE 4: Correlation Analysis")
    print("="*60)
    
    analyzer = BatchAnalyzer()
    
    # Analyze correlation between major tech stocks
    tech_symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'TSLA']
    
    print(f"\n🔗 Analyzing correlation between {len(tech_symbols)} tech stocks...")
    correlation_matrix = analyzer.analyze_correlation(tech_symbols, period='3mo')
    
    if not correlation_matrix.empty:
        print(f"\n📊 Correlation Matrix:")
        print(correlation_matrix.round(3))
        
        # Calculate average correlation
        avg_corr = correlation_matrix.values[np.triu_indices_from(correlation_matrix.values, k=1)].mean()
        print(f"\n📈 Average Correlation: {avg_corr:.3f}")
        
        # Find highest correlation pair
        mask = np.triu(np.ones_like(correlation_matrix, dtype=bool), k=1)
        correlations = correlation_matrix.where(mask)
        
        max_corr = correlations.stack().max()
        max_pair = correlations.stack().idxmax()
        
        print(f"🤝 Highest Correlation: {max_pair[0]} & {max_pair[1]} ({max_corr:.3f})")
    else:
        print("❌ No correlation matrix generated")

def example_daily_report():
    """Example: Daily report generation"""
    print("\n" + "="*60)
    print("EXAMPLE 5: Daily Report Generation")
    print("="*60)
    
    analyzer = BatchAnalyzer()
    
    print("\n📋 Generating daily market report...")
    report = analyzer.generate_daily_report(save_path=False)
    
    if report:
        print("\n✅ Daily Report Generated")
        print(f"\n📅 Date: {report.get('date', 'N/A')}")
        
        # Market summaries
        print("\n📊 Market Summaries:")
        for market, summary in report.get('summary', {}).items():
            print(f"   {market.upper()}: {summary.get('sentiment', 'N/A')} "
                  f"(Score: {summary.get('average_score', 0):.1f})")
        
        # Top picks
        print("\n🏆 Top Picks:")
        for i, pick in enumerate(report.get('top_picks', [])[:3], 1):
            print(f"   {i}. {pick['symbol']} ({pick['market']}): {pick['action']} "
                  f"(Score: {pick['score']:.1f}, Confidence: {pick['confidence']:.1%})")
        
        # Risk assessment
        risk_assessment = report.get('risk_assessment', {})
        print(f"\n⚠️ Risk Assessment: {risk_assessment.get('overall_risk', 'N/A')}")
        
        print("\n💡 Recommendations:")
        for rec in risk_assessment.get('recommendations', [])[:3]:
            print(f"   • {rec}")
    else:
        print("❌ Failed to generate daily report")

def example_custom_batch():
    """Example: Custom batch analysis"""
    print("\n" + "="*60)
    print("EXAMPLE 6: Custom Batch Analysis")
    print("="*60)
    
    analyzer = BatchAnalyzer()
    
    # Define custom portfolio
    portfolio = {
        'Large Cap Tech': ['AAPL', 'MSFT', 'GOOGL', 'AMZN'],
        'Semiconductors': ['NVDA', 'AMD', 'INTC', 'QCOM'],
        'EV & Clean Energy': ['TSLA', 'NIO', 'PLUG', 'ENPH'],
        'Fintech': ['PYPL', 'SQ', 'V', 'MA']
    }
    
    all_results = []
    
    print("\n📊 Analyzing custom portfolio...")
    
    for category, symbols in portfolio.items():
        print(f"\n🔍 Analyzing {category}...")
        
        # Analyze each symbol in the category
        category_results = []
        
        for symbol in symbols:
            result = analyzer.analyze_symbol(symbol, '1d')
            if result:
                result['category'] = category
                category_results.append(result)
        
        if category_results:
            # Create DataFrame for category
            df_category = pd.DataFrame(category_results)
            
            # Calculate category statistics
            avg_score = df_category['score'].mean()
            avg_confidence = df_category['confidence'].mean()
            buy_count = (df_category['action'] == 'BUY').sum()
            
            print(f"   ✅ {len(category_results)}/{len(symbols)} symbols analyzed")
            print(f"   📈 Average Score: {avg_score:.1f}")
            print(f"   🎯 Average Confidence: {avg_confidence:.1%}")
            print(f"   🟢 Buy Signals: {buy_count}")
            
            # Add to all results
            all_results.extend(category_results)
    
    if all_results:
        # Create overall portfolio analysis
        df_portfolio = pd.DataFrame(all_results)
        
        print(f"\n📋 Portfolio Analysis Summary:")
        print(f"   Total Symbols: {len(df_portfolio)}")
        print(f"   Overall Average Score: {df_portfolio['score'].mean():.1f}")
        print(f"   Overall Average Confidence: {df_portfolio['confidence'].mean():.1%}")
        
        # Best performing categories
        category_performance = df_portfolio.groupby('category')['score'].mean().sort_values(ascending=False)
        
        print(f"\n🏆 Best Performing Categories:")
        for category, score in category_performance.head(3).items():
            print(f"   • {category}: Score {score:.1f}")
        
        # Top 3 symbols overall
        top_symbols = df_portfolio.nlargest(3, 'score')
        
        print(f"\n⭐ Top 3 Symbols:")
        for idx, row in top_symbols.iterrows():
            print(f"   {idx+1}. {row['symbol']} ({row['category']}): "
                  f"{row['action']} (Score: {row['score']:.1f})")
    else:
        print("❌ No results from portfolio analysis")

def main():
    """Run all batch analysis examples"""
    print("🚀 TRADING ANALYSIS TOOL - BATCH ANALYSIS EXAMPLES")
    print("="*60)
    
    try:
        # Run each example
        example_batch_watchlist()
        example_parallel_analysis()
        example_sector_analysis()
        example_correlation_analysis()
        example_daily_report()
        example_custom_batch()
        
        print("\n" + "="*60)
        print("✅ All batch analysis examples completed!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Error running batch examples: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
