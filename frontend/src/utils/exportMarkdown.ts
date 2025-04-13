import { ConversationMessage, ModelResponse } from "@/types/models";

/**
 * Converts a conversation to markdown format
 * @param messages The conversation messages to convert
 * @returns A string containing the markdown representation of the conversation
 */
export function conversationToMarkdown(messages: ConversationMessage[]): string {
  if (!messages || messages.length === 0) {
    return "# Empty Conversation";
  }

  let markdown = "# AI Model Comparison\n\n";
  
  messages.forEach((message, index) => {
    if (message.role === "user") {
      // Add user message
      markdown += `## Question ${index + 1}\n\n${message.content}\n\n`;
    } else if (message.role === "assistant") {
      // Add model responses
      if (message.modelResponses && message.modelResponses.length > 0) {
        markdown += "### Model Responses\n\n";
        
        message.modelResponses.forEach((response: ModelResponse) => {
          if (response.error) {
            markdown += `#### ${capitalizeFirstLetter(response.model)}\n\n*Error: ${response.error}*\n\n`;
          } else {
            markdown += `#### ${capitalizeFirstLetter(response.model)}\n\n${response.content}\n\n`;
          }
        });
      }
      
      // Add summary if available
      if (message.summary && message.summary.content) {
        markdown += "### Summary\n\n";
        markdown += `${message.summary.content}\n\n`;
      }
    }
  });
  
  return markdown;
}

/**
 * Helper function to capitalize the first letter of a string
 */
function capitalizeFirstLetter(string: string): string {
  return string.charAt(0).toUpperCase() + string.slice(1);
}

/**
 * Exports conversation as a markdown file
 * @param messages The conversation messages to export
 * @param filename The name of the file to download
 */
export function exportAsMarkdown(messages: ConversationMessage[], filename: string = "conversation"): void {
  const markdown = conversationToMarkdown(messages);
  const blob = new Blob([markdown], { type: "text/markdown;charset=utf-8" });
  
  // Create a download link
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `${filename}.md`;
  
  // Trigger download
  document.body.appendChild(link);
  link.click();
  
  // Clean up
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}
