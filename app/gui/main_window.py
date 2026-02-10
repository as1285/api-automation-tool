from PyQt5.QtWidgets import QMainWindow, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QTextEdit, QTableWidget, QTableWidgetItem, QFileDialog, QMessageBox, QLabel, QSplitter
from PyQt5.QtCore import Qt
from app.core.doc_parser import DocParser
from app.core.test_case_generator import TestCaseGenerator
from app.core.test_executor import TestExecutor
from app.core.report_generator import ReportGenerator
import json

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("接口自动化测试工具")
        self.setGeometry(100, 100, 1200, 800)
        
        # 初始化数据
        self.swagger_doc = None
        self.endpoints = []
        self.test_cases = []
        self.test_results = []
        self.base_url = ''
        
        # 创建主布局
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget)
        
        # 创建接口文档导入标签
        self.create_doc_import_tab()
        
        # 创建测试用例标签
        self.create_test_cases_tab()
        
        # 创建测试执行标签
        self.create_test_execution_tab()
        
        # 创建测试报告标签
        self.create_report_tab()
    
    def create_doc_import_tab(self):
        """创建接口文档导入标签"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 创建输入区域
        input_layout = QHBoxLayout()
        self.doc_path_edit = QLineEdit()
        self.doc_path_edit.setPlaceholderText("输入Swagger文档URL或本地文件路径")
        browse_btn = QPushButton("浏览")
        browse_btn.clicked.connect(self.browse_doc_file)
        parse_btn = QPushButton("解析文档")
        parse_btn.clicked.connect(self.parse_doc)
        
        input_layout.addWidget(self.doc_path_edit)
        input_layout.addWidget(browse_btn)
        input_layout.addWidget(parse_btn)
        
        # 创建结果显示区域
        self.doc_result_edit = QTextEdit()
        self.doc_result_edit.setReadOnly(True)
        
        layout.addLayout(input_layout)
        layout.addWidget(QLabel("解析结果:"))
        layout.addWidget(self.doc_result_edit)
        
        self.tab_widget.addTab(tab, "文档导入")
    
    def create_test_cases_tab(self):
        """创建测试用例标签"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 创建生成按钮
        generate_btn = QPushButton("生成测试用例")
        generate_btn.clicked.connect(self.generate_test_cases)
        layout.addWidget(generate_btn)
        
        # 创建测试用例表格
        self.test_cases_table = QTableWidget()
        self.test_cases_table.setColumnCount(5)
        self.test_cases_table.setHorizontalHeaderLabels(["用例ID", "用例名称", "方法", "路径", "操作"])
        layout.addWidget(self.test_cases_table)
        
        self.tab_widget.addTab(tab, "测试用例")
    
    def create_test_execution_tab(self):
        """创建测试执行标签"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 创建基础URL输入
        url_layout = QHBoxLayout()
        url_layout.addWidget(QLabel("基础URL:"))
        self.base_url_edit = QLineEdit()
        self.base_url_edit.setPlaceholderText("例如: http://localhost:8080")
        url_layout.addWidget(self.base_url_edit)
        layout.addLayout(url_layout)
        
        # 创建执行按钮
        execute_btn = QPushButton("执行测试")
        execute_btn.clicked.connect(self.execute_tests)
        layout.addWidget(execute_btn)
        
        # 创建测试结果表格
        self.test_results_table = QTableWidget()
        self.test_results_table.setColumnCount(6)
        self.test_results_table.setHorizontalHeaderLabels(["用例ID", "用例名称", "方法", "路径", "状态码", "结果"])
        layout.addWidget(self.test_results_table)
        
        self.tab_widget.addTab(tab, "测试执行")
    
    def create_report_tab(self):
        """创建测试报告标签"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 创建报告生成按钮
        report_layout = QHBoxLayout()
        generate_html_btn = QPushButton("生成HTML报告")
        generate_html_btn.clicked.connect(lambda: self.generate_report('html'))
        generate_json_btn = QPushButton("生成JSON报告")
        generate_json_btn.clicked.connect(lambda: self.generate_report('json'))
        
        report_layout.addWidget(generate_html_btn)
        report_layout.addWidget(generate_json_btn)
        layout.addLayout(report_layout)
        
        # 创建报告显示区域
        self.report_edit = QTextEdit()
        self.report_edit.setReadOnly(True)
        layout.addWidget(self.report_edit)
        
        self.tab_widget.addTab(tab, "测试报告")
    
    def browse_doc_file(self):
        """浏览文档文件"""
        file_path, _ = QFileDialog.getOpenFileName(self, "选择接口文档", "", "JSON/YAML文件 (*.json *.yaml *.yml)")
        if file_path:
            self.doc_path_edit.setText(file_path)
    
    def parse_doc(self):
        """解析接口文档"""
        try:
            path = self.doc_path_edit.text().strip()
            if not path:
                QMessageBox.warning(self, "警告", "请输入文档路径")
                return
            
            # 解析文档
            self.swagger_doc = DocParser.parse_swagger(path)
            self.endpoints = DocParser.extract_endpoints(self.swagger_doc)
            
            # 显示结果
            result = f"成功解析文档！\n"
            result += f"接口数量: {len(self.endpoints)}\n\n"
            for i, endpoint in enumerate(self.endpoints[:10]):
                result += f"{i+1}. {endpoint['method']} {endpoint['path']} - {endpoint['summary']}\n"
            if len(self.endpoints) > 10:
                result += f"... 还有 {len(self.endpoints) - 10} 个接口未显示"
            
            self.doc_result_edit.setText(result)
            QMessageBox.information(self, "成功", f"文档解析成功，共发现 {len(self.endpoints)} 个接口")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"解析文档失败: {str(e)}")
    
    def generate_test_cases(self):
        """生成测试用例"""
        try:
            if not self.endpoints:
                QMessageBox.warning(self, "警告", "请先解析接口文档")
                return
            
            # 生成测试用例
            self.test_cases = TestCaseGenerator.generate_test_cases(self.endpoints)
            
            # 更新表格
            self.update_test_cases_table()
            
            QMessageBox.information(self, "成功", f"测试用例生成成功，共生成 {len(self.test_cases)} 个用例")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"生成测试用例失败: {str(e)}")
    
    def update_test_cases_table(self):
        """更新测试用例表格"""
        self.test_cases_table.setRowCount(len(self.test_cases))
        
        for i, test_case in enumerate(self.test_cases):
            self.test_cases_table.setItem(i, 0, QTableWidgetItem(test_case['id']))
            self.test_cases_table.setItem(i, 1, QTableWidgetItem(test_case['name']))
            self.test_cases_table.setItem(i, 2, QTableWidgetItem(test_case['method']))
            self.test_cases_table.setItem(i, 3, QTableWidgetItem(test_case['path']))
            
            # 添加编辑按钮
            edit_btn = QPushButton("编辑")
            edit_btn.clicked.connect(lambda _, idx=i: self.edit_test_case(idx))
            self.test_cases_table.setCellWidget(i, 4, edit_btn)
    
    def edit_test_case(self, index):
        """编辑测试用例"""
        # 这里可以实现编辑测试用例的功能
        QMessageBox.information(self, "编辑测试用例", f"编辑测试用例: {self.test_cases[index]['name']}")
    
    def execute_tests(self):
        """执行测试"""
        try:
            if not self.test_cases:
                QMessageBox.warning(self, "警告", "请先生成测试用例")
                return
            
            # 获取基础URL
            self.base_url = self.base_url_edit.text().strip()
            if not self.base_url:
                QMessageBox.warning(self, "警告", "请输入基础URL")
                return
            
            # 创建执行器
            executor = TestExecutor(self.base_url)
            
            # 执行测试
            self.test_results = executor.execute_test_cases(self.test_cases)
            
            # 更新结果表格
            self.update_test_results_table()
            
            QMessageBox.information(self, "成功", "测试执行完成")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"执行测试失败: {str(e)}")
    
    def update_test_results_table(self):
        """更新测试结果表格"""
        self.test_results_table.setRowCount(len(self.test_results))
        
        for i, result in enumerate(self.test_results):
            test_case = result.get('test_case', {})
            status = "通过" if result['success'] else "失败"
            
            self.test_results_table.setItem(i, 0, QTableWidgetItem(test_case.get('id', '')))
            self.test_results_table.setItem(i, 1, QTableWidgetItem(test_case.get('name', '')))
            self.test_results_table.setItem(i, 2, QTableWidgetItem(test_case.get('method', '')))
            self.test_results_table.setItem(i, 3, QTableWidgetItem(test_case.get('path', '')))
            self.test_results_table.setItem(i, 4, QTableWidgetItem(str(result['status_code'])))
            self.test_results_table.setItem(i, 5, QTableWidgetItem(status))
    
    def generate_report(self, format_type):
        """生成测试报告"""
        try:
            if not self.test_results:
                QMessageBox.warning(self, "警告", "请先执行测试")
                return
            
            if format_type == 'html':
                report = ReportGenerator.generate_html_report(self.test_results)
                # 保存为文件
                file_path, _ = QFileDialog.getSaveFileName(self, "保存HTML报告", "report.html", "HTML文件 (*.html)")
                if file_path:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(report)
                    QMessageBox.information(self, "成功", f"HTML报告已保存到: {file_path}")
                    self.report_edit.setHtml(report)
            
            elif format_type == 'json':
                report = ReportGenerator.generate_json_report(self.test_results)
                # 保存为文件
                file_path, _ = QFileDialog.getSaveFileName(self, "保存JSON报告", "report.json", "JSON文件 (*.json)")
                if file_path:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(report)
                    QMessageBox.information(self, "成功", f"JSON报告已保存到: {file_path}")
                    self.report_edit.setText(report)
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"生成报告失败: {str(e)}")
    
    def browse_doc_file(self):
        """浏览文档文件"""
        file_path, _ = QFileDialog.getOpenFileName(self, "选择接口文档", "", "JSON/YAML文件 (*.json *.yaml *.yml)")
        if file_path:
            self.doc_path_edit.setText(file_path)
    
    def parse_doc(self):
        """解析接口文档"""
        try:
            path = self.doc_path_edit.text().strip()
            if not path:
                QMessageBox.warning(self, "警告", "请输入文档路径")
                return
            
            # 解析文档
            self.swagger_doc = DocParser.parse_swagger(path)
            self.endpoints = DocParser.extract_endpoints(self.swagger_doc)
            
            # 显示结果
            result = f"成功解析文档！\n"
            result += f"接口数量: {len(self.endpoints)}\n\n"
            for i, endpoint in enumerate(self.endpoints[:10]):
                result += f"{i+1}. {endpoint['method']} {endpoint['path']} - {endpoint['summary']}\n"
            if len(self.endpoints) > 10:
                result += f"... 还有 {len(self.endpoints) - 10} 个接口未显示"
            
            self.doc_result_edit.setText(result)
            QMessageBox.information(self, "成功", f"文档解析成功，共发现 {len(self.endpoints)} 个接口")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"解析文档失败: {str(e)}")