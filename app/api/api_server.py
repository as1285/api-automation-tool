from flask import Flask, request, jsonify
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from app.core.test_case_generator import TestCaseGenerator
from app.core.test_executor import TestExecutor
from app.core.report_generator import ReportGenerator
from app.core.enhanced_doc_parser import EnhancedDocParser
from app.core.test_case_manager import TestCaseManager
import json
import threading
import time
from app.utils.logger import logger

class ApiServer:
    """API服务器"""
    
    def __init__(self, host='0.0.0.0', port=5000):
        self.host = host
        self.port = port
        self.app = Flask(__name__)
        self.server_thread = None
        self.is_running = False
        
        # 注册路由
        self._register_routes()
    
    def _register_routes(self):
        """注册API路由"""
        # 健康检查
        @self.app.route('/health', methods=['GET'])
        def health_check():
            return jsonify({"status": "healthy", "message": "API服务器运行正常"})
        
        # 解析接口文档
        @self.app.route('/api/parse-doc', methods=['POST'])
        def parse_doc():
            try:
                data = request.json
                if not data or 'file_path' not in data:
                    return jsonify({"error": "缺少必要参数: file_path"}), 400
                
                file_path = data['file_path']
                doc = EnhancedDocParser.parse_doc(file_path)
                endpoints = EnhancedDocParser.extract_endpoints(doc)
                
                return jsonify({
                    "success": True,
                    "message": f"成功解析文档，共发现 {len(endpoints)} 个接口",
                    "data": endpoints
                })
            except Exception as e:
                logger.error(f"解析文档失败: {str(e)}")
                return jsonify({"success": False, "error": str(e)}), 500
        
        # 生成测试用例
        @self.app.route('/api/generate-test-cases', methods=['POST'])
        def generate_test_cases():
            try:
                data = request.json
                if not data or 'endpoints' not in data:
                    return jsonify({"error": "缺少必要参数: endpoints"}), 400
                
                endpoints = data['endpoints']
                test_cases = TestCaseGenerator.generate_test_cases(endpoints)
                
                return jsonify({
                    "success": True,
                    "message": f"成功生成 {len(test_cases)} 个测试用例",
                    "data": test_cases
                })
            except Exception as e:
                logger.error(f"生成测试用例失败: {str(e)}")
                return jsonify({"success": False, "error": str(e)}), 500
        
        # 执行测试
        @self.app.route('/api/execute-tests', methods=['POST'])
        def execute_tests():
            try:
                data = request.json
                if not data or 'test_cases' not in data or 'base_url' not in data:
                    return jsonify({"error": "缺少必要参数: test_cases, base_url"}), 400
                
                test_cases = data['test_cases']
                base_url = data['base_url']
                
                executor = TestExecutor(base_url)
                results = executor.execute_test_cases(test_cases)
                
                return jsonify({
                    "success": True,
                    "message": f"测试执行完成，共执行 {len(results)} 个用例",
                    "data": results
                })
            except Exception as e:
                logger.error(f"执行测试失败: {str(e)}")
                return jsonify({"success": False, "error": str(e)}), 500
        
        # 生成测试报告
        @self.app.route('/api/generate-report', methods=['POST'])
        def generate_report():
            try:
                data = request.json
                if not data or 'results' not in data or 'format' not in data:
                    return jsonify({"error": "缺少必要参数: results, format"}), 400
                
                results = data['results']
                format_type = data['format']
                
                if format_type == 'html':
                    report = ReportGenerator.generate_html_report(results)
                elif format_type == 'json':
                    report = ReportGenerator.generate_json_report(results)
                else:
                    return jsonify({"error": "不支持的报告格式: " + format_type}), 400
                
                return jsonify({
                    "success": True,
                    "message": f"成功生成 {format_type} 格式报告",
                    "data": report
                })
            except Exception as e:
                logger.error(f"生成报告失败: {str(e)}")
                return jsonify({"success": False, "error": str(e)}), 500
        
        # 导入测试用例
        @self.app.route('/api/import-test-cases', methods=['POST'])
        def import_test_cases():
            try:
                data = request.json
                if not data or 'file_path' not in data:
                    return jsonify({"error": "缺少必要参数: file_path"}), 400
                
                file_path = data['file_path']
                test_cases = TestCaseManager.load_test_cases(file_path)
                
                return jsonify({
                    "success": True,
                    "message": f"成功导入 {len(test_cases)} 个测试用例",
                    "data": test_cases
                })
            except Exception as e:
                logger.error(f"导入测试用例失败: {str(e)}")
                return jsonify({"success": False, "error": str(e)}), 500
        
        # 导出测试用例
        @self.app.route('/api/export-test-cases', methods=['POST'])
        def export_test_cases():
            try:
                data = request.json
                if not data or 'test_cases' not in data or 'file_path' not in data:
                    return jsonify({"error": "缺少必要参数: test_cases, file_path"}), 400
                
                test_cases = data['test_cases']
                file_path = data['file_path']
                
                success = TestCaseManager.save_test_cases(test_cases, file_path)
                if success:
                    return jsonify({
                        "success": True,
                        "message": f"成功导出 {len(test_cases)} 个测试用例到 {file_path}"
                    })
                else:
                    return jsonify({"success": False, "error": "导出测试用例失败"}), 500
            except Exception as e:
                logger.error(f"导出测试用例失败: {str(e)}")
                return jsonify({"success": False, "error": str(e)}), 500
    
    def start(self):
        """启动API服务器"""
        if not self.is_running:
            self.is_running = True
            self.server_thread = threading.Thread(target=self._run, daemon=True)
            self.server_thread.start()
            logger.info(f"API服务器已启动，监听地址: {self.host}:{self.port}")
            return True
        return False
    
    def stop(self):
        """停止API服务器"""
        if self.is_running:
            self.is_running = False
            logger.info("API服务器已停止")
            return True
        return False
    
    def _run(self):
        """运行API服务器"""
        try:
            # 禁用Flask的默认日志，使用我们自己的日志系统
            import logging
            log = logging.getLogger('werkzeug')
            log.setLevel(logging.ERROR)
            
            self.app.run(host=self.host, port=self.port, debug=False, use_reloader=False)
        except Exception as e:
            logger.error(f"API服务器运行失败: {str(e)}")
            self.is_running = False
    
    def is_active(self):
        """检查API服务器是否活跃"""
        return self.is_running and self.server_thread and self.server_thread.is_alive()

# 全局API服务器实例
api_server = ApiServer()