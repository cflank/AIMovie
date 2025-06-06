"""
系统监控工具
云端版本 - API调用监控
"""

import time
import psutil
from prometheus_client import Counter, Histogram, Gauge, start_http_server
from loguru import logger

# 监控指标
API_REQUESTS_TOTAL = Counter('aimovie_api_requests_total', 'Total API requests', ['method', 'endpoint', 'status'])
API_REQUEST_DURATION = Histogram('aimovie_api_request_duration_seconds', 'API request duration')
MEMORY_USAGE = Gauge('aimovie_memory_bytes', 'Memory usage')
CPU_USAGE = Gauge('aimovie_cpu_percent', 'CPU usage percentage')
ACTIVE_TASKS = Gauge('aimovie_active_tasks', 'Number of active tasks')
CLOUD_API_CALLS = Counter('aimovie_cloud_api_calls_total', 'Total cloud API calls', ['service', 'status'])
CLOUD_API_COST = Counter('aimovie_cloud_api_cost_total', 'Total cloud API cost', ['service'])

class CloudMonitor:
    """云端服务监控器"""
    
    def __init__(self, port=9090):
        self.port = port
        self.running = False
        
    def start(self):
        """启动监控服务"""
        try:
            start_http_server(self.port)
            self.running = True
            logger.info(f"监控服务已启动: http://localhost:{self.port}")
        except Exception as e:
            logger.error(f"监控服务启动失败: {e}")
    
    def update_system_metrics(self):
        """更新系统指标"""
        try:
            # CPU使用率
            cpu_percent = psutil.cpu_percent()
            CPU_USAGE.set(cpu_percent)
            
            # 内存使用
            memory = psutil.virtual_memory()
            MEMORY_USAGE.set(memory.used)
            
        except Exception as e:
            logger.error(f"更新系统指标失败: {e}")
    
    def record_api_request(self, method: str, endpoint: str, status: int, duration: float):
        """记录API请求"""
        API_REQUESTS_TOTAL.labels(method=method, endpoint=endpoint, status=status).inc()
        API_REQUEST_DURATION.observe(duration)
    
    def record_cloud_api_call(self, service: str, status: str, cost: float = 0.0):
        """记录云端API调用"""
        CLOUD_API_CALLS.labels(service=service, status=status).inc()
        if cost > 0:
            CLOUD_API_COST.labels(service=service).inc(cost)
    
    def set_active_tasks(self, count: int):
        """设置活跃任务数"""
        ACTIVE_TASKS.set(count)

# 全局监控实例
monitor = CloudMonitor()

def start_monitoring(port=9090):
    """启动监控"""
    monitor.start()

def record_api_call(method: str, endpoint: str, status: int, duration: float):
    """记录API调用"""
    monitor.record_api_request(method, endpoint, status, duration)

def record_cloud_call(service: str, status: str, cost: float = 0.0):
    """记录云端服务调用"""
    monitor.record_cloud_api_call(service, status, cost)

def update_metrics():
    """更新指标"""
    monitor.update_system_metrics()