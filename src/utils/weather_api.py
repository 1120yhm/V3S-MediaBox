#!/usr/bin/env python3
"""
天气API模块

此模块提供天气数据获取功能。
"""
import sys

try:
    import requests
    import json
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

class WeatherAPI:
    """
    天气API类
    
    获取并处理天气数据。
    """
    
    def __init__(self):
        """初始化天气API"""
        self.api_key = "So9YeNhWSdqYR8mMX"
        self.city_id = "101280601"  # 深圳
        self.base_url = "https://api.seniverse.com/v3/weather/now.json"
    
    def get_weather(self):
        """
        获取天气信息
        
        Returns:
            str: 格式化的天气信息
        """
        if not REQUESTS_AVAILABLE:
            # 模拟天气数据
            import random
            weather_list = [
                "深圳\n温度：25℃  天气：晴",
                "深圳\n温度：22℃  天气：阴",
                "深圳\n温度：20℃  天气：雨",
                "深圳\n温度：18℃  天气：雪"
            ]
            return random.choice(weather_list)
        
        try:
            url = f"{self.base_url}?key={self.api_key}&location={self.city_id}&language=zh-CN&unit=c"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = json.loads(response.text)
                now = data["results"][0]["now"]
                city = data["results"][0]["location"]["name"]
                temp = now["temperature"]
                weather = now["text"]
                return f"{city}\n温度：{temp}℃  天气：{weather}"
            else:
                return f"天气请求失败\n状态码：{response.status_code}"
        except Exception as e:
            return f"天气加载失败\n{str(e)[:10]}"