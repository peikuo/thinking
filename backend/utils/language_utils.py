"""
Language detection and processing utilities for the Thinking platform.
"""

def detect_language(text: str) -> str:
    """
    Detect if text is primarily Chinese or English.
    Returns 'zh' for Chinese, 'en' for English or other languages.
    
    Args:
        text: The text to analyze
        
    Returns:
        'zh' for Chinese, 'en' for other languages
    """
    # Simple detection: if more than 10% of characters are Chinese, consider it Chinese
    chinese_chars = sum(1 for char in text if '\u4e00' <= char <= '\u9fff')
    if chinese_chars / max(len(text), 1) > 0.1:
        return "zh"
    return "en"
