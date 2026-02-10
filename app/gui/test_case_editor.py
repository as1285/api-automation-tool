from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                            QTextEdit, QComboBox, QSpinBox, QPushButton, QGroupBox,
                            QGridLayout, QTabWidget, QMessageBox, QWidget)
from PyQt5.QtCore import Qt
from typing import Dict, Any, Optional
import json

class TestCaseEditor(QDialog):
    """测试用例编辑对话框"""
    
    def __init__(self, test_case: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.setWindowTitle("编辑测试用例")
        self.setGeometry(100, 100, 800, 600)
        
        # 保存原始测试用例
        self.original_test_case = test_case.copy()
        # 保存编辑后的测试用例
        self.test_case = test_case.copy()
        
        # 创建布局
        self.layout = QVBoxLayout(self)
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        
        # 基本信息标签页
        self.create_basic_info_tab()
        
        # 请求信息标签页
        self.create_request_info_tab()
        
        # 响应信息标签页
        self.create_response_info_tab()
        
        # 添加标签页
        self.layout.addWidget(self.tab_widget)
        
        # 创建按钮区域
        self.create_button_box()
        
        # 填充数据
        self.fill_data()
    
    def create_basic_info_tab(self):
        """创建基本信息标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 创建表单布局
        form_layout = QGridLayout()
        
        # 用例ID
        form_layout.addWidget(QLabel("用例ID:"), 0, 0)
        self.id_edit = QLineEdit()
        form_layout.addWidget(self.id_edit, 0, 1)
        
        # 用例名称
        form_layout.addWidget(QLabel("用例名称:"), 1, 0)
        self.name_edit = QLineEdit()
        form_layout.addWidget(self.name_edit, 1, 1)
        
        # HTTP方法
        form_layout.addWidget(QLabel("HTTP方法:"), 2, 0)
        self.method_combo = QComboBox()
        self.method_combo.addItems(["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"])
        form_layout.addWidget(self.method_combo, 2, 1)
        
        # 路径
        form_layout.addWidget(QLabel("路径:"), 3, 0)
        self.path_edit = QLineEdit()
        form_layout.addWidget(self.path_edit, 3, 1)
        
        # 描述
        form_layout.addWidget(QLabel("描述:"), 4, 0)
        self.description_edit = QTextEdit()
        self.description_edit.setFixedHeight(100)
        form_layout.addWidget(self.description_edit, 4, 1)
        
        layout.addLayout(form_layout)
        self.tab_widget.addTab(tab, "基本信息")
    
    def create_request_info_tab(self):
        """创建请求信息标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 请求头
        headers_group = QGroupBox("请求头")
        headers_layout = QVBoxLayout(headers_group)
        self.headers_edit = QTextEdit()
        self.headers_edit.setPlaceholderText('{"Content-Type": "application/json", "Authorization": "Bearer token"}')
        headers_layout.addWidget(self.headers_edit)
        layout.addWidget(headers_group)
        
        # 查询参数
        params_group = QGroupBox("查询参数")
        params_layout = QVBoxLayout(params_group)
        self.params_edit = QTextEdit()
        self.params_edit.setPlaceholderText('{"page": 1, "limit": 10}')
        params_layout.addWidget(self.params_edit)
        layout.addWidget(params_group)
        
        # 请求体
        body_group = QGroupBox("请求体")
        body_layout = QVBoxLayout(body_group)
        
        # 请求体类型
        body_type_layout = QHBoxLayout()
        body_type_layout.addWidget(QLabel("类型:"))
        self.body_type_combo = QComboBox()
        self.body_type_combo.addItems(["JSON", "Form Data"])
        self.body_type_combo.currentTextChanged.connect(self.on_body_type_changed)
        body_type_layout.addWidget(self.body_type_combo)
        body_type_layout.addStretch()
        body_layout.addLayout(body_type_layout)
        
        # JSON请求体
        self.json_edit = QTextEdit()
        self.json_edit.setPlaceholderText('{"name": "test", "value": 123}')
        body_layout.addWidget(self.json_edit)
        
        # Form Data请求体
        self.data_edit = QTextEdit()
        self.data_edit.setPlaceholderText('{"username": "test", "password": "123456"}')
        self.data_edit.hide()
        body_layout.addWidget(self.data_edit)
        
        layout.addWidget(body_group)
        self.tab_widget.addTab(tab, "请求信息")
    
    def create_response_info_tab(self):
        """创建响应信息标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 预期状态码
        status_layout = QHBoxLayout()
        status_layout.addWidget(QLabel("预期状态码:"))
        self.expected_status_spin = QSpinBox()
        self.expected_status_spin.setRange(100, 599)
        self.expected_status_spin.setValue(200)
        status_layout.addWidget(self.expected_status_spin)
        status_layout.addStretch()
        layout.addLayout(status_layout)
        
        # 预期响应
        expected_response_group = QGroupBox("预期响应")
        expected_response_layout = QVBoxLayout(expected_response_group)
        self.expected_response_edit = QTextEdit()
        self.expected_response_edit.setPlaceholderText('{"code": 200, "message": "success"}')
        expected_response_layout.addWidget(self.expected_response_edit)
        layout.addWidget(expected_response_group)
        
        self.tab_widget.addTab(tab, "响应信息")
    
    def create_button_box(self):
        """创建按钮区域"""
        button_layout = QHBoxLayout()
        
        # 取消按钮
        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        # 保存按钮
        self.save_button = QPushButton("保存")
        self.save_button.clicked.connect(self.save)
        button_layout.addWidget(self.save_button)
        
        button_layout.addStretch()
        self.layout.addLayout(button_layout)
    
    def fill_data(self):
        """填充数据"""
        # 基本信息
        self.id_edit.setText(self.test_case.get('id', ''))
        self.name_edit.setText(self.test_case.get('name', ''))
        method = self.test_case.get('method', 'GET')
        if method in ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]:
            self.method_combo.setCurrentText(method)
        self.path_edit.setText(self.test_case.get('path', ''))
        self.description_edit.setText(self.test_case.get('description', ''))
        
        # 请求信息
        headers = self.test_case.get('headers', {})
        self.headers_edit.setText(json.dumps(headers, ensure_ascii=False, indent=2))
        
        params = self.test_case.get('params', {})
        self.params_edit.setText(json.dumps(params, ensure_ascii=False, indent=2))
        
        # 请求体
        json_data = self.test_case.get('json', {})
        if json_data:
            self.body_type_combo.setCurrentText("JSON")
            self.json_edit.setText(json.dumps(json_data, ensure_ascii=False, indent=2))
        else:
            data = self.test_case.get('data', {})
            if data:
                self.body_type_combo.setCurrentText("Form Data")
                self.data_edit.setText(json.dumps(data, ensure_ascii=False, indent=2))
                self.json_edit.hide()
                self.data_edit.show()
        
        # 响应信息
        expected_status = self.test_case.get('expected_status', 200)
        self.expected_status_spin.setValue(expected_status)
        
        expected_response = self.test_case.get('expected_response', {})
        self.expected_response_edit.setText(json.dumps(expected_response, ensure_ascii=False, indent=2))
    
    def on_body_type_changed(self, text):
        """请求体类型变更处理"""
        if text == "JSON":
            self.data_edit.hide()
            self.json_edit.show()
        else:
            self.json_edit.hide()
            self.data_edit.show()
    
    def save(self):
        """保存数据"""
        try:
            # 基本信息
            self.test_case['id'] = self.id_edit.text().strip()
            self.test_case['name'] = self.name_edit.text().strip()
            self.test_case['method'] = self.method_combo.currentText()
            self.test_case['path'] = self.path_edit.text().strip()
            self.test_case['description'] = self.description_edit.toPlainText().strip()
            
            # 请求信息
            headers_text = self.headers_edit.toPlainText().strip()
            if headers_text:
                self.test_case['headers'] = json.loads(headers_text)
            else:
                self.test_case['headers'] = {}
            
            params_text = self.params_edit.toPlainText().strip()
            if params_text:
                self.test_case['params'] = json.loads(params_text)
            else:
                self.test_case['params'] = {}
            
            # 请求体
            if self.body_type_combo.currentText() == "JSON":
                json_text = self.json_edit.toPlainText().strip()
                if json_text:
                    self.test_case['json'] = json.loads(json_text)
                else:
                    self.test_case['json'] = {}
                # 清除form data
                if 'data' in self.test_case:
                    del self.test_case['data']
            else:
                data_text = self.data_edit.toPlainText().strip()
                if data_text:
                    self.test_case['data'] = json.loads(data_text)
                else:
                    self.test_case['data'] = {}
                # 清除json
                if 'json' in self.test_case:
                    del self.test_case['json']
            
            # 响应信息
            self.test_case['expected_status'] = self.expected_status_spin.value()
            
            expected_response_text = self.expected_response_edit.toPlainText().strip()
            if expected_response_text:
                self.test_case['expected_response'] = json.loads(expected_response_text)
            else:
                self.test_case['expected_response'] = {}
            
            # 验证必要字段
            if not self.test_case['id']:
                QMessageBox.warning(self, "警告", "用例ID不能为空")
                return
            
            if not self.test_case['name']:
                QMessageBox.warning(self, "警告", "用例名称不能为空")
                return
            
            if not self.test_case['path']:
                QMessageBox.warning(self, "警告", "路径不能为空")
                return
            
            # 保存成功
            self.accept()
            
        except json.JSONDecodeError as e:
            QMessageBox.critical(self, "错误", f"JSON格式错误: {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存失败: {str(e)}")
    
    def get_test_case(self) -> Dict[str, Any]:
        """获取编辑后的测试用例"""
        return self.test_case
