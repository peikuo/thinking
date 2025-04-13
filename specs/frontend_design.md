# Think Together (集思广益) Frontend Design Specification

## Overview

Think Together is a web application that allows users to compare responses from multiple AI models (OpenAI, Grok, Qwen, DeepSeek) side by side. This document outlines the frontend architecture, component structure, state management approach, and design decisions.

## Tech Stack

- **Framework**: React with TypeScript
- **Styling**: Tailwind CSS
- **State Management**: React Context API with custom hooks
- **Build Tool**: Vite
- **UI Components**: Shadcn/UI

## Architecture

The application follows a component-based architecture with a clear separation of concerns:

1. **Components**: UI elements that render the interface
2. **Contexts**: Global state management
3. **Hooks**: Reusable logic and state management
4. **Types**: TypeScript type definitions
5. **Lib**: Utility functions and helpers

### Directory Structure

```
frontend/
├── public/
│   ├── favicon.svg
│   └── title-locale.js
├── src/
│   ├── components/
│   │   ├── ui/                 # Shadcn UI components
│   │   ├── ApiKeySettings.tsx  # API key management UI
│   │   ├── AppHeader.tsx       # Application header
│   │   ├── ConversationHistorySidebar.tsx  # Sidebar with conversation history
│   │   ├── ConversationThread.tsx  # Displays conversation messages
│   │   ├── DeleteConfirmationDialog.tsx  # Confirmation dialog for deletions
│   │   ├── IndexContent.tsx    # Main content container
│   │   ├── MainLayout.tsx      # Overall layout structure
│   │   ├── ModelResponseCard.tsx  # Individual model response display
│   │   ├── PromptInput.tsx     # User input component
│   │   └── WelcomeScreen.tsx   # Initial welcome screen
│   ├── contexts/
│   │   ├── AppContext.tsx      # Main application context
│   │   └── LanguageContext.tsx # Localization context
│   ├── hooks/
│   │   ├── useApiKeys.ts       # API key management
│   │   ├── useConversations.ts # Conversation state management
│   │   ├── useModelApi.ts      # API interaction logic
│   │   └── useSidebar.ts       # Sidebar visibility management
│   ├── lib/
│   │   └── utils.ts            # Utility functions
│   ├── types/
│   │   ├── api.ts              # API-related types
│   │   └── models.ts           # Data model types
│   ├── App.tsx                 # Root application component
│   └── main.tsx                # Application entry point
```

## Component Design

### Main Components

#### AppHeader
- Displays the application title and language switcher
- Contains the sidebar toggle button
- Responsive design that adapts to different screen sizes

#### ConversationHistorySidebar
- Lists all user conversations with delete functionality
- Highlights the active conversation
- Includes confirmation dialog for conversation deletion
- Collapsible on mobile devices

#### PromptInput
- Text area for user input with auto-resize
- Send button with loading state
- Localized placeholder text
- Increased font size (1.125rem) for better readability

#### ModelResponseCard
- Displays individual AI model responses
- Shows loading state with skeleton UI
- Error handling for failed API calls
- Color-coded headers for each model
- Increased font size (1.05rem) for better readability

#### DeleteConfirmationDialog
- Modal dialog for confirming deletion actions
- Localized text for title, description, and buttons
- Displays the conversation title being deleted
- Red highlight for the delete button to indicate destructive action

### Layout

The application uses a responsive layout with the following structure:

1. **Header**: Fixed at the top with app title and controls
2. **Sidebar**: Collapsible sidebar on the left for conversation history
3. **Main Content**: Central area that displays:
   - Welcome screen (when no conversation is active)
   - Conversation thread (when a conversation is active)
4. **Input Area**: Fixed at the bottom for user input

## State Management

The application uses a combination of React Context and custom hooks for state management:

### Contexts

#### AppContext
- Combines all custom hooks into a single provider
- Makes state and actions available throughout the application
- Simplifies component access to global state

#### LanguageContext
- Manages language selection (English/Chinese)
- Provides translation function for UI text
- Persists language preference in localStorage

