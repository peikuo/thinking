import React from 'react';
import { useLanguage } from '@/contexts/LanguageContext';

const WelcomeScreen: React.FC = () => {
  const { t } = useLanguage();
  
  return (
    <div className="text-center py-16 backdrop-blur-sm bg-white/30 rounded-xl border border-gray-200 shadow-sm p-8 transition-all duration-500">
      <div className="p-4 rounded-full bg-gradient-to-br from-[#10A37F] to-[#0E8D6E] mx-auto w-16 h-16 flex items-center justify-center text-white mb-6">
        <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"></path>
        </svg>
      </div>
      <h2 className="text-2xl font-semibold mb-4 text-gray-800">
        {t('welcome')}
      </h2>
      <p className="text-gray-600 mb-6 max-w-2xl mx-auto">
        {t('welcomeDescription')}
      </p>
    </div>
  );
};

export default WelcomeScreen;
