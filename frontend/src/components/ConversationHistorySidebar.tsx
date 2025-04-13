
import React, { useState } from "react";
import { 
  Sidebar, 
  SidebarContent, 
  SidebarHeader,
  SidebarMenu,
  SidebarMenuItem,
  SidebarMenuButton,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
} from "@/components/ui/sidebar";
import { History, MessageSquare, Trash2 } from "lucide-react";
import { useLanguage } from "@/contexts/LanguageContext";
import { Conversation } from "@/hooks/useConversations";
import DeleteConfirmationDialog from "./DeleteConfirmationDialog";

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

  return (
    <Sidebar 
      className={isOpen ? "" : "md:hidden"}
      collapsible={isOpen ? "none" : "offcanvas"}
    >
      <SidebarHeader className="flex items-center justify-between px-4 py-2">
        <div className="flex items-center gap-2">
          <History className="h-5 w-5 text-slate-600" />
          <span className="text-base font-medium text-slate-800">
            {t('history')}
          </span>
        </div>
      </SidebarHeader>
      
      <SidebarContent>
        {conversations.length > 0 ? (
          <SidebarGroup>
            <SidebarGroupLabel>{t('recentConversations')}</SidebarGroupLabel>
            <SidebarGroupContent>
              <SidebarMenu>
                {conversations.map((conversation) => (
                  <SidebarMenuItem key={conversation.id}>
                    {editingConversationId === conversation.id ? (
                      <div className="flex items-center w-full pl-3 pr-10 py-2">
                        <MessageSquare className="h-4 w-4 mr-2 flex-shrink-0" />
                        <input
                          type="text"
                          value={editTitle}
                          onChange={handleTitleChange}
                          onKeyDown={(e) => handleTitleKeyDown(e, conversation.id)}
                          onBlur={() => handleTitleBlur(conversation.id)}
                          autoFocus
                          className="w-full bg-transparent border-none focus:outline-none focus:ring-1 focus:ring-slate-400 rounded px-1 text-base"
                        />
                      </div>
                    ) : (
                      <SidebarMenuButton 
                        isActive={activeConversationId === conversation.id}
                        onClick={() => onSelectConversation(conversation.id)}
                        onDoubleClick={() => handleDoubleClick(conversation)}
                        tooltip={conversation.title}
                        className="text-base pr-8" // Added right padding to make room for delete button
                      >
                        <MessageSquare className="h-4 w-4" />
                        <span className="truncate text-base max-w-[calc(100%-28px)]">{conversation.title}</span>
                      </SidebarMenuButton>
                    )}
                    <button 
                      className="absolute right-2 top-1/2 -translate-y-1/2 transition-colors z-10 bg-slate-100 rounded-full p-1 hover:bg-slate-200"
                      onClick={(e) => handleDeleteClick(e, conversation)}
                      aria-label={t('delete')}
                      title={t('delete')}
                    >
                      <Trash2 className="h-3.5 w-3.5 text-slate-400 hover:text-red-500" />
                    </button>
                  </SidebarMenuItem>
                ))}
              </SidebarMenu>
            </SidebarGroupContent>
          </SidebarGroup>
        ) : (
          <div className="flex flex-col items-center justify-center h-full px-4 py-8 text-center text-muted-foreground">
            <History className="h-12 w-12 mb-4 text-muted-foreground/50" />
            <p className="text-sm">{t('noHistoryYet')}</p>
            <p className="text-xs mt-1">
              {t('conversationsWillAppear')}
            </p>
          </div>
        )}
      </SidebarContent>
      
      <SidebarFooter className="px-4 py-2 text-xs text-muted-foreground">
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
