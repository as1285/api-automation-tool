from typing import List, Dict, Any

class TestCaseGenerator:
    @staticmethod
    def generate_test_cases(endpoints: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """根据接口信息生成测试用例"""
        test_cases = []
        
        for endpoint in endpoints:
            test_case = {
                'id': f"test_{endpoint['method']}_{endpoint['path'].replace('/', '_').replace('{', '').replace('}', '')}",
                'name': f"{endpoint['summary'] or endpoint['path']}",
                'method': endpoint['method'],
                'path': endpoint['path'],
                'headers': {},
                'params': {},
                'data': {},
                'json': {},
                'expected_status': 200,
                'expected_response': {},
                'description': endpoint['description']
            }
            
            # 处理参数
            for param in endpoint.get('parameters', []):
                if param['in'] == 'query':
                    test_case['params'][param['name']] = ''
                elif param['in'] == 'path':
                    # 路径参数在实际请求时需要替换
                    pass
                elif param['in'] == 'header':
                    test_case['headers'][param['name']] = ''
                elif param['in'] == 'cookie':
                    # 暂不处理cookie
                    pass
            
            # 处理请求体
            request_body = endpoint.get('requestBody', {})
            if request_body:
                content = request_body.get('content', {})
                if 'application/json' in content:
                    test_case['json'] = TestCaseGenerator._extract_schema_example(
                        content['application/json'].get('schema', {})
                    )
                elif 'application/x-www-form-urlencoded' in content:
                    test_case['data'] = TestCaseGenerator._extract_schema_example(
                        content['application/x-www-form-urlencoded'].get('schema', {})
                    )
            
            test_cases.append(test_case)
        
        return test_cases
    
    @staticmethod
    def _extract_schema_example(schema: Dict[str, Any]) -> Dict[str, Any]:
        """从schema中提取示例数据"""
        if 'example' in schema:
            return schema['example']
        elif schema.get('type') == 'object':
            example = {}
            properties = schema.get('properties', {})
            for name, prop in properties.items():
                example[name] = TestCaseGenerator._extract_schema_example(prop)
            return example
        elif schema.get('type') == 'array':
            return []
        elif schema.get('type') == 'string':
            return ''
        elif schema.get('type') == 'number':
            return 0
        elif schema.get('type') == 'boolean':
            return False
        else:
            return {}