import React, { useEffect, useRef, useState } from 'react';
// Import mermaid dynamically to avoid build issues
// We'll initialize it when the component mounts

interface MermaidDiagramProps {
  chart: string;
}

const MermaidDiagram: React.FC<MermaidDiagramProps> = ({ chart }) => {
  const ref = useRef<HTMLDivElement>(null);
  const [error, setError] = useState<string | null>(null);
  const [rendered, setRendered] = useState(false);

  useEffect(() => {
    if (ref.current && !rendered) {
      // Dynamically import mermaid
      import('mermaid').then(async (mermaidModule) => {
        const mermaid = mermaidModule.default;
        
        try {
          // Initialize mermaid with default configuration
          mermaid.initialize({
            startOnLoad: false,
            theme: 'default',
            securityLevel: 'loose',
            fontFamily: 'sans-serif',
          });
          
          // Reset the element content
          ref.current.innerHTML = chart;
          
          // Render the diagram
          await mermaid.run({
            nodes: [ref.current],
          });
          
          setRendered(true);
          setError(null);
        } catch (err) {
          console.error('Mermaid rendering error:', err);
          setError('Failed to render diagram. Check your syntax.');
        }
      }).catch((err) => {
        console.error('Failed to load Mermaid library:', err);
        setError('Failed to load diagram rendering library.');
      });
    }
  }, [chart, rendered]);

  // If there's an error, show it
  if (error) {
    return (
      <div className="p-4 border border-red-300 bg-red-50 rounded text-red-600">
        <p className="font-bold">Diagram Error</p>
        <p>{error}</p>
        <pre className="mt-2 p-2 bg-gray-100 rounded text-sm overflow-x-auto">{chart}</pre>
      </div>
    );
  }

  return (
    <div className="mermaid-diagram-wrapper my-4 overflow-x-auto">
      <div ref={ref} className="mermaid">
        {chart}
      </div>
    </div>
  );
};

export default MermaidDiagram;
