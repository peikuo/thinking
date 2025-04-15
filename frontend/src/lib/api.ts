import { toast } from "sonner";
import { ModelResponse, ComparisonSummary, ConversationMessage } from "@/types/models";

// API base URL - this should be configurable in a real environment
const API_BASE_URL = 'http://localhost:8000';

// Helper function to create API headers with API keys
const createHeaders = (apiKeys?: Record<string, string>) => {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };
  
  // Add API keys to headers if provided
  if (apiKeys) {
    // Encode API keys to handle non-ASCII characters
    if (apiKeys.openai) headers['X-OpenAI-API-Key'] = encodeURIComponent(apiKeys.openai);
    if (apiKeys.grok) headers['X-Grok-API-Key'] = encodeURIComponent(apiKeys.grok);
    if (apiKeys.qwen) headers['X-Qwen-API-Key'] = encodeURIComponent(apiKeys.qwen);
    if (apiKeys.deepseek) headers['X-DeepSeek-API-Key'] = encodeURIComponent(apiKeys.deepseek);
  }
  
  return headers;
};

// Function to query a single model with streaming support
async function querySingleModel(
  model: 'openai' | 'grok' | 'qwen' | 'deepseek',
  messages: { role: string, content: string }[],
  apiKeys?: Record<string, string>,
  language: string = 'en',
  onStreamUpdate?: (chunk: { content: string, model: string }) => void
): Promise<ModelResponse> {
  try {
    // If streaming callback is provided, use streaming mode
    const useStreaming = !!onStreamUpdate;
    
    const response = await fetch(`${API_BASE_URL}/api/chat/${model}`, {
      method: 'POST',
      headers: createHeaders(apiKeys),
      body: JSON.stringify({ messages, language, stream: useStreaming })
    });
    
    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`${model} API error: ${response.status} - ${errorText}`);
    }
    
    // Handle streaming response
    if (useStreaming) {
      // Create a reader from the response body stream
      const reader = response.body!.getReader();
      const decoder = new TextDecoder();
      let fullContent = '';
      
      try {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          
          // Decode the chunk and process each SSE message
          const chunk = decoder.decode(value, { stream: true });
          const lines = chunk.split('\n\n');
          
          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.substring(6));
                
                // Check if this is the end of the stream
                if (data.done) {
                  break;
                }
                
                // Handle error in stream
                if (data.error) {
                  throw new Error(data.error);
                }
                
                // Update content and call the callback
                if (data.content) {
                  fullContent += data.content;
                  console.log(`Streaming chunk for ${data.model}:`, data.content);
                  onStreamUpdate?.({ content: data.content, model: data.model });
                }
              } catch (e) {
                console.error('Error parsing SSE message:', e);
              }
            }
          }
        }
        
        return { model, content: fullContent };
      } catch (error) {
        console.error(`Error in stream for ${model}:`, error);
        const errorMessage = error instanceof Error ? error.message : `Unknown error with ${model} stream`;
        return { model, content: fullContent, error: errorMessage };
      } finally {
        reader.releaseLock();
      }
    } else {
      // Handle non-streaming response
      const data = await response.json();
      return { model, content: data.content };
    }
  } catch (error) {
    console.error(`Error querying ${model}:`, error);
    const errorMessage = error instanceof Error ? error.message : `Unknown error with ${model}`;
    return { model, content: "", error: errorMessage };
  }
}

