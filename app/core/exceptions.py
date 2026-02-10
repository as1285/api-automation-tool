from typing import Optional, Dict, Any

class APIAutomationError(Exception):
    """接口自动化错误基类"""
    
    def __init__(self, message: str, code: int = 500, details: Optional[Dict[str, Any]] = None, solution: Optional[str] = None):
        """
        初始化错误
        
        Args:
            message: 错误消息
            code: 错误代码
            details: 错误详细信息
            solution: 解决方案建议
        """
        self.message = message
        self.code = code
        self.details = details or {}
        self.solution = solution
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'code': self.code,
            'message': self.message,
            'details': self.details,
            'solution': self.solution
        }

class DocParseError(APIAutomationError):
    """文档解析错误"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None, solution: Optional[str] = None):
        super().__init__(message, code=400, details=details, solution=solution)

class NetworkError(APIAutomationError):
    """网络错误"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None, solution: Optional[str] = None):
        super().__init__(message, code=503, details=details, solution=solution)

class TestExecutionError(APIAutomationError):
    """测试执行错误"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None, solution: Optional[str] = None):
        super().__init__(message, code=500, details=details, solution=solution)

class ReportGenerateError(APIAutomationError):
    """报告生成错误"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None, solution: Optional[str] = None):
        super().__init__(message, code=500, details=details, solution=solution)

class ConfigError(APIAutomationError):
    """配置错误"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None, solution: Optional[str] = None):
        super().__init__(message, code=400, details=details, solution=solution)

class ValidationError(APIAutomationError):
    """验证错误"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None, solution: Optional[str] = None):
        super().__init__(message, code=400, details=details, solution=solution)

# 错误代码定义
ERROR_CODES = {
    # 文档解析错误
    'DOC_PARSE_FAILED': 40001,
    'DOC_FORMAT_ERROR': 40002,
    'DOC_NOT_FOUND': 40003,
    
    # 网络错误
    'NETWORK_TIMEOUT': 50301,
    'NETWORK_CONNECTION_ERROR': 50302,
    'NETWORK_UNKNOWN_ERROR': 50303,
    
    # 测试执行错误
    'TEST_EXECUTION_FAILED': 50001,
    'TEST_CASE_INVALID': 50002,
    
    # 报告生成错误
    'REPORT_GENERATE_FAILED': 50011,
    'REPORT_SAVE_FAILED': 50012,
    
    # 配置错误
    'CONFIG_LOAD_FAILED': 40011,
    'CONFIG_INVALID': 40012,
    
    # 验证错误
    'VALIDATION_FAILED': 40021,
    'PARAMETER_MISSING': 40022
}

# 错误解决方案映射
ERROR_SOLUTIONS = {
    'DOC_PARSE_FAILED': '检查文档格式是否正确，确保是有效的Swagger/OpenAPI文档',
    'DOC_FORMAT_ERROR': '确保文档格式正确，YAML格式需要正确的缩进，JSON格式需要正确的语法',
    'DOC_NOT_FOUND': '检查文档路径或URL是否正确，确保文件存在或URL可访问',
    'NETWORK_TIMEOUT': '检查网络连接是否正常，增加超时时间，或尝试在网络状况较好时重试',
    'NETWORK_CONNECTION_ERROR': '检查网络连接是否正常，确保目标服务器可访问',
    'NETWORK_UNKNOWN_ERROR': '检查网络连接，查看服务器日志，或联系网络管理员',
    'TEST_EXECUTION_FAILED': '检查测试用例配置是否正确，确保基础URL可访问',
    'TEST_CASE_INVALID': '检查测试用例格式是否正确，确保所有必要字段都已填写',
    'REPORT_GENERATE_FAILED': '检查测试结果是否存在，确保报告生成目录可写',
    'REPORT_SAVE_FAILED': '检查报告保存路径是否存在，确保有写入权限',
    'CONFIG_LOAD_FAILED': '检查配置文件格式是否正确，确保文件存在',
    'CONFIG_INVALID': '检查配置项是否正确，确保所有必要的配置项都已设置',
    'VALIDATION_FAILED': '检查输入参数是否符合要求，确保所有必填字段都已填写',
    'PARAMETER_MISSING': '确保所有必要的参数都已提供，检查参数名称是否正确'
}

# 错误处理工具函数
def get_error_solution(error_code: str) -> str:
    """获取错误解决方案"""
    return ERROR_SOLUTIONS.get(error_code, '请检查相关配置和输入，或联系技术支持')

def create_error(error_type: str, message: str, details: Optional[Dict[str, Any]] = None) -> APIAutomationError:
    """
    创建错误实例
    
    Args:
        error_type: 错误类型
        message: 错误消息
        details: 错误详细信息
    
    Returns:
        APIAutomationError: 错误实例
    """
    solution = get_error_solution(error_type)
    
    error_map = {
        'DOC_PARSE_FAILED': DocParseError,
        'DOC_FORMAT_ERROR': DocParseError,
        'DOC_NOT_FOUND': DocParseError,
        'NETWORK_TIMEOUT': NetworkError,
        'NETWORK_CONNECTION_ERROR': NetworkError,
        'NETWORK_UNKNOWN_ERROR': NetworkError,
        'TEST_EXECUTION_FAILED': TestExecutionError,
        'TEST_CASE_INVALID': TestExecutionError,
        'REPORT_GENERATE_FAILED': ReportGenerateError,
        'REPORT_SAVE_FAILED': ReportGenerateError,
        'CONFIG_LOAD_FAILED': ConfigError,
        'CONFIG_INVALID': ConfigError,
        'VALIDATION_FAILED': ValidationError,
        'PARAMETER_MISSING': ValidationError
    }
    
    error_class = error_map.get(error_type, APIAutomationError)
    return error_class(message, details=details, solution=solution)
