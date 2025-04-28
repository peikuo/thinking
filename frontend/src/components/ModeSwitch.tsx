import React from 'react';
import { Button } from '@/components/ui/button';
import { 
  ToggleGroup, 
  ToggleGroupItem 
} from "@/components/ui/toggle-group";
import { MessageCircle, Users } from 'lucide-react';
import { useMode } from '@/contexts/ModeContext';
import { useLanguage } from '@/contexts/LanguageContext';

const ModeSwitch: React.FC = () => {
  const { mode, setMode } = useMode();
  const { t } = useLanguage();

  return (
    <div className="flex items-center justify-center mb-4">
      <ToggleGroup type="single" value={mode} onValueChange={(value) => value && setMode(value as 'chat' | 'discuss')}>
        <ToggleGroupItem value="chat" aria-label="Chat Mode" className="flex items-center gap-2">
          <MessageCircle className="h-4 w-4" />
          <span>{t('chatMode')}</span>
        </ToggleGroupItem>
        <ToggleGroupItem value="discuss" aria-label="Discuss Mode" className="flex items-center gap-2">
          <Users className="h-4 w-4" />
          <span>{t('discussMode')}</span>
        </ToggleGroupItem>
      </ToggleGroup>
    </div>
  );
};

export default ModeSwitch;
