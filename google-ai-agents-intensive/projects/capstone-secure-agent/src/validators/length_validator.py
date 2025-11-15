"""
Length Validator Agent
Prevents large prompt attacks, DoS, and cost attacks

Following SOLID principles:
- Single Responsibility: Only validates length/tokens
- Open/Closed: Extensible for new limits
- Liskov Substitution: Implements IValidator
- Interface Segregation: Focused interface
- Dependency Inversion: Depends on abstractions
"""

from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass
import time
from collections import defaultdict
import re

from src.core.interfaces import IValidator
from src.core.models import ValidationResult, Action


@dataclass
class LengthValidationResult:
    """
    Result of length validation
    
    Attributes:
        valid: Whether input passes validation
        reason: Explanation for the decision
        char_count: Number of characters
        token_count: Estimated number of tokens
        estimated_cost: Estimated API cost in USD
        recommended_action: Suggested action (allow/block/truncate/rate_limit)
    """
    valid: bool
    reason: str
    char_count: int
    token_count: int
    estimated_cost: float
    recommended_action: str


class LengthValidator(IValidator):
    """
    Validates input length to prevent:
    - Context overflow attacks
    - Denial of Service (DoS) attacks  
    - Cost attacks (excessive API usage)
    - Resource exhaustion
    - Hidden injections in large text
    
    Multi-layer defense:
    1. Fast character count check (O(1))
    2. Token estimation (O(n))
    3. Rate limiting per user
    4. Cost monitoring
    """
    
    # Character limits (very fast to check)
    MAX_CHARS = 50_000          # 50K characters
    
    # Token limits (by tier)
    MAX_TOKENS_FREE = 2_000     # Free tier
    MAX_TOKENS_STARTER = 8_000  # Starter tier
    MAX_TOKENS_PRO = 16_000     # Pro tier
    MAX_TOKENS_ENTERPRISE = 32_000  # Enterprise tier
    
    # Rate limiting
    MAX_REQUESTS_PER_MINUTE = 100
    MAX_TOKENS_PER_MINUTE = 100_000
    
    # Cost estimates (Gemini Flash pricing)
    COST_PER_1K_INPUT_TOKENS = 0.00015    # $0.00015 per 1K input tokens
    COST_PER_1K_OUTPUT_TOKENS = 0.0006    # $0.0006 per 1K output tokens (estimate 2x input)
    
    def __init__(self, tier: str = 'free'):
        """
        Initialize length validator
        
        Args:
            tier: Customer tier (free, starter, pro, enterprise)
        """
        self.tier = tier
        self.max_tokens = self._get_max_tokens()
        
        # Rate limiting state (in-memory, use Redis in production)
        self.request_counts: Dict[str, List[float]] = defaultdict(list)
        self.token_counts: Dict[str, List[Tuple[float, int]]] = defaultdict(list)
    
    
    def _get_max_tokens(self) -> int:
        """Get max tokens based on customer tier"""
        limits = {
            'free': self.MAX_TOKENS_FREE,
            'starter': self.MAX_TOKENS_STARTER,
            'pro': self.MAX_TOKENS_PRO,
            'enterprise': self.MAX_TOKENS_ENTERPRISE
        }
        return limits.get(self.tier, self.MAX_TOKENS_STARTER)
    
    
    def validate(self, user_input: str, user_id: Optional[str] = None) -> LengthValidationResult:
        """
        Validate input length through multi-layer checks
        
        Args:
            user_input: User's input text
            user_id: Optional user ID for rate limiting
            
        Returns:
            LengthValidationResult with validation outcome
        """
        
        # Layer 1: Fast character count check (O(1) - instant)
        char_count = len(user_input)
        
        if char_count > self.MAX_CHARS:
            return LengthValidationResult(
                valid=False,
                reason=f"Input too long: {char_count:,} characters (max: {self.MAX_CHARS:,})",
                char_count=char_count,
                token_count=0,
                estimated_cost=0.0,
                recommended_action="block"
            )
        
        # Layer 2: Token estimation (O(n) - fast heuristic)
        token_count = self._estimate_tokens(user_input)
        
        if token_count > self.max_tokens:
            return LengthValidationResult(
                valid=False,
                reason=f"Token limit exceeded: {token_count:,} tokens (max: {self.max_tokens:,} for {self.tier} tier)",
                char_count=char_count,
                token_count=token_count,
                estimated_cost=self._estimate_cost(token_count),
                recommended_action="truncate" if token_count < self.max_tokens * 2 else "block"
            )
        
        # Layer 3: Rate limiting (if user_id provided)
        if user_id:
            rate_limit_result = self._check_rate_limits(user_id, token_count)
            if not rate_limit_result['valid']:
                return LengthValidationResult(
                    valid=False,
                    reason=rate_limit_result['reason'],
                    char_count=char_count,
                    token_count=token_count,
                    estimated_cost=0.0,
                    recommended_action="rate_limit"
                )
        
        # All checks passed
        return LengthValidationResult(
            valid=True,
            reason="Input length valid",
            char_count=char_count,
            token_count=token_count,
            estimated_cost=self._estimate_cost(token_count),
            recommended_action="allow"
        )
    
    
    def _estimate_tokens(self, text: str) -> int:
        """
        Estimate token count using fast heuristics
        
        Rule of thumb:
        - English: ~4 characters per token
        - Code: ~3 characters per token
        - Special chars: ~2 characters per token
        
        This is a conservative estimate (may slightly overestimate)
        
        Args:
            text: Input text
            
        Returns:
            Estimated number of tokens
        """
        # Count different character types
        alphanumeric = len(re.findall(r'[a-zA-Z0-9]', text))
        whitespace = len(re.findall(r'\s', text))
        special = len(text) - alphanumeric - whitespace
        
        # Estimate tokens
        # Alphanumeric: ~4 chars/token
        # Whitespace: usually not counted
        # Special: ~2 chars/token
        estimated_tokens = (alphanumeric / 4) + (special / 2)
        
        # Add some buffer (10%) for safety
        return int(estimated_tokens * 1.1)
    
    
    def _estimate_cost(self, token_count: int) -> float:
        """
        Estimate API cost for this request
        
        Assumptions:
        - Input tokens: actual count
        - Output tokens: 2x input (conservative estimate)
        
        Args:
            token_count: Number of input tokens
            
        Returns:
            Estimated cost in USD
        """
        input_cost = (token_count / 1000) * self.COST_PER_1K_INPUT_TOKENS
        output_cost = (token_count * 2 / 1000) * self.COST_PER_1K_OUTPUT_TOKENS
        
        return input_cost + output_cost
    
    
    def _check_rate_limits(self, user_id: str, token_count: int) -> Dict:
        """
        Check if user exceeds rate limits
        
        Tracks:
        - Requests per minute
        - Tokens per minute
        
        Args:
            user_id: User identifier
            token_count: Tokens in current request
            
        Returns:
            Dict with 'valid' and 'reason' keys
        """
        current_time = time.time()
        minute_ago = current_time - 60
        
        # Clean old entries (older than 1 minute)
        self.request_counts[user_id] = [
            t for t in self.request_counts[user_id] if t > minute_ago
        ]
        self.token_counts[user_id] = [
            (t, tokens) for t, tokens in self.token_counts[user_id] if t > minute_ago
        ]
        
        # Check request rate
        requests_last_minute = len(self.request_counts[user_id])
        if requests_last_minute >= self.MAX_REQUESTS_PER_MINUTE:
            return {
                'valid': False,
                'reason': f"Rate limit exceeded: {requests_last_minute} requests in last minute (max: {self.MAX_REQUESTS_PER_MINUTE})"
            }
        
        # Check token rate
        tokens_last_minute = sum(tokens for _, tokens in self.token_counts[user_id])
        if tokens_last_minute + token_count > self.MAX_TOKENS_PER_MINUTE:
            return {
                'valid': False,
                'reason': f"Token rate limit exceeded: {tokens_last_minute + token_count:,} tokens in last minute (max: {self.MAX_TOKENS_PER_MINUTE:,})"
            }
        
        # Record this request
        self.request_counts[user_id].append(current_time)
        self.token_counts[user_id].append((current_time, token_count))
        
        return {'valid': True, 'reason': 'Within rate limits'}
    
    
    def truncate_safely(self, text: str, max_tokens: Optional[int] = None) -> str:
        """
        Safely truncate text to fit within token limit
        
        Strategy:
        - Estimate token-to-character ratio
        - Truncate at character level
        - Add clear indicator
        
        Args:
            text: Input text
            max_tokens: Maximum tokens (uses default if None)
            
        Returns:
            Truncated text with indicator
        """
        max_tokens = max_tokens or self.max_tokens
        
        # Estimate characters per token (conservative: 3)
        max_chars = max_tokens * 3
        
        if len(text) <= max_chars:
            return text
        
        # Truncate at sentence boundary if possible
        truncated = text[:max_chars]
        
        # Try to end at sentence
        last_period = truncated.rfind('.')
        last_newline = truncated.rfind('\n')
        
        cut_point = max(last_period, last_newline)
        if cut_point > max_chars * 0.8:  # Only if we don't lose too much
            truncated = truncated[:cut_point + 1]
        
        # Add clear indicator
        return truncated + "\n\n[... Content truncated due to length limit ...]"
    
    
    def get_stats(self, user_id: str) -> Dict:
        """
        Get usage statistics for a user
        
        Args:
            user_id: User identifier
            
        Returns:
            Dict with detailed usage stats
        """
        current_time = time.time()
        minute_ago = current_time - 60
        hour_ago = current_time - 3600
        day_ago = current_time - 86400
        
        # Helper to count items in time window
        def count_in_window(items: List, cutoff: float) -> int:
            return sum(1 for t in items if t > cutoff)
        
        def sum_tokens_in_window(items: List[Tuple[float, int]], cutoff: float) -> int:
            return sum(tokens for t, tokens in items if t > cutoff)
        
        # Get user's data
        requests = self.request_counts.get(user_id, [])
        tokens = self.token_counts.get(user_id, [])
        
        # Calculate stats
        tokens_day = sum_tokens_in_window(tokens, day_ago)
        
        return {
            'user_id': user_id,
            'tier': self.tier,
            'limits': {
                'max_tokens_per_request': self.max_tokens,
                'max_requests_per_minute': self.MAX_REQUESTS_PER_MINUTE,
                'max_tokens_per_minute': self.MAX_TOKENS_PER_MINUTE
            },
            'usage': {
                'requests': {
                    'last_minute': count_in_window(requests, minute_ago),
                    'last_hour': count_in_window(requests, hour_ago),
                    'last_day': count_in_window(requests, day_ago)
                },
                'tokens': {
                    'last_minute': sum_tokens_in_window(tokens, minute_ago),
                    'last_hour': sum_tokens_in_window(tokens, hour_ago),
                    'last_day': tokens_day
                }
            },
            'estimated_cost_today': self._estimate_cost(tokens_day),
            'within_limits': {
                'requests': count_in_window(requests, minute_ago) < self.MAX_REQUESTS_PER_MINUTE,
                'tokens': sum_tokens_in_window(tokens, minute_ago) < self.MAX_TOKENS_PER_MINUTE
            }
        }


# Export
__all__ = ['LengthValidator', 'LengthValidationResult']

