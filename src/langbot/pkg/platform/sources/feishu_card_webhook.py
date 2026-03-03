"""
飞书卡片 Webhook 配置助手
自动生成 Webhook 配置和验证签名
"""
import hashlib
import hmac
import time
import json
from typing import Dict, Optional


class LarkCardWebhookHelper:
    """飞书卡片 Webhook 助手"""
    
    def __init__(self, encrypt_key: str = ""):
        self.encrypt_key = encrypt_key
    
    @staticmethod
    def verify_signature(
        signature: str,
        timestamp: str,
        nonce: str,
        token: str
    ) -> bool:
        """
        验证签名
        
        Args:
            signature: 签名
            timestamp: 时间戳
            nonce: 随机字符串
            token: Verification Token
            
        Returns:
            签名是否有效
        """
        # 排序并拼接
        sorted_params = sorted([timestamp, nonce, token])
        sign_string = ''.join(sorted_params)
        
        # SHA1 加密
        signature_calculated = hashlib.sha1(sign_string.encode('utf-8')).hexdigest()
        
        return signature_calculated == signature
    
    @staticmethod
    def encrypt(encrypt_key: str, content: str) -> str:
        """
        加密内容
        
        Args:
            encrypt_key: 加密密钥
            content: 要加密的内容
            
        Returns:
            加密后的字符串
        """
        from Crypto.Cipher import AES
        import base64
        import hashlib
        
        # 生成 AES 密钥
        key = hashlib.sha256(encrypt_key.encode('utf-8')).digest()
        
        # PKCS7 填充
        padding_len = 16 - len(content) % 16
        content_padded = content + (chr(padding_len) * padding_len)
        
        # AES 加密
        cipher = AES.new(key, AES.MODE_CBC, key[:16])
        encrypted = cipher.encrypt(content_padded.encode('utf-8'))
        
        # Base64 编码
        return base64.b64encode(encrypted).decode('utf-8')
    
    @staticmethod
    def decrypt(encrypt_key: str, encrypted_content: str) -> str:
        """
        解密内容
        
        Args:
            encrypt_key: 加密密钥
            encrypted_content: 加密的内容
            
        Returns:
            解密后的字符串
        """
        from Crypto.Cipher import AES
        import base64
        import hashlib
        
        # 生成 AES 密钥
        key = hashlib.sha256(encrypt_key.encode('utf-8')).digest()
        
        # Base64 解码
        encrypted = base64.b64decode(encrypted_content)
        
        # AES 解密
        cipher = AES.new(key, AES.MODE_CBC, key[:16])
        decrypted = cipher.decrypt(encrypted)
        
        # 去除 PKCS7 填充
        padding_len = decrypted[-1]
        return decrypted[:-padding_len].decode('utf-8')
    
    @staticmethod
    def generate_config_url(
        app_id: str,
        webhook_url: str,
        verification_token: str = ""
    ) -> Dict:
        """
        生成配置信息
        
        Returns:
            配置字典
        """
        config = {
            "webhook_url": webhook_url,
            "callback_url": f"{webhook_url}/callback",
            "verification_token": verification_token,
            "permissions": [
                "im:message:send_as_bot",
                "im:message:receive",
                "im:chat:message"
            ]
        }
        return config
    
    @staticmethod
    def build_callback_response(
        challenge: str = None,
        code: int = 0,
        message: str = "success"
    ) -> Dict:
        """
        构建回调响应
        
        Args:
            challenge: URL 验证挑战
            code: 响应码
            message: 响应消息
            
        Returns:
            响应字典
        """
        if challenge:
            return {"challenge": challenge}
        return {"code": code, "message": message}
    
    @staticmethod
    def parse_callback_event(data: Dict) -> Dict:
        """
        解析回调事件
        
        Returns:
            解析后的事件字典
        """
        event_type = data.get('type', '')
        
        result = {
            "type": event_type,
            "raw": data
        }
        
        if event_type == 'url_verification':
            result["challenge"] = data.get('challenge', '')
            result["token"] = data.get('token', '')
            
        elif event_type == 'im.card.action.callback':
            action = data.get('action', {})
            result["callback_id"] = action.get('callback_id', '')
            result["value"] = action.get('value', {})
            result["operator"] = data.get('operator', {})
            result["message_id"] = data.get('message', {}).get('message_id', '')
            
        elif event_type == 'im.message.receive_v1':
            result["message_id"] = data.get('message', {}).get('message_id', '')
            result["chat_id"] = data.get('message', {}).get('chat_id', '')
            result["content"] = data.get('message', {}).get('body', {}).get('content', '')
            result["sender"] = data.get('sender', {})
        
        return result


# ==================== 配置生成器 ====================

class CardWebhookConfigGenerator:
    """卡片 Webhook 配置生成器"""
    
    @staticmethod
    def generate_env_example(
        app_id: str = "cli_xxxxx",
        app_secret: str = "your_app_secret",
        verification_token: str = "your_token",
        encrypt_key: str = "your_encrypt_key"
    ) -> str:
        """生成环境变量示例"""
        return f"""# 飞书应用配置
LARK_APP_ID={app_id}
LARK_APP_SECRET={app_secret}
LARK_VERIFICATION_TOKEN={verification_token}
LARK_ENCRYPT_KEY={encrypt_key}

# Webhook 配置
LARK_WEBHOOK_URL=https://your-domain.com/webhook
LARK_CALLBACK_URL=https://your-domain.com/webhook/callback

# 卡片配置
LARK_CARD_UPDATE_TIMEOUT=300
LARK_CARD_MAX_RETRY=3
"""
    
    @staticmethod
    def generate_docker_compose() -> str:
        """生成 Docker Compose 配置"""
        return """version: '3.8'

services:
  langbot:
    image: langbot/langbot
    ports:
      - "5300:5300"
    environment:
      - LARK_APP_ID=${LARK_APP_ID}
      - LARK_APP_SECRET=${LARK_APP_SECRET}
      - LARK_VERIFICATION_TOKEN=${LARK_VERIFICATION_TOKEN}
      - LARK_ENCRYPT_KEY=${LARK_ENCRYPT_KEY}
    volumes:
      - ./config:/app/config
    restart: unless-stopped
"""
    
    @staticmethod
    def generate_config_yaml() -> str:
        """生成 YAML 配置文件"""
        return """feishu:
  card:
    # 卡片配置
    enabled: true
    timeout: 300
    max_retry: 3
    
  webhook:
    # Webhook 配置
    url: ${LARK_WEBHOOK_URL}
    callback_url: ${LARK_CALLBACK_URL}
    
  callbacks:
    # 回调绑定配置
    bindings:
      - callback_id: confirm
        action: reply
        description: 确认操作
      - callback_id: cancel  
        action: reply
        description: 取消操作
      - callback_id: submit
        action: update
        description: 提交表单
"""


# ==================== 便捷函数 ====================

def verify_lark_callback(
    signature: str,
    timestamp: str,
    nonce: str,
    token: str
) -> bool:
    """验证飞书回调签名"""
    return LarkCardWebhookHelper.verify_signature(signature, timestamp, nonce, token)


def parse_card_callback(data: Dict) -> Dict:
    """解析卡片回调"""
    return LarkCardWebhookHelper.parse_callback_event(data)


def build_callback_response(challenge: str = None) -> Dict:
    """构建回调响应"""
    return LarkCardWebhookHelper.build_callback_response(challenge)
