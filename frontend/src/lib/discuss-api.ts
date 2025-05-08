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

  // Check if we have a stored conversation history for discuss mode
  let storedHistory;
  try {
    // First check if we're loading an existing conversation from the main conversation storage
    const savedConversations = localStorage.getItem('ai-comparison-conversations');
    if (savedConversations) {
      const conversations = JSON.parse(savedConversations);
      // Find the most recent discuss mode conversation (should be the first one if we just clicked on it)
      const discussConversation = conversations.find((conv: any) => conv.isDiscussMode === true);
      
      if (discussConversation && discussConversation.messages) {
        // Extract the conversation history from the discuss mode conversation
        const userMessages = discussConversation.messages.filter((msg: any) => msg.role === 'user');
        const assistantMessages = discussConversation.messages.filter((msg: any) => msg.role === 'assistant');
        
        // Build the conversation history
        storedHistory = [];
        
        // Add user messages
        userMessages.forEach((msg: any) => {
          storedHistory.push({ role: 'user', content: msg.content });
        });
        
        // Add assistant messages if available
        if (assistantMessages.length > 0 && assistantMessages[0].modelResponses) {
          assistantMessages[0].modelResponses.forEach((response: any) => {
            storedHistory.push({ 
              role: 'assistant', 
              content: `[${response.model}] ${response.content}` 
            });
          });
        }
      }
    }
    
    // If we didn't find a history in the main conversation storage, check the discuss-specific storage
    if (!storedHistory) {
      const savedDiscussHistory = localStorage.getItem('thinking-discuss-history');
      if (savedDiscussHistory) {
        storedHistory = JSON.parse(savedDiscussHistory);
      }
    }
  } catch (error) {
    console.error('Error loading discuss history:', error);
  }

  // Initialize with existing history or just the new prompt
  let messages;
  let conversationHistory;
  
  if (storedHistory && storedHistory.length > 0) {
    // Use stored history and add the new prompt
    conversationHistory = [...storedHistory];
    // Add the new user message if it's not already the last user message
    const lastUserMsg = conversationHistory.filter(m => m.role === 'user').pop();
    if (!lastUserMsg || lastUserMsg.content !== prompt) {
      conversationHistory.push({ role: "user", content: prompt });
    }
    messages = conversationHistory;
  } else {
    // Start a new conversation
    messages = [{ role: "user", content: prompt }];
    conversationHistory = [...messages];
  }
  
  const allResponses: Record<string, string> = {};
  let previousModel: string | null = null;
  let previousResponse: string | null = null;

  // Process models in sequence
  for (const model of modelOrder) {
    try {
      console.log(`Sending conversation history to ${model}:`, conversationHistory);
      const response = await callDiscussModel(
        model,
        conversationHistory, // Use the full conversation history
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
        
        // Add the assistant's response to the conversation history
        conversationHistory.push({
          role: "assistant",
          content: `[${model}] ${response.content}`
        });
        
        // Save the updated conversation history
        try {
          localStorage.setItem('thinking-discuss-history', JSON.stringify(conversationHistory));
          
          // Also update the conversation title in the main conversation storage
          const savedConversations = localStorage.getItem('ai-comparison-conversations');
          if (savedConversations) {
            const conversations = JSON.parse(savedConversations);
            // Find the most recent discuss mode conversation
            const discussIndex = conversations.findIndex((conv: any) => conv.isDiscussMode === true);
            
            if (discussIndex !== -1) {
              // Get the first user message as the title
              const userMessages = conversationHistory.filter((msg: any) => msg.role === 'user');
              if (userMessages.length > 0) {
                const firstUserMsg = userMessages[0].content;
                const title = firstUserMsg.length > 30 ? firstUserMsg.substring(0, 30) + '...' : firstUserMsg;
                
                // Update the title
                conversations[discussIndex].title = title;
                // Update the messages to include all history
                conversations[discussIndex].messages = [
                  ...conversationHistory.filter((msg: any) => msg.role === 'user'),
                  {
                    role: 'assistant',
                    content: Object.values(allResponses).join('\n\n---\n\n'),
                    modelResponses: Object.entries(allResponses).map(([model, content]) => ({
                      model,
                      content,
                      loading: false
                    }))
                  }
                ];
                
                // Save the updated conversations
                localStorage.setItem('ai-comparison-conversations', JSON.stringify(conversations));
              }
            }
          }
        } catch (error) {
          console.error('Error saving discuss history:', error);
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
    // Use consistent URL pattern for API requests
    const requestUrl = `/api/discuss/summary`;
    const response = await fetch(requestUrl, {
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
                
                // Check if this is the end of the stream
                if (data.done) {
                  break;
                }
                
                // Handle error in stream
                if (data.error) {
                  throw new Error(data.error);
                }
                
                if (data.content) {
                  fullContent += data.content;
                  // Process streaming summary chunk
                  onStreamUpdate(fullContent);
                }
              } catch (e) {
                console.error('Error parsing SSE message:', e);
              }
            }
          }
        }
        
        return { content: fullContent };
      } catch (e) {
        console.error('Error reading stream:', e);
        const errorMessage = e instanceof Error ? e.message : 'Unknown error in summary stream';
        return { content: fullContent, error: errorMessage };
      } finally {
        // Always release the reader lock when done
        reader.releaseLock();
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
    // Use API_BASE_URL for consistent behavior between environments
    const requestUrl = `/api/discuss/${model}`;
    const response = await fetch(requestUrl, {
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
                
                // Check if this is the end of the stream
                if (data.done) {
                  break;
                }
                
                // Handle error in stream
                if (data.error) {
                  throw new Error(data.error);
                }
                
                if (data.content) {
                  // For new streaming implementation, we're getting delta content
                  fullContent += data.content;
                  // Process streaming chunk
                  onStreamUpdate(fullContent);
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
        // Always release the reader lock when done
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
