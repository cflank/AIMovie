class CostOptimizer:
    def __init__(self):
        self.api_costs = {
            'qwen-turbo': 0.008,      # ¥/1K tokens
            'ernie-bot': 0.012,       # ¥/1K tokens  
            'gpt-3.5': 0.014,        # ¥/1K tokens
            'aliyun-vision': 0.002,   # ¥/次
            'tencent-video': 0.005,   # ¥/分钟
            'xfyun-asr': 0.003,      # ¥/分钟
        }
        
    def select_optimal_provider(self, task_type: str, content_size: int):
        """根据任务类型和内容大小选择最优提供商"""
        if task_type == 'text_generation':
            if content_size < 1000:  # 小任务用通义千问
                return 'qwen-turbo'
            else:  # 大任务用文心一言
                return 'ernie-bot'
        elif task_type == 'vision':
            return 'aliyun-vision'  # 阿里云视觉最便宜
        elif task_type == 'speech':
            return 'xfyun-asr'      # 讯飞语音性价比高
        
    def estimate_cost(self, tasks: List[Dict]) -> float:
        """估算总成本"""
        total_cost = 0
        for task in tasks:
            provider = self.select_optimal_provider(
                task['type'], task['size']
            )
            cost = self.api_costs[provider] * task['units']
            total_cost += cost
        return total_cost