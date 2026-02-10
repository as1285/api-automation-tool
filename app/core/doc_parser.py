import requests
import yaml
import json
from typing import Dict, List, Any
from app.core.exceptions import create_error, DocParseError

class DocParser:
    @staticmethod
    def parse_swagger(url_or_path: str) -> Dict[str, Any]:
        """解析Swagger/OpenAPI文档"""
        try:
            if url_or_path.startswith('http'):
                # 从URL获取
                try:
                    response = requests.get(url_or_path, timeout=30)
                    response.raise_for_status()
                except requests.exceptions.Timeout:
                    error = create_error('NETWORK_TIMEOUT', f'文档URL请求超时: {url_or_path}')
                    raise error
                except requests.exceptions.ConnectionError:
                    error = create_error('NETWORK_CONNECTION_ERROR', f'文档URL连接失败: {url_or_path}')
                    raise error
                except requests.exceptions.RequestException as e:
                    error = create_error('NETWORK_UNKNOWN_ERROR', f'文档URL请求失败: {str(e)}')
                    raise error
                
                # 解析内容
                try:
                    if url_or_path.endswith('.yaml') or url_or_path.endswith('.yml'):
                        return yaml.safe_load(response.text)
                    else:
                        return response.json()
                except yaml.YAMLError as e:
                    error = create_error('DOC_FORMAT_ERROR', f'YAML格式解析失败: {str(e)}')
                    raise error
                except json.JSONDecodeError as e:
                    error = create_error('DOC_FORMAT_ERROR', f'JSON格式解析失败: {str(e)}')
                    raise error
            else:
                # 从本地文件获取
                try:
                    with open(url_or_path, 'r', encoding='utf-8') as f:
                        try:
                            if url_or_path.endswith('.yaml') or url_or_path.endswith('.yml'):
                                return yaml.safe_load(f)
                            else:
                                return json.load(f)
                        except yaml.YAMLError as e:
                            error = create_error('DOC_FORMAT_ERROR', f'YAML格式解析失败: {str(e)}')
                            raise error
                        except json.JSONDecodeError as e:
                            error = create_error('DOC_FORMAT_ERROR', f'JSON格式解析失败: {str(e)}')
                            raise error
                except FileNotFoundError:
                    error = create_error('DOC_NOT_FOUND', f'文档文件不存在: {url_or_path}')
                    raise error
                except Exception as e:
                    error = create_error('DOC_PARSE_FAILED', f'文档解析失败: {str(e)}')
                    raise error
        except DocParseError:
            raise
        except Exception as e:
            error = create_error('DOC_PARSE_FAILED', f'文档解析失败: {str(e)}')
            raise error
    
    @staticmethod
    def extract_endpoints(swagger_doc: Dict[str, Any]) -> List[Dict[str, Any]]:
        """从Swagger文档中提取接口信息"""
        try:
            endpoints = []
            paths = swagger_doc.get('paths', {})
            
            if not paths:
                error = create_error('DOC_PARSE_FAILED', '文档中未找到paths字段')
                raise error
            
            for path, methods in paths.items():
                for method, details in methods.items():
                    endpoint = {
                        'path': path,
                        'method': method.upper(),
                        'summary': details.get('summary', ''),
                        'description': details.get('description', ''),
                        'parameters': details.get('parameters', []),
                        'requestBody': details.get('requestBody', {}),
                        'responses': details.get('responses', {})
                    }
                    endpoints.append(endpoint)
            
            if not endpoints:
                error = create_error('DOC_PARSE_FAILED', '文档中未找到有效的接口信息')
                raise error
            
            return endpoints
        except DocParseError:
            raise
        except Exception as e:
            error = create_error('DOC_PARSE_FAILED', f'提取接口信息失败: {str(e)}')
            raise error