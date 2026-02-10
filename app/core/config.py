import os
from dotenv import load_dotenv
from typing import Dict, Any, Optional

# 加载环境变量
load_dotenv()

class Config:
    """配置管理类"""
    
    # 默认配置
    DEFAULT_CONFIG: Dict[str, Any] = {
        # 网络配置
        'DEFAULT_TIMEOUT': 30,
        'DEFAULT_RETRY_COUNT': 3,
        'DEFAULT_HEADERS': {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        },
        
        # 测试配置
        'DEFAULT_BASE_URL': '',
        'DEFAULT_EXPECTED_STATUS': 200,
        'TEST_CONCURRENCY': 5,
        
        # 报告配置
        'REPORT_DIR': 'reports',
        'HTML_REPORT_TEMPLATE': None,
        
        # 日志配置
        'LOG_LEVEL': 'INFO',
        'LOG_FILE': 'api_automation.log',
        
        # 文档解析配置
        'SUPPORTED_DOC_FORMATS': ['swagger', 'openapi', 'postman', 'rap', 'yapi'],
        'SWAGGER_VERSION_SUPPORT': ['2.0', '3.0'],
        
        # 界面配置
        'WINDOW_WIDTH': 1200,
        'WINDOW_HEIGHT': 800,
        'DEFAULT_FONT': 'Microsoft YaHei',
        'FONT_SIZE': 10
    }
    
    def __init__(self):
        """初始化配置"""
        self._config: Dict[str, Any] = self.DEFAULT_CONFIG.copy()
        self._load_from_env()
    
    def _load_from_env(self):
        """从环境变量加载配置"""
        # 网络配置
        if os.getenv('DEFAULT_TIMEOUT'):
            self._config['DEFAULT_TIMEOUT'] = int(os.getenv('DEFAULT_TIMEOUT'))
        if os.getenv('DEFAULT_RETRY_COUNT'):
            self._config['DEFAULT_RETRY_COUNT'] = int(os.getenv('DEFAULT_RETRY_COUNT'))
        
        # 测试配置
        if os.getenv('DEFAULT_BASE_URL'):
            self._config['DEFAULT_BASE_URL'] = os.getenv('DEFAULT_BASE_URL')
        if os.getenv('DEFAULT_EXPECTED_STATUS'):
            self._config['DEFAULT_EXPECTED_STATUS'] = int(os.getenv('DEFAULT_EXPECTED_STATUS'))
        if os.getenv('TEST_CONCURRENCY'):
            self._config['TEST_CONCURRENCY'] = int(os.getenv('TEST_CONCURRENCY'))
        
        # 报告配置
        if os.getenv('REPORT_DIR'):
            self._config['REPORT_DIR'] = os.getenv('REPORT_DIR')
        
        # 日志配置
        if os.getenv('LOG_LEVEL'):
            self._config['LOG_LEVEL'] = os.getenv('LOG_LEVEL')
        if os.getenv('LOG_FILE'):
            self._config['LOG_FILE'] = os.getenv('LOG_FILE')
    
    def get(self, key: str, default: Optional[Any] = None) -> Any:
        """获取配置项"""
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any):
        """设置配置项"""
        self._config[key] = value
    
    def update(self, config: Dict[str, Any]):
        """批量更新配置项"""
        self._config.update(config)
    
    def get_all(self) -> Dict[str, Any]:
        """获取所有配置项"""
        return self._config.copy()
    
    def load_from_file(self, file_path: str):
        """从配置文件加载配置"""
        try:
            import yaml
            with open(file_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                if config:
                    self.update(config)
        except Exception as e:
            print(f"加载配置文件失败: {e}")

# 创建全局配置实例
config = Config()
