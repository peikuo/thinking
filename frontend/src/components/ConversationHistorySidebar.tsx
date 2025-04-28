
import React, { useState, useMemo } from "react";
import { 
  Sidebar, 
  SidebarContent, 
  SidebarHeader,
  SidebarMenu,
  SidebarMenuItem,
  SidebarMenuButton,
  SidebarFooter,
} from "@/components/ui/sidebar";
import { History, MessageSquare, Trash2, PlusCircle, ChevronDown, ChevronRight } from "lucide-react";
import { useLanguage } from "@/contexts/LanguageContext";
import { Conversation } from "@/hooks/useConversations";
import DeleteConfirmationDialog from "./DeleteConfirmationDialog";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface ConversationHistorySidebarProps {
  conversations: Conversation[];
  activeConversationId: string | null;
  isOpen: boolean;
  onSelectConversation: (id: string) => void;
  onDeleteConversation: (id: string) => void;
  onRenameConversation: (id: string, newTitle: string) => void;
}

const ConversationHistorySidebar: React.FC<ConversationHistorySidebarProps> = ({
  conversations,
  activeConversationId,
  isOpen,
  onSelectConversation,
  onDeleteConversation,
  onRenameConversation,
}) => {
  const { t } = useLanguage();
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [conversationToDelete, setConversationToDelete] = useState<Conversation | null>(null);
  const [editingConversationId, setEditingConversationId] = useState<string | null>(null);
  const [editTitle, setEditTitle] = useState('');
  const [activeTab, setActiveTab] = useState('today');
  // Track which sections are collapsed
  const [collapsedSections, setCollapsedSections] = useState<Record<string, boolean>>({});
  
  // Group conversations by relative time periods
  const groupedConversations = useMemo(() => {
    // Create result object
    const result: Record<string, Conversation[]> = {};
    
    // Sort conversations by timestamp (newest first)
    const sortedConversations = [...conversations].sort((a, b) => b.timestamp - a.timestamp);
    
    // Define time thresholds
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate()).getTime();
    const yesterday = today - (1 * 86400000); // 1 day in milliseconds
    const threeDaysAgo = today - (3 * 86400000);
    const sevenDaysAgo = today - (7 * 86400000);
    const fifteenDaysAgo = today - (15 * 86400000);
    const thirtyDaysAgo = today - (30 * 86400000);
    const halfYearAgo = today - (180 * 86400000); // ~6 months
    const oneYearAgo = today - (365 * 86400000);
    
    // Group conversations by time periods
    sortedConversations.forEach(conv => {
      const timestamp = conv.timestamp;
      let periodKey;
      
      if (timestamp >= today) {
        periodKey = t('today');
      } else if (timestamp >= yesterday) {
        periodKey = t('yesterday');
      } else if (timestamp >= sevenDaysAgo) {
        periodKey = t('sevenDaysAgo');
      } else if (timestamp >= threeDaysAgo) {
        periodKey = t('threeDaysAgo');
      } else if (timestamp >= thirtyDaysAgo) {
        periodKey = t('last30Days');
      } else if (timestamp >= halfYearAgo) {
        periodKey = t('halfYearAgo');
      } else if (timestamp >= oneYearAgo) {
        periodKey = t('oneYearAgo');
      } else {
        // More than a year ago - show the year
        const date = new Date(timestamp);
        periodKey = String(date.getFullYear());
      }
      
      if (!result[periodKey]) {
        result[periodKey] = [];
      }
      result[periodKey].push(conv);
    });
    
    return result;
  }, [conversations, t]);

  const handleDeleteClick = (e: React.MouseEvent, conversation: Conversation) => {
    e.stopPropagation();
    setConversationToDelete(conversation);
    setDeleteDialogOpen(true);
  };

  const handleConfirmDelete = () => {
    if (conversationToDelete) {
      onDeleteConversation(conversationToDelete.id);
      setDeleteDialogOpen(false);
      setConversationToDelete(null);
    }
  };

  const handleCancelDelete = () => {
    setDeleteDialogOpen(false);
    setConversationToDelete(null);
  };

  const handleDoubleClick = (conversation: Conversation) => {
    setEditingConversationId(conversation.id);
    setEditTitle(conversation.title);
  };

  const handleTitleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setEditTitle(e.target.value);
  };

  const handleTitleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>, conversationId: string) => {
    if (e.key === 'Enter') {
      if (editTitle.trim()) {
        onRenameConversation(conversationId, editTitle.trim());
      }
      setEditingConversationId(null);
    } else if (e.key === 'Escape') {
      setEditingConversationId(null);
    }
  };

  const handleTitleBlur = (conversationId: string) => {
    if (editTitle.trim()) {
      onRenameConversation(conversationId, editTitle.trim());
    }
    setEditingConversationId(null);
  };

  // Toggle section collapse state
  const toggleSection = (sectionKey: string) => {
    setCollapsedSections(prev => ({
      ...prev,
      [sectionKey]: !prev[sectionKey]
    }));
  };
  
  // Render a conversation item in OpenAI style
  const renderConversationItem = (conversation: Conversation) => (
    <SidebarMenuItem key={conversation.id}>
      {editingConversationId === conversation.id ? (
        <div className="flex items-center w-full pl-3 pr-10 py-2">
          <input
            type="text"
            value={editTitle}
            onChange={handleTitleChange}
            onKeyDown={(e) => handleTitleKeyDown(e, conversation.id)}
            onBlur={() => handleTitleBlur(conversation.id)}
            autoFocus
            className="w-full bg-transparent border-none focus:outline-none focus:ring-1 focus:ring-slate-400 rounded px-1 text-sm"
          />
        </div>
      ) : (
        <SidebarMenuButton 
          isActive={activeConversationId === conversation.id}
          onClick={() => onSelectConversation(conversation.id)}
          onDoubleClick={() => handleDoubleClick(conversation)}
          tooltip={conversation.title}
          className="text-sm py-2 pr-8 hover:bg-gray-100 rounded-md" // OpenAI style
        >
          <span className="truncate max-w-[calc(100%-28px)]">{conversation.title}</span>
        </SidebarMenuButton>
      )}
      <button 
        className="absolute right-2 top-1/2 -translate-y-1/2 opacity-0 group-hover:opacity-100 transition-opacity z-10 p-1 hover:bg-gray-200 rounded-md"
        onClick={(e) => handleDeleteClick(e, conversation)}
        aria-label={t('delete')}
        title={t('delete')}
      >
        <Trash2 className="h-3.5 w-3.5 text-gray-500 hover:text-red-500" />
      </button>
    </SidebarMenuItem>
  );

  // Render empty state
  const renderEmptyState = () => (
    <div className="px-4 py-3 text-center text-sm text-gray-500">
      <p>{t('noHistoryYet')}</p>
    </div>
  );

  return (
    <Sidebar 
      className={isOpen ? "" : "md:hidden"}
      collapsible={isOpen ? "none" : "offcanvas"}
    >
      <SidebarHeader className="flex items-center justify-between px-4 py-3 border-b border-gray-200">
        <div className="flex items-center gap-2">
          <span className="text-base font-medium text-gray-800">
            {t('history')}
          </span>
        </div>
        <Button variant="ghost" size="sm" className="h-8 w-8 p-0 rounded-full">
          <PlusCircle className="h-4 w-4" />
          <span className="sr-only">New chat</span>
        </Button>
      </SidebarHeader>
      
      <SidebarContent className="px-2 py-2">
        {conversations.length > 0 ? (
          <div className="space-y-6">
            {/* Render each date section in chronological order */}
            {Object.entries(groupedConversations)
              // Sort sections with Today and Yesterday first, then other dates in reverse chronological order
              .sort(([dateA], [dateB]) => {
                const orderA = dateA === t('today') ? 0 : dateA === t('yesterday') ? 1 : 2;
                const orderB = dateB === t('today') ? 0 : dateB === t('yesterday') ? 1 : 2;
                
                if (orderA !== orderB) return orderA - orderB;
                return dateA.localeCompare(dateB);
              })
              .map(([dateStr, convs]) => (
                <div key={dateStr} className="space-y-1 mb-2">
                  {/* Collapsible section heading */}
                  <button 
                    onClick={() => toggleSection(dateStr)}
                    className="w-full flex items-center px-3 py-1 text-xs font-medium text-gray-500 uppercase tracking-wider hover:bg-gray-100 rounded-md"
                  >
                    {collapsedSections[dateStr] ? 
                      <ChevronRight className="h-3 w-3 mr-1" /> : 
                      <ChevronDown className="h-3 w-3 mr-1" />
                    }
                    {dateStr}
                  </button>
                  
                  {/* Conversations for this period - only show if not collapsed */}
                  {!collapsedSections[dateStr] && (
                    <SidebarMenu>
                      {convs.map(renderConversationItem)}
                    </SidebarMenu>
                  )}
                </div>
              ))}
            
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center h-full px-4 py-8 text-center text-gray-500">
            <History className="h-12 w-12 mb-4 opacity-50" />
            <p className="text-sm">{t('noHistoryYet')}</p>
            <p className="text-xs mt-1">
              {t('conversationsWillAppear')}
            </p>
          </div>
        )}
      </SidebarContent>
      
      <SidebarFooter className="px-4 py-2 text-xs text-gray-500 border-t border-gray-200">
        <p>{t('storedLocally')}</p>
      </SidebarFooter>

      {conversationToDelete && (
        <DeleteConfirmationDialog
          isOpen={deleteDialogOpen}
          onClose={handleCancelDelete}
          onConfirm={handleConfirmDelete}
          title={conversationToDelete.title}
        />
      )}
    </Sidebar>
  );
};

export default ConversationHistorySidebar;
