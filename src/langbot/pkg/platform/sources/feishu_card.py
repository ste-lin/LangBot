"""
飞书交互卡片模块 v2.0
提供按钮、选择器、表单等交互组件
支持飞书卡片 2.0 全部组件
"""
import json
import uuid
from typing import Optional, Callable, Dict, Any, List, Union


class FeishuCardBuilder:
    """飞书交互卡片构建器 v2.0"""
    
    # 按钮类型
    BUTTON_PRIMARY = "primary"
    BUTTON_DEFAULT = "default"
    BUTTON_DANGER = "danger"
    
    # 卡片模板颜色
    TEMPLATE_BLUE = "blue"
    TEMPLATE_GREEN = "green"
    TEMPLATE_RED = "red"
    TEMPLATE_GREY = "grey"
    TEMPLATE_YELLOW = "yellow"
    TEMPLATE_ORANGE = "orange"
    TEMPLATE_CYAN = "cyan"
    TEMPLATE_PURPLE = "purple"
    
    def __init__(self):
        self.elements: List[Dict] = []
        self.header: Optional[Dict] = None
        self.config: Dict = {"update_multi": True}
        self.card_id: Optional[str] = None
        self.callback_id: str = str(uuid.uuid4())
        self._image_count = 0
    
    # ==================== Header ====================
    
    def set_header(
        self, 
        title: str, 
        template: str = "blue"
    ) -> "FeishuCardBuilder":
        """设置卡片标题"""
        self.header = {
            "title": {
                "tag": "plain_text",
                "content": title
            },
            "template": template
        }
        return self
    
    # ==================== 基础元素 ====================
    
    def add_div(
        self, 
        text: str, 
        markdown: bool = True
    ) -> "FeishuCardBuilder":
        """添加文本块"""
        self.elements.append({
            "tag": "div",
            "text": {
                "tag": "lark_md" if markdown else "plain_text",
                "content": text
            }
        })
        return self
    
    def add_hr(self) -> "FeishuCardBuilder":
        """添加分割线"""
        self.elements.append({
            "tag": "hr"
        })
        return self
    
    def add_image(
        self, 
        img_url: str, 
        alt: str = "",
        fit: str = "contain"
    ) -> "FeishuCardBuilder":
        """添加图片"""
        self._image_count += 1
        self.elements.append({
            "tag": "img",
            "img_url": img_url,
            "alt": {
                "tag": "plain_text",
                "content": alt or f"image_{self._image_count}"
            },
            "fit": fit
        })
        return self
    
    # ==================== 按钮组件 ====================
    
    def add_button(
        self, 
        text: str, 
        callback_id: str, 
        value: Optional[Dict] = None,
        type: str = "primary",
        url: Optional[str] = None
    ) -> "FeishuCardBuilder":
        """添加单个按钮"""
        btn: Dict = {
            "tag": "button",
            "text": {
                "tag": "plain_text",
                "content": text
            },
            "type": type,
            "value": value or {"callback_id": callback_id}
        }
        
        if url:
            # 链接按钮
            btn["url"] = url
            del btn["value"]
        else:
            # 回调按钮
            btn["callback_id"] = callback_id
        
        self.elements.append({
            "tag": "action",
            "actions": [btn]
        })
        return self
    
    def add_button_group(
        self, 
        buttons: List[Dict],
        layout: str = "default"
    ) -> "FeishuCardBuilder":
        """添加按钮组"""
        actions = []
        for btn in buttons:
            action: Dict = {
                "tag": "button",
                "text": {
                    "tag": "plain_text",
                    "content": btn["text"]
                },
                "type": btn.get("type", "default")
            }
            
            if btn.get("url"):
                action["url"] = btn["url"]
            else:
                action["callback_id"] = btn["callback_id"]
                action["value"] = btn.get("value", {"callback_id": btn["callback_id"]})
            
            actions.append(action)
        
        self.elements.append({
            "tag": "action",
            "actions": actions
        })
        return self
    
    def add_confirm(
        self, 
        title: str, 
        content: str,
        confirm_text: str = "确认",
        cancel_text: str = "取消",
        confirm_callback: str = "confirm",
        cancel_callback: str = "cancel"
    ) -> "FeishuCardBuilder":
        """添加确认对话框"""
        # 标题
        self.set_header(title, self.TEMPLATE_BLUE)
        
        # 内容
        self.add_div(content)
        
        # 按钮组
        self.add_button_group([
            {"text": cancel_text, "type": "default", "callback_id": cancel_callback},
            {"text": confirm_text, "type": "primary", "callback_id": confirm_callback}
        ])
        
        return self
    
    # ==================== 选择器组件 ====================
    
    def add_static_select(
        self,
        label: str,
        callback_id: str,
        options: List[Dict],
        placeholder: str = "请选择",
        initial_value: Optional[str] = None
    ) -> "FeishuCardBuilder":
        """添加下拉选择器（单选）"""
        element: Dict = {
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
                ]
            }
        }
        
        if initial_value:
            element["element"]["initial_value"] = initial_value
        
        element["callback_id"] = callback_id
        
        self.elements.append(element)
        return self
    
    def add_multi_select(
        self,
        label: str,
        callback_id: str,
        options: List[Dict],
        placeholder: str = "请选择多个",
        initial_values: Optional[List[str]] = None
    ) -> "FeishuCardBuilder":
        """添加下拉选择器（多选）"""
        element: Dict = {
            "tag": "input",
            "label": {
                "tag": "plain_text",
                "content": label
            },
            "element": {
                "tag": "multi_static_select",
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
                ]
            }
        }
        
        if initial_values:
            element["element"]["initial_values"] = initial_values
        
        element["callback_id"] = callback_id
        
        self.elements.append(element)
        return self
    
    def add_pulled_merge_select(
        self,
        label: str,
        callback_id: str,
        options: List[Dict],
        placeholder: str = "请选择",
        initial_value: Optional[str] = None,
        expand: int = 1
    ) -> "FeishuCardBuilder":
        """添加可拉取合并的选择器（支持动态加载更多选项）"""
        element: Dict = {
            "tag": "input",
            "label": {
                "tag": "plain_text",
                "content": label
            },
            "element": {
                "tag": "pulled_merge_select",
                "placeholder": {
                    "tag": "plain_text",
                    "content": "请选择或搜索"
                },
                "options": [
                    {
                        "text": {
                            "tag": "plain_text",
                            "content": opt["text"]
                        },
                        "value": opt["value"]
                    }
                    for opt in options[:20]  # 初始显示20个
                ],
                "expand": expand,
                "placeholder": {
                    "tag": "plain_text", 
                    "content": placeholder
                }
            }
        }
        
        if initial_value:
            element["element"]["initial_value"] = initial_value
        
        element["callback_id"] = callback_id
        
        self.elements.append(element)
        return self
    
    def add_overflow(
        self,
        options: List[Dict]
    ) -> "FeishuCardBuilder":
        """添加溢出菜单（更多操作）"""
        self.elements.append({
            "tag": "overflow",
            "actions": [
                {
                    "tag": "option",
                    "text": {
                        "tag": "plain_text",
                        "content": opt["text"]
                    },
                    "value": opt.get("value", opt["text"]),
                    "url": opt.get("url", "")
                }
                for opt in options
            ]
        })
        return self
    
    # ==================== 输入框组件 ====================
    
    def add_text_input(
        self,
        label: str,
        callback_id: str,
        placeholder: str = "请输入",
        initial_value: Optional[str] = None,
        multiline: bool = False
    ) -> "FeishuCardBuilder":
        """添加文本输入框"""
        element: Dict = {
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
            }
        }
        
        if initial_value:
            element["element"]["initial_value"] = initial_value
        
        element["callback_id"] = callback_id
        
        self.elements.append(element)
        return self
    
    def add_number_input(
        self,
        label: str,
        callback_id: str,
        placeholder: str = "请输入数字",
        initial_value: Optional[str] = None,
        min: Optional[int] = None,
        max: Optional[int] = None
    ) -> "FeishuCardBuilder":
        """添加数字输入框"""
        element: Dict = {
            "tag": "input",
            "label": {
                "tag": "plain_text",
                "content": label
            },
            "element": {
                "tag": "number_input",
                "placeholder": {
                    "tag": "plain_text",
                    "content": placeholder
                }
            }
        }
        
        if initial_value:
            element["element"]["initial_value"] = initial_value
        if min is not None:
            element["element"]["min"] = min
        if max is not None:
            element["element"]["max"] = max
        
        element["callback_id"] = callback_id
        
        self.elements.append(element)
        return self
    
    # ==================== 日期选择器 ====================
    
    def add_date_picker(
        self,
        label: str,
        callback_id: str,
        placeholder: str = "选择日期",
        initial_date: Optional[str] = None
    ) -> "FeishuCardBuilder":
        """添加日期选择器"""
        element: Dict = {
            "tag": "input",
            "label": {
                "tag": "plain_text",
                "content": label
            },
            "element": {
                "tag": "date_picker",
                "placeholder": {
                    "tag": "plain_text",
                    "content": placeholder
                }
            }
        }
        
        if initial_date:
            element["element"]["initial_date"] = initial_date
        
        element["callback_id"] = callback_id
        
        self.elements.append(element)
        return self
    
    def add_datetime_picker(
        self,
        label: str,
        callback_id: str,
        placeholder: str = "选择日期和时间",
        initial_datetime: Optional[str] = None
    ) -> "FeishuCardBuilder":
        """添加日期时间选择器"""
        element: Dict = {
            "tag": "input",
            "label": {
                "tag": "plain_text",
                "content": label
            },
            "element": {
                "tag": "datetime_picker",
                "placeholder": {
                    "tag": "plain_text",
                    "content": placeholder
                }
            }
        }
        
        if initial_datetime:
            element["element"]["initial_datetime"] = initial_datetime
        
        element["callback_id"] = callback_id
        
        self.elements.append(element)
        return self
    
    def add_time_picker(
        self,
        label: str,
        callback_id: str,
        placeholder: str = "选择时间",
        initial_time: Optional[str] = None
    ) -> "FeishuCardBuilder":
        """添加时间选择器"""
        element: Dict = {
            "tag": "input",
            "label": {
                "tag": "plain_text",
                "content": label
            },
            "element": {
                "tag": "time_picker",
                "placeholder": {
                    "tag": "plain_text",
                    "content": placeholder
                }
            }
        }
        
        if initial_time:
            element["element"]["initial_time"] = initial_time
        
        element["callback_id"] = callback_id
        
        self.elements.append(element)
        return self
    
    # ==================== 构建输出 ====================
    
    def build(self) -> Dict:
        """构建卡片 JSON"""
        card: Dict = {
            "config": self.config,
            "elements": self.elements
        }
        
        if self.header:
            card["header"] = self.header
        
        return card
    
    def build_json(self) -> str:
        """构建卡片 JSON 字符串"""
        return json.dumps(self.build(), ensure_ascii=False)
    
    def set_update_multi(self, value: bool = True) -> "FeishuCardBuilder":
        """设置是否支持多次更新"""
        self.config["update_multi"] = value
        return self


