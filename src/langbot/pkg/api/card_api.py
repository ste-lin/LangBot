"""
飞书卡片 API 接口封装
提供 RESTful API 接口
"""
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import json


@dataclass
class CardAPIResponse:
    """API 响应"""
    code: int = 0
    message: str = "success"
    data: Any = None
    
    def to_dict(self) -> Dict:
        return {
            "code": self.code,
            "message": self.message,
            "data": self.data
        }
    
    @classmethod
    def success(cls, data: Any = None) -> "CardAPIResponse":
        return cls(code=0, message="success", data=data)
    
    @classmethod
    def error(cls, message: str, code: int = 1) -> "CardAPIResponse":
        return cls(code=code, message=message, data=None)


class FeishuCardAPI:
    """飞书卡片 API"""
    
    def __init__(self, adapter=None):
        self.adapter = adapter
    
    # ==================== 卡片操作 ====================
    
    async def create_card(
        self,
        receive_id: str,
        card_content: Dict,
        msg_type: str = "interactive"
    ) -> CardAPIResponse:
        """创建卡片消息"""
        try:
            if self.adapter:
                message_id = await self.adapter.send_card_message(
                    chat_id=receive_id,
                    card_content=card_content
                )
                return CardAPIResponse.success({"message_id": message_id})
            return CardAPIResponse.error("Adapter not configured")
        except Exception as e:
            return CardAPIResponse.error(str(e))
    
    async def update_card(
        self,
        message_id: str,
        card_content: Dict
    ) -> CardAPIResponse:
        """更新卡片"""
        try:
            if self.adapter:
                await self.adapter.update_card_with_result(
                    message_id=message_id,
                    callback_id="",
                    result={"type": "card", "content": card_content},
                    user_id=""
                )
                return CardAPIResponse.success()
            return CardAPIResponse.error("Adapter not configured")
        except Exception as e:
            return CardAPIResponse.error(str(e))
    
    async def reply_card(
        self,
        message_id: str,
        card_content: Dict,
        callback_handlers: Dict = None
    ) -> CardAPIResponse:
        """回复卡片"""
        try:
            if self.adapter:
                await self.adapter.reply_interactive_card(
                    message_source=None,
                    card_content=card_content,
                    callback_handlers=callback_handlers
                )
                return CardAPIResponse.success()
            return CardAPIResponse.error("Adapter not configured")
        except Exception as e:
            return CardAPIResponse.error(str(e))
    
    # ==================== 模板操作 ====================
    
    def list_templates(self, category: str = None) -> CardAPIResponse:
        """列出模板"""
        from feishu_card import list_templates
        templates = list_templates(category)
        return CardAPIResponse.success(templates)
    
    def get_template(self, template_id: str) -> CardAPIResponse:
        """获取模板"""
        from feishu_card import get_template
        template = get_template(template_id)
        if template:
            return CardAPIResponse.success(template)
        return CardAPIResponse.error("Template not found", 404)
    
    def create_from_template(
        self,
        template_id: str,
        **kwargs
    ) -> CardAPIResponse:
        """从模板创建卡片"""
        from feishu_card import quick_card
        try:
            card = quick_card(template_id, **kwargs)
            return CardAPIResponse.success(card)
        except Exception as e:
            return CardAPIResponse.error(str(e))
    
    # ==================== 回调操作 ====================
    
    def handle_callback(
        self,
        callback_data: Dict
    ) -> CardAPIResponse:
        """处理回调"""
        from feishu_card_callback import create_binding_manager
        
        action = callback_data.get("action", {})
        callback_id = action.get("callback_id", "")
        value = action.get("value", {})
        user_id = callback_data.get("operator", {}).get("user_id", "")
        
        manager = create_binding_manager()
        result = manager.handle_callback(callback_id, value, user_id)
        
        return CardAPIResponse.success(result)
    
    def list_bindings(self) -> CardAPIResponse:
        """列出回调绑定"""
        from feishu_card_callback import create_binding_manager
        manager = create_binding_manager()
        bindings = manager.list_bindings()
        return CardAPIResponse.success(bindings)
    
    def register_binding(
        self,
        callback_id: str,
        action: str,
        handler_type: str,
        handler_config: Dict = None,
        description: str = ""
    ) -> CardAPIResponse:
        """注册回调绑定"""
        from feishu_card_callback import create_binding_manager
        manager = create_binding_manager()
        manager.register_binding(
            callback_id=callback_id,
            action=action,
            handler_type=handler_type,
            handler_config=handler_config or {},
            description=description
        )
        return CardAPIResponse.success()


