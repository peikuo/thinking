import React, { useEffect, useRef, useState } from 'react';
import mermaid from 'mermaid';

// Initialize mermaid with default configuration
mermaid.initialize({
  startOnLoad: false,
  theme: 'default',
  securityLevel: 'loose',
  fontFamily: 'sans-serif',
});

interface MermaidDiagramProps {
  chart: string;
}

const MermaidDiagram: React.FC<MermaidDiagramProps> = ({ chart }) => {
  const ref = useRef<HTMLDivElement>(null);
  const [error, setError] = useState<string | null>(null);
  const [rendered, setRendered] = useState(false);

  useEffect(() => {
    if (ref.current && !rendered) {
      try {
        // Reset the element content
        ref.current.innerHTML = chart;
        
        // Render the diagram
        mermaid.run({
          nodes: [ref.current],
        }).then(() => {
          setRendered(true);
          setError(null);
        }).catch((err) => {
          console.error('Mermaid rendering error:', err);
          setError('Failed to render diagram. Check your syntax.');
        });
      } catch (err) {
        console.error('Mermaid error:', err);
        setError('Failed to render diagram. Check your syntax.');
      }
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
