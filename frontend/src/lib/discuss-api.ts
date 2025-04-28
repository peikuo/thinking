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
        true, // Enable streaming for better user experience
        (streamContent) => {
          // Update responses as streaming chunks arrive
          if (onModelResponse) {
            allResponses[model] = streamContent;
            onModelResponse(model, streamContent);
          }
        }
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
// Function to generate a summary of the discussion
export async function requestDiscussionSummary(
  userPrompt: string,
  responses: Record<string, string>,
  apiKeys?: Record<string, string>,
  language: string = 'en',
  onStreamUpdate?: (content: string) => void
) {
  try {
    const response = await fetch(`/api/discuss/summary`, {
      method: 'POST',
      headers: createHeaders(apiKeys),
      body: JSON.stringify({
        user_prompt: userPrompt,
        responses,
        language,
        stream: !!onStreamUpdate
      })
    });

    if (!response.ok) {
      throw new Error(`Error from summary API: ${response.statusText}`);
    }

    // Handle streaming response
    if (onStreamUpdate && response.body) {
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let fullContent = "";

      try {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          
          const chunk = decoder.decode(value, { stream: true });
          const lines = chunk.split('\n\n');
          
          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.substring(6));
                if (data.content) {
                  fullContent += data.content;
                  onStreamUpdate(fullContent);
                }
              } catch (e) {
                console.error('Error parsing SSE message:', e);
              }
            }
          }
        }
        
        // Signal that streaming is complete
        onStreamUpdate(fullContent);
        return { content: fullContent };
      } catch (e) {
        console.error('Error reading stream:', e);
        throw e;
      }
    } else {
      // Non-streaming response
      const data = await response.json();
      return data;
    }
  } catch (error) {
    console.error('Error requesting summary:', error);
    throw error;
  }
}

export async function callDiscussModel(
  model: 'openai' | 'grok' | 'qwen' | 'deepseek' | 'doubao' | 'glm',
  messages: { role: string, content: string }[],
  previousModel: string | null = null,
  previousResponse: string | null = null,
  apiKeys?: Record<string, string>,
  language: string = 'en',
  stream: boolean = true, // Default to streaming for better UX
  onStreamUpdate?: (content: string) => void
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
      let fullContent = "";

      try {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          
          const chunk = decoder.decode(value, { stream: true });
          const lines = chunk.split('\n\n');
          
          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.substring(6));
                if (data.content) {
                  // For new streaming implementation, we're getting delta content
                  fullContent += data.content;
                  onStreamUpdate(fullContent);
                }
              } catch (e) {
                console.error('Error parsing SSE message:', e);
              }
            }
          }
        }
        
        // Signal that streaming is complete for this model
        onStreamUpdate?.(fullContent);
        return { model, content: fullContent };
      } catch (error) {
        console.error(`Streaming error for ${model}:`, error);
        throw error;
      } finally {
        reader.releaseLock();
      }
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
