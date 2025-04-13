import React, { memo } from 'react';

interface WaveLoadingAnimationProps {
  color: string;
  text?: string;
}

const WaveLoadingAnimation: React.FC<WaveLoadingAnimationProps> = memo(({ 
  color, 
  text = "Thinking..." 
}) => {
  return (
    <div className="flex flex-col items-start space-y-2">
      <div className="flex items-center space-x-2">
        <div className="flex space-x-1">
          {[0, 1, 2, 3, 4].map((i) => (
            <div 
              key={i}
              className={`h-2 w-2 rounded-full animate-pulse opacity-75`}
              style={{ 
                backgroundColor: color,
                animationDelay: `${i * 150}ms`,
                animationDuration: '1.5s'
              }}
            />
          ))}
        </div>
        <span className="text-sm text-gray-500 animate-pulse">{text}</span>
      </div>
    </div>
  );
});

export default WaveLoadingAnimation;
