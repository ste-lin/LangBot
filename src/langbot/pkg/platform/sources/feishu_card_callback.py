"""
回调绑定配置管理
支持通过配置文件定义卡片回调处理器
"""
import json
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field


@dataclass
class CallbackBinding:
    """回调绑定配置"""
    callback_id: str
    action: str  # 处理动作: reply, update, replace, dialog
    handler_type: str  # python, webhook, template
    handler_config: Dict = field(default_factory=dict)
    description: str = ""
    enabled: bool = True


@dataclass  
class CardCallbackConfig:
    """卡片回调配置"""
    card_id: str
    bindings: List[CallbackBinding] = field(default_factory=list)
    timeout: int = 300  # 超时时间(秒)
    retry: int = 3  # 重试次数


class CallbackBindingManager:
    """回调绑定管理器"""
    
    def __init__(self):
        self._bindings: Dict[str, CallbackBinding] = {}
        self._card_configs: Dict[str, CardCallbackConfig] = {}
        self._handlers: Dict[str, Callable] = {}
    
    def register_binding(
        self,
        callback_id: str,
        action: str = "reply",
        handler_type: str = "python",
        handler_config: Optional[Dict] = None,
        description: str = "",
        enabled: bool = True
    ) -> "CallbackBindingManager":
        """注册回调绑定"""
        binding = CallbackBinding(
            callback_id=callback_id,
            action=action,
            handler_type=handler_type,
            handler_config=handler_config or {},
            description=description,
            enabled=enabled
        )
        self._bindings[callback_id] = binding
        return self
    
    def register_handler(
        self,
        callback_id: str,
        handler: Callable
    ) -> "CallbackBindingManager":
        """注册处理器函数"""
        self._handlers[callback_id] = handler
        return self
    
    def get_binding(self, callback_id: str) -> Optional[CallbackBinding]:
        """获取绑定配置"""
        return self._bindings.get(callback_id)
    
    def get_handler(self, callback_id: str) -> Optional[Callable]:
        """获取处理器"""
        return self._handlers.get(callback_id)
    
    def handle_callback(
        self,
        callback_id: str,
        value: Dict,
        user_id: str,
        context: Dict = None
    ) -> Optional[Dict]:
        """处理回调"""
        binding = self.get_binding(callback_id)
        if not binding or not binding.enabled:
            return None
        
        handler = self.get_handler(callback_id)
        if not handler:
            # 尝试查找通用处理器
            handler = self._handlers.get("_default")
        
        if not handler:
            return {"error": f"No handler for {callback_id}"}
        
        try:
            result = handler(
                callback_id=callback_id,
                value=value,
                user_id=user_id,
                context=context or {}
            )
            return result
        except Exception as e:
            return {"error": str(e)}
    
    def load_from_json(self, json_str: str) -> bool:
        """从 JSON 加载配置"""
        try:
            config = json.loads(json_str)
            
            # 加载全局绑定
            for binding_config in config.get("bindings", []):
                self.register_binding(
                    callback_id=binding_config["callback_id"],
                    action=binding_config.get("action", "reply"),
                    handler_type=binding_config.get("handler_type", "python"),
                    handler_config=binding_config.get("handler_config", {}),
                    description=binding_config.get("description", ""),
                    enabled=binding_config.get("enabled", True)
                )
            
            return True
        except Exception as e:
            print(f"Load config error: {e}")
            return False
    
    def save_to_json(self) -> str:
        """导出配置为 JSON"""
        bindings = []
        for binding in self._bindings.values():
            bindings.append({
                "callback_id": binding.callback_id,
                "action": binding.action,
                "handler_type": binding.handler_type,
                "handler_config": binding.handler_config,
                "description": binding.description,
                "enabled": binding.enabled
            })
        
        return json.dumps({
            "bindings": bindings
        }, ensure_ascii=False, indent=2)
    
    def list_bindings(self) -> List[Dict]:
        """列出所有绑定"""
        return [
            {
                "callback_id": b.callback_id,
                "action": b.action,
                "handler_type": b.handler_type,
                "description": b.description,
                "enabled": b.enabled,
                "has_handler": b.callback_id in self._handlers
            }
            for b in self._bindings.values()
        ]


# ==================== 预置回调配置 ====================

def get_default_bindings() -> List[Dict]:
    """获取默认回调绑定配置"""
    return [
        # 通用操作
        {
            "callback_id": "confirm",
            "action": "reply",
            "handler_type": "template",
            "handler_config": {"template": "success"},
            "description": "确认操作"
        },
        {
            "callback_id": "cancel",
            "action": "reply",
            "handler_type": "template", 
            "handler_config": {"template": "cancelled"},
            "description": "取消操作"
        },
        {
            "callback_id": "submit",
            "action": "update",
            "handler_type": "template",
            "handler_config": {"template": "loading"},
            "description": "提交表单"
        },
        # 客服类
        {
            "callback_id": "cs_product",
            "action": "reply",
            "handler_type": "template",
            "handler_config": {"template": "cs_product"},
            "description": "产品咨询"
        },
        {
            "callback_id": "cs_after_sales",
            "action": "reply",
            "handler_type": "template",
            "handler_config": {"template": "cs_after_sales"},
            "description": "售后服务"
        },
        # 订单类
        {
            "callback_id": "query_order",
            "action": "reply",
            "handler_type": "webhook",
            "handler_config": {"url": "/api/orders/query"},
            "description": "查询订单"
        },
        {
            "callback_id": "pay_order",
            "action": "reply",
            "handler_type": "webhook",
            "handler_config": {"url": "/api/orders/pay"},
            "description": "支付订单"
        }
    ]


# ==================== 便捷函数 ====================

def create_binding_manager(config: str = None) -> CallbackBindingManager:
    """创建回调绑定管理器"""
    manager = CallbackBindingManager()
    
    # 加载默认配置
    if config:
        manager.load_from_json(config)
    else:
        # 加载默认绑定
        for binding in get_default_bindings():
            manager.register_binding(**binding)
    
    return manager