# ==================== 回调管理器 ====================

class FeishuCardManager:
    """飞书交互卡片管理器"""
    
    def __init__(self):
        self.handlers: Dict[str, Callable] = {}
        self.card_states: Dict[str, Dict] = {}
        self.pending_inputs: Dict[str, Dict] = {}  # 等待用户输入的会话
    
    def register_handler(
        self, 
        callback_id: str, 
        handler: Callable,
        description: str = ""
    ):
        """注册回调处理器"""
        self.handlers[callback_id] = {
            "handler": handler,
            "description": description
        }
    
    def unregister_handler(self, callback_id: str):
        """注销回调处理器"""
        if callback_id in self.handlers:
            del self.handlers[callback_id]
    
    async def handle_callback(
        self, 
        callback_id: str, 
        value: Dict, 
        user_id: str,
        message_id: str = ""
    ) -> Optional[Dict]:
        """处理卡片回调"""
        # 解析 callback_id 获取实际处理器
        # 支持格式: "action_name" 或 "action_name_extra"
        handler = None
        handler_key = callback_id
        
        # 尝试精确匹配
        if callback_id in self.handlers:
            handler = self.handlers[callback_id]["handler"]
        else:
            # 尝试前缀匹配
            for key in self.handlers:
                if callback_id.startswith(key + "_") or callback_id.startswith(key):
                    handler = self.handlers[key]["handler"]
                    handler_key = key
                    break
        
        if handler:
            try:
                result = await handler(
                    callback_id=handler_key,
                    value=value,
                    user_id=user_id,
                    message_id=message_id
                )
                return result
            except Exception as e:
                return {
                    "type": "text",
                    "content": f"处理出错: {str(e)}"
                }
        
        return None
    
    def save_card_state(
        self, 
        card_id: str, 
        state: Dict,
        ttl: int = 600
    ):
        """保存卡片状态"""
        import time
        self.card_states[card_id] = {
            "state": state,
            "expire_at": time.time() + ttl
        }
    
    def get_card_state(self, card_id: str) -> Optional[Dict]:
        """获取卡片状态"""
        import time
        if card_id in self.card_states:
            card_data = self.card_states[card_id]
            if card_data["expire_at"] > time.time():
                return card_data["state"]
            else:
                del self.card_states[card_id]
        return None
    
    def cleanup_expired(self):
        """清理过期状态"""
        import time
        expired = [
            k for k, v in self.card_states.items() 
            if v["expire_at"] <= time.time()
        ]
        for k in expired:
            del self.card_states[k]


