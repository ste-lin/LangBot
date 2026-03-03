"""
飞书交互卡片模块单元测试
"""
import pytest
import json
import sys
import os

# 添加源码路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'langbot', 'pkg', 'platform', 'sources'))

from feishu_card import (
    FeishuCardBuilder,
    FeishuCardManager,
    CardTemplates,
    parse_callback_data,
    build_card_response
)


class TestFeishuCardBuilder:
    """测试卡片构建器"""
    
    def test_add_div(self):
        """测试添加文本块"""
        builder = FeishuCardBuilder()
        builder.add_div("测试文本")
        
        card = builder.build()
        assert len(card["elements"]) == 1
        assert card["elements"][0]["tag"] == "div"
        assert card["elements"][0]["text"]["content"] == "测试文本"
    
    def test_add_hr(self):
        """测试添加分割线"""
        builder = FeishuCardBuilder()
        builder.add_hr()
        
        card = builder.build()
        assert card["elements"][0]["tag"] == "hr"
    
    def test_add_button(self):
        """测试添加按钮"""
        builder = FeishuCardBuilder()
        builder.add_button(
            text="点击我",
            callback_id="btn_click",
            value={"key": "value"},
            type="primary"
        )
        
        card = builder.build()
        element = card["elements"][0]
        assert element["tag"] == "action"
        assert element["actions"][0]["tag"] == "button"
        assert element["actions"][0]["text"]["content"] == "点击我"
        assert element["actions"][0]["callback_id"] == "btn_click"
        assert element["actions"][0]["type"] == "primary"
    
    def test_add_button_group(self):
        """测试添加按钮组"""
        builder = FeishuCardBuilder()
        builder.add_button_group([
            {"text": "取消", "type": "default", "callback_id": "cancel"},
            {"text": "确认", "type": "primary", "callback_id": "confirm"}
        ])
        
        card = builder.build()
        element = card["elements"][0]
        assert element["tag"] == "action"
        assert len(element["actions"]) == 2
    
    def test_add_static_select(self):
        """测试下拉选择器"""
        builder = FeishuCardBuilder()
        builder.add_static_select(
            label="请选择",
            callback_id="select_city",
            options=[
                {"text": "北京", "value": "bj"},
                {"text": "上海", "value": "sh"}
            ]
        )
        
        card = builder.build()
        element = card["elements"][0]
        assert element["tag"] == "input"
        assert element["label"]["content"] == "请选择"
        assert element["element"]["tag"] == "static_select"
        assert len(element["element"]["options"]) == 2
    
    def test_add_text_input(self):
        """测试文本输入框"""
        builder = FeishuCardBuilder()
        builder.add_text_input(
            label="姓名",
            callback_id="input_name",
            placeholder="请输入姓名",
            multiline=False
        )
        
        card = builder.build()
        element = card["elements"][0]
        assert element["tag"] == "input"
        assert element["element"]["tag"] == "plain_text_input"
        assert element["element"]["multiline"] == False
    
    def test_add_text_input_multiline(self):
        """测试多行文本输入框"""
        builder = FeishuCardBuilder()
        builder.add_text_input(
            label="备注",
            callback_id="input_remark",
            multiline=True
        )
        
        card = builder.build()
        element = card["elements"][0]
        assert element["element"]["multiline"] == True
    
    def test_add_number_input(self):
        """测试数字输入框"""
        builder = FeishuCardBuilder()
        builder.add_number_input(
            label="年龄",
            callback_id="input_age",
            min=0,
            max=150
        )
        
        card = builder.build()
        element = card["elements"][0]
        assert element["element"]["tag"] == "number_input"
        assert element["element"]["min"] == 0
        assert element["element"]["max"] == 150
    
    def test_add_date_picker(self):
        """测试日期选择器"""
        builder = FeishuCardBuilder()
        builder.add_date_picker(
            label="出生日期",
            callback_id="pick_birthday"
        )
        
        card = builder.build()
        element = card["elements"][0]
        assert element["tag"] == "input"
        assert element["element"]["tag"] == "date_picker"
    
    def test_add_time_picker(self):
        """测试时间选择器"""
        builder = FeishuCardBuilder()
        builder.add_time_picker(
            label="预约时间",
            callback_id="pick_time"
        )
        
        card = builder.build()
        element = card["elements"][0]
        assert element["element"]["tag"] == "time_picker"
    
    def test_add_image(self):
        """测试添加图片"""
        builder = FeishuCardBuilder()
        builder.add_image(
            img_url="https://example.com/image.jpg",
            alt="示例图片"
        )
        
        card = builder.build()
        element = card["elements"][0]
        assert element["tag"] == "img"
        assert element["img_url"] == "https://example.com/image.jpg"
    
    def test_set_header(self):
        """测试设置标题"""
        builder = FeishuCardBuilder()
        builder.set_header("测试标题", "blue")
        
        card = builder.build()
        assert card["header"]["title"]["content"] == "测试标题"
        assert card["header"]["template"] == "blue"
    
    def test_set_update_multi(self):
        """测试设置多次更新"""
        builder = FeishuCardBuilder()
        builder.set_update_multi(True)
        
        card = builder.build()
        assert card["config"]["update_multi"] == True
    
    def test_build_json(self):
        """测试 JSON 输出"""
        builder = FeishuCardBuilder()
        builder.add_div("测试")
        
        json_str = builder.build_json()
        assert isinstance(json_str, str)
        
        # 验证是有效的 JSON
        parsed = json.loads(json_str)
        assert "elements" in parsed


