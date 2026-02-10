import json
import yaml
from typing import Dict, List, Any, Optional
from app.core.exceptions import create_error, DocParseError
from app.utils.logger import logger
from app.utils.common_utils import get_file_extension

class EnhancedDocParser:
    """增强版文档解析器，支持多种格式的接口文档"""
    
    @staticmethod
    def detect_doc_format(doc_content: str, file_path: Optional[str] = None) -> str:
        """
        检测文档格式
        
        Args:
            doc_content: 文档内容
            file_path: 文件路径（可选）
        
        Returns:
            str: 文档格式，如 'swagger', 'openapi', 'postman', 'rap', 'yapi'
        """
        # 首先根据文件扩展名判断
        if file_path:
            ext = get_file_extension(file_path)
            if ext in ['json', 'yaml', 'yml']:
                # 尝试解析内容
                try:
                    if ext in ['yaml', 'yml']:
                        data = yaml.safe_load(doc_content)
                    else:
                        data = json.loads(doc_content)
                    
                    # 根据内容特征判断
                    if isinstance(data, dict):
                        # Swagger/OpenAPI
                        if 'swagger' in data:
                            return 'swagger'
                        elif 'openapi' in data:
                            return 'openapi'
                        # Postman Collection
                        elif 'info' in data and 'item' in data:
                            if 'schema' in data and 'https://schema.getpostman.com/' in data['schema']:
                                return 'postman'
                        # RAP
                        elif 'project' in data and 'modules' in data:
                            return 'rap'
                        # YAPI
                        elif 'api' in data or 'cat' in data:
                            return 'yapi'
                except Exception:
                    pass
        
        # 默认返回 swagger
        return 'swagger'
    
    @staticmethod
    def parse_doc(doc_path: str) -> Dict[str, Any]:
        """
        解析文档
        
        Args:
            doc_path: 文档路径或URL
        
        Returns:
            Dict[str, Any]: 解析后的文档数据
        """
        try:
            # 获取文档内容
            if doc_path.startswith('http'):
                import requests
                response = requests.get(doc_path, timeout=30)
                response.raise_for_status()
                doc_content = response.text
            else:
                with open(doc_path, 'r', encoding='utf-8') as f:
                    doc_content = f.read()
            
            # 检测文档格式
            doc_format = EnhancedDocParser.detect_doc_format(doc_content, doc_path)
            logger.info(f"检测到文档格式: {doc_format}")
            
            # 根据格式解析
            if doc_format in ['swagger', 'openapi']:
                return EnhancedDocParser.parse_swagger(doc_content, doc_path)
            elif doc_format == 'postman':
                return EnhancedDocParser.parse_postman(doc_content)
            elif doc_format == 'rap':
                return EnhancedDocParser.parse_rap(doc_content)
            elif doc_format == 'yapi':
                return EnhancedDocParser.parse_yapi(doc_content)
            else:
                error = create_error('DOC_FORMAT_ERROR', f'不支持的文档格式: {doc_format}')
                raise error
                
        except DocParseError:
            raise
        except Exception as e:
            error = create_error('DOC_PARSE_FAILED', f'文档解析失败: {str(e)}')
            raise error
    
    @staticmethod
    def parse_swagger(doc_content: str, doc_path: Optional[str] = None) -> Dict[str, Any]:
        """
        解析Swagger/OpenAPI文档
        
        Args:
            doc_content: 文档内容
            doc_path: 文档路径（可选）
        
        Returns:
            Dict[str, Any]: 解析后的文档数据
        """
        try:
            # 根据文件扩展名判断解析方式
            if doc_path and (doc_path.endswith('.yaml') or doc_path.endswith('.yml')):
                return yaml.safe_load(doc_content)
            else:
                # 尝试JSON解析
                try:
                    return json.loads(doc_content)
                except json.JSONDecodeError:
                    # 尝试YAML解析
                    return yaml.safe_load(doc_content)
        except Exception as e:
            error = create_error('DOC_FORMAT_ERROR', f'Swagger文档解析失败: {str(e)}')
            raise error
    
    @staticmethod
    def parse_postman(doc_content: str) -> Dict[str, Any]:
        """
        解析Postman Collection文档
        
        Args:
            doc_content: 文档内容
        
        Returns:
            Dict[str, Any]: 转换为Swagger格式的文档数据
        """
        try:
            postman_data = json.loads(doc_content)
            
            # 转换为Swagger格式
            swagger_data = {
                'swagger': '2.0',
                'info': {
                    'title': postman_data.get('info', {}).get('name', 'Postman Collection'),
                    'version': postman_data.get('info', {}).get('version', '1.0.0'),
                    'description': postman_data.get('info', {}).get('description', '')
                },
                'paths': {}
            }
            
            # 处理项目
            items = postman_data.get('item', [])
            EnhancedDocParser._process_postman_items(items, swagger_data['paths'])
            
            return swagger_data
        except Exception as e:
            error = create_error('DOC_FORMAT_ERROR', f'Postman文档解析失败: {str(e)}')
            raise error
    
    @staticmethod
    def _process_postman_items(items: List[Dict[str, Any]], paths: Dict[str, Any], base_path: str = ''):
        """
        处理Postman项目
        
        Args:
            items: 项目列表
            paths: 路径字典
            base_path: 基础路径
        """
        for item in items:
            if 'item' in item:
                # 文件夹
                folder_name = item.get('name', '')
                new_base_path = f"{base_path}/{folder_name}" if folder_name else base_path
                EnhancedDocParser._process_postman_items(item['item'], paths, new_base_path)
            elif 'request' in item:
                # 请求
                request = item['request']
                method = request.get('method', 'GET').lower()
                url = request.get('url', {})
                
                # 处理URL
                if isinstance(url, dict):
                    path = url.get('path', [])
                    if isinstance(path, list):
                        path_str = '/'.join([str(p) for p in path])
                    else:
                        path_str = str(path)
                    host = url.get('host', [''])[0] if isinstance(url.get('host'), list) else url.get('host', '')
                    full_path = f"/{path_str}" if path_str else '/' 
                else:
                    full_path = str(url)
                
                # 确保路径以/开头
                if not full_path.startswith('/'):
                    full_path = '/' + full_path
                
                # 添加到paths
                if full_path not in paths:
                    paths[full_path] = {}
                
                # 构建请求信息
                paths[full_path][method] = {
                    'summary': item.get('name', ''),
                    'description': item.get('description', ''),
                    'parameters': [],
                    'responses': {}
                }
                
                # 处理参数
                if isinstance(url, dict) and 'query' in url:
                    for param in url['query']:
                        paths[full_path][method]['parameters'].append({
                            'in': 'query',
                            'name': param.get('key', ''),
                            'type': 'string',
                            'required': param.get('value', '') != ''
                        })
                
                # 处理请求体
                if 'body' in request:
                    paths[full_path][method]['requestBody'] = {
                        'content': {
                            'application/json': {
                                'schema': {
                                    'type': 'object'
                                }
                            }
                        }
                    }
    
    @staticmethod
    def parse_rap(doc_content: str) -> Dict[str, Any]:
        """
        解析RAP文档
        
        Args:
            doc_content: 文档内容
        
        Returns:
            Dict[str, Any]: 转换为Swagger格式的文档数据
        """
        try:
            rap_data = json.loads(doc_content)
            
            # 转换为Swagger格式
            swagger_data = {
                'swagger': '2.0',
                'info': {
                    'title': rap_data.get('project', {}).get('name', 'RAP Project'),
                    'version': '1.0.0',
                    'description': rap_data.get('project', {}).get('description', '')
                },
                'paths': {}
            }
            
            # 处理模块
            modules = rap_data.get('modules', [])
            for module in modules:
                interfaces = module.get('interfaces', [])
                for interface in interfaces:
                    path = interface.get('url', '')
                    method = interface.get('method', 'GET').lower()
                    
                    if not path:
                        continue
                    
                    # 确保路径以/开头
                    if not path.startswith('/'):
                        path = '/' + path
                    
                    # 添加到paths
                    if path not in swagger_data['paths']:
                        swagger_data['paths'][path] = {}
                    
                    # 构建请求信息
                    swagger_data['paths'][path][method] = {
                        'summary': interface.get('name', ''),
                        'description': interface.get('description', ''),
                        'parameters': [],
                        'responses': {}
                    }
                    
                    # 处理参数
                    request_parameters = interface.get('requestParameters', [])
                    for param in request_parameters:
                        swagger_data['paths'][path][method]['parameters'].append({
                            'in': 'query' if param.get('type') == 'query' else 'body',
                            'name': param.get('name', ''),
                            'type': param.get('dataType', 'string'),
                            'required': param.get('required', False)
                        })
            
            return swagger_data
        except Exception as e:
            error = create_error('DOC_FORMAT_ERROR', f'RAP文档解析失败: {str(e)}')
            raise error
    
    @staticmethod
    def parse_yapi(doc_content: str) -> Dict[str, Any]:
        """
        解析YAPI文档
        
        Args:
            doc_content: 文档内容
        
        Returns:
            Dict[str, Any]: 转换为Swagger格式的文档数据
        """
        try:
            yapi_data = json.loads(doc_content)
            
            # 转换为Swagger格式
            swagger_data = {
                'swagger': '2.0',
                'info': {
                    'title': yapi_data.get('project', {}).get('name', 'YAPI Project'),
                    'version': '1.0.0',
                    'description': yapi_data.get('project', {}).get('description', '')
                },
                'paths': {}
            }
            
            # 处理接口
            apis = yapi_data.get('api', [])
            for api in apis:
                path = api.get('path', '')
                method = api.get('method', 'GET').lower()
                
                if not path:
                    continue
                
                # 确保路径以/开头
                if not path.startswith('/'):
                    path = '/' + path
                
                # 添加到paths
                if path not in swagger_data['paths']:
                    swagger_data['paths'][path] = {}
                
                # 构建请求信息
                swagger_data['paths'][path][method] = {
                    'summary': api.get('title', ''),
                    'description': api.get('desc', ''),
                    'parameters': [],
                    'responses': {}
                }
                
                # 处理参数
                req_params = api.get('req_params', [])
                for param in req_params:
                    swagger_data['paths'][path][method]['parameters'].append({
                        'in': param.get('in', 'query'),
                        'name': param.get('name', ''),
                        'type': param.get('type', 'string'),
                        'required': param.get('required', False)
                    })
            
            return swagger_data
        except Exception as e:
            error = create_error('DOC_FORMAT_ERROR', f'YAPI文档解析失败: {str(e)}')
            raise error
    
    @staticmethod
    def extract_endpoints(swagger_doc: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        从Swagger文档中提取接口信息
        
        Args:
            swagger_doc: Swagger文档数据
        
        Returns:
            List[Dict[str, Any]]: 接口信息列表
        """
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
