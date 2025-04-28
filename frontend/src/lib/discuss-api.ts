import { toast } from "sonner";
import { ModelResponse } from "@/types/models";
import { createHeaders } from "./api";

// Sequential model discussion API functions
export async function requestSequentialDiscussion(
  prompt: string,
  modelOrder: ('openai' | 'grok' | 'qwen' | 'deepseek' | 'doubao' | 'glm')[],
  apiKeys?: Record<string, string>,
  language: string = 'en',
  onModelResponse?: (model: string, content: string) => void
): Promise<Record<string, string>> {
  if (!modelOrder || modelOrder.length === 0) {
    throw new Error("No models specified for discussion");
  }

  const messages = [{ role: "user", content: prompt }];
  const allResponses: Record<string, string> = {};
  let previousModel: string | null = null;
  let previousResponse: string | null = null;

  // Process models in sequence
  for (const model of modelOrder) {
    try {
      const response = await callDiscussModel(
        model,
        messages,
        previousModel,
        previousResponse,
        apiKeys,
        language,
        false // We'll handle streaming separately for now
      );

      if (response.content) {
        allResponses[model] = response.content;
        
        // Call the callback if provided
        if (onModelResponse) {
          onModelResponse(model, response.content);
        }
        
        // Update previous values for the next iteration
        previousModel = model;
        previousResponse = response.content;
      }
    } catch (error) {
      console.error(`Error calling ${model} in discussion mode:`, error);
      toast.error(`Failed to get response from ${model}`);
    }
  }

  return allResponses;
}

// Function to call a single model in discuss mode
export async function callDiscussModel(
  model: 'openai' | 'grok' | 'qwen' | 'deepseek' | 'doubao' | 'glm',
  messages: { role: string, content: string }[],
  previousModel: string | null = null,
  previousResponse: string | null = null,
  apiKeys?: Record<string, string>,
  language: string = 'en',
  stream: boolean = false,
  onStreamUpdate?: (chunk: string) => void
): Promise<ModelResponse> {
  try {
    const response = await fetch(`/api/discuss/${model}`, {
      method: 'POST',
      headers: createHeaders(apiKeys),
      body: JSON.stringify({
        messages,
        previous_model: previousModel,
        previous_response: previousResponse,
        language,
        stream
      })
    });

    if (!response.ok) {
      throw new Error(`Error from ${model} API: ${response.statusText}`);
    }

    // Handle streaming response
    if (stream && response.body && onStreamUpdate) {
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let content = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        const chunk = decoder.decode(value, { stream: true });
        content += chunk;
        onStreamUpdate(content);
      }
      
      return {
        model,
        content
      };
    } 
    
    // Handle non-streaming response
    const data = await response.json();
    return {
      model,
      content: data.content || data.message || data.answer || ""
    };
  } catch (error) {
    console.error(`Error in callDiscussModel for ${model}:`, error);
    throw error;
  }
}
