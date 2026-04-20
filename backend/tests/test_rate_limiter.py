import pytest
from datetime import datetime, timedelta
from app.services.rate_limiter import RateLimiter


class TestRateLimiter:
    
    def test_first_request_allowed(self):
        limiter = RateLimiter(hourly_limit=10, daily_limit=30)
        allowed, message = limiter.check_rate_limit("192.168.1.1")
        assert allowed is True
        assert message == ""
    
    def test_hourly_limit_enforcement(self):
        limiter = RateLimiter(hourly_limit=3, daily_limit=30, cooldown_seconds=0)
        client_ip = "192.168.1.1"
        
        for i in range(3):
            allowed, _ = limiter.check_rate_limit(client_ip)
            assert allowed is True
            limiter.record_request(client_ip)
        
        allowed, message = limiter.check_rate_limit(client_ip)
        assert allowed is False
        assert "Hourly demo limit reached" in message
    
    def test_daily_limit_enforcement(self):
        limiter = RateLimiter(hourly_limit=100, daily_limit=5, cooldown_seconds=0)
        client_ip = "192.168.1.2"
        
        for i in range(5):
            allowed, _ = limiter.check_rate_limit(client_ip)
            assert allowed is True
            limiter.record_request(client_ip)
        
        allowed, message = limiter.check_rate_limit(client_ip)
        assert allowed is False
        assert "Daily demo limit reached" in message
    
    def test_global_limit_enforcement(self):
        limiter = RateLimiter(hourly_limit=100, daily_limit=100, global_monthly_limit=5)
        
        for i in range(5):
            client_ip = f"192.168.1.{i}"
            allowed, _ = limiter.check_rate_limit(client_ip)
            assert allowed is True
            limiter.record_request(client_ip)
        
        allowed, message = limiter.check_rate_limit("192.168.1.100")
        assert allowed is False
        assert "Service temporarily unavailable" in message
    
    def test_cooldown_enforcement(self):
        limiter = RateLimiter(cooldown_seconds=5)
        client_ip = "192.168.1.3"
        
        allowed, _ = limiter.check_rate_limit(client_ip)
        assert allowed is True
        limiter.record_request(client_ip)
        
        allowed, message = limiter.check_rate_limit(client_ip)
        assert allowed is False
        assert "wait" in message.lower()
    
    def test_different_ips_independent(self):
        limiter = RateLimiter(hourly_limit=2, daily_limit=5)
        
        for i in range(2):
            limiter.record_request("192.168.1.1")
        
        allowed, _ = limiter.check_rate_limit("192.168.1.2")
        assert allowed is True
    
    def test_get_stats(self):
        limiter = RateLimiter(hourly_limit=10, daily_limit=30, global_monthly_limit=500)
        client_ip = "192.168.1.1"
        
        limiter.record_request(client_ip)
        limiter.record_request(client_ip)
        
        stats = limiter.get_stats(client_ip)
        assert stats["hourly_count"] == 2
        assert stats["daily_count"] == 2
        assert stats["global_count"] == 2
        assert stats["hourly_limit"] == 10
        assert stats["daily_limit"] == 30
