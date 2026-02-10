import json
import html
from datetime import datetime
from typing import List, Dict, Any

class ReportGenerator:
    @staticmethod
    def generate_html_report(results: List[Dict[str, Any]]) -> str:
        """生成HTML格式的测试报告（增强版）"""
        total = len(results)
        passed = sum(1 for r in results if r['success'])
        failed = total - passed
        
        # 计算成功率
        success_rate = (passed / total * 100) if total > 0 else 0
        
        # 计算平均响应时间
        avg_response_time = sum(r['response_time'] for r in results if r['response_time'] > 0) / len([r for r in results if r['response_time'] > 0]) if results else 0
        
        # 按方法统计
        method_stats = {}
        for result in results:
            test_case = result.get('test_case', {})
            method = test_case.get('method', 'UNKNOWN')
            if method not in method_stats:
                method_stats[method] = {'total': 0, 'passed': 0, 'failed': 0}
            method_stats[method]['total'] += 1
            if result['success']:
                method_stats[method]['passed'] += 1
            else:
                method_stats[method]['failed'] += 1
        
        # 生成统计图表数据
        chart_data = {
            'labels': list(method_stats.keys()),
            'passed': [method_stats[m]['passed'] for m in method_stats],
            'failed': [method_stats[m]['failed'] for m in method_stats]
        }
        
        # 生成报告内容
        html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>接口测试报告</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.3.0/dist/chart.umd.min.js"></script>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; }}
        .report-container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
        .summary-card {{ border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .stat-card {{ transition: transform 0.3s ease; }}
        .stat-card:hover {{ transform: translateY(-5px); }}
        .success-bg {{ background-color: #d4edda; }}
        .danger-bg {{ background-color: #f8d7da; }}
        .info-bg {{ background-color: #d1ecf1; }}
        .warning-bg {{ background-color: #fff3cd; }}
        .test-case {{ margin-bottom: 15px; border: 1px solid #e9ecef; border-radius: 4px; }}
        .test-case-header {{ padding: 10px 15px; background-color: #f8f9fa; border-bottom: 1px solid #e9ecef; }}
        .test-case-body {{ padding: 15px; }}
        .test-case-success {{ border-left: 4px solid #28a745; }}
        .test-case-failed {{ border-left: 4px solid #dc3545; }}
        .response-content {{ background-color: #f8f9fa; padding: 10px; border-radius: 4px; font-family: 'Courier New', monospace; white-space: pre-wrap; word-wrap: break-word; }}
        .timeline {{ position: relative; padding-left: 30px; }}
        .timeline-item {{ margin-bottom: 10px; position: relative; }}
        .timeline-item::before {{ content: ''; position: absolute; left: -15px; top: 5px; width: 10px; height: 10px; border-radius: 50%; background-color: #007bff; }}
    </style>
</head>
<body>
    <div class="report-container">
        <!-- 报告标题 -->
        <div class="text-center mb-5">
            <h1 class="text-primary">接口自动化测试报告</h1>
            <p class="text-muted">生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <!-- 摘要卡片 -->
        <div class="summary-card bg-white p-4 mb-5">
            <div class="row mb-4">
                <div class="col-md-3">
                    <div class="stat-card success-bg p-3 rounded-lg text-center">
                        <h3 class="text-success">{passed}</h3>
                        <p class="mb-0">通过</p>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="stat-card danger-bg p-3 rounded-lg text-center">
                        <h3 class="text-danger">{failed}</h3>
                        <p class="mb-0">失败</p>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="stat-card info-bg p-3 rounded-lg text-center">
                        <h3 class="text-info">{total}</h3>
                        <p class="mb-0">总用例</p>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="stat-card warning-bg p-3 rounded-lg text-center">
                        <h3 class="text-warning">{success_rate:.2f}%</h3>
                        <p class="mb-0">成功率</p>
                    </div>
                </div>
            </div>
            
            <div class="row mb-4">
                <div class="col-md-6">
                    <div class="bg-light p-3 rounded-lg">
                        <h5 class="text-dark mb-2">平均响应时间</h5>
                        <p class="text-xl">{avg_response_time:.3f} 秒</p>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="bg-light p-3 rounded-lg">
                        <h5 class="text-dark mb-2">测试环境</h5>
                        <p>接口自动化测试平台 v1.0</p>
                    </div>
                </div>
            </div>
            
            <!-- 图表 -->
            <div class="row mt-5">
                <div class="col-md-12">
                    <h4 class="mb-3">测试结果统计</h4>
                    <div style="height: 300px;">
                        <canvas id="testResultsChart"></canvas>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- 测试详情 -->
        <div class="bg-white p-4 rounded-lg shadow-sm">
            <h2 class="text-secondary mb-4">测试详情</h2>
            
            {''.join(ReportGenerator._generate_enhanced_result_row(r) for r in results)}
        </div>
    </div>
    
    <script>
        // 初始化图表
        const ctx = document.getElementById('testResultsChart').getContext('2d');
        const chart = new Chart(ctx, {{
            type: 'bar',
            data: {{
                labels: {json.dumps(chart_data['labels'])},
                datasets: [
                    {{
                        label: '通过',
                        data: {json.dumps(chart_data['passed'])},
                        backgroundColor: 'rgba(40, 167, 69, 0.6)',
                        borderColor: 'rgba(40, 167, 69, 1)',
                        borderWidth: 1
                    }},
                    {{
                        label: '失败',
                        data: {json.dumps(chart_data['failed'])},
                        backgroundColor: 'rgba(220, 53, 69, 0.6)',
                        borderColor: 'rgba(220, 53, 69, 1)',
                        borderWidth: 1
                    }}
                ]
            }},
            options: {{
                responsive: true,
                scales: {{
                    y: {{
                        beginAtZero: true,
                        title: {{
                            display: true,
                            text: '用例数量'
                        }}
                    }},
                    x: {{
                        title: {{
                            display: true,
                            text: 'HTTP方法'
                        }}
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
        """
        
        return html_content
    
    @staticmethod
    def _generate_enhanced_result_row(result: Dict[str, Any]) -> str:
        """生成增强版测试结果行"""
        test_case = result.get('test_case', {})
        status = '通过' if result['success'] else '失败'
        status_class = 'test-case-success' if result['success'] else 'test-case-failed'
        
        # 获取请求信息
        method = test_case.get('method', '')
        path = test_case.get('path', '')
        headers = test_case.get('headers', {})
        params = test_case.get('params', {})
        json_data = test_case.get('json', {})
        data = test_case.get('data', {})
        
        # 获取响应信息
        status_code = result.get('status_code', 0)
        response_time = result.get('response_time', 0)
        response_text = result.get('response_text', '')
        error = result.get('error', '')
        retry_count = result.get('retry_count', 0)
        
        # 构建请求体信息
        request_body = ''
        if json_data:
            request_body = json.dumps(json_data, ensure_ascii=False, indent=2)
        elif data:
            request_body = json.dumps(data, ensure_ascii=False, indent=2)
        
        return f"""
        <div class="test-case {status_class}">
            <div class="test-case-header d-flex justify-content-between align-items-center">
                <div>
                    <h5 class="mb-0 font-weight-bold">{test_case.get('name', '')}</h5>
                    <p class="text-sm text-muted mb-0">
                        <span class="badge badge-primary">{method}</span>
                        <span class="ml-2">{path}</span>
                        <span class="ml-2">用例ID: {test_case.get('id', '')}</span>
                    </p>
                </div>
                <div>
                    <span class="badge { 'badge-success' if result['success'] else 'badge-danger' }">{status}</span>
                    <span class="ml-2 text-sm">{response_time:.3f}s</span>
                </div>
            </div>
            <div class="test-case-body">
                <div class="row mb-3">
                    <div class="col-md-6">
                        <h6 class="text-dark mb-2">请求信息</h6>
                        <div class="mb-2">
                            <strong>请求头:</strong>
                            <div class="response-content">{json.dumps(headers, ensure_ascii=False, indent=2)}</div>
                        </div>
                        <div class="mb-2">
                            <strong>查询参数:</strong>
                            <div class="response-content">{json.dumps(params, ensure_ascii=False, indent=2)}</div>
                        </div>
                        {f'''
                        <div class="mb-2">
                            <strong>请求体:</strong>
                            <div class="response-content">{html.escape(request_body)}</div>
                        </div>
                        ''' if request_body else ''}
                    </div>
                    <div class="col-md-6">
                        <h6 class="text-dark mb-2">响应信息</h6>
                        <div class="mb-2">
                            <strong>状态码:</strong> <span class="badge badge-info">{status_code}</span>
                        </div>
                        <div class="mb-2">
                            <strong>响应时间:</strong> {response_time:.3f} 秒
                        </div>
                        {f'''
                        <div class="mb-2">
                            <strong>重试次数:</strong> {retry_count}
                        </div>
                        ''' if retry_count > 0 else ''}
                        <div class="mb-2">
                            <strong>响应内容:</strong>
                            <div class="response-content">{html.escape(response_text[:1000])}{'...' if len(response_text) > 1000 else ''}</div>
                        </div>
                        {f'''
                        <div class="mb-2">
                            <strong>错误信息:</strong>
                            <div class="response-content text-danger">{html.escape(error)}</div>
                        </div>
                        ''' if error else ''}
                    </div>
                </div>
            </div>
        </div>
        """
    
    @staticmethod
    def generate_json_report(results: List[Dict[str, Any]]) -> str:
        """生成JSON格式的测试报告"""
        total = len(results)
        passed = sum(1 for r in results if r['success'])
        failed = total - passed
        success_rate = (passed / total * 100) if total > 0 else 0
        avg_response_time = sum(r['response_time'] for r in results if r['response_time'] > 0) / len([r for r in results if r['response_time'] > 0]) if results else 0
        
        # 按方法统计
        method_stats = {}
        for result in results:
            test_case = result.get('test_case', {})
            method = test_case.get('method', 'UNKNOWN')
            if method not in method_stats:
                method_stats[method] = {'total': 0, 'passed': 0, 'failed': 0}
            method_stats[method]['total'] += 1
            if result['success']:
                method_stats[method]['passed'] += 1
            else:
                method_stats[method]['failed'] += 1
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'summary': {
                'total': total,
                'passed': passed,
                'failed': failed,
                'success_rate': success_rate,
                'avg_response_time': avg_response_time
            },
            'method_stats': method_stats,
            'results': results
        }
        return json.dumps(report, ensure_ascii=False, indent=2)