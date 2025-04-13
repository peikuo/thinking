import React from "react";
import { Download } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useLanguage } from "@/contexts/LanguageContext";
import { useApp } from "@/contexts/AppContext";
import { exportAsMarkdown } from "@/utils/exportMarkdown";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { toast } from "sonner";

const ExportButton: React.FC = () => {
  const { t } = useLanguage();
  const { messages, activeConversationId } = useApp();

  const handleExport = () => {
    if (messages.length === 0) {
      toast.error(t('noContentToExport'), {
        description: t('noContent'),
      });
      return;
    }

    const filename = `conversation-${activeConversationId?.substring(0, 8) || "export"}-${new Date().toISOString().split('T')[0]}`;
    exportAsMarkdown(messages, filename);
    
    toast.success(t('conversationExported'), {
      description: t('exportSuccess'),
    });
  };

  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          <Button
            onClick={handleExport}
            variant="outline"
            size="icon"
            className="border-slate-200 hover:border-slate-300 hover:bg-slate-50"
          >
            <Download className="h-4 w-4 text-slate-600" />
          </Button>
        </TooltipTrigger>
        <TooltipContent>
          <p>{t('exportAsMarkdown')}</p>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
};

export default ExportButton;
