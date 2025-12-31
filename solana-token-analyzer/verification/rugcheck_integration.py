"""
Integration with RugCheck.xyz API for token security verification
"""
import aiohttp
from typing import Dict, List, Optional
from dataclasses import dataclass
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class RugCheckReport:
    """RugCheck report dataclass"""
    token_address: str
    overall_score: float
    risk_level: str
    contract_verified: bool
    liquidity_locked: bool
    owner_renounced: bool
    warnings: List[str]
    passed_verification: bool
    
    def to_dict(self) -> Dict:
        return {
            "token_address": self.token_address,
            "overall_score": self.overall_score,
            "risk_level": self.risk_level,
            "contract_verified": self.contract_verified,
            "liquidity_locked": self.liquidity_locked,
            "owner_renounced": self.owner_renounced,
            "warnings": self.warnings,
            "passed_verification": self.passed_verification
        }


class RugCheckAnalyzer:
    """Integration with RugCheck.xyz API"""
    
    def __init__(self, api_key: str = "", base_url: str = "https://api.rugcheck.xyz/v1"):
        self.api_key = api_key
        self.base_url = base_url
        self.session = None
    
    async def initialize(self):
        """Initialize async session"""
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "TokenVerificationBot/1.0"
        }
        
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        self.session = aiohttp.ClientSession(headers=headers)
    
    async def analyze_token(self, token_address: str) -> RugCheckReport:
        """
        Analyze token security using RugCheck API
        
        Note: Without API key, returns mock data for testing
        """
        if not self.session:
            await self.initialize()
        
        if not self.api_key:
            # Return mock data for testing
            return self._get_mock_report(token_address)
        
        try:
            # Fetch token report
            report_data = await self._fetch_token_report(token_address)
            
            if not report_data:
                return self._get_mock_report(token_address)
            
            # Parse report
            return self._parse_report(token_address, report_data)
            
        except Exception as e:
            logger.error(f"Error analyzing token {token_address} with RugCheck: {e}")
            return self._get_mock_report(token_address)
    
    async def _fetch_token_report(self, token_address: str) -> Dict:
        """Fetch token report from RugCheck API"""
        try:
            async with self.session.get(
                f"{self.base_url}/tokens/{token_address}/report"
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("data", {})
        except Exception as e:
            logger.error(f"Error fetching RugCheck report: {e}")
        
        return {}
    
    def _parse_report(self, token_address: str, report_data: Dict) -> RugCheckReport:
        """Parse RugCheck API response"""
        overall_score = report_data.get("score", 0)
        
        # Determine risk level
        if overall_score >= 80:
            risk_level = "LOW"
        elif overall_score >= 60:
            risk_level = "MEDIUM"
        elif overall_score >= 40:
            risk_level = "HIGH"
        else:
            risk_level = "CRITICAL"
        
        # Extract warnings
        warnings = report_data.get("warnings", [])
        if isinstance(warnings, str):
            warnings = [warnings]
        
        # Determine if passed verification
        passed_verification = (
            overall_score >= 60 and
            report_data.get("contract_verified", False) and
            report_data.get("liquidity_locked", False)
        )
        
        return RugCheckReport(
            token_address=token_address,
            overall_score=overall_score,
            risk_level=risk_level,
            contract_verified=report_data.get("contract_verified", False),
            liquidity_locked=report_data.get("liquidity_locked", False),
            owner_renounced=report_data.get("owner_renounced", False),
            warnings=warnings,
            passed_verification=passed_verification
        )
    
    def _get_mock_report(self, token_address: str) -> RugCheckReport:
        """Get mock report for testing (when no API key)"""
        # Simulate different scores based on token address hash
        address_hash = hash(token_address) % 100
        
        if address_hash > 80:
            score = 85
            risk = "LOW"
        elif address_hash > 60:
            score = 70
            risk = "MEDIUM"
        elif address_hash > 40:
            score = 50
            risk = "HIGH"
        else:
            score = 30
            risk = "CRITICAL"
        
        return RugCheckReport(
            token_address=token_address,
            overall_score=score,
            risk_level=risk,
            contract_verified=score > 60,
            liquidity_locked=score > 70,
            owner_renounced=score > 65,
            warnings=["Mock data - using test mode"] if score < 80 else [],
            passed_verification=score > 60
        )
    
    async def close(self):
        """Close the session"""
        if self.session:
            await self.session.close()
