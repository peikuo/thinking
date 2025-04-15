import React, { useEffect, useState } from 'react';
import { ArrowUp, ArrowDown } from 'lucide-react';

const ScrollButton: React.FC = () => {
  const [visible, setVisible] = useState(false);
  const [isAtTop, setIsAtTop] = useState(true);
  
  useEffect(() => {
    const handleScroll = () => {
      const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
      const scrollHeight = document.documentElement.scrollHeight;
      const clientHeight = document.documentElement.clientHeight;
      
      // Check if page is scrollable - add a small buffer to account for rounding errors
      const isScrollable = scrollHeight > clientHeight + 5;
      
      // If not scrollable, always hide the button
      if (!isScrollable) {
        setVisible(false);
        return;
      }
      
      // Check if we're at the top or bottom
      const isTop = scrollTop < 100;
      const isBottom = scrollTop + clientHeight >= scrollHeight - 100;
      
      // Only show button if we're at the top or bottom
      setVisible(isTop || isBottom);
      setIsAtTop(isTop);
    };
    
    // Initial check
    handleScroll();
    
    // Add scroll event listener
    window.addEventListener('scroll', handleScroll);
    window.addEventListener('resize', handleScroll);
    
    // Clean up
    return () => {
      window.removeEventListener('scroll', handleScroll);
      window.removeEventListener('resize', handleScroll);
    };
  }, []);
  
  const scrollToPosition = () => {
    if (isAtTop) {
      // If at top, scroll to bottom
      window.scrollTo({
        top: document.documentElement.scrollHeight,
        behavior: 'smooth'
      });
    } else {
      // Otherwise, scroll to top
      window.scrollTo({
        top: 0,
        behavior: 'smooth'
      });
    }
  };
  
  if (!visible) return null;
  
  return (
    <button
      onClick={scrollToPosition}
      className="fixed left-4 bottom-4 z-50 p-2 rounded-full bg-[#10A37F] text-white shadow-lg hover:bg-[#0E8D6E] transition-all duration-300"
      aria-label={isAtTop ? "Scroll to bottom" : "Scroll to top"}
    >
      {isAtTop ? <ArrowDown size={20} /> : <ArrowUp size={20} />}
    </button>
  );
};

export default ScrollButton;
