"""
Main entry point for Solana Token Analyzer
"""
import asyncio
import sys
import os
from datetime import datetime

# Add module paths
sys.path.append(os.path.join(os.path.dirname(__file__), 'analyzer'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'verification'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'security'))

from analyzer.secure_analyzer import SecureWalletAnalyzer
from analyzer.performance_analyzer import NewTokenPerformanceAnalyzer
from verification.rugcheck_integration import RugCheckAnalyzer
from verification.tweetscout_integration import TweetScoutAnalyzer


class SolanaTokenAnalyzer:
    """Main analyzer class"""
    
    def __init__(self):
        self.wallet_analyzer = None
        self.performance_analyzer = None
        self.rugcheck_analyzer = None
        self.tweetscout_analyzer = None
    
    async def initialize(self):
        """Initialize all analyzers"""
        print("🚀 Initializing Solana Token Analyzer...")
        
        self.wallet_analyzer = SecureWalletAnalyzer()
        self.performance_analyzer = NewTokenPerformanceAnalyzer()
        self.rugcheck_analyzer = RugCheckAnalyzer()
        self.tweetscout_analyzer = TweetScoutAnalyzer()
        
        print("✅ All analyzers initialized!")
    
    async def analyze_wallet(self, wallet_address: str):
        """Analyze a single wallet"""
        print(f"\n🔍 Analyzing wallet: {wallet_address[:8]}...{wallet_address[-6:]}")
        
        if not self.wallet_analyzer:
            await self.initialize()
        
        result = await self.wallet_analyzer.analyze_wallet_safely(wallet_address)
        
        print(f"\n📊 Analysis Results:")
        print(f"   Security Score: {result.get('security_score', 0)}/100")
        print(f"   Safe Tokens: {len(result.get('safe_tokens', []))}")
        print(f"   Flagged Tokens: {len(result.get('flagged_tokens', []))}")
        print(f"   Total Tokens: {result.get('token_count', 0)}")
        
        if result.get('warnings'):
            print(f"\n⚠️  Warnings:")
            for warning in result['warnings'][:5]:  # Show first 5 warnings
                print(f"   • {warning}")
        
        if result.get('recommendations'):
            print(f"\n💡 Recommendations:")
            for rec in result['recommendations']:
                print(f"   • {rec}")
        
        return result
    
    async def analyze_token_performance(self, token_address: str, symbol: str = ""):
        """Analyze token performance metrics"""
        print(f"\n📈 Analyzing token performance: {token_address[:8]}...")
        
        if not self.performance_analyzer:
            await self.initialize()
        
        metrics = await self.performance_analyzer.analyze_token(token_address, symbol)
        
        if metrics:
            print(f"\n📊 Performance Metrics:")
            print(f"   Symbol: {metrics.symbol}")
            print(f"   Win Rate (30D): {metrics.win_rate_30d:.1f}%")
            print(f"   PnL (30D): {metrics.pnl_30d:.1f}%")
            print(f"   Transactions (7D): {metrics.transaction_count_7d}")
            print(f"   Volume (7D): ${metrics.volume_7d_usd:,.0f}")
            print(f"   Holders: {metrics.holder_count}")
            print(f"   Liquidity: ${metrics.liquidity_usd:,.0f}")
            print(f"   Composite Score: {metrics.composite_score:.1f}/100")
            print(f"   Passes Filters: {'✅' if metrics.passes_filters else '❌'}")
            
            if metrics.filter_violations:
                print(f"\n❌ Filter Violations:")
                for violation in metrics.filter_violations:
                    print(f"   • {violation}")
        
        return metrics
    
    async def verify_token(self, token_address: str):
        """Verify token using RugCheck and TweetScout"""
        print(f"\n🔒 Verifying token: {token_address[:8]}...")
        
        if not self.rugcheck_analyzer:
            await self.initialize()
        
        # RugCheck verification
        print("   Checking RugCheck...")
        rugcheck_report = await self.rugcheck_analyzer.analyze_token(token_address)
        
        print(f"   RugCheck Score: {rugcheck_report.overall_score}/100")
        print(f"   Risk Level: {rugcheck_report.risk_level}")
        print(f"   Contract Verified: {'✅' if rugcheck_report.contract_verified else '❌'}")
        print(f"   Liquidity Locked: {'✅' if rugcheck_report.liquidity_locked else '❌'}")
        
        # TweetScout verification
        print("\n   Checking TweetScout...")
        tweetscout_report = await self.tweetscout_analyzer.analyze_token(token_address)
        
        print(f"   Developer Score: {tweetscout_report.developer_score}/100")
        print(f"   Project Activity: {tweetscout_report.project_activity_score}/100")
        print(f"   Community Score: {tweetscout_report.community_score}/100")
        print(f"   Overall Social Score: {tweetscout_report.overall_score}/100")
        
        # Combined verification
        combined_score = (
            rugcheck_report.overall_score * 0.5 +
            tweetscout_report.overall_score * 0.5
        )
        
        print(f"\n🔐 Combined Verification Score: {combined_score:.1f}/100")
        
        if combined_score >= 65:
            print("✅ Token passes verification!")
        else:
            print("❌ Token fails verification requirements")
        
        return {
            "rugcheck": rugcheck_report.to_dict(),
            "tweetscout": tweetscout_report.to_dict(),
            "combined_score": combined_score,
            "passed": combined_score >= 65
        }
    
    async def close(self):
        """Close all connections"""
        print("\n🔌 Closing connections...")
        
        if self.wallet_analyzer:
            await self.wallet_analyzer.close()
        
        if self.performance_analyzer:
            await self.performance_analyzer.close()
        
        if self.rugcheck_analyzer:
            await self.rugcheck_analyzer.close()
        
        if self.tweetscout_analyzer:
            await self.tweetscout_analyzer.close()
        
        print("✅ All connections closed!")


async def main():
    """Main function"""
    print("=" * 50)
    print("🔍 SOLANA TOKEN ANALYZER")
    print("=" * 50)
    
    analyzer = SolanaTokenAnalyzer()
    
    try:
        await analyzer.initialize()
        
        while True:
            print("\n" + "=" * 50)
            print("Select an option:")
            print("1. 🔍 Analyze Wallet")
            print("2. 📈 Analyze Token Performance")
            print("3. 🔒 Verify Token")
            print("4. 🚪 Exit")
            print("=" * 50)
            
            choice = input("\nEnter your choice (1-4): ").strip()
            
            if choice == "1":
                wallet_address = input("Enter wallet address: ").strip()
                if wallet_address:
                    await analyzer.analyze_wallet(wallet_address)
                else:
                    print("❌ Please enter a valid wallet address")
            
            elif choice == "2":
                token_address = input("Enter token address: ").strip()
                symbol = input("Enter token symbol (optional): ").strip()
                if token_address:
                    await analyzer.analyze_token_performance(token_address, symbol)
                else:
                    print("❌ Please enter a valid token address")
            
            elif choice == "3":
                token_address = input("Enter token address: ").strip()
                if token_address:
                    await analyzer.verify_token(token_address)
                else:
                    print("❌ Please enter a valid token address")
            
            elif choice == "4":
                print("\n👋 Goodbye!")
                break
            
            else:
                print("❌ Invalid choice. Please enter 1-4")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        await analyzer.close()


if __name__ == "__main__":
    # Handle Windows event loop policy
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    asyncio.run(main())
