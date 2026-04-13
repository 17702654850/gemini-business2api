import re
from typing import Optional

def extract_verification_code(text: str) -> Optional[str]:
    """提取验证码 (增强版)"""
    if not text:
        return None

    # --- 核心预处理：净化文本 ---
    # 1. 移除常见的零宽字符（破解 Google 等大厂的防爬机制）
    clean_text = text.replace('\u200b', '').replace('\u200c', '').replace('\u200d', '')
    # 2. 移除所有 HTML 标签，替换为空格，防止标签将验证码和关键字隔开
    clean_text = re.sub(r'<[^>]+>', ' ', clean_text)

    # 策略1: 上下文关键词匹配（中英文冒号）
    # 改进点：用 (?![A-Za-z0-9]) 替代 \b，完美兼容紧跟中文字符的情况
    # 改进点：扩大冒号和验证码之间的容忍度 ([\s\n]*)
    context_pattern = r"(?:验证码|驗證碼|code|verification|passcode|pin)[^:：]{0,15}[:：][\s\n]*([A-Za-z0-9]{4,8})(?![A-Za-z0-9])"
    match = re.search(context_pattern, clean_text, re.IGNORECASE)
    if match:
        candidate = match.group(1)
        # 排除 CSS 单位值或无关 Hex 颜色
        if not re.match(r"^\d+(?:px|pt|em|rem|vh|vw|%)$", candidate, re.IGNORECASE):
            return candidate.upper()

    # 策略2: 6位字母数字混合（兜底策略）
    # 改进点：增加前后边界限制 (?<!...) 和 (?!...)，防止匹配到超长哈希值的一部分
    match = re.search(r"(?<![A-Za-z0-9])([A-Za-z0-9]{6})(?![A-Za-z0-9])", clean_text, re.IGNORECASE)
    if match:
        return match.group(1).upper()

    # 策略3: 6位纯数字（降级兜底）
    digits = re.search(r"(?<![0-9])(\d{6})(?![0-9])", clean_text)
    if digits:
        return digits.group(1)

    return None
