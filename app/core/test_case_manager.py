import json
import yaml
from typing import List, Dict, Any, Optional
from app.core.exceptions import create_error, ValidationError
from app.utils.logger import logger
from app.utils.common_utils import ensure_dir_exists, get_file_extension

class TestCaseManager:
    """测试用例管理类"""
    
    @staticmethod
    def save_test_cases(test_cases: List[Dict[str, Any]], file_path: str) -> bool:
        """
        保存测试用例到文件
        
        Args:
            test_cases: 测试用例列表
            file_path: 文件路径
        
        Returns:
            bool: 是否保存成功
        """
        try:
            # 确保目录存在
            dir_path = file_path.rsplit('/', 1)[0] if '/' in file_path else ''
            if dir_path:
                ensure_dir_exists(dir_path)
            
            # 根据文件扩展名选择保存格式
            ext = get_file_extension(file_path)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                if ext in ['yaml', 'yml']:
                    yaml.dump(test_cases, f, ensure_ascii=False, default_flow_style=False)
                else:
                    json.dump(test_cases, f, ensure_ascii=False, indent=2)
            
            logger.info(f"测试用例保存成功: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"测试用例保存失败: {str(e)}")
            return False
    
    @staticmethod
    def load_test_cases(file_path: str) -> List[Dict[str, Any]]:
        """
        从文件加载测试用例
        
        Args:
            file_path: 文件路径
        
        Returns:
            List[Dict[str, Any]]: 测试用例列表
        """
        try:
            # 根据文件扩展名选择加载格式
            ext = get_file_extension(file_path)
            
            with open(file_path, 'r', encoding='utf-8') as f:
                if ext in ['yaml', 'yml']:
                    test_cases = yaml.safe_load(f)
                else:
                    test_cases = json.load(f)
            
            # 验证测试用例格式
            if not isinstance(test_cases, list):
                error = create_error('VALIDATION_FAILED', '测试用例文件格式错误，应为列表')
                raise error
            
            # 验证每个测试用例
            for i, test_case in enumerate(test_cases):
                if not isinstance(test_case, dict):
                    error = create_error('VALIDATION_FAILED', f'测试用例 {i+1} 格式错误，应为字典')
                    raise error
                
                # 检查必要字段
                required_fields = ['id', 'name', 'method', 'path']
                for field in required_fields:
                    if field not in test_case:
                        error = create_error('PARAMETER_MISSING', f'测试用例 {i+1} 缺少必要字段: {field}')
                        raise error
            
            logger.info(f"测试用例加载成功: {file_path}")
            return test_cases
            
        except ValidationError:
            raise
        except Exception as e:
            error = create_error('VALIDATION_FAILED', f'测试用例加载失败: {str(e)}')
            raise error
    
    @staticmethod
    def import_test_cases(file_path: str) -> List[Dict[str, Any]]:
        """
        导入测试用例
        
        Args:
            file_path: 文件路径
        
        Returns:
            List[Dict[str, Any]]: 导入的测试用例列表
        """
        return TestCaseManager.load_test_cases(file_path)
    
    @staticmethod
    def export_test_cases(test_cases: List[Dict[str, Any]], file_path: str) -> bool:
        """
        导出测试用例
        
        Args:
            test_cases: 测试用例列表
            file_path: 文件路径
        
        Returns:
            bool: 是否导出成功
        """
        return TestCaseManager.save_test_cases(test_cases, file_path)
    
    @staticmethod
    def validate_test_case(test_case: Dict[str, Any]) -> bool:
        """
        验证测试用例格式
        
        Args:
            test_case: 测试用例
        
        Returns:
            bool: 是否验证通过
        """
        try:
            # 检查必要字段
            required_fields = ['id', 'name', 'method', 'path']
            for field in required_fields:
                if field not in test_case:
                    error = create_error('PARAMETER_MISSING', f'测试用例缺少必要字段: {field}')
                    raise error
            
            # 检查字段类型
            if not isinstance(test_case['method'], str):
                error = create_error('VALIDATION_FAILED', '测试用例method字段应为字符串')
                raise error
            
            if not isinstance(test_case['path'], str):
                error = create_error('VALIDATION_FAILED', '测试用例path字段应为字符串')
                raise error
            
            # 检查可选字段类型
            optional_fields = ['headers', 'params', 'data', 'json', 'expected_status']
            for field in optional_fields:
                if field in test_case:
                    if field in ['headers', 'params', 'data', 'json']:
                        if not isinstance(test_case[field], dict):
                            error = create_error('VALIDATION_FAILED', f'测试用例{field}字段应为字典')
                            raise error
                    elif field == 'expected_status':
                        if not isinstance(test_case[field], int):
                            error = create_error('VALIDATION_FAILED', '测试用例expected_status字段应为整数')
                            raise error
            
            return True
            
        except ValidationError:
            raise
        except Exception as e:
            error = create_error('VALIDATION_FAILED', f'测试用例验证失败: {str(e)}')
            raise error
    
    @staticmethod
    def generate_test_case_id(method: str, path: str) -> str:
        """
        生成测试用例ID
        
        Args:
            method: HTTP方法
            path: 路径
        
        Returns:
            str: 测试用例ID
        """
        # 移除路径中的特殊字符
        clean_path = path.replace('/', '_').replace('{', '').replace('}', '')
        return f"test_{method.lower()}_{clean_path}"
    
    @staticmethod
    def update_test_case(test_cases: List[Dict[str, Any]], index: int, updated_test_case: Dict[str, Any]) -> bool:
        """
        更新测试用例
        
        Args:
            test_cases: 测试用例列表
            index: 要更新的测试用例索引
            updated_test_case: 更新后的测试用例
        
        Returns:
            bool: 是否更新成功
        """
        try:
            # 验证测试用例格式
            TestCaseManager.validate_test_case(updated_test_case)
            
            # 更新测试用例
            if 0 <= index < len(test_cases):
                test_cases[index] = updated_test_case
                logger.info(f"测试用例更新成功: {updated_test_case['id']}")
                return True
            else:
                logger.error(f"测试用例索引无效: {index}")
                return False
                
        except Exception as e:
            logger.error(f"测试用例更新失败: {str(e)}")
            return False
    
    @staticmethod
    def add_test_case(test_cases: List[Dict[str, Any]], test_case: Dict[str, Any]) -> bool:
        """
        添加测试用例
        
        Args:
            test_cases: 测试用例列表
            test_case: 要添加的测试用例
        
        Returns:
            bool: 是否添加成功
        """
        try:
            # 验证测试用例格式
            TestCaseManager.validate_test_case(test_case)
            
            # 检查ID是否重复
            existing_ids = [tc['id'] for tc in test_cases]
            if test_case['id'] in existing_ids:
                # 生成新ID
                test_case['id'] = f"{test_case['id']}_new"
                logger.warning(f"测试用例ID重复，已生成新ID: {test_case['id']}")
            
            # 添加测试用例
            test_cases.append(test_case)
            logger.info(f"测试用例添加成功: {test_case['id']}")
            return True
            
        except Exception as e:
            logger.error(f"测试用例添加失败: {str(e)}")
            return False
    
    @staticmethod
    def delete_test_case(test_cases: List[Dict[str, Any]], index: int) -> bool:
        """
        删除测试用例
        
        Args:
            test_cases: 测试用例列表
            index: 要删除的测试用例索引
        
        Returns:
            bool: 是否删除成功
        """
        try:
            if 0 <= index < len(test_cases):
                deleted_test_case = test_cases.pop(index)
                logger.info(f"测试用例删除成功: {deleted_test_case['id']}")
                return True
            else:
                logger.error(f"测试用例索引无效: {index}")
                return False
                
        except Exception as e:
            logger.error(f"测试用例删除失败: {str(e)}")
            return False
