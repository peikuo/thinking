
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
import { Settings, ExternalLink } from "lucide-react";
import { useLanguage } from "@/contexts/LanguageContext";
import { getModelDisplayName } from '../utils/modelDisplayName';
import { useApp } from "@/contexts/AppContext";
import { ApiKeys } from "@/hooks/useApiKeys";

interface ApiKeySettingsProps {
  onSaveKeys: (keys: ApiKeys) => void;
}

const ApiKeySettings: React.FC<ApiKeySettingsProps> = ({ onSaveKeys }) => {
  const { t, language } = useLanguage();
  const { apiKeys: currentApiKeys } = useApp();
  const [apiKeys, setApiKeys] = useState<ApiKeys>({
    openai: "",
    grok: "",
    qwen: "",
    deepseek: "",
    glm: "",
    doubao: ""
  });
  const [open, setOpen] = useState(false);
  
  // API provider URLs
  const providerUrls = {
    openai: "https://platform.openai.com/docs/overview",
    grok: "https://x.ai/api",
    qwen: "https://www.alibabacloud.com/help/zh/model-studio/",
    deepseek: "https://platform.deepseek.com/",
    glm: "https://www.bigmodel.cn/dev/welcome",
    doubao: "https://www.volcengine.com/mcp-marketplace"
  };
  
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
          {/* English locale: OpenAI, Grok, Qwen, DeepSeek */}
          {language === 'en' && (
            <>
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Label htmlFor="openai-key">{getModelDisplayName('openai', language)} {t('openaiKey')}</Label>
                  <a href={providerUrls.openai} target="_blank" rel="noopener noreferrer" className="text-xs text-blue-500 flex items-center gap-1">
                    <span>Get API Key</span>
                    <ExternalLink className="h-3 w-3" />
                  </a>
                </div>
                <Input
                  id="openai-key"
                  type="password"
                  placeholder="sk-..."
                  value={apiKeys.openai}
                  onChange={(e) => handleChange("openai", e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Label htmlFor="grok-key">{getModelDisplayName('grok', language)} {t('grokKey')}</Label>
                  <a href={providerUrls.grok} target="_blank" rel="noopener noreferrer" className="text-xs text-blue-500 flex items-center gap-1">
                    <span>Get API Key</span>
                    <ExternalLink className="h-3 w-3" />
                  </a>
                </div>
                <Input
                  id="grok-key"
                  type="password"
                  placeholder="grok-..."
                  value={apiKeys.grok}
                  onChange={(e) => handleChange("grok", e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Label htmlFor="qwen-key">{t('qwenKey')}</Label>
                  <a href={providerUrls.qwen} target="_blank" rel="noopener noreferrer" className="text-xs text-blue-500 flex items-center gap-1">
                    <span>Get API Key</span>
                    <ExternalLink className="h-3 w-3" />
                  </a>
                </div>
                <Input
                  id="qwen-key"
                  type="password"
                  placeholder="qwen-..."
                  value={apiKeys.qwen}
                  onChange={(e) => handleChange("qwen", e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Label htmlFor="deepseek-key">{t('deepseekKey')}</Label>
                  <a href={providerUrls.deepseek} target="_blank" rel="noopener noreferrer" className="text-xs text-blue-500 flex items-center gap-1">
                    <span>Get API Key</span>
                    <ExternalLink className="h-3 w-3" />
                  </a>
                </div>
                <Input
                  id="deepseek-key"
                  type="password"
                  placeholder="deepseek-..."
                  value={apiKeys.deepseek}
                  onChange={(e) => handleChange("deepseek", e.target.value)}
                />
              </div>
            </>
          )}

          {/* Chinese locale: GLM, Doubao, DeepSeek, Qwen */}
          {language === 'zh' && (
            <>
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Label htmlFor="glm-key">{getModelDisplayName('glm', language)} {t('glmKey')}</Label>
                  <a href={providerUrls.glm} target="_blank" rel="noopener noreferrer" className="text-xs text-blue-500 flex items-center gap-1">
                    <span>获取API密钥</span>
                    <ExternalLink className="h-3 w-3" />
                  </a>
                </div>
                <Input
                  id="glm-key"
                  type="password"
                  placeholder="glm-..."
                  value={apiKeys.glm}
                  onChange={(e) => handleChange("glm", e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Label htmlFor="doubao-key">{getModelDisplayName('doubao', language)} {t('doubaoKey')}</Label>
                  <a href={providerUrls.doubao} target="_blank" rel="noopener noreferrer" className="text-xs text-blue-500 flex items-center gap-1">
                    <span>获取API密钥</span>
                    <ExternalLink className="h-3 w-3" />
                  </a>
                </div>
                <Input
                  id="doubao-key"
                  type="password"
                  placeholder="doubao-..."
                  value={apiKeys.doubao}
                  onChange={(e) => handleChange("doubao", e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Label htmlFor="deepseek-key">{t('deepseekKey')}</Label>
                  <a href={providerUrls.deepseek} target="_blank" rel="noopener noreferrer" className="text-xs text-blue-500 flex items-center gap-1">
                    <span>获取API密钥</span>
                    <ExternalLink className="h-3 w-3" />
                  </a>
                </div>
                <Input
                  id="deepseek-key"
                  type="password"
                  placeholder="deepseek-..."
                  value={apiKeys.deepseek}
                  onChange={(e) => handleChange("deepseek", e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Label htmlFor="qwen-key">{t('qwenKey')}</Label>
                  <a href={providerUrls.qwen} target="_blank" rel="noopener noreferrer" className="text-xs text-blue-500 flex items-center gap-1">
                    <span>获取API密钥</span>
                    <ExternalLink className="h-3 w-3" />
                  </a>
                </div>
                <Input
                  id="qwen-key"
                  type="password"
                  placeholder="qwen-..."
                  value={apiKeys.qwen}
                  onChange={(e) => handleChange("qwen", e.target.value)}
                />
              </div>
            </>
          )}
        </div>
        <div className="flex justify-end">
          <Button onClick={handleSave}>{t('save')}</Button>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default ApiKeySettings;
