"""
Security filters module for token analysis
"""
import re
import yaml
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import aiohttp
from solders.pubkey import Pubkey
import json

@dataclass
class SecurityConfig:
    """Security configuration dataclass"""
    blacklisted_tokens: Set[str]
    blacklisted_developers: Set[str]
    blacklisted_mints: Set[str]
    scam_patterns: List[str]
    minimum_requirements: Dict
    suspicious_indicators: Dict
    
    @classmethod
    def from_yaml(cls, config_path: str = "config/config.yaml"):
        """Load security configuration from YAML file"""
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        filters = config.get('filters', {})
        
        return cls(
            blacklisted_tokens=set(filters.get('blacklisted_tokens', [])),
            blacklisted_developers=set(filters.get('blacklisted_developers', [])),
            blacklisted_mints=set(filters.get('blacklisted_mints', [])),
            scam_patterns=filters.get('scam_patterns', []),
            minimum_requirements=filters.get('minimum_requirements', {}),
            suspicious_indicators=filters.get('suspicious_indicators', {})
        )


class TokenSecurityFilter:
    """Enhanced security filter for token analysis"""
    
    def __init__(self, config: SecurityConfig):
        self.config = config
        self.compiled_patterns = [re.compile(pattern) for pattern in config.scam_patterns]
        
        # Cache for recent checks
        self._checked_tokens = {}
        self._token_metadata_cache = {}
    
    async def is_token_safe(self, token_address: str, metadata: Dict) -> Tuple[bool, List[str]]:
        """
        Comprehensive token safety check
        
        Returns: (is_safe, list_of_warnings)
        """
        warnings = []
        
        # Check blacklists
        if token_address in self.config.blacklisted_tokens:
            return False, ["Token is blacklisted"]
        
        if metadata.get('mint') in self.config.blacklisted_mints:
            return False, ["Mint is blacklisted"]
        
        # Check developer/creator
        creator = metadata.get('creator')
        if creator and creator in self.config.blacklisted_developers:
            return False, ["Developer is blacklisted"]
        
        # Check name/symbol for scam patterns
        name = metadata.get('name', '').lower()
        symbol = metadata.get('symbol', '').lower()
        
        for pattern in self.compiled_patterns:
            if pattern.match(name) or pattern.match(symbol):
                warnings.append(f"Name/symbol matches scam pattern: {pattern.pattern}")
        
        # Check minimum requirements
        if not self._meets_minimum_requirements(metadata):
            warnings.append("Does not meet minimum requirements")
        
        # Check for suspicious indicators
        suspicious_warnings = await self._check_suspicious_indicators(token_address, metadata)
        warnings.extend(suspicious_warnings)
        
        is_safe = len([w for w in warnings if 'blacklisted' in w.lower()]) == 0
        
        return is_safe, warnings
    
    def _meets_minimum_requirements(self, metadata: Dict) -> bool:
        """Check if token meets minimum requirements"""
        min_req = self.config.minimum_requirements
        
        liquidity = metadata.get('liquidity_usd', 0)
        holders = metadata.get('holders', 0)
        age_hours = metadata.get('age_hours', 0)
        volume = metadata.get('volume_24h_usd', 0)
        
        return all([
            liquidity >= min_req.get('liquidity_usd', 0),
            holders >= min_req.get('holders', 0),
            age_hours >= min_req.get('age_hours', 0),
            volume >= min_req.get('volume_24h_usd', 0)
        ])
    
    async def _check_suspicious_indicators(self, token_address: str, metadata: Dict) -> List[str]:
        """Check for suspicious activity indicators"""
        warnings = []
        indicators = self.config.suspicious_indicators
        
        # Check holder concentration
        top_holders_percent = metadata.get('top_10_holders_percent', 0)
        if top_holders_percent > indicators.get('high_owner_concentration', 100):
            warnings.append(f"High owner concentration: {top_holders_percent}%")
        
        # Check holder count
        holders = metadata.get('holders', 0)
        if holders < indicators.get('low_holder_count', 0):
            warnings.append(f"Low holder count: {holders}")
        
        # Check age
        age_hours = metadata.get('age_hours', 0)
        if age_hours < indicators.get('recent_creation_hours', 0):
            warnings.append(f"Recently created: {age_hours} hours")
        
        return warnings


class DeveloperReputationChecker:
    """Check developer reputation across multiple tokens"""
    
    def __init__(self, config: SecurityConfig):
        self.config = config
        self.developer_tokens = {}
        self.developer_scores = {}
    
    async def analyze_developer(self, developer_address: str) -> Dict:
        """
        Analyze developer reputation
        
        Returns: {
            "address": str,
            "reputation_score": float (0-100),
            "tokens_created": int,
            "rug_pull_count": int,
            "success_rate": float,
            "warnings": List[str]
        }
        """
        # Check if developer is blacklisted
        if developer_address in self.config.blacklisted_developers:
            return {
                "address": developer_address,
                "reputation_score": 0,
                "tokens_created": 0,
                "rug_pull_count": 0,
                "success_rate": 0,
                "warnings": ["Developer is blacklisted"]
            }
        
        # For now, return neutral score (can be extended with actual API calls)
        return {
            "address": developer_address,
            "reputation_score": 50,
            "tokens_created": 0,
            "rug_pull_count": 0,
            "success_rate": 0,
            "warnings": ["No detailed analysis available"]
        }
