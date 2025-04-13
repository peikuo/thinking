
import React, { useState, useEffect } from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Settings } from "lucide-react";
import { useLanguage } from "@/contexts/LanguageContext";
import { useApp } from "@/contexts/AppContext";
import { ApiKeys } from "@/hooks/useApiKeys";

interface ApiKeySettingsProps {
  onSaveKeys: (keys: ApiKeys) => void;
}

const ApiKeySettings: React.FC<ApiKeySettingsProps> = ({ onSaveKeys }) => {
  const { t } = useLanguage();
  const { apiKeys: currentApiKeys } = useApp();
  const [apiKeys, setApiKeys] = useState<ApiKeys>({
    openai: "",
    grok: "",
    qwen: "",
    deepseek: ""
  });
  const [open, setOpen] = useState(false);
  
  // Load current API keys when dialog opens
  useEffect(() => {
    if (open) {
      setApiKeys(currentApiKeys);
    }
  }, [open, currentApiKeys]);

  const handleChange = (model: string, value: string) => {
    setApiKeys(prev => ({
      ...prev,
      [model]: value
    }));
  };

  const handleSave = () => {
    onSaveKeys(apiKeys);
    setOpen(false);
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="outline" size="icon" className="rounded-full">
          <Settings className="h-4 w-4" />
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>{t('apiKeys')}</DialogTitle>
          <DialogDescription>
            {t('apiKeysDescription')}
          </DialogDescription>
        </DialogHeader>
        <div className="space-y-4 py-4">
          <div className="space-y-2">
            <Label htmlFor="openai-key">{t('openaiKey')}</Label>
            <Input
              id="openai-key"
              type="password"
              placeholder="sk-..."
              value={apiKeys.openai}
              onChange={(e) => handleChange("openai", e.target.value)}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="grok-key">{t('grokKey')}</Label>
            <Input
              id="grok-key"
              type="password"
              placeholder="grok-..."
              value={apiKeys.grok}
              onChange={(e) => handleChange("grok", e.target.value)}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="qwen-key">{t('qwenKey')}</Label>
            <Input
              id="qwen-key"
              type="password"
              placeholder="qwen-..."
              value={apiKeys.qwen}
              onChange={(e) => handleChange("qwen", e.target.value)}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="deepseek-key">{t('deepseekKey')}</Label>
            <Input
              id="deepseek-key"
              type="password"
              placeholder="deepseek-..."
              value={apiKeys.deepseek}
              onChange={(e) => handleChange("deepseek", e.target.value)}
            />
          </div>
        </div>
        <div className="flex justify-end">
          <Button onClick={handleSave}>{t('save')}</Button>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default ApiKeySettings;