### Custom Hooks

#### useConversations
- Manages conversation state (create, select, delete)
- Handles conversation messages
- Persists conversations in localStorage

#### useApiKeys
- Manages API keys for different models
- Validates and stores API keys securely
- Persists API keys in localStorage

#### useModelApi
- Handles API requests to the backend
- Manages loading and error states
- Processes model responses

#### useSidebar
- Controls sidebar visibility
- Persists sidebar state in localStorage
- Provides toggle functionality

## Styling

The application uses Tailwind CSS for styling with a consistent design system:

### Color Palette

- **Primary**: `#10A37F` (green)
- **Secondary**: `#0E8D6E` (darker green)
- **Background**: White with subtle transparency (`bg-white/80`)
- **Text**: Slate-800 for headings, slate-600 for body text
- **Accent**: Model-specific colors for visual differentiation
- **Destructive**: Red-500 for delete actions

### Typography

- **Headings**: 
  - App title: 1.5rem (24px)
  - Card titles: 1.25rem (20px)
- **Body Text**: 
  - Standard text: 1rem (16px)
  - Input text: 1.125rem (18px)
  - Response text: 1.05rem (16.8px)
- **Small Text**: 0.875rem (14px) for secondary information

### UI Components

The application uses Shadcn/UI components with custom styling:

- **Cards**: For model responses with subtle shadows and hover effects
- **Buttons**: Green primary buttons, red for destructive actions
- **Inputs**: Clean text areas with focus states
- **Sidebar**: Collapsible with hover effects for items
- **Dialog**: Modal dialogs for confirmations

## Localization

The application supports both English and Chinese languages:

### Implementation

- Uses LanguageContext for managing translations
- All UI text is accessed through the translation function (`t`)
- Language preference is stored in localStorage
- Dynamic page title based on selected language

### Key UI Elements in Both Languages

| Element | English | Chinese |
|---------|---------|---------|
| App Title | Think Together | 集思广益 |
| App Description | Combining the wisdom of multiple AI models | 汇集多个AI模型的智慧 |
| Input Placeholder | Ask any question to compare AI model responses... | 提出问题，汇集多个AI模型的智慧... |
| Send Button | Send | 发送 |
| Delete | Delete | 删除 |
| Cancel | Cancel | 取消 |

## Performance Optimizations

The application includes several performance optimizations:

1. **Memoization**: Key components use React.memo to prevent unnecessary re-renders
2. **Lazy Loading**: Components are loaded only when needed
3. **Optimized Dependencies**: useEffect hooks have proper dependency arrays
4. **Local Storage**: Persistent data is stored locally to reduce API calls
5. **Debouncing**: Input changes are debounced to reduce processing overhead

## Accessibility

The application follows accessibility best practices:

1. **Keyboard Navigation**: All interactive elements are keyboard accessible
2. **Screen Reader Support**: Proper ARIA labels and roles
3. **Color Contrast**: Text meets WCAG AA standards for readability
4. **Focus Management**: Visible focus indicators for keyboard users
5. **Responsive Design**: Adapts to different screen sizes and orientations

## Future Enhancements

Potential areas for future frontend improvements:

1. **Dark Mode**: Implement theme switching functionality
2. **Additional Languages**: Expand localization support beyond English and Chinese
3. **Conversation Export**: Allow users to export conversations as PDF or text
4. **Custom Themes**: Allow users to customize the UI colors and appearance
5. **Voice Input**: Add speech-to-text functionality for prompt input
6. **Keyboard Shortcuts**: Implement keyboard shortcuts for common actions
7. **Model Comparison View**: Add side-by-side comparison of specific aspects of responses
8. **Response Analytics**: Add metrics and analysis of model responses

## Conclusion

The Think Together frontend is designed to be user-friendly, accessible, and performant. The component-based architecture with custom hooks and context providers ensures a maintainable codebase that can be easily extended with new features. The responsive design and localization support make the application accessible to a wide range of users.
