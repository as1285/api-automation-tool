import requests
import yaml
import json
from typing import Dict, List, Any

class DocParser:
    @staticmethod
    def parse_swagger(url_or_path: str) -> Dict[str, Any]:
        """解析Swagger/OpenAPI文档"""
        if url_or_path.startswith('http'):
            # 从URL获取
            response = requests.get(url_or_path)
            response.raise_for_status()
            if url_or_path.endswith('.yaml') or url_or_path.endswith('.yml'):
                return yaml.safe_load(response.text)
            else:
                return response.json()
        else:
            # 从本地文件获取
            with open(url_or_path, 'r', encoding='utf-8') as f:
                if url_or_path.endswith('.yaml') or url_or_path.endswith('.yml'):
                    return yaml.safe_load(f)
                else:
                    return json.load(f)
    
    @staticmethod
    def extract_endpoints(swagger_doc: Dict[str, Any]) -> List[Dict[str, Any]]:
        """从Swagger文档中提取接口信息"""
        endpoints = []
        paths = swagger_doc.get('paths', {})
        
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
        
        return endpoints