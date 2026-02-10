import os
import importlib.util
import sys
from typing import Dict, Any, List, Optional
from app.utils.logger import logger

class PluginInterface:
    """插件接口"""
    
    @property
    def name(self) -> str:
        """插件名称"""
        raise NotImplementedError
    
    @property
    def version(self) -> str:
        """插件版本"""
        raise NotImplementedError
    
    @property
    def description(self) -> str:
        """插件描述"""
        raise NotImplementedError
    
    def initialize(self, app: Any) -> bool:
        """初始化插件"""
        raise NotImplementedError
    
    def shutdown(self) -> bool:
        """关闭插件"""
        raise NotImplementedError

class PluginManager:
    """插件管理器"""
    
    def __init__(self):
        self.plugins: Dict[str, PluginInterface] = {}
        self.plugin_paths: List[str] = []
        
    def add_plugin_path(self, path: str) -> None:
        """添加插件路径"""
        if os.path.exists(path) and path not in self.plugin_paths:
            self.plugin_paths.append(path)
            logger.info(f"添加插件路径: {path}")
    
    def load_plugins(self, app: Any) -> List[str]:
        """加载所有插件"""
        loaded_plugins = []
        
        for plugin_path in self.plugin_paths:
            if not os.path.exists(plugin_path):
                continue
            
            for item in os.listdir(plugin_path):
                item_path = os.path.join(plugin_path, item)
                if os.path.isdir(item_path):
                    # 检查是否是插件目录
                    if os.path.exists(os.path.join(item_path, "__init__.py")):
                        plugin = self._load_plugin(item_path, app)
                        if plugin:
                            loaded_plugins.append(plugin.name)
                elif item.endswith(".py") and not item.startswith("_"):
                    # 检查是否是插件文件
                    plugin = self._load_plugin(item_path, app)
                    if plugin:
                        loaded_plugins.append(plugin.name)
        
        logger.info(f"共加载 {len(loaded_plugins)} 个插件: {', '.join(loaded_plugins)}")
        return loaded_plugins
    
    def _load_plugin(self, plugin_file: str, app: Any) -> Optional[PluginInterface]:
        """加载单个插件"""
        try:
            # 提取模块名
            module_name = os.path.basename(plugin_file).replace(".py", "")
            
            # 加载模块
            spec = importlib.util.spec_from_file_location(module_name, plugin_file)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = module
                spec.loader.exec_module(module)
                
                # 查找插件类
                for name, obj in module.__dict__.items():
                    if (isinstance(obj, type) and 
                        issubclass(obj, PluginInterface) and 
                        obj != PluginInterface):
                        # 创建插件实例
                        plugin_instance = obj()
                        
                        # 初始化插件
                        if plugin_instance.initialize(app):
                            self.plugins[plugin_instance.name] = plugin_instance
                            logger.info(f"成功加载插件: {plugin_instance.name} v{plugin_instance.version}")
                            return plugin_instance
                        else:
                            logger.warning(f"插件初始化失败: {plugin_instance.name}")
                            return None
            
        except Exception as e:
            logger.error(f"加载插件失败 ({plugin_file}): {str(e)}")
        
        return None
    
    def get_plugin(self, name: str) -> Optional[PluginInterface]:
        """获取插件"""
        return self.plugins.get(name)
    
    def get_all_plugins(self) -> Dict[str, PluginInterface]:
        """获取所有插件"""
        return self.plugins
    
    def unload_plugins(self) -> None:
        """卸载所有插件"""
        for name, plugin in self.plugins.items():
            try:
                if plugin.shutdown():
                    logger.info(f"成功卸载插件: {name}")
                else:
                    logger.warning(f"插件卸载失败: {name}")
            except Exception as e:
                logger.error(f"卸载插件时发生错误 ({name}): {str(e)}")
        
        self.plugins.clear()
        logger.info("所有插件已卸载")

# 全局插件管理器实例
plugin_manager = PluginManager()