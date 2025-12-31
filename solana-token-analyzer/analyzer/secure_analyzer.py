"""
Secure wallet analyzer with enhanced security filters
"""
import asyncio
from typing import Dict, List, Optional
from datetime import datetime
import aiohttp
from solders.pubkey import Pubkey
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Commitment

from security.filters import TokenSecurityFilter, SecurityConfig, DeveloperReputationChecker


class SecureWalletAnalyzer:
    """Wallet analyzer with enhanced security filters"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        import yaml
        
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        self.security_config = SecurityConfig.from_yaml(config_path)
        self.security_filter = TokenSecurityFilter(self.security_config)
        self.dev_checker = DeveloperReputationChecker(self.security_config)
        
        # Initialize clients
        rpc_url = self.config['solana']['rpc_endpoints']['primary']
        self.client = AsyncClient(rpc_url, commitment=Commitment("confirmed"))
        
        self.session = aiohttp.ClientSession()
    
    async def analyze_wallet_safely(self, wallet_address: str) -> Dict:
        """
        Analyze wallet with security checks
        
        Returns: {
            "wallet": str,
            "safe_tokens": List[Dict],
            "flagged_tokens": List[Dict],
            "security_score": float,
            "warnings": List[str],
            "recommendations": List[str]
        }
        """
        try:
            # Get all token accounts
            token_accounts = await self._get_token_accounts(wallet_address)
            
            safe_tokens = []
            flagged_tokens = []
            all_warnings = []
            
            # Analyze each token
            for token_account in token_accounts:
                token_address = str(token_account.pubkey)
                
                # Skip if blacklisted
                if token_address in self.security_config.blacklisted_tokens:
                    flagged_tokens.append({
                        "address": token_address[:8] + "...",
                        "reason": "Blacklisted token",
                        "severity": "high"
                    })
                    continue
                
                # Get token metadata
                metadata = await self._get_token_metadata(token_address)
                
                if not metadata:
                    continue
                
                # Security check
                is_safe, warnings = await self.security_filter.is_token_safe(
                    token_address, metadata
                )
                
                token_data = {
                    "address": token_address[:8] + "...",
                    "symbol": metadata.get('symbol', 'UNKNOWN'),
                    "name": metadata.get('name', 'Unknown'),
                    "price": metadata.get('price', 0),
                    "liquidity": metadata.get('liquidity_usd', 0),
                    "balance": token_account.account.data.parsed['info']['tokenAmount']['uiAmount'],
                    "security_warnings": warnings
                }
                
                if is_safe:
                    safe_tokens.append(token_data)
                else:
                    token_data['flagged_reason'] = 'Failed security checks'
                    flagged_tokens.append(token_data)
                
                all_warnings.extend(warnings)
            
            # Calculate wallet security score
            security_score = self._calculate_wallet_security_score(
                safe_tokens, flagged_tokens
            )
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
                safe_tokens, flagged_tokens, security_score
            )
            
            return {
                "wallet": wallet_address[:8] + "..." + wallet_address[-6:],
                "safe_tokens": safe_tokens,
                "flagged_tokens": flagged_tokens,
                "token_count": len(safe_tokens) + len(flagged_tokens),
                "security_score": security_score,
                "warnings": list(set(all_warnings)),
                "recommendations": recommendations,
                "analysis_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "wallet": wallet_address,
                "error": str(e),
                "security_score": 0,
                "warnings": ["Analysis failed"],
                "analysis_timestamp": datetime.utcnow().isoformat()
            }
    
    async def _get_token_accounts(self, wallet_address: str):
        """Get token accounts from Solana blockchain"""
        try:
            response = await self.client.get_token_accounts_by_owner(
                Pubkey.from_string(wallet_address),
                program_id=Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
            )
            return response.value
        except Exception as e:
            print(f"Error getting token accounts: {e}")
            return []
    
    async def _get_token_metadata(self, token_address: str) -> Optional[Dict]:
        """Get token metadata from DexScreener"""
        try:
            async with self.session.get(
                f"https://api.dexscreener.com/latest/dex/tokens/{token_address}"
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    pairs = data.get('pairs', [])
                    
                    if pairs:
                        pair = pairs[0]
                        return {
                            "name": pair.get('baseToken', {}).get('name', 'Unknown'),
                            "symbol": pair.get('baseToken', {}).get('symbol', 'UNKNOWN'),
                            "price": float(pair.get('priceUsd', 0)),
                            "liquidity_usd": float(pair.get('liquidity', {}).get('usd', 0)),
                            "volume_24h_usd": float(pair.get('volume', {}).get('h24', 0)),
                            "price_change_24h": float(pair.get('priceChange', {}).get('h24', 0)),
                            "dex": pair.get('dexId'),
                            "pair_address": pair.get('pairAddress')
                        }
        except Exception as e:
            print(f"Error fetching metadata for {token_address}: {e}")
        
        return None
    
    def _calculate_wallet_security_score(self, safe_tokens: List, flagged_tokens: List) -> float:
        """Calculate overall wallet security score (0-100)"""
        total_tokens = len(safe_tokens) + len(flagged_tokens)
        if total_tokens == 0:
            return 100.0
        
        safe_ratio = len(safe_tokens) / total_tokens
        score = safe_ratio * 100
        
        return round(score, 2)
    
    def _generate_recommendations(self, safe_tokens: List, 
                                 flagged_tokens: List, score: float) -> List[str]:
        """Generate security recommendations"""
        recommendations = []
        
        if flagged_tokens:
            recommendations.append(
                f"Consider removing {len(flagged_tokens)} flagged tokens"
            )
        
        if score < 70:
            recommendations.append("Wallet security score is low. Review flagged tokens.")
        
        if len(safe_tokens) == 0 and len(flagged_tokens) > 0:
            recommendations.append("All tokens in wallet are flagged. Immediate action recommended.")
        
        return recommendations
    
    async def close(self):
        """Close connections"""
        await self.client.close()
        await self.session.close()
