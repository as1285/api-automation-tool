import requests
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from app.core.config import config
from app.utils.common_utils import replace_path_params
from app.utils.logger import logger

class TestExecutor:
    def __init__(self, base_url: str = ''):
        self.base_url = base_url
        self.timeout = config.get('DEFAULT_TIMEOUT')
        self.retry_count = config.get('DEFAULT_RETRY_COUNT')
        self.default_headers = config.get('DEFAULT_HEADERS')
        self.logger = logger
        self.concurrency = config.get('TEST_CONCURRENCY', 5)
    
    def execute_test_case(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """执行单个测试用例"""
        retry_count = self.retry_count
        last_error = None
        test_case_id = test_case.get('id', 'unknown')
        
        self.logger.info(f"开始执行测试用例: {test_case_id} - {test_case.get('name')}")
        
        while retry_count >= 0:
            try:
                # 构建完整URL
                path = test_case['path']
                # 处理路径参数
                processed_path = replace_path_params(path, test_case['params'])
                url = self.base_url.rstrip('/') + processed_path
                
                self.logger.debug(f"请求URL: {test_case['method']} {url}")
                
                # 构建请求参数
                headers = self.default_headers.copy()
                headers.update(test_case['headers'])
                
                kwargs = {
                    'headers': headers,
                    'params': {k: v for k, v in test_case['params'].items() if f'{{{k}}}' not in test_case['path']},
                    'timeout': self.timeout
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
                    'error': '',
                    'retry_count': self.retry_count - retry_count
                }
                
                try:
                    result['response_json'] = response.json()
                except:
                    pass
                
                self.logger.info(f"测试用例执行完成: {test_case_id} - 状态码: {result['status_code']} - 耗时: {result['response_time']:.3f}s - 结果: {'成功' if result['success'] else '失败'}")
                
                return result
                
            except Exception as e:
                last_error = e
                self.logger.warning(f"测试用例执行失败 (重试 {self.retry_count - retry_count}/{self.retry_count}): {test_case_id} - {str(e)}")
                retry_count -= 1
                if retry_count < 0:
                    result = {
                        'success': False,
                        'status_code': 0,
                        'response_time': 0,
                        'response_text': '',
                        'response_json': {},
                        'error': str(last_error),
                        'retry_count': self.retry_count
                    }
                    self.logger.error(f"测试用例执行最终失败: {test_case_id} - {str(last_error)}")
                    return result
        
        # 理论上不会执行到这里
        self.logger.error(f"测试用例执行异常: {test_case_id} - Unknown error")
        return {
            'success': False,
            'status_code': 0,
            'response_time': 0,
            'response_text': '',
            'response_json': {},
            'error': 'Unknown error',
            'retry_count': self.retry_count
        }
    
    def execute_test_cases(self, test_cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """执行多个测试用例（支持并发）"""
        results = []
        total = len(test_cases)
        self.logger.info(f"开始执行测试用例，共 {total} 个，并发数: {self.concurrency}")
        
        # 使用线程池并发执行
        with ThreadPoolExecutor(max_workers=self.concurrency) as executor:
            # 提交所有任务
            future_to_test_case = {executor.submit(self.execute_test_case, test_case): test_case for test_case in test_cases}
            
            # 收集结果
            for i, future in enumerate(as_completed(future_to_test_case), 1):
                test_case = future_to_test_case[future]
                try:
                    result = future.result()
                    result['test_case'] = test_case
                    results.append(result)
                    
                    # 记录进度
                    if i % 10 == 0 or i == total:
                        self.logger.info(f"测试执行进度: {i}/{total}")
                        
                except Exception as e:
                    self.logger.error(f"测试用例执行异常: {test_case.get('id', 'unknown')} - {str(e)}")
                    result = {
                        'success': False,
                        'status_code': 0,
                        'response_time': 0,
                        'response_text': '',
                        'response_json': {},
                        'error': str(e),
                        'retry_count': 0,
                        'test_case': test_case
                    }
                    results.append(result)
        
        self.logger.info(f"测试用例执行完成，共 {total} 个，成功 {sum(1 for r in results if r['success'])} 个")
        return results