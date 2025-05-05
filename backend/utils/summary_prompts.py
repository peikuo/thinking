from typing import Dict


def get_summary_prompt(question: str, responses: Dict[str, str], language: str = "en") -> str:
    """
    Generate a prompt for summarizing model responses.
    
    Args:
        question: The original question asked
        responses: Dictionary mapping model names to their responses
        language: Language code for the summary (en or zh)
        
    Returns:
        Formatted prompt for the summary model
    """
    # Localized templates
    templates = {
        "en": {
            "intro": "I need you to create a table comparing AI responses to this question:",
            "question_prefix": "QUESTION: ",
            "table_instruction": "Create a clear, well-formatted markdown table that compares how each model answered this question. The table should have a row for each key point or concept from the responses. Each model should have its own column, and the cells should indicate whether and how the model addressed each point. Make sure to catch subtle differences in reasoning, level of detail, accuracy, and approach.",
            "similarity_instruction": "After the table, provide a brief paragraph analyzing the similarities and differences in how the models approached this question.",
            "model_responses": "Here are the model responses to compare:"
        },
        "zh": {
            "intro": "我需要你创建一个表格，比较AI对这个问题的回答：",
            "question_prefix": "问题：",
            "table_instruction": "创建一个清晰、格式良好的markdown表格，比较每个模型对这个问题的回答方式。表格应该为每个回答中的关键点或概念设置一行。每个模型应该有自己的列，单元格应该指出每个模型是否以及如何处理了每个要点。确保捕捉到推理方式、详细程度、准确性和方法上的微妙差异。",
            "similarity_instruction": "在表格之后，提供一个简短的段落，分析模型在处理这个问题时的相似点和不同点。",
            "model_responses": "以下是要比较的模型回答："
        }
    }
    
    # Use the appropriate language template
    template = templates.get(language, templates["en"])
    
    # Construct the prompt
    prompt = f"{template['intro']}\n\n{template['question_prefix']}{question}\n\n{template['table_instruction']}\n\n{template['similarity_instruction']}\n\n{template['model_responses']}\n\n"
    
    # Add each model's response
    for model_name, response in responses.items():
        prompt += f"\n---\n{model_name.upper()}:\n{response}\n"
    
    return prompt