# ==================== 表单验证 ====================

class FormValidator:
    """表单验证器"""
    
    # 验证规则类型
    RULE_REQUIRED = "required"
    RULE_MIN_LENGTH = "min_length"
    RULE_MAX_LENGTH = "max_length"
    RULE_PATTERN = "pattern"
    RULE_MIN = "min"
    RULE_MAX = "max"
    RULE_EMAIL = "email"
    RULE_PHONE = "phone"
    RULE_URL = "url"
    
    # 内置验证规则
    BUILTIN_RULES = {
        "email": {
            "pattern": r'^[\w\.-]+@[\w\.-]+\.\w+$',
            "message": "请输入有效的邮箱地址"
        },
        "phone": {
            "pattern": r'^1[3-9]\d{9}$',
            "message": "请输入有效的手机号"
        },
        "url": {
            "pattern": r'^https?://[\w\.-]+',
            "message": "请输入有效的URL"
        },
        "id_card": {
            "pattern": r'^\d{17}[\dXx]$',
            "message": "请输入有效的身份证号码"
        }
    }
    
    @staticmethod
    def validate(value: Any, rules: List[Dict]) -> Dict:
        """
        验证值
        
        Args:
            value: 要验证的值
            rules: 验证规则列表
            
        Returns:
            {"valid": bool, "message": "错误信息"}
        """
        for rule in rules:
            rule_type = rule.get("type")
            
            # 必填验证
            if rule_type == FormValidator.RULE_REQUIRED:
                if value is None or str(value).strip() == "":
                    return {
                        "valid": False,
                        "message": rule.get("message", "此项为必填项")
                    }
            
            # 最小长度
            elif rule_type == FormValidator.RULE_MIN_LENGTH:
                if value is not None and len(str(value)) < rule.get("min", 0):
                    return {
                        "valid": False,
                        "message": rule.get("message", f"长度不能少于{rule.get('min')}个字符")
                    }
            
            # 最大长度
            elif rule_type == FormValidator.RULE_MAX_LENGTH:
                if value is not None and len(str(value)) > rule.get("max", 0):
                    return {
                        "valid": False,
                        "message": rule.get("message", f"长度不能超过{rule.get('max')}个字符")
                    }
            
            # 正则验证
            elif rule_type == FormValidator.RULE_PATTERN:
                import re
                pattern = rule.get("pattern")
                if value is not None and not re.match(pattern, str(value)):
                    return {
                        "valid": False,
                        "message": rule.get("message", "格式不正确")
                    }
            
            # 最小值
            elif rule_type == FormValidator.RULE_MIN:
                try:
                    if value is not None and float(value) < rule.get("min", 0):
                        return {
                            "valid": False,
                            "message": rule.get("message", f"值不能小于{rule.get('min')}")
                        }
                except (ValueError, TypeError):
                    return {"valid": False, "message": "请输入有效的数字"}
            
            # 最大值
            elif rule_type == FormValidator.RULE_MAX:
                try:
                    if value is not None and float(value) > rule.get("max", 0):
                        return {
                            "valid": False,
                            "message": rule.get("message", f"值不能大于{rule.get('max')}")
                        }
                except (ValueError, TypeError):
                    return {"valid": False, "message": "请输入有效的数字"}
            
            # 内置规则
            elif rule_type in FormValidator.BUILTIN_RULES:
                import re
                rule_def = FormValidator.BUILTIN_RULES[rule_type]
                if value is not None and not re.match(rule_def["pattern"], str(value)):
                    return {
                        "valid": False,
                        "message": rule.get("message", rule_def["message"])
                    }
        
        return {"valid": True, "message": ""}
    
    @staticmethod
    def validate_form(form_data: Dict, schema: Dict) -> Dict:
        """
        验证整个表单
        
        Args:
            form_data: 表单数据 {callback_id: value}
            schema: 表单Schema {callback_id: {label, rules: []}}
            
        Returns:
            {"valid": bool, "errors": {callback_id: message}}
        """
        errors = {}
        
        for field_id, field_def in schema.items():
            value = form_data.get(field_id, "")
            rules = field_def.get("rules", [])
            label = field_def.get("label", field_id)
            
            # 添加必填规则
            if field_def.get("required", False):
                rules.insert(0, {
                    "type": FormValidator.RULE_REQUIRED,
                    "message": f"{label}为必填项"
                })
            
            # 执行验证
            result = FormValidator.validate(value, rules)
            if not result["valid"]:
                errors[field_id] = result["message"]
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }


