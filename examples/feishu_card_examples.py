"""
飞书交互卡片使用示例
展示各种场景的完整代码
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'langbot', 'pkg', 'platform', 'sources'))

from feishu_card import (
    FeishuCardBuilder,
    FeishuCardManager,
    ConversationStateMachine,
    ConversationContext,
    FormValidator,
    CardTemplates
)


# ==================== 示例 1: 简单的按钮交互 ====================

def example_simple_buttons():
    """简单按钮交互示例"""
    # 创建卡片
    card = (
        FeishuCardBuilder()
        .set_header("请选择操作", "blue")
        .add_div("请问有什么可以帮助您的？")
        .add_button_group([
            {"text": "查询订单", "type": "default", "callback_id": "query_order"},
            {"text": "售后服务", "type": "default", "callback_id": "after_sales"},
            {"text": "联系客服", "type": "primary", "callback_id": "contact_service"}
        ])
        .build()
    )
    
    # 注册回调处理器
    manager = FeishuCardManager()
    
    async def handle_query_order(callback_id, value, user_id, message_id):
        return {
            "type": "card",
            "content": CardTemplates.form(
                title="查询订单",
                fields=[
                    {"type": "text", "label": "订单号", "callback_id": "order_no", "placeholder": "请输入订单号"}
                ],
                submit_callback="submit_query"
            )
        }
    
    manager.register_handler("query_order", handle_query_order)
    
    return card


# ==================== 示例 2: 带验证的表单 ====================

def example_form_with_validation():
    """带验证的表单示例"""
    
    # 定义表单验证规则
    form_schema = {
        "name": {
            "label": "姓名",
            "required": True,
            "rules": [
                {"type": "min_length", "min": 2, "message": "姓名至少2个字符"},
                {"type": "max_length", "max": 20, "message": "姓名最多20个字符"}
            ]
        },
        "email": {
            "label": "邮箱",
            "required": True,
            "rules": [
                {"type": "email"}
            ]
        },
        "phone": {
            "label": "手机号",
            "required": False,
            "rules": [
                {"type": "phone"}
            ]
        },
        "age": {
            "label": "年龄",
            "required": False,
            "rules": [
                {"type": "number"},
                {"type": "min", "min": 18, "message": "年龄必须大于18岁"},
                {"type": "max", "max": 100, "message": "年龄不能超过100岁"}
            ]
        }
    }
    
    # 创建表单卡片
    card = (
        FeishuCardBuilder()
        .set_header("用户信息登记", "blue")
        .add_text_input(
            label="姓名 *",
            callback_id="name",
            placeholder="请输入姓名"
        )
        .add_text_input(
            label="邮箱 *",
            callback_id="email",
            placeholder="请输入邮箱"
        )
        .add_text_input(
            label="手机号",
            callback_id="phone",
            placeholder="请输入手机号"
        )
        .add_number_input(
            label="年龄",
            callback_id="age",
            placeholder="请输入年龄"
        )
        .add_button_group([
            {"text": "取消", "type": "default", "callback_id": "cancel"},
            {"text": "提交", "type": "primary", "callback_id": "submit_form"}
        ])
        .build()
    )
    
    # 验证函数
    def validate_form_data(form_data: dict):
        return FormValidator.validate_form(form_data, form_schema)
    
    return card, validate_form_data


# ==================== 示例 3: 多轮对话 ====================

def example_multi_turn_conversation():
    """多轮对话示例"""
    
    # 创建状态机
    state_machine = ConversationStateMachine(default_ttl=300)
    
    # 注册对话处理器
    async def handle_start(ctx: ConversationContext, params: dict):
        """处理开始"""
        ctx.set_data("purpose", params.get("purpose", "咨询"))
        ctx.set_state("awaiting_topic")
        
        return CardTemplates.menu(
            title="请选择咨询类型",
            options=[
                {"text": "产品咨询", "value": "product"},
                {"text": "价格咨询", "value": "price"},
                {"text": "技术支持", "value": "tech"}
            ],
            callback_prefix="select_topic"
        )
    
    async def handle_select_topic(ctx: ConversationContext, params: dict):
        """处理主题选择"""
        topic = params.get("selected")
        ctx.set_data("topic", topic)
        
        if topic == "product":
            ctx.set_state("awaiting_product_type")
            return CardTemplates.form(
                title="产品咨询",
                fields=[
                    {"type": "select", "label": "产品类型", "callback_id": "product_type",
                     "options": [{"text": "PC端", "value": "pc"}, {"text": "移动端", "value": "mobile"}]},
                    {"type": "text", "label": "具体需求", "callback_id": "requirement", "multiline": True}
                ],
                submit_callback="submit_product"
            )
        elif topic == "price":
            ctx.set_state("awaiting_budget")
            return CardTemplates.form(
                title="价格咨询",
                fields=[
                    {"type": "select", "label": "预算范围", "callback_id": "budget",
                     "options": [{"text": "1万以下", "value": "low"}, 
                                 {"text": "1-10万", "value": "mid"},
                                 {"text": "10万以上", "value": "high"}]}
                ],
                submit_callback="submit_price"
            )
        else:
            ctx.set_state("awaiting_description")
            return CardTemplates.form(
                title="技术支持",
                fields=[
                    {"type": "text", "label": "问题描述", "callback_id": "description", 
                     "multiline": True, "placeholder": "请描述您遇到的问题"}
                ],
                submit_callback="submit_tech"
            )
    
    async def handle_submit(ctx: ConversationContext, params: dict):
        """处理提交"""
        # 保存表单数据
        for key, value in params.items():
            ctx.set_data(key, value)
        
        ctx.set_state(ConversationState.COMPLETED)
        
        return CardTemplates.success(
            title="提交成功",
            content=f"感谢您的咨询，我们已收到您的{ctx.get_data('purpose')}请求"
        )
    
    # 注册处理器
    state_machine.register_handler("start", handle_start)
    state_machine.register_handler("select_topic", handle_select_topic)
    state_machine.register_handler("submit", handle_submit)
    
    return state_machine


# ==================== 示例 4: 订单处理流程 ====================

def example_order_flow():
    """订单处理流程示例"""
    
    card = (
        FeishuCardBuilder()
        .set_header("订单管理", "blue")
        .add_div("**订单号:** 20260303001")
        .add_div("**商品:** iPhone 15 Pro Max")
        .add_div("**金额:** ¥9999")
        .add_hr()
        .add_static_select(
            label="选择操作",
            callback_id="select_action",
            options=[
                {"text": "确认订单", "value": "confirm"},
                {"text": "修改订单", "value": "modify"},
                {"text": "取消订单", "value": "cancel"}
            ]
        )
        .add_button_group([
            {"text": "取消", "type": "default", "callback_id": "cancel"},
            {"text": "确认", "type": "primary", "callback_id": "submit_action"}
        ])
        .build()
    )
    
    # 回调处理
    async def handle_confirm(callback_id, value, user_id, message_id):
        return CardTemplates.success(
            title="订单已确认",
            content="您的订单已确认，我们将尽快发货"
        )
    
    async def handle_modify(callback_id, value, user_id, message_id):
        return CardTemplates.form(
            title="修改订单",
            fields=[
                {"type": "text", "label": "收货地址", "callback_id": "address"},
                {"type": "text", "label": "联系电话", "callback_id": "phone"},
                {"type": "text", "label": "备注", "callback_id": "remark", "multiline": True}
            ],
            submit_callback="submit_modify"
        )
    
    async def handle_cancel(callback_id, value, user_id, message_id):
        return CardTemplates.confirm(
            title="确认取消",
            content="确定要取消此订单吗？取消后无法恢复。",
            confirm_callback="confirm_cancel",
            cancel_callback="back"
        )
    
    return card


# ==================== 示例 5: 问卷调查 ====================

def example_survey():
    """问卷调查示例"""
    
    card = CardTemplates.survey(
        title="产品满意度调查",
        questions=[
            {
                "type": "rating",
                "label": "请对产品整体满意度评分",
                "callback_id": "overall_rating",
                "max": 5
            },
            {
                "type": "choice",
                "label": "您是从哪里了解到我们的？",
                "callback_id": "source",
                "options": [
                    {"text": "搜索引擎", "value": "search"},
                    {"text": "朋友推荐", "value": "friend"},
                    {"text": "社交媒体", "value": "social"},
                    {"text": "广告", "value": "ad"},
                    {"text": "其他", "value": "other"}
                ]
            },
            {
                "type": "multi_choice",
                "label": "您最关注产品的哪些方面？",
                "callback_id": "concerns",
                "options": [
                    {"text": "功能", "value": "feature"},
                    {"text": "价格", "value": "price"},
                    {"text": "用户体验", "value": "ux"},
                    {"text": "售后服务", "value": "service"},
                    {"text": "品牌", "value": "brand"}
                ]
            },
            {
                "type": "text",
                "label": "您还有其他建议吗？",
                "callback_id": "suggestion",
                "multiline": True,
                "placeholder": "请畅所欲言..."
            }
        ]
    )
    
    return card


# ==================== 示例 6: 预约系统 ====================

def example_appointment():
    """预约系统示例"""
    
    card = (
        FeishuCardBuilder()
        .set_header("会议室预约", "blue")
        .add_static_select(
            label="选择会议室",
            callback_id="room",
            options=[
                {"text": "1号会议室 (10人)", "value": "room1"},
                {"text": "2号会议室 (20人)", "value": "room2"},
                {"text": "3号会议室 (50人)", "value": "room3"}
            ]
        )
        .add_date_picker(
            label="选择日期",
            callback_id="date"
        )
        .add_time_picker(
            label="开始时间",
            callback_id="start_time"
        )
        .add_time_picker(
            label="结束时间",
            callback_id="end_time"
        )
        .add_text_input(
            label="会议主题",
            callback_id="topic",
            placeholder="请输入会议主题"
        )
        .add_text_input(
            label="参会人数",
            callback_id="attendees",
            placeholder="请输入参会人数"
        )
        .add_button_group([
            {"text": "取消", "type": "default", "callback_id": "cancel"},
            {"text": "提交预约", "type": "primary", "callback_id": "submit_appointment"}
        ])
        .build()
    )
    
    # 验证预约数据
    def validate_appointment(form_data: dict):
        errors = {}
        
        # 必填验证
        if not form_data.get("room"):
            errors["room"] = "请选择会议室"
        if not form_data.get("date"):
            errors["date"] = "请选择日期"
        if not form_data.get("start_time"):
            errors["start_time"] = "请选择开始时间"
        if not form_data.get("end_time"):
            errors["end_time"] = "请选择结束时间"
        if not form_data.get("topic"):
            errors["topic"] = "请输入会议主题"
        
        # 时间验证
        if form_data.get("start_time") and form_data.get("end_time"):
            if form_data["start_time"] >= form_data["end_time"]:
                errors["end_time"] = "结束时间必须晚于开始时间"
        
        return {"valid": len(errors) == 0, "errors": errors}
    
    return card, validate_appointment


# ==================== 运行示例 ====================

if __name__ == "__main__":
    import json
    
    print("=" * 50)
    print("示例 1: 简单按钮")
    print("=" * 50)
    print(json.dumps(example_simple_buttons(), ensure_ascii=False, indent=2))
    
    print("\n" + "=" * 50)
    print("示例 2: 带验证的表单")
    print("=" * 50)
    card, validator = example_form_with_validation()
    print(json.dumps(card, ensure_ascii=False, indent=2))
    
    # 测试验证
    test_data = {"name": "张三", "email": "invalid"}
    result = validator(test_data)
    print(f"验证结果: {result}")
    
    test_data = {"name": "张三", "email": "zhangsan@example.com"}
    result = validator(test_data)
    print(f"验证结果: {result}")
    
    print("\n" + "=" * 50)
    print("示例 5: 问卷调查")
    print("=" * 50)
    print(json.dumps(example_survey(), ensure_ascii=False, indent=2))
