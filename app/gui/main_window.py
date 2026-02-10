from PyQt5.QtWidgets import QMainWindow, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QTextEdit, QTableWidget, QTableWidgetItem, QFileDialog, QMessageBox, QLabel, QSplitter, QProgressBar, QStatusBar, QApplication
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QColor, QPalette
from app.core.enhanced_doc_parser import EnhancedDocParser
from app.core.test_case_generator import TestCaseGenerator
from app.core.test_executor import TestExecutor
from app.core.report_generator import ReportGenerator
from app.core.test_case_manager import TestCaseManager
from app.core.plugin_system import plugin_manager
from app.api.api_server import api_server
from app.gui.test_case_editor import TestCaseEditor
import json
import os

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("接口自动化测试工具")
        self.setGeometry(100, 100, 1200, 800)
        
        # 设置现代化样式
        self.set_modern_style()
        
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
        self.tab_widget.setMinimumSize(1150, 700)
        self.main_layout.addWidget(self.tab_widget)
        
        # 创建状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # 创建进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(300)
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)
        
        # 创建状态标签
        self.status_label = QLabel("就绪")
        self.status_bar.addWidget(self.status_label)
        
        # 初始化插件系统
        self.initialize_plugins()
        
        # 创建接口文档导入标签
        self.create_doc_import_tab()
        
        # 创建测试用例标签
        self.create_test_cases_tab()
        
        # 创建测试执行标签
        self.create_test_execution_tab()
        
        # 创建测试报告标签
        self.create_report_tab()
        
        # 启动API服务器
        self.start_api_server()
    
    def set_modern_style(self):
        """设置现代化样式"""
        # 设置字体
        font = QFont("Microsoft YaHei", 9)
        self.setFont(font)
        
        # 设置窗口背景
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(240, 240, 240))
        self.setPalette(palette)
        
        # 设置标签页样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QTabWidget {
                background-color: #ffffff;
                border-radius: 8px;
                padding: 5px;
                margin: 5px;
            }
            QTabBar::tab {
                background-color: #f5f5f5;
                color: #333333;
                padding: 8px 16px;
                border-radius: 4px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #2196F3;
                color: #ffffff;
            }
            QPushButton {
                background-color: #2196F3;
                color: #ffffff;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #1565C0;
            }
            QLineEdit {
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                padding: 6px;
                background-color: #ffffff;
            }
            QLineEdit:focus {
                border-color: #2196F3;
                outline: none;
            }
            QTextEdit {
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                padding: 6px;
                background-color: #ffffff;
            }
            QTableWidget {
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                background-color: #ffffff;
            }
            QTableWidget::item {
                padding: 4px;
            }
            QTableWidget::item:selected {
                background-color: #E3F2FD;
                color: #1976D2;
            }
            QProgressBar {
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                background-color: #f5f5f5;
            }
            QProgressBar::chunk {
                background-color: #2196F3;
                border-radius: 2px;
            }
        """)
    
    def initialize_plugins(self):
        """初始化插件系统"""
        # 添加默认插件路径
        plugin_paths = [
            os.path.join(os.path.dirname(__file__), "..", "plugins"),
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "plugins")
        ]
        
        for path in plugin_paths:
            plugin_manager.add_plugin_path(os.path.abspath(path))
        
        # 确保插件目录存在
        for path in plugin_paths:
            abs_path = os.path.abspath(path)
            if not os.path.exists(abs_path):
                os.makedirs(abs_path, exist_ok=True)
        
        # 加载插件
        self.status_label.setText("正在加载插件...")
        loaded_plugins = plugin_manager.load_plugins(self)
        
        if loaded_plugins:
            self.status_label.setText(f"已加载 {len(loaded_plugins)} 个插件")
        else:
            self.status_label.setText("就绪")
    
    def start_api_server(self):
        """启动API服务器"""
        try:
            if api_server.start():
                # 延迟显示，确保服务器有足够时间启动
                from PyQt5.QtCore import QTimer
                QTimer.singleShot(1000, lambda: self.status_label.setText("API服务器已启动，监听地址: 0.0.0.0:5000"))
            else:
                self.status_label.setText("API服务器启动失败")
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.status_label.setText(f"API服务器启动失败: {str(e)}")
    
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
        
        # 创建按钮区域
        button_layout = QHBoxLayout()
        
        # 生成按钮
        generate_btn = QPushButton("生成测试用例")
        generate_btn.clicked.connect(self.generate_test_cases)
        button_layout.addWidget(generate_btn)
        
        # 导入按钮
        import_btn = QPushButton("导入测试用例")
        import_btn.clicked.connect(self.import_test_cases)
        button_layout.addWidget(import_btn)
        
        # 导出按钮
        export_btn = QPushButton("导出测试用例")
        export_btn.clicked.connect(self.export_test_cases)
        button_layout.addWidget(export_btn)
        
        # 保存按钮
        save_btn = QPushButton("保存测试用例")
        save_btn.clicked.connect(self.save_test_cases)
        button_layout.addWidget(save_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
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
        """解析文档"""
        try:
            path = self.doc_path_edit.text().strip()
            if not path:
                QMessageBox.warning(self, "警告", "请输入文档路径")
                return
            
            # 解析文档
            self.swagger_doc = EnhancedDocParser.parse_doc(path)
            self.endpoints = EnhancedDocParser.extract_endpoints(self.swagger_doc)
            
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
            # 检查是否是自定义错误
            if hasattr(e, 'solution') and e.solution:
                error_message = f"解析文档失败: {str(e)}\n\n解决方案: {e.solution}"
            else:
                error_message = f"解析文档失败: {str(e)}"
            QMessageBox.critical(self, "错误", error_message)
    
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
        if 0 <= index < len(self.test_cases):
            test_case = self.test_cases[index]
            editor = TestCaseEditor(test_case, self)
            if editor.exec_() == TestCaseEditor.Accepted:
                updated_test_case = editor.get_test_case()
                if TestCaseManager.update_test_case(self.test_cases, index, updated_test_case):
                    self.update_test_cases_table()
                    QMessageBox.information(self, "成功", "测试用例更新成功")
                else:
                    QMessageBox.critical(self, "错误", "测试用例更新失败")
    
    def import_test_cases(self):
        """导入测试用例"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(self, "选择测试用例文件", "", "JSON/YAML文件 (*.json *.yaml *.yml)")
            if file_path:
                imported_test_cases = TestCaseManager.load_test_cases(file_path)
                self.test_cases.extend(imported_test_cases)
                self.update_test_cases_table()
                QMessageBox.information(self, "成功", f"导入测试用例成功，共导入 {len(imported_test_cases)} 个用例")
        except Exception as e:
            # 检查是否是自定义错误
            if hasattr(e, 'solution') and e.solution:
                error_message = f"导入测试用例失败: {str(e)}\n\n解决方案: {e.solution}"
            else:
                error_message = f"导入测试用例失败: {str(e)}"
            QMessageBox.critical(self, "错误", error_message)
    
    def export_test_cases(self):
        """导出测试用例"""
        try:
            if not self.test_cases:
                QMessageBox.warning(self, "警告", "没有测试用例可导出")
                return
            
            file_path, _ = QFileDialog.getSaveFileName(self, "保存测试用例文件", "test_cases.json", "JSON文件 (*.json);;YAML文件 (*.yaml *.yml)")
            if file_path:
                if TestCaseManager.export_test_cases(self.test_cases, file_path):
                    QMessageBox.information(self, "成功", "测试用例导出成功")
                else:
                    QMessageBox.critical(self, "错误", "测试用例导出失败")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导出测试用例失败: {str(e)}")
    
    def save_test_cases(self):
        """保存测试用例"""
        try:
            if not self.test_cases:
                QMessageBox.warning(self, "警告", "没有测试用例可保存")
                return
            
            file_path, _ = QFileDialog.getSaveFileName(self, "保存测试用例文件", "test_cases.json", "JSON文件 (*.json);;YAML文件 (*.yaml *.yml)")
            if file_path:
                if TestCaseManager.save_test_cases(self.test_cases, file_path):
                    QMessageBox.information(self, "成功", "测试用例保存成功")
                else:
                    QMessageBox.critical(self, "错误", "测试用例保存失败")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存测试用例失败: {str(e)}")
    
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
            
            # 更新状态
            self.status_label.setText("正在执行测试...")
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, len(self.test_cases))
            
            # 创建执行器
            executor = TestExecutor(self.base_url)
            
            # 执行测试
            self.test_results = executor.execute_test_cases(self.test_cases)
            
            # 模拟进度更新
            for i in range(len(self.test_cases) + 1):
                self.progress_bar.setValue(i)
                self.status_label.setText(f"执行测试用例 {i}/{len(self.test_cases)}")
                # 处理事件循环，确保UI更新
                QApplication.processEvents()
            
            # 更新结果表格
            self.update_test_results_table()
            
            # 重置状态
            self.progress_bar.setVisible(False)
            self.status_label.setText("测试执行完成")
            
            QMessageBox.information(self, "成功", "测试执行完成")
            
        except Exception as e:
            # 重置状态
            self.progress_bar.setVisible(False)
            self.status_label.setText("就绪")
            
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
    
    def generate_html_report(self):
        """生成HTML报告"""
        self.generate_report('html')
    
    def generate_json_report(self):
        """生成JSON报告"""
        self.generate_report('json')