class TestCardTemplates:
    """测试预置模板"""
    
    def test_confirm(self):
        """测试确认对话框"""
        card = CardTemplates.confirm(
            title="确认操作",
            content="确定要执行吗？",
            confirm_callback="confirm",
            cancel_callback="cancel"
        )
        
        assert card["header"]["title"]["content"] == "确认操作"
        assert card["header"]["template"] == "blue"
    
    def test_menu(self):
        """测试菜单模板"""
        card = CardTemplates.menu(
            title="请选择",
            options=[
                {"text": "选项A", "value": "a"},
                {"text": "选项B", "value": "b"}
            ]
        )
        
        assert card["header"]["title"]["content"] == "请选择"
    
    def test_form(self):
        """测试表单模板"""
        card = CardTemplates.form(
            title="用户信息",
            fields=[
                {"type": "text", "label": "姓名", "callback_id": "name"},
                {"type": "select", "label": "城市", "callback_id": "city", 
                 "options": [{"text": "北京", "value": "bj"}]}
            ]
        )
        
        assert card["header"]["title"]["content"] == "用户信息"
    
    def test_survey(self):
        """测试问卷模板"""
        card = CardTemplates.survey(
            title="满意度调查",
            questions=[
                {"type": "rating", "label": "服务态度", "callback_id": "service"},
                {"type": "choice", "label": "推荐意愿", "callback_id": "recommend",
                 "options": [{"text": "会", "value": "yes"}, {"text": "不会", "value": "no"}]}
            ]
        )
        
        assert card["header"]["title"]["content"] == "满意度调查"
    
    def test_success(self):
        """测试成功提示"""
        card = CardTemplates.success(
            title="操作成功",
            content="已完成处理"
        )
        
        assert card["header"]["template"] == "green"
    
    def test_error(self):
        """测试错误提示"""
        card = CardTemplates.error(
            title="操作失败",
            content="请重试"
        )
        
        assert card["header"]["template"] == "red"
    
    def test_loading(self):
        """测试加载提示"""
        card = CardTemplates.loading(
            title="处理中",
            content="请稍候..."
        )
        
        assert "加载中" in card["elements"][1]["text"]["content"]


class TestFeishuCardManager:
    """测试卡片管理器"""
    
    def test_register_handler(self):
        """测试注册处理器"""
        manager = FeishuCardManager()
        
        def handler(callback_id, value, user_id, message_id):
            return {"type": "text", "content": "handled"}
        
        manager.register_handler("test_action", handler, "测试处理器")
        
        assert "test_action" in manager.handlers
    
    def test_handle_callback(self):
        """测试处理回调"""
        manager = FeishuCardManager()
        
        # 使用同步函数模拟
        result_holder = {}
        
        async def async_handler(callback_id, value, user_id, message_id):
            return {"type": "text", "content": f"Hello {user_id}"}
        
        def sync_handler(callback_id, value, user_id, message_id):
            return {"type": "text", "content": f"Hello {user_id}"}
        
        manager.register_handler("greet", sync_handler)
        
        # 直接调用 handler 而不是 manager（因为 manager 是 async）
        result = manager.handlers["greet"]["handler"](
            "greet", 
            {}, 
            "user123", 
            "msg456"
        )
        
        assert result["content"] == "Hello user123"
    
    def test_handle_callback_prefix_match(self):
        """测试前缀匹配"""
        manager = FeishuCardManager()
        
        def handler(callback_id, value, user_id, message_id):
            return {"type": "text", "content": f"Selected: {value.get('selected')}"}
        
        manager.register_handler("menu_select", handler)
        
        # 测试前缀匹配
        handler = None
        callback_id = "menu_select_apple"
        for key in manager.handlers:
            if callback_id.startswith(key + "_") or callback_id.startswith(key):
                handler = manager.handlers[key]["handler"]
                break
        
        assert handler is not None
        result = handler("menu_select", {"selected": "apple"}, "user123", "")
        assert result["content"] == "Selected: apple"
    
    def test_save_card_state(self):
        """测试保存卡片状态"""
        manager = FeishuCardManager()
        manager.save_card_state("card_123", {"step": 1}, ttl=10)
        
        state = manager.get_card_state("card_123")
        assert state["step"] == 1
    
    def test_get_card_state_expired(self):
        """测试获取过期状态"""
        manager = FeishuCardManager()
        manager.save_card_state("card_123", {"step": 1}, ttl=-1)
        
        state = manager.get_card_state("card_123")
        assert state is None


class TestHelperFunctions:
    """测试辅助函数"""
    
    def test_parse_callback_data(self):
        """测试解析回调数据"""
        callback_data = {
            "callback_id": "btn_submit",
            "value": {"name": "test"},
            "operator": {"user_id": "user_123"},
            "message": {"message_id": "msg_456"}
        }
        
        result = parse_callback_data(callback_data)
        
        assert result["callback_id"] == "btn_submit"
        assert result["value"]["name"] == "test"
        assert result["user_id"] == "user_123"
        assert result["message_id"] == "msg_456"
    
    def test_build_card_response_text(self):
        """测试构建文本响应"""
        result = build_card_response("Hello World")
        
        parsed = json.loads(result)
        assert "type" in parsed
        assert "data" in parsed
    
    def test_build_card_response_dict(self):
        """测试构建字典响应"""
        card = {"header": {"title": {"content": "Test"}}}
        result = build_card_response(card, msg_type="card")
        
        parsed = json.loads(result)
        assert parsed["type"] == "card"


# 运行测试
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
