import requests
from typing import List, Dict, Any

class TestExecutor:
    def __init__(self, base_url: str = ''):
        self.base_url = base_url
    
    def execute_test_case(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """执行单个测试用例"""
        try:
            # 构建完整URL
            url = self.base_url.rstrip('/') + test_case['path']
            
            # 处理路径参数
            for param_name, param_value in test_case['params'].items():
                if f'{{{param_name}}}' in url:
                    url = url.replace(f'{{{param_name}}}', str(param_value))
            
            # 构建请求参数
            kwargs = {
                'headers': test_case['headers'],
                'params': {k: v for k, v in test_case['params'].items() if f'{{{k}}}' not in test_case['path']}
            }
            
            if test_case['json']:
                kwargs['json'] = test_case['json']
            elif test_case['data']:
                kwargs['data'] = test_case['data']
            
            # 发送请求
            method = test_case['method'].lower()
            response = getattr(requests, method)(url, **kwargs)
            
            # 构建结果
            result = {
                'success': response.status_code == test_case['expected_status'],
                'status_code': response.status_code,
                'response_time': response.elapsed.total_seconds(),
                'response_text': response.text,
                'response_json': {},
                'error': ''
            }
            
            try:
                result['response_json'] = response.json()
            except:
                pass
            
        except Exception as e:
            result = {
                'success': False,
                'status_code': 0,
                'response_time': 0,
                'response_text': '',
                'response_json': {},
                'error': str(e)
            }
        
        return result
    
    def execute_test_cases(self, test_cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """执行多个测试用例"""
        results = []
        for test_case in test_cases:
            result = self.execute_test_case(test_case)
            result['test_case'] = test_case
            results.append(result)
        return results