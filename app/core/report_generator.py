import json
import html
from datetime import datetime
from typing import List, Dict, Any

class ReportGenerator:
    @staticmethod
    def generate_html_report(results: List[Dict[str, Any]]) -> str:
        """生成HTML格式的测试报告"""
        total = len(results)
        passed = sum(1 for r in results if r['success'])
        failed = total - passed
        
        # 计算成功率
        success_rate = (passed / total * 100) if total > 0 else 0
        
        # 生成报告内容
        html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>接口测试报告</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        .summary {{ background-color: #f5f5f5; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
        .stats {{ display: flex; gap: 20px; margin: 10px 0; }}
        .stat {{ background-color: #e3f2fd; padding: 10px; border-radius: 5px; }}
        .passed {{ color: green; }}
        .failed {{ color: red; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        tr:nth-child(even) {{ background-color: #f9f9f9; }}
        .details {{ margin-top: 10px; padding: 10px; background-color: #f5f5f5; border-radius: 5px; }}
    </style>
</head>
<body>
    <h1>接口测试报告</h1>
    <div class="summary">
        <p>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <div class="stats">
            <div class="stat">总用例数: {total}</div>
            <div class="stat passed">通过: {passed}</div>
            <div class="stat failed">失败: {failed}</div>
            <div class="stat">成功率: {success_rate:.2f}%</div>
        </div>
    </div>
    <h2>测试详情</h2>
    <table>
        <tr>
            <th>用例ID</th>
            <th>用例名称</th>
            <th>方法</th>
            <th>路径</th>
            <th>状态码</th>
            <th>响应时间(秒)</th>
            <th>结果</th>
            <th>详情</th>
        </tr>
        
        {''.join(ReportGenerator._generate_result_row(r) for r in results)}
        
    </table>
</body>
</html>
        """
        
        return html_content
    
    @staticmethod
    def _generate_result_row(result: Dict[str, Any]) -> str:
        """生成测试结果表格行"""
        test_case = result.get('test_case', {})
        status = '通过' if result['success'] else '失败'
        status_class = 'passed' if result['success'] else 'failed'
        
        details = f"""
        <div class="details">
            <p><strong>请求参数:</strong> {json.dumps(test_case.get('params', {}), ensure_ascii=False)}</p>
            <p><strong>请求体:</strong> {json.dumps(test_case.get('json', {}), ensure_ascii=False)}</p>
            <p><strong>响应内容:</strong> {html.escape(result['response_text'])}</p>
            {f'<p><strong>错误信息:</strong> {html.escape(result.get('error', ''))}</p>' if not result['success'] else ''}
        </div>
        """
        
        return f"""
        <tr>
            <td>{test_case.get('id', '')}</td>
            <td>{test_case.get('name', '')}</td>
            <td>{test_case.get('method', '')}</td>
            <td>{test_case.get('path', '')}</td>
            <td>{result['status_code']}</td>
            <td>{result['response_time']:.3f}</td>
            <td class="{status_class}">{status}</td>
            <td>{details}</td>
        </tr>
        """
    
    @staticmethod
    def generate_json_report(results: List[Dict[str, Any]]) -> str:
        """生成JSON格式的测试报告"""
        report = {
            'generated_at': datetime.now().isoformat(),
            'total': len(results),
            'passed': sum(1 for r in results if r['success']),
            'failed': sum(1 for r in results if not r['success']),
            'results': results
        }
        return json.dumps(report, ensure_ascii=False, indent=2)