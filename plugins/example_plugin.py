from app.core.plugin_system import PluginInterface

class ExamplePlugin(PluginInterface):
    """示例插件"""
    
    @property
    def name(self) -> str:
        return "ExamplePlugin"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def description(self) -> str:
        return "这是一个示例插件，用于测试插件系统"
    
    def initialize(self, app: any) -> bool:
        """初始化插件"""
        print(f"初始化示例插件: {self.name} v{self.version}")
        print(f"插件描述: {self.description}")
        
        # 可以在这里添加插件的初始化逻辑
        # 例如，向应用程序添加新的功能、修改现有功能等
        
        return True
    
    def shutdown(self) -> bool:
        """关闭插件"""
        print(f"关闭示例插件: {self.name}")
        
        # 可以在这里添加插件的清理逻辑
        
        return True