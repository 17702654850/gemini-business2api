import re
import html
from typing import Optional

def extract_verification_code(text: str) -> Optional[str]:
    """提取验证码 (终极清洗版)"""
    if not text:
        return None

    # 1. 反转义 HTML 实体 (将 &nbsp; 变回空格，防止正则被不可见实体阻断)
    clean_text = html.unescape(text)

    # 2. 移除零宽字符 (破解大厂的反爬虫隐藏字符)
    clean_text = re.sub(r'[\u200b\u200c\u200d\ufeff]', '', clean_text)

    # 3. 【核心杀手锏】连根拔起 <style> 和 <script> 标签！
    # 直接删掉 CSS 块，彻底消灭 f0f0f0, margin, padding 等 6 位字符的干扰
    clean_text = re.sub(r'<(style|script)[^>]*>.*?</\1>', ' ', clean_text, flags=re.IGNORECASE | re.DOTALL)

    # 4. 移除所有剩余的 HTML 尖括号标签
    clean_text = re.sub(r'<[^>]+>', ' ', clean_text)

    # 5. 【关键优化】压平文本：将所有连续的换行和多余空格压缩为一个单空格
    # 这一步会将 "验证码是：\n\n   ZU3W99" 完美整理成 "验证码是： ZU3W99"
    clean_text = re.sub(r'\s+', ' ', clean_text).strip()

    # 策略1: 上下文关键词匹配
    context_pattern = r"(?:验证码|驗證碼|code|verification|passcode|pin)[^:：]{0,15}[:：]\s*([A-Za-z0-9]{4,8})(?![A-Za-z0-9])"
    match = re.search(context_pattern, clean_text, re.IGNORECASE)
    if match:
        candidate = match.group(1)
        if not re.match(r"^\d+(?:px|pt|em|rem|vh|vw|%)$", candidate, re.IGNORECASE):
            return candidate.upper()

    # 策略2: 6位字母数字混合（增强版兜底）
    matches = re.finditer(r"(?<![A-Za-z0-9])([A-Za-z0-9]{6})(?![A-Za-z0-9])", clean_text, re.IGNORECASE)
    for m in matches:
        candidate = m.group(1)
        # 安全校验：验证码通常包含至少一个数字。
        # 这一行可以过滤掉 HTML 里残留的纯英文 6 字母单词（如 system, bottom）
        if any(c.isdigit() for c in candidate):
            return candidate.upper()

    # 策略3: 6位纯数字（降级）
    digits = re.search(r"(?<![0-9])(\d{6})(?![0-9])", clean_text)
    if digits:
        return digits.group(1)

    return None
