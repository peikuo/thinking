import { toast } from "sonner";
import { ModelResponse, ComparisonSummary, ConversationMessage } from "@/types/models";

// API base URL - using relative path to work in any environment
const API_BASE_URL = '';  // Empty string means use the current domain

// Helper function to process API URLs
const logApiRequest = (url: string) => {
  // Simply return the URL without logging in production
  return url;
};

// Helper function to create API headers with API keys
export const createHeaders = (apiKeys?: Record<string, string>) => {
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
    if (apiKeys.doubao) headers['X-Doubao-API-Key'] = encodeURIComponent(apiKeys.doubao);
    if (apiKeys.glm) headers['X-GLM-API-Key'] = encodeURIComponent(apiKeys.glm);
  }
  
  return headers;
};

// Function to query a single model with streaming support
async function querySingleModel(
  model: 'openai' | 'grok' | 'qwen' | 'deepseek' | 'doubao' | 'glm',
  messages: { role: string, content: string }[],
  apiKeys?: Record<string, string>,
  language: string = 'en',
  onStreamUpdate?: (chunk: { content: string, model: string }) => void
): Promise<ModelResponse> {
  try {
    // If streaming callback is provided, use streaming mode
    const useStreaming = !!onStreamUpdate;
    
    const requestUrl = `${API_BASE_URL}/api/chat/${model}`;
    const response = await fetch(logApiRequest(requestUrl), {
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
                  // Process streaming chunk
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
    // Double-check language from localStorage to ensure consistency
    const storedLanguage = localStorage.getItem('ai-comparison-language') || 'en';
    
    // Use the stored language to determine models (overriding the parameter if needed)
    // This ensures consistency with the conversation display
    const effectiveLanguage = storedLanguage as 'en' | 'zh';
    
    // Determine which models to query based on language
    let defaultModels = effectiveLanguage === 'zh' 
      ? ['deepseek', 'qwen', 'doubao', 'glm']
      : ['openai', 'grok', 'qwen', 'deepseek'];
    
    // Force language-specific models if no specific selection was made
    // This ensures we always use the right models for the current language
    const modelsToQuery = selectedModels || defaultModels;
    
    console.log(`Using models for ${effectiveLanguage} locale:`, modelsToQuery);
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
      
      // Track if we've seen any assistant responses for this model
      let hasModelResponses = false;
      
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
            hasModelResponses = true;
          }
        }
      }
      
      // If we have no assistant responses for this model (e.g., when switching locales),
      // only keep the most recent user message to avoid overwhelming the model
      let filteredHistory = [...modelHistory];
      if (!hasModelResponses && modelHistory.length > 1) {
        // Find the last user message
        const lastUserMessageIndex = modelHistory.map(m => m.role).lastIndexOf('user');
        if (lastUserMessageIndex >= 0) {
          // Only keep the last user message
          filteredHistory = [modelHistory[lastUserMessageIndex]];
        }
      }
      
      // Use the filtered history for the rest of the function
      const finalHistory = filteredHistory;
      
      // Add the current prompt if it's not already the last message
      if (finalHistory.length === 0 || 
          finalHistory[finalHistory.length - 1].role !== 'user' || 
          finalHistory[finalHistory.length - 1].content !== prompt) {
        finalHistory.push(currentMessage);
      }
      
      // Limit to the 5 most recent messages
      return finalHistory.slice(-10); // Keep 5 exchanges (up to 10 messages)
    };
    
    // Add model queries ONLY for the models we want to query
    // This ensures we don't create requests for models that aren't relevant to the current language
    const addModelQuery = (model: 'openai' | 'grok' | 'qwen' | 'deepseek' | 'doubao' | 'glm') => {
      if (modelsToQuery.includes(model)) {
        const messages = prepareModelHistory(model);
        console.log(`${model} messages:`, messages);
        modelPromises.push(querySingleModel(
          model, 
          messages, 
          apiKeys, 
          language, 
          onStreamUpdate ? (chunk) => onStreamUpdate(model, chunk.content) : undefined
        ));
      }
    };
    
    // ONLY add queries for models that are in modelsToQuery
    // This is the critical fix - we only process the models relevant to the current language
    modelsToQuery.forEach(model => {
      addModelQuery(model as 'openai' | 'grok' | 'qwen' | 'deepseek' | 'doubao' | 'glm');
    });
    
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
    
    // Create error responses based on language
    const allModels = ['openai', 'grok', 'qwen', 'deepseek', 'doubao', 'glm'] as const;
    const modelResponses: ModelResponse[] = allModels.map(model => ({
      model: model as 'openai' | 'grok' | 'qwen' | 'deepseek' | 'doubao' | 'glm',
      content: "",
      error: errorMessage
    }));
    
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
    const summaryUrl = `${API_BASE_URL}/api/chat/summary`;
    const summaryResponse = await fetch(logApiRequest(summaryUrl), {
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