# ==================== 多轮对话状态机 ====================

class ConversationState:
    """对话状态"""
    PENDING = "pending"      # 等待用户输入
    IN_PROGRESS = "progress"  # 进行中
    COMPLETED = "completed"   # 已完成
    CANCELLED = "cancelled" # 已取消
    TIMEOUT = "timeout"     # 超时


class ConversationContext:
    """对话上下文"""
    
    def __init__(
        self,
        conversation_id: str,
        user_id: str,
        initial_state: str = ConversationState.PENDING,
        ttl: int = 600
    ):
        self.conversation_id = conversation_id
        self.user_id = user_id
        self.state = initial_state
        self.data: Dict = {}
        self.history: List[Dict] = []
        self.created_at = None
        self.updated_at = None
        self.ttl = ttl
        
        import time
        self.created_at = time.time()
        self.updated_at = time.time()
    
    def set_state(self, state: str):
        """设置状态"""
        self.state = state
        self.touch()
    
    def set_data(self, key: str, value: Any):
        """设置数据"""
        self.data[key] = value
        self.touch()
    
    def get_data(self, key: str, default: Any = None) -> Any:
        """获取数据"""
        return self.data.get(key, default)
    
    def add_history(self, action: str, data: Dict):
        """添加历史记录"""
        import time
        self.history.append({
            "action": action,
            "data": data,
            "timestamp": time.time()
        })
    
    def touch(self):
        """更新最后活跃时间"""
        import time
        self.updated_at = time.time()
    
    def is_expired(self) -> bool:
        """检查是否过期"""
        import time
        return time.time() - self.updated_at > self.ttl
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "conversation_id": self.conversation_id,
            "user_id": self.user_id,
            "state": self.state,
            "data": self.data,
            "history": self.history,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }


