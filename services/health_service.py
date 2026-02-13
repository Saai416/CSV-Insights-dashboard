import time
from typing import Dict, Any
from datetime import datetime
from models import db
from services.llm_service import LLMService


class HealthService:
    """Service for production health checks."""
    
    @staticmethod
    def check_backend() -> Dict[str, Any]:
        """Check backend health.
        
        Backend is always "up" if route is reachable.
        
        Returns:
            Status dictionary
        """
        start_time = time.time()
        # Backend is up if we can execute this code
        end_time = time.time()
        response_time_ms = int((end_time - start_time) * 1000)
        
        return {
            'status': 'up',
            'response_time_ms': max(1, response_time_ms)  # Minimum 1ms
        }
    
    @staticmethod
    def check_database() -> Dict[str, Any]:
        """Check database health.
        
        Executes lightweight test query (SELECT 1).
        Measures response time.
        Catches exceptions and marks as "down" on failure.
        
        Returns:
            Status dictionary
        """
        try:
            start_time = time.time()
            
            # Execute test query
            result = db.session.execute(db.text('SELECT 1')).fetchone()
            
            end_time = time.time()
            response_time_ms = int((end_time - start_time) * 1000)
            
            if result and result[0] == 1:
                return {
                    'status': 'up',
                    'response_time_ms': max(1, response_time_ms)
                }
            else:
                return {
                    'status': 'down',
                    'response_time_ms': 0,
                    'error': 'Unexpected query result'
                }
                
        except Exception as e:
            # Database is down
            return {
                'status': 'down',
                'response_time_ms': 0,
                'error': 'Database connection failed'
            }
    
    @staticmethod
    def check_llm() -> Dict[str, Any]:
        """Check LLM service health.
        
        Sends minimal test prompt: "Respond with OK only."
        Sets 5-second timeout.
        Measures response time.
        
        Returns:
            Status dictionary
        """
        try:
            llm_service = LLMService()
            is_healthy, response_time_ms, error = llm_service.health_check()
            
            if is_healthy:
                return {
                    'status': 'up',
                    'response_time_ms': response_time_ms
                }
            else:
                return {
                    'status': 'down',
                    'response_time_ms': response_time_ms,
                    'error': error
                }
                
        except Exception as e:
            return {
                'status': 'down',
                'response_time_ms': 0,
                'error': 'LLM health check failed'
            }
    
    @staticmethod
    def calculate_overall_status(services: Dict[str, Dict[str, Any]]) -> str:
        """Calculate overall system health status.
        
        Rules:
        - All services up → "healthy"
        - 1 service down → "degraded"
        - 2+ services down → "unhealthy"
        
        Args:
            services: Dictionary of service statuses
            
        Returns:
            Overall status string
        """
        down_count = sum(1 for service in services.values() if service.get('status') == 'down')
        
        if down_count == 0:
            return 'healthy'
        elif down_count == 1:
            return 'degraded'
        else:
            return 'unhealthy'
    
    @staticmethod
    def get_full_status() -> Dict[str, Any]:
        """Get full system health status.
        
        This method is fail-safe - it will never crash.
        All checks are wrapped in try/except.
        Even if DB and LLM fail, it returns valid JSON.
        
        Returns:
            Complete status dictionary
        """
        try:
            # Perform all health checks
            backend_status = HealthService.check_backend()
            database_status = HealthService.check_database()
            llm_status = HealthService.check_llm()
            
            services = {
                'backend': backend_status,
                'database': database_status,
                'llm': llm_status
            }
            
            # Calculate overall status
            overall_status = HealthService.calculate_overall_status(services)
            
            return {
                'overall_status': overall_status,
                'services': services,
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }
            
        except Exception as e:
            # Fail-safe: return degraded status
            return {
                'overall_status': 'unhealthy',
                'services': {
                    'backend': {'status': 'down', 'response_time_ms': 0, 'error': 'Health check system error'},
                    'database': {'status': 'down', 'response_time_ms': 0, 'error': 'Unknown'},
                    'llm': {'status': 'down', 'response_time_ms': 0, 'error': 'Unknown'}
                },
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }
