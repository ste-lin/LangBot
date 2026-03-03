"""
飞书卡片 Pipeline 集成模块
将飞书卡片能力集成到 LangBot Pipeline 流程中
"""
import json
from typing import Dict, Optional, Any


class CardPipelineStage:
    """卡片 Pipeline 阶段"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.enabled = self.config.get("enabled", True)
    
    async def process(self, context: Dict) -> Dict:
        """
        处理 Pipeline 上下文
        
        Args:
            context: Pipeline 上下文
            
        Returns:
            处理后的上下文
        """
        if not self.enabled:
            return context
        
        # 检查是否需要发送卡片
        if context.get("card"):
            card_config = context.get("card", {})
            card_type = card_config.get("type")
            
            # 根据卡片类型处理
            if card_type == "form":
                context["response_card"] = await self._build_form_card(card_config)
            elif card_type == "menu":
                context["response_card"] = await self._build_menu_card(card_config)
            elif card_type == "confirm":
                context["response_card"] = await self._build_confirm_card(card_config)
            elif card_type == "template":
                context["response_card"] = await self._build_template_card(card_config)
        
        # 检查是否处理卡片回调
        if context.get("callback"):
            callback_config = context.get("callback", {})
            context["callback_result"] = await self._handle_callback(callback_config)
        
        return context
    
    async def _build_form_card(self, config: Dict) -> Dict:
        """构建表单卡片"""
        from feishu_card import FeishuCardBuilder, CardTemplates
        
        fields = config.get("fields", [])
        
        if config.get("template"):
            # 使用模板
            return CardTemplates.form(
                title=config.get("title", "填写表单"),
                fields=fields,
                submit_callback=config.get("submit_callback", "form_submit")
            )
        
        # 手动构建
        builder = FeishuCardBuilder().set_header(config.get("title", "填写表单"), "blue")
        
        for field in fields:
            field_type = field.get("type")
            cb_id = field.get("callback_id")
            
            if field_type == "text":
                builder.add_text_input(
                    label=field.get("label", ""),
                    callback_id=cb_id,
                    placeholder=field.get("placeholder", ""),
                    multiline=field.get("multiline", False)
                )
            elif field_type == "select":
                builder.add_static_select(
                    label=field.get("label", ""),
                    callback_id=cb_id,
                    options=field.get("options", []),
                    placeholder=field.get("placeholder", "请选择")
                )
        
        builder.add_button_group([
            {"text": "取消", "type": "default", "callback_id": config.get("cancel_callback", "cancel")},
            {"text": "提交", "type": "primary", "callback_id": config.get("submit_callback", "submit")}
        ])
        
        return builder.build()
    
    async def _build_menu_card(self, config: Dict) -> Dict:
        """构建菜单卡片"""
        from feishu_card import FeishuCardBuilder, CardTemplates
        
        options = config.get("options", [])
        
        return CardTemplates.menu(
            title=config.get("title", "请选择"),
            options=options,
            callback_prefix=config.get("callback_prefix", "menu")
        )
    
    async def _build_confirm_card(self, config: Dict) -> Dict:
        """构建确认卡片"""
        from feishu_card import CardTemplates
        
        return CardTemplates.confirm(
            title=config.get("title", "确认"),
            content=config.get("content", ""),
            confirm_callback=config.get("confirm_callback", "confirm"),
            cancel_callback=config.get("cancel_callback", "cancel")
        )
    
    async def _build_template_card(self, config: Dict) -> Dict:
        """构建模板卡片"""
        from feishu_card import quick_card, TemplateMarket
        
        template_id = config.get("template_id")
        template_params = config.get("params", {})
        
        if template_id:
            return quick_card(template_id, **template_params)
        
        return {}
    
    async def _handle_callback(self, config: Dict) -> Dict:
        """处理卡片回调"""
        from feishu_card_callback import create_binding_manager
        
        callback_id = config.get("callback_id")
        value = config.get("value", {})
        user_id = config.get("user_id", "")
        
        # 创建绑定管理器
        manager = create_binding_manager()
        
        # 处理回调
        result = manager.handle_callback(callback_id, value, user_id)
        
        return result


class CardResponseBuilder:
    """卡片响应构建器 - 用于 Pipeline 中快速构建响应"""
    
    @staticmethod
    def simple_text(text: str) -> Dict:
        """简单文本响应"""
        return {"type": "text", "content": text}
    
    @staticmethod
    def card(card_data: Dict) -> Dict:
        """卡片响应"""
        return {"type": "card", "content": card_data}
    
    @staticmethod
    def interactive_card(card_data: Dict, callback_handlers: Dict = None) -> Dict:
        """交互卡片响应"""
        result = {
            "type": "interactive_card",
            "content": card_data
        }
        if callback_handlers:
            result["handlers"] = callback_handlers
        return result
    
    @staticmethod
    def with_callback(card_data: Dict, callback_id: str, handler: callable) -> Dict:
        """带回调的卡片"""
        return {
            "type": "card_with_callback",
            "content": card_data,
            "callback": {
                "callback_id": callback_id,
                "handler": handler
            }
        }


# ==================== Pipeline 集成示例 ====================

def create_card_pipeline_config() -> Dict:
    """创建卡片 Pipeline 配置"""
    return {
        "name": "feishu_card",
        "stage_class": "CardPipelineStage",
        "enabled": True,
        "config": {
            "enabled": True,
            "timeout": 300
        }
    }


# ==================== 使用示例 ====================

async def example_pipeline_usage():
    """Pipeline 使用示例"""
    
    # 示例上下文
    context = {
        "user_id": "user_123",
        "message": "我想预约会议室",
        # 需要发送卡片
        "card": {
            "type": "form",
            "title": "会议室预约",
            "fields": [
                {"type": "select", "label": "会议室", "callback_id": "room",
                 "options": [{"text": "1号会议室", "value": "r1"}, {"text": "2号会议室", "value": "r2"}]},
                {"type": "text", "label": "会议主题", "callback_id": "topic"},
                {"type": "text", "label": "参会人数", "callback_id": "count"}
            ],
            "submit_callback": "book_room"
        }
    }
    
    # 创建 Pipeline 阶段
    stage = CardPipelineStage()
    
    # 处理
    result = await stage.process(context)
    
    print(result.get("response_card"))
    
    # 示例：处理回调
    callback_context = {
        "callback": {
            "callback_id": "book_room",
            "value": {"room": "r1", "topic": "周会", "count": "10"},
            "user_id": "user_123"
        }
    }
    
    result = await stage.process(callback_context)
    print(result.get("callback_result"))
