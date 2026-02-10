import os
import time
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

# 路径参数处理
def replace_path_params(path: str, params: Dict[str, Any]) -> str:
    """
    替换路径中的参数
    
    Args:
        path: 路径字符串，如 "/api/users/{id}"
        params: 参数字典，如 {"id": 123}
    
    Returns:
        str: 替换后的路径，如 "/api/users/123"
    """
    result = path
    for param_name, param_value in params.items():
        placeholder = f"{{{param_name}}}"
        if placeholder in result:
            result = result.replace(placeholder, str(param_value))
    return result

# 文件操作
def ensure_dir_exists(dir_path: str):
    """
    确保目录存在，如果不存在则创建
    
    Args:
        dir_path: 目录路径
    """
    if not os.path.exists(dir_path):
        os.makedirs(dir_path, exist_ok=True)

def get_file_extension(file_path: str) -> str:
    """
    获取文件扩展名
    
    Args:
        file_path: 文件路径
    
    Returns:
        str: 文件扩展名，不含点号
    """
    return os.path.splitext(file_path)[1].lstrip('.').lower()

# 时间处理
def get_timestamp() -> str:
    """
    获取当前时间戳
    
    Returns:
        str: 时间戳字符串，格式为 "20231225123456"
    """
    return datetime.now().strftime("%Y%m%d%H%M%S")

def format_time(seconds: float) -> str:
    """
    格式化时间
    
    Args:
        seconds: 秒数
    
    Returns:
        str: 格式化后的时间字符串
    """
    if seconds < 0.001:
        return f"{seconds * 1000000:.2f}μs"
    elif seconds < 1:
        return f"{seconds * 1000:.2f}ms"
    else:
        return f"{seconds:.2f}s"

# 数据验证
def is_valid_url(url: str) -> bool:
    """
    验证URL是否有效
    
    Args:
        url: URL字符串
    
    Returns:
        bool: 是否有效
    """
    return url.startswith('http://') or url.startswith('https://')

def is_valid_file(file_path: str) -> bool:
    """
    验证文件是否存在且有效
    
    Args:
        file_path: 文件路径
    
    Returns:
        bool: 是否有效
    """
    return os.path.exists(file_path) and os.path.isfile(file_path)

# 数据转换
def dict_to_str(data: Dict[str, Any], indent: int = 2) -> str:
    """
    将字典转换为字符串
    
    Args:
        data: 字典数据
        indent: 缩进空格数
    
    Returns:
        str: 格式化后的字符串
    """
    import json
    return json.dumps(data, ensure_ascii=False, indent=indent)

def str_to_dict(data_str: str) -> Dict[str, Any]:
    """
    将字符串转换为字典
    
    Args:
        data_str: 字符串数据
    
    Returns:
        Dict[str, Any]: 转换后的字典
    """
    import json
    try:
        return json.loads(data_str)
    except json.JSONDecodeError:
        return {}

# 列表操作
def chunk_list(lst: List[Any], size: int) -> List[List[Any]]:
    """
    将列表分块
    
    Args:
        lst: 原始列表
        size: 块大小
    
    Returns:
        List[List[Any]]: 分块后的列表
    """
    return [lst[i:i+size] for i in range(0, len(lst), size)]

# 字符串操作
def camel_to_snake(camel_str: str) -> str:
    """
    驼峰命名转下划线命名
    
    Args:
        camel_str: 驼峰命名字符串
    
    Returns:
        str: 下划线命名字符串
    """
    import re
    return re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', camel_str).lower()

def snake_to_camel(snake_str: str) -> str:
    """
    下划线命名转驼峰命名
    
    Args:
        snake_str: 下划线命名字符串
    
    Returns:
        str: 驼峰命名字符串
    """
    parts = snake_str.split('_')
    return parts[0] + ''.join(part.capitalize() for part in parts[1:])