class ConversationStateMachine:
    """多轮对话状态机"""
    
    def __init__(self, default_ttl: int = 600):
        self.conversations: Dict[str, ConversationContext] = {}
        self.default_ttl = default_ttl
        self.handlers: Dict[str, Callable] = {}
    
    def start_conversation(
        self,
        conversation_id: str,
        user_id: str,
        initial_data: Dict = None
    ) -> ConversationContext:
        """开始一个新对话"""
        ctx = ConversationContext(
            conversation_id=conversation_id,
            user_id=user_id,
            ttl=self.default_ttl
        )
        
        if initial_data:
            for key, value in initial_data.items():
                ctx.set_data(key, value)
        
        ctx.add_history("start", {"conversation_id": conversation_id})
        self.conversations[conversation_id] = ctx
        
        return ctx
    
    def get_conversation(self, conversation_id: str) -> Optional[ConversationContext]:
        """获取对话上下文"""
        ctx = self.conversations.get(conversation_id)
        
        if ctx is None:
            return None
        
        # 检查是否过期
        if ctx.is_expired():
            self.end_conversation(conversation_id, ConversationState.TIMEOUT)
            return None
        
        return ctx
    
    def update_state(
        self,
        conversation_id: str,
        state: str,
        data: Dict = None
    ) -> Optional[ConversationContext]:
        """更新对话状态"""
        ctx = self.get_conversation(conversation_id)
        
        if ctx is None:
            return None
        
        ctx.set_state(state)
        
        if data:
            for key, value in data.items():
                ctx.set_data(key, value)
            ctx.add_history("update_state", {"state": state, "data": data})
        
        return ctx
    
    def end_conversation(
        self,
        conversation_id: str,
        final_state: str = ConversationState.COMPLETED
    ) -> Optional[ConversationContext]:
        """结束对话"""
        ctx = self.conversations.get(conversation_id)
        
        if ctx:
            ctx.set_state(final_state)
            ctx.add_history("end", {"final_state": final_state})
        
        return ctx
    
    def delete_conversation(self, conversation_id: str):
        """删除对话"""
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
    
    def register_handler(
        self,
        action: str,
        handler: Callable[[ConversationContext, Dict], Dict]
    ):
        """注册动作处理器"""
        self.handlers[action] = handler
    
    async def handle_action(
        self,
        conversation_id: str,
        action: str,
        params: Dict = None
    ) -> Optional[Dict]:
        """处理动作"""
        ctx = self.get_conversation(conversation_id)
        
        if ctx is None:
            return {"error": "对话不存在或已过期"}
        
        if action not in self.handlers:
            return {"error": f"未找到处理器: {action}"}
        
        handler = self.handlers[action]
        
        try:
            result = await handler(ctx, params or {})
            ctx.add_history(action, params or {})
            return result
        except Exception as e:
            return {"error": str(e)}
    
    def cleanup_expired(self):
        """清理过期对话"""
        expired = [
            cid for cid, ctx in self.conversations.items()
            if ctx.is_expired()
        ]
        
        for cid in expired:
            self.end_conversation(cid, ConversationState.TIMEOUT)
        
        return len(expired)
    
    def get_active_conversations(self, user_id: str = None) -> List[ConversationContext]:
        """获取活跃对话"""
        result = []
        
        for ctx in self.conversations.values():
            if ctx.state in (ConversationState.PENDING, ConversationState.IN_PROGRESS):
                if user_id is None or ctx.user_id == user_id:
                    if not ctx.is_expired():
                        result.append(ctx)
        
        return result


