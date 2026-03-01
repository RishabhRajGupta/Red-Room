"""API pool manager with automatic cycling, load balancing, and failover."""

import random
import time
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import structlog

logger = structlog.get_logger()


@dataclass
class APIKey:
    """Represents a single API key with usage tracking."""
    
    provider: str  # gemini, openai, anthropic, etc.
    key: str
    name: str = ""  # Optional friendly name
    
    # Rate limiting
    requests_per_minute: int = 60
    requests_per_day: int = 1000
    
    # Usage tracking
    requests_this_minute: int = 0
    requests_today: int = 0
    total_requests: int = 0
    
    # Error tracking
    consecutive_errors: int = 0
    last_error: Optional[str] = None
    last_error_time: Optional[datetime] = None
    
    # Timing
    last_request_time: Optional[datetime] = None
    last_reset_minute: datetime = field(default_factory=datetime.now)
    last_reset_day: datetime = field(default_factory=datetime.now)
    
    # Status
    is_active: bool = True
    cooldown_until: Optional[datetime] = None
    
    def is_available(self) -> bool:
        """Check if API key is available for use."""
        now = datetime.now()
        
        # Check if in cooldown
        if self.cooldown_until and now < self.cooldown_until:
            return False
        
        # Check if disabled
        if not self.is_active:
            return False
        
        # Reset counters if needed
        self._reset_counters(now)
        
        # Check rate limits
        if self.requests_this_minute >= self.requests_per_minute:
            return False
        
        if self.requests_today >= self.requests_per_day:
            return False
        
        return True
    
    def _reset_counters(self, now: datetime):
        """Reset usage counters based on time."""
        # Reset minute counter
        if now - self.last_reset_minute >= timedelta(minutes=1):
            self.requests_this_minute = 0
            self.last_reset_minute = now
        
        # Reset day counter
        if now - self.last_reset_day >= timedelta(days=1):
            self.requests_today = 0
            self.last_reset_day = now
    
    def record_request(self):
        """Record a successful request."""
        now = datetime.now()
        self._reset_counters(now)
        
        self.requests_this_minute += 1
        self.requests_today += 1
        self.total_requests += 1
        self.last_request_time = now
        self.consecutive_errors = 0
    
    def record_error(self, error: str):
        """Record an error."""
        self.consecutive_errors += 1
        self.last_error = error
        self.last_error_time = datetime.now()
        
        # Put in cooldown if too many errors
        if self.consecutive_errors >= 3:
            self.cooldown_until = datetime.now() + timedelta(minutes=5)
            logger.warning(
                "api_key_cooldown",
                provider=self.provider,
                name=self.name,
                consecutive_errors=self.consecutive_errors
            )
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics."""
        return {
            "provider": self.provider,
            "name": self.name,
            "requests_this_minute": self.requests_this_minute,
            "requests_today": self.requests_today,
            "total_requests": self.total_requests,
            "consecutive_errors": self.consecutive_errors,
            "is_active": self.is_active,
            "is_available": self.is_available(),
            "utilization_minute": f"{(self.requests_this_minute / self.requests_per_minute) * 100:.1f}%",
            "utilization_day": f"{(self.requests_today / self.requests_per_day) * 100:.1f}%"
        }


class APIPool:
    """
    Manages a pool of API keys with automatic cycling and load balancing.
    
    Features:
    - Automatic failover when rate limits hit
    - Random selection for load distribution
    - Weighted selection based on remaining capacity
    - Error tracking and cooldown
    - Usage statistics
    """
    
    def __init__(self):
        """Initialize API pool."""
        self.api_keys: Dict[str, List[APIKey]] = {}  # provider -> [APIKey]
        self.selection_strategy = "weighted_random"  # random, round_robin, weighted_random
        self._round_robin_index: Dict[str, int] = {}
        
        logger.info("api_pool_initialized")
    
    def add_api_key(
        self,
        provider: str,
        key: str,
        name: str = "",
        requests_per_minute: int = 60,
        requests_per_day: int = 1000
    ):
        """
        Add an API key to the pool.
        
        Args:
            provider: Provider name (gemini, openai, anthropic, etc.)
            key: API key
            name: Optional friendly name
            requests_per_minute: Rate limit per minute
            requests_per_day: Rate limit per day
        """
        if provider not in self.api_keys:
            self.api_keys[provider] = []
        
        api_key = APIKey(
            provider=provider,
            key=key,
            name=name or f"{provider}_{len(self.api_keys[provider]) + 1}",
            requests_per_minute=requests_per_minute,
            requests_per_day=requests_per_day
        )
        
        self.api_keys[provider].append(api_key)
        
        logger.info(
            "api_key_added",
            provider=provider,
            name=api_key.name,
            total_keys=len(self.api_keys[provider])
        )
    
    def get_api_key(self, provider: str) -> Optional[APIKey]:
        """
        Get an available API key for the provider.
        
        Uses intelligent selection strategy:
        - weighted_random: Randomly select with preference for less-used keys
        - random: Pure random selection
        - round_robin: Cycle through keys in order
        
        Args:
            provider: Provider name
            
        Returns:
            Available APIKey or None if all exhausted
        """
        if provider not in self.api_keys:
            logger.warning("no_api_keys_for_provider", provider=provider)
            return None
        
        keys = self.api_keys[provider]
        available_keys = [k for k in keys if k.is_available()]
        
        if not available_keys:
            logger.warning(
                "all_api_keys_exhausted",
                provider=provider,
                total_keys=len(keys)
            )
            return None
        
        # Select key based on strategy
        if self.selection_strategy == "weighted_random":
            selected = self._weighted_random_selection(available_keys)
        elif self.selection_strategy == "random":
            selected = random.choice(available_keys)
        elif self.selection_strategy == "round_robin":
            selected = self._round_robin_selection(provider, available_keys)
        else:
            selected = random.choice(available_keys)
        
        logger.info(
            "api_key_selected",
            provider=provider,
            name=selected.name,
            strategy=self.selection_strategy,
            available_keys=len(available_keys)
        )
        
        return selected
    
    def _weighted_random_selection(self, keys: List[APIKey]) -> APIKey:
        """
        Select key with weighted random based on remaining capacity.
        
        Keys with more remaining capacity have higher chance of selection.
        """
        # Calculate weights based on remaining capacity
        weights = []
        for key in keys:
            # Weight based on remaining capacity (both minute and day)
            minute_remaining = key.requests_per_minute - key.requests_this_minute
            day_remaining = key.requests_per_day - key.requests_today
            
            # Normalize to 0-1 range
            minute_capacity = minute_remaining / key.requests_per_minute
            day_capacity = day_remaining / key.requests_per_day
            
            # Combined weight (favor keys with more capacity)
            weight = (minute_capacity * 0.7 + day_capacity * 0.3) * 100
            weights.append(max(weight, 1))  # Minimum weight of 1
        
        # Weighted random selection
        return random.choices(keys, weights=weights)[0]
    
    def _round_robin_selection(self, provider: str, keys: List[APIKey]) -> APIKey:
        """Select key using round-robin strategy."""
        if provider not in self._round_robin_index:
            self._round_robin_index[provider] = 0
        
        index = self._round_robin_index[provider] % len(keys)
        self._round_robin_index[provider] += 1
        
        return keys[index]
    
    def record_success(self, api_key: APIKey):
        """Record successful API call."""
        api_key.record_request()
        
        logger.debug(
            "api_request_success",
            provider=api_key.provider,
            name=api_key.name,
            requests_today=api_key.requests_today
        )
    
    def record_error(self, api_key: APIKey, error: str):
        """Record API error."""
        api_key.record_error(error)
        
        logger.warning(
            "api_request_error",
            provider=api_key.provider,
            name=api_key.name,
            error=error,
            consecutive_errors=api_key.consecutive_errors
        )
    
    def get_pool_stats(self) -> Dict[str, Any]:
        """Get statistics for all API keys."""
        stats = {
            "total_providers": len(self.api_keys),
            "total_keys": sum(len(keys) for keys in self.api_keys.values()),
            "selection_strategy": self.selection_strategy,
            "providers": {}
        }
        
        for provider, keys in self.api_keys.items():
            available = sum(1 for k in keys if k.is_available())
            total_requests = sum(k.total_requests for k in keys)
            
            stats["providers"][provider] = {
                "total_keys": len(keys),
                "available_keys": available,
                "total_requests": total_requests,
                "keys": [k.get_usage_stats() for k in keys]
            }
        
        return stats
    
    def set_selection_strategy(self, strategy: str):
        """
        Set API key selection strategy.
        
        Args:
            strategy: 'weighted_random', 'random', or 'round_robin'
        """
        valid_strategies = ["weighted_random", "random", "round_robin"]
        if strategy not in valid_strategies:
            raise ValueError(f"Invalid strategy. Must be one of: {valid_strategies}")
        
        self.selection_strategy = strategy
        logger.info("selection_strategy_changed", strategy=strategy)
    
    def disable_key(self, provider: str, name: str):
        """Disable a specific API key."""
        if provider in self.api_keys:
            for key in self.api_keys[provider]:
                if key.name == name:
                    key.is_active = False
                    logger.info("api_key_disabled", provider=provider, name=name)
                    return
    
    def enable_key(self, provider: str, name: str):
        """Enable a specific API key."""
        if provider in self.api_keys:
            for key in self.api_keys[provider]:
                if key.name == name:
                    key.is_active = True
                    key.consecutive_errors = 0
                    key.cooldown_until = None
                    logger.info("api_key_enabled", provider=provider, name=name)
                    return
    
    def print_stats(self):
        """Print pool statistics in a nice format."""
        from rich.console import Console
        from rich.table import Table
        
        console = Console()
        stats = self.get_pool_stats()
        
        console.print(f"\n[bold]API Pool Statistics[/bold]")
        console.print(f"Total Providers: {stats['total_providers']}")
        console.print(f"Total Keys: {stats['total_keys']}")
        console.print(f"Selection Strategy: {stats['selection_strategy']}\n")
        
        for provider, provider_stats in stats["providers"].items():
            table = Table(title=f"{provider.upper()} API Keys")
            
            table.add_column("Name", style="cyan")
            table.add_column("Status", style="green")
            table.add_column("Requests (Min)", style="yellow")
            table.add_column("Requests (Day)", style="yellow")
            table.add_column("Total", style="blue")
            table.add_column("Errors", style="red")
            
            for key_stats in provider_stats["keys"]:
                status = "✅ Available" if key_stats["is_available"] else "❌ Unavailable"
                errors = str(key_stats["consecutive_errors"]) if key_stats["consecutive_errors"] > 0 else "-"
                
                table.add_row(
                    key_stats["name"],
                    status,
                    f"{key_stats['requests_this_minute']} ({key_stats['utilization_minute']})",
                    f"{key_stats['requests_today']} ({key_stats['utilization_day']})",
                    str(key_stats["total_requests"]),
                    errors
                )
            
            console.print(table)
            console.print()


# Global API pool instance
_api_pool: Optional[APIPool] = None


def get_api_pool() -> APIPool:
    """Get global API pool instance."""
    global _api_pool
    if _api_pool is None:
        _api_pool = APIPool()
    return _api_pool


def load_api_keys_from_env():
    """
    Load API keys from environment variables.
    
    Supports two formats:
    1. Comma-separated: GEMINI_API_KEYS=key1,key2,key3
    2. Individual: GEMINI_API_KEY, GEMINI_API_KEY_2, GEMINI_API_KEY_3
    
    Comma-separated format takes precedence.
    """
    import os
    
    pool = get_api_pool()
    
    # Provider configurations
    providers = {
        "gemini": {
            "keys_var": "GEMINI_API_KEYS",  # Comma-separated
            "key_var": "GEMINI_API_KEY",    # Single key
            "rpm": 60,  # requests per minute
            "rpd": 1500  # requests per day (free tier)
        },
        "openai": {
            "keys_var": "OPENAI_API_KEYS",
            "key_var": "OPENAI_API_KEY",
            "rpm": 60,
            "rpd": 200  # free tier is very limited
        },
        "anthropic": {
            "keys_var": "ANTHROPIC_API_KEYS",
            "key_var": "ANTHROPIC_API_KEY",
            "rpm": 50,
            "rpd": 1000
        }
    }
    
    for provider, config in providers.items():
        keys_added = 0
        
        # Check for comma-separated keys first (preferred format)
        keys_str = os.getenv(config["keys_var"])
        if keys_str:
            # Split by comma and strip whitespace
            keys = [k.strip() for k in keys_str.split(",") if k.strip()]
            
            for idx, key in enumerate(keys, 1):
                pool.add_api_key(
                    provider=provider,
                    key=key,
                    name=f"{provider}_{idx}",
                    requests_per_minute=config["rpm"],
                    requests_per_day=config["rpd"]
                )
                keys_added += 1
            
            logger.info(
                "loaded_comma_separated_keys",
                provider=provider,
                count=keys_added
            )
        else:
            # Fallback to individual key format
            # Check for primary key
            key = os.getenv(config["key_var"])
            if key:
                pool.add_api_key(
                    provider=provider,
                    key=key,
                    name=f"{provider}_1",
                    requests_per_minute=config["rpm"],
                    requests_per_day=config["rpd"]
                )
                keys_added += 1
            
            # Check for additional keys (KEY_2, KEY_3, etc.)
            index = 2
            while True:
                key = os.getenv(f"{config['key_var']}_{index}")
                if not key:
                    break
                
                pool.add_api_key(
                    provider=provider,
                    key=key,
                    name=f"{provider}_{index}",
                    requests_per_minute=config["rpm"],
                    requests_per_day=config["rpd"]
                )
                keys_added += 1
                index += 1
            
            if keys_added > 0:
                logger.info(
                    "loaded_individual_keys",
                    provider=provider,
                    count=keys_added
                )
    
    total_keys = pool.get_pool_stats()["total_keys"]
    logger.info("api_keys_loaded_from_env", total_keys=total_keys)
    
    if total_keys == 0:
        logger.warning("no_api_keys_found", note="Set GEMINI_API_KEYS, OPENAI_API_KEYS, or ANTHROPIC_API_KEYS")
    
    return pool
