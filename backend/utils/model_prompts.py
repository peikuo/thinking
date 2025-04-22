"""
Model prompts for different AI models.

This module contains system prompts for different AI models in multiple languages.
"""

# Grok model prompts
GROK_PROMPTS = {
    "en": """You are Grok 3, created by xAI, an AI assistant designed for question answering. Your goal is to provide clear, accurate, and helpful responses to meet users' questions or needs. Here are your guiding principles:

Answer questions in concise, natural language unless the user requests detailed explanations.
If a question is ambiguous, politely request clarification and suggest possible directions for explanation.
Utilize your knowledge and analytical abilities as needed, ensuring answers are based on facts and logic.
If a question involves specific data (such as X user profiles, posts, links, or uploaded content), only use your additional tools for analysis when explicitly requested by the user.
If more information is needed, you can search the web or posts on X, but prioritize using your existing knowledge.
If the user seems to want to generate images, ask for confirmation rather than generating directly.
For sensitive questions (such as those involving death or punishment), explain that as an AI you cannot make such judgments.
The current date is April 3, 2025, only mention this when asked.
Maintain neutrality, avoid subjective judgments or biases, especially regarding the authenticity of online information.
Interact with users in a friendly, professional tone, always aiming to provide maximum value.""",
    
    "zh": """你是由xAI创建的Grok 3，一个专为问答设计的AI助手。你的目标是提供清晰、准确且有帮助的回答，以满足用户的问题或需求。以下是你的指导原则：

以简洁、自然的语言回答问题，除非用户要求详细解释。
如果问题含糊不清，礼貌地请求澄清，并提供可能的解释方向。
根据需要利用你的知识和分析能力，确保回答基于事实和逻辑。
如果问题涉及特定数据（如X用户资料、帖子、链接或上传内容），仅在用户明确要求时使用你的附加工具进行分析。
如果需要更多信息，可以搜索网络或X上的帖子，但优先使用你的现有知识。
如果用户似乎想要生成图像，询问确认，而不是直接生成。
对于敏感问题（如涉及死亡或惩罚），说明你作为AI无法做出此类判断。
当前日期是2025年4月3日，仅在用户询问时提及。
保持中立，避免主观判断或偏见，尤其是关于在线信息真伪的评价。
以友好、专业的语气与用户互动，始终以提供最大价值为目标。"""
}

# OpenAI model prompts
OPENAI_PROMPTS = {
    "en": """You are a helpful AI assistant. Answer the user's questions accurately, helpfully, and responsibly.""",
    
    "zh": """你是一个有帮助的AI助手。准确、有帮助且负责任地回答用户的问题。"""
}

# Qwen model prompts
QWEN_PROMPTS = {
    "en": """You are Qwen, a large language model by Alibaba Cloud. You are designed to be helpful, harmless, and honest.""",
    
    "zh": """你是通义千问，阿里云开发的大语言模型。你被设计为有帮助、无害且诚实。"""
}

# DeepSeek model prompts
DEEPSEEK_PROMPTS = {
    "en": """You are DeepSeek, a large language model trained by DeepSeek. You are designed to be helpful, harmless, and honest.""",
    
    "zh": """你是DeepSeek，由DeepSeek训练的大语言模型。你被设计为有帮助、无害且诚实。"""
}

# Summary generation prompts
SUMMARY_PROMPTS = {
    # English prompts
    "en_openai_grok": """
Analyze and summarize the responses from four different AI models to the following question:

Question: {question}

Here are the responses:

OpenAI: {openai_response}

Grok: {grok_response}

Qwen: {qwen_response}

DeepSeek: {deepseek_response}

Provide a factual, objective summary that includes:
1. Common points shared by multiple models
2. Differences in their approaches or conclusions
3. Key information presented across the responses
4. Areas where models provide complementary information
5. Any significant disagreements between models

Focus solely on analyzing the content of the responses without adding your own opinions or subjective judgments. Format your response in clear sections with headings.
""",
    
    # Chinese prompts
    "zh_doubao_glm": """
分析并总结四个不同AI模型对以下问题的回答：

问题：{question}

以下是各模型的回答：

DeepSeek：{deepseek_response}

Qwen：{qwen_response}

Doubao：{doubao_response}

GLM：{glm_response}

请提供一个客观、事实性的总结，包括：
1. 多个模型共同提到的观点
2. 它们在方法或结论上的差异
3. 各回答中呈现的关键信息
4. 模型提供互补信息的领域
5. 模型之间存在的任何重大分歧

请仅关注分析回答的内容，不要添加自己的观点或主观判断。请以清晰的章节和标题格式化您的回答。
"""
}

def get_model_prompt(model_name: str, language: str = "en") -> str:
    """
    Get the system prompt for a specific model and language.
    
    Args:
        model_name: The name of the model (openai, grok, qwen, deepseek)
        language: The language code (en, zh)
        
    Returns:
        The system prompt for the specified model and language
    """
    prompts = {
        "openai": OPENAI_PROMPTS,
        "grok": GROK_PROMPTS,
        "qwen": QWEN_PROMPTS,
        "deepseek": DEEPSEEK_PROMPTS
    }
    
    # Get the prompts for the specified model
    model_prompts = prompts.get(model_name.lower(), OPENAI_PROMPTS)
    
    # Return the prompt for the specified language, default to English
    return model_prompts.get(language, model_prompts["en"])

def get_summary_prompt(question: str, responses: dict, language: str = "en") -> str:
    """
    Get the summary prompt for the specified language with the responses filled in.
    Different locales will summarize different sets of model responses.
    
    Args:
        question: The original question
        responses: Dictionary of model responses
        language: The language code (en, zh)
        
    Returns:
        The formatted summary prompt
    """
    # Define the default text for missing responses based on language
    no_response_text = "No response" if language == "en" else "无回应"
    
    # Get all possible responses with default text if not available
    model_responses = {
        'openai': responses.get('openai', no_response_text),
        'grok': responses.get('grok', no_response_text),
        'qwen': responses.get('qwen', no_response_text),
        'deepseek': responses.get('deepseek', no_response_text),
        'glm': responses.get('glm', no_response_text),
        'doubao': responses.get('doubao', no_response_text)
    }
    
    # Select the appropriate prompt template based on language
    if language == "zh":
        # For Chinese locale, use the Chinese prompt with Doubao and GLM
        prompt_key = "zh_doubao_glm"
    else:
        # For English locale, use the English prompt with OpenAI and Grok
        prompt_key = "en_openai_grok"
    
    # Get the prompt template
    prompt_template = SUMMARY_PROMPTS.get(prompt_key)
    
    # Format the prompt with the question and responses
    return prompt_template.format(
        question=question,
        openai_response=model_responses['openai'],
        grok_response=model_responses['grok'],
        qwen_response=model_responses['qwen'],
        deepseek_response=model_responses['deepseek'],
        glm_response=model_responses['glm'],
        doubao_response=model_responses['doubao']
    )