# ==================== 预置模板 ====================

class CardTemplates:
    """飞书卡片预置模板"""
    
    # ==================== 对话类 ====================
    
    @staticmethod
    def confirm(
        title: str,
        content: str,
        confirm_callback: str = "confirm",
        cancel_callback: str = "cancel"
    ) -> Dict:
        """确认对话框"""
        return FeishuCardBuilder() \
            .set_header(title, "blue") \
            .add_div(content) \
            .add_button_group([
                {"text": "取消", "type": "default", "callback_id": cancel_callback},
                {"text": "确认", "type": "primary", "callback_id": confirm_callback}
            ]) \
            .build()
    
    @staticmethod
    def menu(
        title: str,
        options: List[Dict],
        callback_prefix: str = "menu_select"
    ) -> Dict:
        """菜单选择"""
        builder = FeishuCardBuilder().set_header(title, "blue")
        for opt in options:
            builder.add_button(
                text=opt["text"],
                callback_id=f"{callback_prefix}_{opt['value']}",
                value={"selected": opt["value"]},
                type=opt.get("type", "default")
            )
        return builder.build()
    
    @staticmethod
    def quick_reply(
        title: str,
        replies: List[Dict]
    ) -> Dict:
        """快捷回复"""
        builder = FeishuCardBuilder().set_header(title, "blue")
        for reply in replies:
            builder.add_button(
                text=reply["text"],
                callback_id=f"quick_reply_{reply['value']}",
                type=reply.get("type", "default")
            )
        return builder.build()
    
    # ==================== 表单类 ====================
    
    @staticmethod
    def form(
        title: str,
        fields: List[Dict],
        submit_callback: str = "form_submit",
        cancel_callback: str = "form_cancel"
    ) -> Dict:
        """通用表单"""
        builder = FeishuCardBuilder().set_header(title, "blue")
        
        for field in fields:
            cb_id = field["callback_id"]
            
            if field["type"] == "text":
                builder.add_text_input(
                    label=field["label"],
                    callback_id=cb_id,
                    placeholder=field.get("placeholder", "请输入"),
                    initial_value=field.get("initial_value"),
                    multiline=field.get("multiline", False)
                )
            elif field["type"] == "number":
                builder.add_number_input(
                    label=field["label"],
                    callback_id=cb_id,
                    placeholder=field.get("placeholder", "请输入数字"),
                    initial_value=field.get("initial_value")
                )
            elif field["type"] == "select":
                builder.add_static_select(
                    label=field["label"],
                    callback_id=cb_id,
                    options=field["options"],
                    placeholder=field.get("placeholder", "请选择"),
                    initial_value=field.get("initial_value")
                )
            elif field["type"] == "multi_select":
                builder.add_multi_select(
                    label=field["label"],
                    callback_id=cb_id,
                    options=field["options"],
                    placeholder=field.get("placeholder", "请选择"),
                    initial_values=field.get("initial_values")
                )
            elif field["type"] == "date":
                builder.add_date_picker(
                    label=field["label"],
                    callback_id=cb_id,
                    placeholder=field.get("placeholder", "选择日期"),
                    initial_date=field.get("initial_date")
                )
            elif field["type"] == "datetime":
                builder.add_datetime_picker(
                    label=field["label"],
                    callback_id=cb_id,
                    placeholder=field.get("placeholder", "选择日期和时间"),
                    initial_datetime=field.get("initial_datetime")
                )
        
        builder.add_button_group([
            {"text": "取消", "type": "default", "callback_id": cancel_callback},
            {"text": "提交", "type": "primary", "callback_id": submit_callback}
        ])
        
        return builder.build()
    
    @staticmethod
    def survey(
        title: str,
        questions: List[Dict]
    ) -> Dict:
        """问卷调查"""
        builder = FeishuCardBuilder().set_header(title, "blue")
        
        for q in questions:
            if q["type"] == "rating":
                # 评分题 - 使用按钮组
                builder.add_div(f"**{q['label']}**")
                star_buttons = []
                for i in range(1, q.get("max", 5) + 1):
                    star_buttons.append({
                        "text": "⭐" * i,
                        "callback_id": f"{q['callback_id']}_{i}",
                        "value": {"score": i}
                    })
                builder.add_button_group(star_buttons)
            elif q["type"] == "choice":
                # 选择题
                builder.add_static_select(
                    label=q["label"],
                    callback_id=q["callback_id"],
                    options=q["options"]
                )
            elif q["type"] == "multi_choice":
                # 多选题
                builder.add_multi_select(
                    label=q["label"],
                    callback_id=q["callback_id"],
                    options=q["options"]
                )
            elif q["type"] == "text":
                # 文本题
                builder.add_text_input(
                    label=q["label"],
                    callback_id=q["callback_id"],
                    placeholder=q.get("placeholder", "请输入"),
                    multiline=q.get("multiline", False)
                )
        
        builder.add_button("提交", "survey_submit", {}, "primary")
        
        return builder.build()
    
    # ==================== 展示类 ====================
    
    @staticmethod
    def result(
        title: str,
        items: List[Dict],
        image_url: Optional[str] = None
    ) -> Dict:
        """结果展示"""
        builder = FeishuCardBuilder().set_header(title, "green")
        
        if image_url:
            builder.add_image(image_url)
        
        for item in items:
            if item.get("type") == "link":
                builder.add_button(
                    text=item["label"],
                    callback_id="",
                    url=item["value"],
                    type="default"
                )
            else:
                builder.add_div(f"**{item['label']}**: {item['value']}")
        
        return builder.build()
    
    @staticmethod
    def loading(
        title: str = "处理中...",
        content: str = "请稍候"
    ) -> Dict:
        """加载中"""
        return FeishuCardBuilder() \
            .set_header(title, "blue") \
            .add_div(content) \
            .add_div("⏳ 加载中...") \
            .build()
    
    @staticmethod
    def success(
        title: str = "操作成功",
        content: str = ""
    ) -> Dict:
        """成功提示"""
        return FeishuCardBuilder() \
            .set_header(title, "green") \
            .add_div("✅ " + content) \
            .build()
    
    @staticmethod
    def error(
        title: str = "操作失败",
        content: str = ""
    ) -> Dict:
        """错误提示"""
        return FeishuCardBuilder() \
            .set_header(title, "red") \
            .add_div("❌ " + content) \
            .build()


# ==================== 辅助函数 ====================

def parse_callback_data(callback_data: Dict) -> Dict:
    """解析回调数据"""
    return {
        "callback_id": callback_data.get("callback_id", ""),
        "value": callback_data.get("value", {}),
        "user_id": callback_data.get("operator", {}).get("user_id", ""),
        "message_id": callback_data.get("message", {}).get("message_id", "")
    }


def build_card_response(
    content: Union[str, Dict],
    msg_type: str = "text"
) -> str:
    """构建卡片消息响应"""
    if isinstance(content, str):
        content = {"text": content}
    
    return json.dumps({
        "type": "card",
        "data": {
            "template_variable": {
                "content": json.dumps(content, ensure_ascii=False)
            }
        }
    }, ensure_ascii=False)
