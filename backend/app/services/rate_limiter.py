from typing import Dict, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class RateLimiter:
    def __init__(
        self,
        hourly_limit: int = 10,
        daily_limit: int = 30,
        global_monthly_limit: int = 500,
        cooldown_seconds: int = 2
    ):
        self.hourly_limit = hourly_limit
        self.daily_limit = daily_limit
        self.global_monthly_limit = global_monthly_limit
        self.cooldown_seconds = cooldown_seconds
        
        self.hourly_counts: Dict[str, Tuple[datetime, int]] = {}
        self.daily_counts: Dict[str, Tuple[datetime, int]] = {}
        self.last_request: Dict[str, datetime] = {}
        
        self.global_count = 0
        self.global_reset_date = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if datetime.now() < self.global_reset_date:
            self.global_reset_date = (self.global_reset_date - timedelta(days=1)).replace(day=1)
    
    def check_rate_limit(self, client_ip: str) -> Tuple[bool, str]:
        now = datetime.now()
        
        if self.global_count >= self.global_monthly_limit:
            logger.warning(f"Global monthly limit reached: {self.global_count}/{self.global_monthly_limit}")
            return False, "Service temporarily unavailable due to usage limits."
        
        hourly_allowed, hourly_msg = self._check_hourly_limit(client_ip, now)
        if not hourly_allowed:
            return False, hourly_msg
        
        daily_allowed, daily_msg = self._check_daily_limit(client_ip, now)
        if not daily_allowed:
            return False, daily_msg
        
        if client_ip in self.last_request:
            time_since_last = (now - self.last_request[client_ip]).total_seconds()
            if time_since_last < self.cooldown_seconds:
                return False, f"Please wait {self.cooldown_seconds} seconds between requests."
        
        return True, ""
    
    def record_request(self, client_ip: str) -> None:
        now = datetime.now()
        
        self.global_count += 1
        
        if client_ip in self.hourly_counts:
            reset_time, count = self.hourly_counts[client_ip]
            self.hourly_counts[client_ip] = (reset_time, count + 1)
        else:
            self.hourly_counts[client_ip] = (now + timedelta(hours=1), 1)
        
        if client_ip in self.daily_counts:
            reset_time, count = self.daily_counts[client_ip]
            self.daily_counts[client_ip] = (reset_time, count + 1)
        else:
            self.daily_counts[client_ip] = (now + timedelta(days=1), 1)
        
        self.last_request[client_ip] = now
        
        logger.info(f"Request from {client_ip} - Hourly: {self.hourly_counts[client_ip][1]}/{self.hourly_limit}, Daily: {self.daily_counts[client_ip][1]}/{self.daily_limit}, Global: {self.global_count}/{self.global_monthly_limit}")
    
    def _check_hourly_limit(self, client_ip: str, now: datetime) -> Tuple[bool, str]:
        if client_ip in self.hourly_counts:
            reset_time, count = self.hourly_counts[client_ip]
            if now >= reset_time:
                self.hourly_counts[client_ip] = (now + timedelta(hours=1), 0)
                return True, ""
            if count >= self.hourly_limit:
                return False, "Hourly demo limit reached. Please try again later."
        return True, ""
    
    def _check_daily_limit(self, client_ip: str, now: datetime) -> Tuple[bool, str]:
        if client_ip in self.daily_counts:
            reset_time, count = self.daily_counts[client_ip]
            if now >= reset_time:
                self.daily_counts[client_ip] = (now + timedelta(days=1), 0)
                return True, ""
            if count >= self.daily_limit:
                return False, "Daily demo limit reached. Please try tomorrow."
        return True, ""
    
    def reset_monthly(self) -> None:
        now = datetime.now()
        if now.month != self.global_reset_date.month or now.year != self.global_reset_date.year:
            self.global_count = 0
            self.global_reset_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            logger.info("Monthly global limit reset")
    
    def get_stats(self, client_ip: str = None) -> Dict:
        if client_ip:
            hourly_count = self.hourly_counts.get(client_ip, (None, 0))[1]
            daily_count = self.daily_counts.get(client_ip, (None, 0))[1]
            return {
                "hourly_count": hourly_count,
                "hourly_limit": self.hourly_limit,
                "daily_count": daily_count,
                "daily_limit": self.daily_limit,
                "global_count": self.global_count,
                "global_limit": self.global_monthly_limit
            }
        return {
            "global_count": self.global_count,
            "global_limit": self.global_monthly_limit
        }
