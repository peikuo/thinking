import React from 'react';
import { Button } from '@/components/ui/button';
import { LayoutGrid, Rows3 } from 'lucide-react';
import { useLayout } from '@/contexts/LayoutContext';
import { useLanguage } from '@/contexts/LanguageContext';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';

const LayoutSwitcher: React.FC = () => {
  const { layout, setLayout } = useLayout();
  const { t } = useLanguage();
  
  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setLayout(layout === 'default' ? 'compact' : 'default')}
            className="h-9 w-9"
          >
            {layout === 'default' ? (
              <LayoutGrid className="h-5 w-5" />
            ) : (
              <Rows3 className="h-5 w-5" />
            )}
          </Button>
        </TooltipTrigger>
        <TooltipContent side="bottom">
          {layout === 'default' 
            ? t('switchToCompactLayout') 
            : t('switchToDefaultLayout')}
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
};

export default LayoutSwitcher;
