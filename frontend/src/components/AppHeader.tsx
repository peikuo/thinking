
import React from "react";
import { PlusCircle, PanelLeftClose, PanelLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import ApiKeySettings from "./ApiKeySettings";
import LanguageSwitcher from "./LanguageSwitcher";
import LayoutSwitcher from "./LayoutSwitcher";
import ExportButton from "./ExportButton";
import { useLanguage } from "@/contexts/LanguageContext";
import { useApp } from "@/contexts/AppContext";
import { useNewConversation } from "@/hooks/useNewConversation";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";

interface AppHeaderProps {
  onNewConversation: () => void;
  onToggleSidebar: () => void;
  sidebarOpen?: boolean;
}

const AppHeader: React.FC<AppHeaderProps> = ({ onNewConversation: _onNewConversation, onToggleSidebar, sidebarOpen = true }) => {
  const { t } = useLanguage();
  const { saveApiKeys } = useApp();
  
  // Use our custom hook that handles both discuss and chat modes
  const handleNewConversation = useNewConversation();

  return (
    <header className="sticky top-0 border-b bg-white/90 backdrop-blur-sm z-50 shadow-sm">
      <div className="container flex h-14 items-center relative z-10">
        <div className="flex items-center gap-3">
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <Button variant="outline" size="icon" onClick={onToggleSidebar} className="mr-1">
                  {sidebarOpen ? (
                    <PanelLeftClose className="h-5 w-5 text-slate-700" />
                  ) : (
                    <PanelLeft className="h-5 w-5 text-slate-700" />
                  )}
                </Button>
              </TooltipTrigger>
              <TooltipContent>
                <p>{sidebarOpen ? t('hideHistory') : t('showHistory')}</p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>
          <h1 className="text-lg font-medium text-slate-900">
            {t('compare')}
          </h1>
        </div>
        <div className="ml-auto flex items-center gap-3">
          <div className="text-sm text-slate-500 hidden md:block">
            {t('modelWillRespond')}
          </div>
          <LayoutSwitcher />
          <LanguageSwitcher />
          <ExportButton />
          <ApiKeySettings onSaveKeys={saveApiKeys} />
          <Button
            onClick={handleNewConversation}
            variant="outline"
            className="gap-2 border-slate-200 hover:border-slate-300 hover:bg-slate-50"
          >
            <PlusCircle className="h-4 w-4 text-slate-600" />
            <span className="font-medium">{t('newConversation')}</span>
          </Button>
        </div>
      </div>
    </header>
  );
};

export default AppHeader;