// Function to query all models or selected models in parallel without requesting summary
export async function queryAllModels(
  prompt: string,
  apiKeys?: Record<string, string>,
  language: string = 'en',
  onStreamUpdate?: (model: string, content: string) => void,
  selectedModels?: string[],
  conversationHistory?: ConversationMessage[]
): Promise<{
  modelResponses: ModelResponse[],
  summary: ComparisonSummary
}> {
  try {
    // Determine which models to query
    const modelsToQuery = selectedModels || ['openai', 'grok', 'qwen', 'deepseek'];
    console.log('Querying models:', modelsToQuery);
    
    // Make parallel requests to selected model endpoints
    const modelPromises = [];
    
    // Helper function to prepare model-specific conversation history
    const prepareModelHistory = (modelName: string): { role: string, content: string }[] => {
      // Default message with current prompt
      const currentMessage = { role: 'user', content: prompt };
      
      // If no conversation history, just return the current prompt
      if (!conversationHistory || conversationHistory.length === 0) {
        return [currentMessage];
      }
      
      // Extract model-specific history (only this model's responses)
      const modelHistory: { role: string, content: string }[] = [];
      
      // Process conversation history to extract relevant messages
      for (let i = 0; i < conversationHistory.length; i++) {
        const msg = conversationHistory[i];
        
        // Add user messages
        if (msg.role === 'user') {
          modelHistory.push({ role: 'user', content: msg.content });
        }
        // Add only this model's responses
        else if (msg.role === 'assistant' && msg.modelResponses) {
          const modelResponse = msg.modelResponses.find(r => r.model === modelName);
          if (modelResponse && modelResponse.content) {
            modelHistory.push({ role: 'assistant', content: modelResponse.content });
          }
        }
      }
      
      // Add the current prompt if it's not already the last message
      if (modelHistory.length === 0 || 
          modelHistory[modelHistory.length - 1].role !== 'user' || 
          modelHistory[modelHistory.length - 1].content !== prompt) {
        modelHistory.push(currentMessage);
      }
      
      // Limit to the 5 most recent messages
      return modelHistory.slice(-10); // Keep 5 exchanges (up to 10 messages)
    };
    
    if (modelsToQuery.includes('openai')) {
      const openaiMessages = prepareModelHistory('openai');
      console.log('OpenAI messages:', openaiMessages);
      modelPromises.push(querySingleModel('openai', openaiMessages, apiKeys, language, onStreamUpdate ? 
        (chunk) => onStreamUpdate('openai', chunk.content) : undefined));
    }
    
    if (modelsToQuery.includes('grok')) {
      const grokMessages = prepareModelHistory('grok');
      console.log('Grok messages:', grokMessages);
      modelPromises.push(querySingleModel('grok', grokMessages, apiKeys, language, onStreamUpdate ? 
        (chunk) => onStreamUpdate('grok', chunk.content) : undefined));
    }
    
    if (modelsToQuery.includes('qwen')) {
      const qwenMessages = prepareModelHistory('qwen');
      console.log('Qwen messages:', qwenMessages);
      modelPromises.push(querySingleModel('qwen', qwenMessages, apiKeys, language, onStreamUpdate ? 
        (chunk) => onStreamUpdate('qwen', chunk.content) : undefined));
    }
    
    if (modelsToQuery.includes('deepseek')) {
      const deepseekMessages = prepareModelHistory('deepseek');
      console.log('DeepSeek messages:', deepseekMessages);
      modelPromises.push(querySingleModel('deepseek', deepseekMessages, apiKeys, language, onStreamUpdate ? 
        (chunk) => onStreamUpdate('deepseek', chunk.content) : undefined));
    }
    
    const modelResponses = await Promise.all(modelPromises);
    
    // Only generate summary if more than one model is queried
    const emptySummary: ComparisonSummary = { content: "" };
    return {
      modelResponses,
      summary: modelsToQuery.length > 1 ? emptySummary : { content: "", skipSummary: true }
    };
  } catch (error) {
    console.error("Error in queryAllModels:", error);
    toast.error("Failed to query AI models");
    
    // Return error responses for all models
    const errorMessage = error instanceof Error ? error.message : "Unknown error occurred";
    const modelResponses: ModelResponse[] = [
      { model: 'openai', content: "", error: errorMessage },
      { model: 'grok', content: "", error: errorMessage },
      { model: 'qwen', content: "", error: errorMessage },
      { model: 'deepseek', content: "", error: errorMessage }
    ];
    
    const emptySummary: ComparisonSummary = {
      content: ""
    };
    
    return { modelResponses, summary: emptySummary };
  }
}

// Function to request summary after model responses are rendered
export async function requestSummary(
  prompt: string,
  modelResponses: ModelResponse[],
  apiKeys?: Record<string, string>,
  language: string = 'en',
  onStreamUpdate?: (content: string) => void
): Promise<ComparisonSummary> {
  try {
    // Prepare responses for summary
    const responsesForSummary: Record<string, string> = {};
    
    modelResponses.forEach(response => {
      if (response.content && !response.error) {
        responsesForSummary[response.model] = response.content;
      }
    });
    
    // Check if we have valid responses to summarize
    if (Object.keys(responsesForSummary).length === 0) {
      return { content: "" };
    }
    
    // If streaming callback is provided, use streaming mode
    const useStreaming = !!onStreamUpdate;
    
    // Request summary from API
    const summaryResponse = await fetch(`${API_BASE_URL}/api/summary`, {
      method: 'POST',
      headers: createHeaders(apiKeys),
      body: JSON.stringify({
        responses: responsesForSummary,
        question: prompt,
        language,
        stream: useStreaming
      })
    });
    
    if (!summaryResponse.ok) {
      const errorText = await summaryResponse.text();
      throw new Error(`Summary API error: ${summaryResponse.status} - ${errorText}`);
    }
    
    // Handle streaming response
    if (useStreaming) {
      console.log('Summary streaming mode enabled');
      // Create a reader from the response body stream
      const reader = summaryResponse.body!.getReader();
      const decoder = new TextDecoder();
      let summaryContent = "";
      
      try {
        // Process the stream
        while (true) {
          const { done, value } = await reader.read();
          
          if (done) {
            break;
          }
          
          // Decode the chunk
          const chunk = decoder.decode(value);
          console.log('Received summary chunk:', chunk);
          
          // Process each line in the chunk
          const lines = chunk.split('\n');
          
          for (const line of lines) {
            // Skip empty lines
            if (!line.trim() || !line.startsWith('data:')) {
              continue;
            }
            
            // Parse the data
            try {
              const jsonData = JSON.parse(line.substring(5).trim());
              console.log('Parsed summary data:', jsonData);
              
              if (jsonData.done) {
                // End of stream
                console.log('Summary stream done, model:', jsonData.model);
                continue;
              }
              
              if (jsonData.error) {
                console.error('Streaming error:', jsonData.error);
                continue;
              }
              
              if (jsonData.content) {
                // Add to summary content
                summaryContent += jsonData.content;
                console.log('Adding content from model:', jsonData.model, 'content:', jsonData.content);
                
                // Call the update callback - this is for summary content, regardless of what model name is in the response
                // The backend might send 'deepseek' as the model name even for summary content
                if (onStreamUpdate) {
                  onStreamUpdate(jsonData.content);
                }
              }
            } catch (e) {
              console.error('Error parsing streaming data:', e, line);
            }
          }
        }
      } finally {
        reader.releaseLock();
      }
      
      return { content: summaryContent };
    } else {
      // Handle non-streaming response
      const summaryData = await summaryResponse.json();
      return { content: summaryData.summary };
    }
  } catch (error) {
    console.error("Error generating summary:", error);
    // Return empty summary if generation fails
    return { content: "" };
  }
}

