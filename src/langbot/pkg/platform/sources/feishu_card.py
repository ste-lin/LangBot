"""
飞书交互卡片模块
提供按钮、选择器、表单等交互组件
"""
import json
import uuid
from typing import Optional, Callable, Dict, Any, List


class FeishuCardBuilder:
    """飞书交互卡片构建器"""
    
    def __init__(self):
        self.elements: List[Dict] = []
        self.card_id: Optional[str] = None
        self.callback_id: str = str(uuid.uuid4())
    
    def add_div(self, text: str) -> "FeishuCardBuilder":
        """添加分割线"""
        self.elements.append({
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": text
            }
        })
        return self
    
    def add_button(
        self, 
        text: str, 
        callback_id: str, 
        value: Optional[Dict] = None,
        type: str = "primary"
    ) -> "FeishuCardBuilder":
        """添加按钮"""
        btn = {
            "tag": "action",
            "actions": [
                {
                    "tag": "button",
                    "text": {
                        "tag": "plain_text",
                        "content": text
                    },
                    "type": type,
                    "value": value or {"action": callback_id},
                    "callback_id": callback_id
                }
            ]
        }
        self.elements.append(btn)
        return self
    
    def add_buttons_row(
        self, 
        buttons: List[Dict]
    ) -> "FeishuCardBuilder":
        """添加一行按钮"""
        actions = []
        for btn in buttons:
            actions.append({
                "tag": "button",
                "text": {
                    "tag": "plain_text",
                    "content": btn["text"]
                },
                "type": btn.get("type", "default"),
                "value": btn.get("value", {"action": btn["callback_id"]}),
                "callback_id": btn["callback_id"]
            })
        self.elements.append({
            "tag": "action",
            "actions": actions
        })
        return self
    
    def add_select(
        self,
        label: str,
        callback_id: str,
        options: List[Dict],
        placeholder: str = "请选择"
    ) -> "FeishuCardBuilder":
        """添加选择器"""
        self.elements.append({
            "tag": "input",
            "label": {
                "tag": "plain_text",
                "content": label
            },
            "element": {
                "tag": "static_select",
                "placeholder": {
                    "tag": "plain_text",
                    "content": placeholder
                },
                "options": [
                    {
                        "text": {
                            "tag": "plain_text",
                            "content": opt["text"]
                        },
                        "value": opt["value"]
                    }
                    for opt in options
                ],
                "value": {
                    "tag": "variable",
                    "children": callback_id
                }
            },
            "callback_id": callback_id
        })
        return self
    
    def add_input(
        self,
        label: str,
        callback_id: str,
        placeholder: str = "请输入",
        multiline: bool = False
    ) -> "FeishuCardBuilder":
        """添加输入框"""
        self.elements.append({
            "tag": "input",
            "label": {
                "tag": "plain_text",
                "content": label
            },
            "element": {
                "tag": "plain_text_input",
                "placeholder": {
                    "tag": "plain_text",
                    "content": placeholder
                },
                "multiline": multiline
            },
            "callback_id": callback_id
        })
        return self
    
    def add_image(self, url: str, alt: str = "") -> "FeishuCardBuilder":
        """添加图片"""
        self.elements.append({
            "tag": "img",
            "img_url": url,
            "alt": {
                "tag": "plain_text",
                "content": alt
            }
        })
        return self
    
    def add_note(self, text: str) -> "FeishuCardBuilder":
        """添加备注"""
        self.elements.append({
            "tag": "note",
            "elements": [
                {
                    "tag": "plain_text",
                    "content": text,
                    "text_align": "left",
                    "text_color": "grey"
                }
            ]
        })
        return self
    
    def set_title(self, title: str) -> "FeishuCardBuilder":
        """设置卡片标题"""
        self.title = title
        return self
    
    def build(self) -> Dict:
        """构建卡片 JSON"""
        card = {
            "config": {
                "update_multi": True
            },
            "elements": self.elements
        }
        
        if hasattr(self, 'title'):
            card["header"] = {
                "title": {
                    "tag": "plain_text",
                    "content": self.title
                },
                "template": "blue"
            }
        
        return card
    
    def build_json(self) -> str:
        """构建卡片 JSON 字符串"""
        return json.dumps(self.build(), ensure_ascii=False)


class FeishuCardManager:
    """飞书交互卡片管理器"""
    
    def __init__(self):
        self.handlers: Dict[str, Callable] = {}
        self.card_states: Dict[str, Dict] = {}
    
    def register_handler(self, callback_id: str, handler: Callable):
        """注册回调处理器"""
        self.handlers[callback_id] = handler
    
    async def handle_callback(
        self, 
        callback_id: str, 
        value: Dict, 
        user_id: str
    ) -> Optional[Dict]:
        """处理卡片回调"""
        if callback_id in self.handlers:
            handler = self.handlers[callback_id]
            return await handler(callback_id, value, user_id)
        return None
    
    def save_card_state(self, card_id: str, state: Dict):
        """保存卡片状态"""
        self.card_states[card_id] = state
    
    def get_card_state(self, card_id: str) -> Optional[Dict]:
        """获取卡片状态"""
        return self.card_states.get(card_id)


# 预置卡片模板
class CardTemplates:
    """卡片模板"""
    
    @staticmethod
    def confirm_dialog(title: str, content: str, confirm_callback: str, cancel_callback: str):
        """确认对话框"""
        return FeishuCardBuilder() \
            .set_title(title) \
            .add_div(content) \
            .add_buttons_row([
                {"text": "取消", "type": "default", "callback_id": cancel_callback},
                {"text": "确认", "type": "primary", "callback_id": confirm_callback}
            ]) \
            .build()
    
    @staticmethod
    def menu_selection(title: str, options: List[Dict], callback_id: str):
        """菜单选择"""
        builder = FeishuCardBuilder().set_title(title)
        for opt in options:
            builder.add_button(
                opt["text"],
                f"{callback_id}_{opt['value']}",
                {"selected": opt["value"]},
                opt.get("type", "default")
            )
        return builder.build()
    
    @staticmethod
    def form_card(title: str, fields: List[Dict], submit_callback: str):
        """表单卡片"""
        builder = FeishuCardBuilder().set_title(title)
        for field in fields:
            if field["type"] == "select":
                builder.add_select(
                    field["label"],
                    field["callback_id"],
                    field["options"],
                    field.get("placeholder", "请选择")
                )
            elif field["type"] == "input":
                builder.add_input(
                    field["label"],
                    field["callback_id"],
                    field.get("placeholder", "请输入"),
                    field.get("multiline", False)
                )
        builder.add_button("提交", submit_callback, {}, "primary")
        return builder.build()
    
    @staticmethod
    def result_card(title: str, items: List[Dict]):
        """结果展示卡片"""
        builder = FeishuCardBuilder().set_title(title)
        for item in items:
            builder.add_div(f"**{item['label']}**: {item['value']}")
        return builder.build()