class CardAPIRouter:
    """卡片 API 路由"""
    
    def __init__(self):
        self.api = FeishuCardAPI()
    
    async def dispatch(self, path: str, method: str, data: Dict = None) -> Dict:
        """分发请求"""
        data = data or {}
        
        # 路由映射
        routes = {
            # 卡片操作
            ("POST", "/cards"): self.api.create_card,
            ("PUT", "/cards/{id}"): self.api.update_card,
            ("POST", "/cards/{id}/reply"): self.api.reply_card,
            
            # 模板操作
            ("GET", "/templates"): lambda: self.api.list_templates(data.get("category")),
            ("GET", "/templates/{id}"): lambda: self.api.get_template(data.get("template_id")),
            ("POST", "/templates/create"): lambda: self.api.create_from_template(
                data.get("template_id"), **data.get("params", {})
            ),
            
            # 回调操作
            ("POST", "/callbacks"): self.api.handle_callback,
            ("GET", "/callbacks"): lambda: self.api.list_bindings(),
            ("POST", "/callbacks/register"): lambda: self.api.register_binding(
                data.get("callback_id"),
                data.get("action"),
                data.get("handler_type"),
                data.get("handler_config"),
                data.get("description")
            ),
        }
        
        key = (method, path)
        if key in routes:
            handler = routes[key]
            if callable(handler):
                result = handler()
                if hasattr(result, 'to_dict'):
                    return result.to_dict()
                return result
        
        return CardAPIResponse.error("Not found", 404).to_dict()


# ==================== FastAPI 集成 ====================

def create_card_api_routes():
    """创建 FastAPI 路由"""
    try:
        from fastapi import APIRouter
        
        router = APIRouter(prefix="/api/cards", tags=["cards"])
        api = FeishuCardAPI()
        
        @router.post("/")
        async def create_card(request: Dict):
            return await api.create_card(
                receive_id=request.get("receive_id"),
                card_content=request.get("card")
            )
        
        @router.put("/{message_id}")
        async def update_card(message_id: str, request: Dict):
            return await api.update_card(
                message_id=message_id,
                card_content=request.get("card")
            )
        
        @router.get("/templates")
        async def list_templates(category: str = None):
            return api.list_templates(category)
        
        @router.get("/templates/{template_id}")
        async def get_template(template_id: str):
            return api.get_template(template_id)
        
        @router.post("/callbacks")
        async def handle_callback(request: Dict):
            return api.handle_callback(request)
        
        return router
    
    except ImportError:
        # FastAPI 未安装，返回 None
        return None


# ==================== Flask 集成 ====================

def create_card_api_blueprint():
    """创建 Flask Blueprint"""
    try:
        from flask import Blueprint, request, jsonify
        
        blueprint = Blueprint('cards', __name__, url_prefix='/api/cards')
        api = FeishuCardAPI()
        
        @blueprint.route('/', methods=['POST'])
        def create_card():
            data = request.json or {}
            import asyncio
            result = asyncio.run(api.create_card(
                receive_id=data.get('receive_id'),
                card_content=data.get('card')
            ))
            return jsonify(result.to_dict())
        
        @blueprint.route('/templates', methods=['GET'])
        def list_templates():
            category = request.args.get('category')
            return jsonify(api.list_templates(category).to_dict())
        
        @blueprint.route('/callbacks', methods=['POST'])
        def handle_callback():
            data = request.json or {}
            return jsonify(api.handle_callback(data).to_dict())
        
        return blueprint
    
    except ImportError:
        return None
