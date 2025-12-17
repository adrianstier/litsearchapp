import { useEffect, useRef } from 'react';
import { Network } from 'vis-network';
import { DataSet } from 'vis-data';
import '../styles/CitationNetwork.css';

export default function CitationNetwork({ data }) {
  const containerRef = useRef(null);
  const networkRef = useRef(null);

  useEffect(() => {
    if (!data || !containerRef.current) return;

    // Prepare nodes
    const nodes = new DataSet(
      data.nodes.map(node => ({
        id: node.id,
        label: node.label,
        title: node.label, // Tooltip
        color: getNodeColor(node.type),
        shape: node.type === 'seed' ? 'star' : 'dot',
        size: node.type === 'seed' ? 30 : 20,
        font: {
          size: node.type === 'seed' ? 16 : 12,
          color: '#333',
          face: 'Inter, system-ui, sans-serif'
        }
      }))
    );

    // Prepare edges
    const edges = new DataSet(
      data.edges.map(edge => ({
        from: edge.from,
        to: edge.to,
        arrows: 'to',
        color: {
          color: '#999',
          highlight: '#2563eb',
          hover: '#2563eb'
        },
        width: 2,
        smooth: {
          type: 'cubicBezier',
          forceDirection: 'horizontal',
          roundness: 0.4
        }
      }))
    );

    // Network options
    const options = {
      nodes: {
        borderWidth: 2,
        borderWidthSelected: 3,
        chosen: {
          node: (values) => {
            values.borderWidth = 3;
            values.shadow = true;
          }
        }
      },
      edges: {
        chosen: {
          edge: (values) => {
            values.width = 4;
          }
        }
      },
      physics: {
        enabled: true,
        solver: 'forceAtlas2Based',
        forceAtlas2Based: {
          gravitationalConstant: -50,
          centralGravity: 0.01,
          springLength: 200,
          springConstant: 0.08,
          damping: 0.4,
          avoidOverlap: 0.5
        },
        stabilization: {
          enabled: true,
          iterations: 150,
          updateInterval: 25
        }
      },
      interaction: {
        hover: true,
        tooltipDelay: 200,
        navigationButtons: true,
        keyboard: true
      },
      layout: {
        hierarchical: {
          enabled: false
        }
      }
    };

    // Create network
    networkRef.current = new Network(containerRef.current, { nodes, edges }, options);

    // Event handlers
    networkRef.current.on('click', (params) => {
      if (params.nodes.length > 0) {
        const nodeId = params.nodes[0];
        console.log('Clicked node:', nodeId);
        // Could navigate to paper detail page here
        // window.location.href = `/paper/${nodeId}`;
      }
    });

    networkRef.current.on('stabilizationIterationsDone', () => {
      networkRef.current.setOptions({ physics: false });
    });

    // Cleanup
    return () => {
      if (networkRef.current) {
        networkRef.current.destroy();
        networkRef.current = null;
      }
    };
  }, [data]);

  const getNodeColor = (type) => {
    switch (type) {
      case 'seed':
        return {
          background: '#2563eb',
          border: '#1e40af',
          highlight: { background: '#1d4ed8', border: '#1e3a8a' },
          hover: { background: '#1d4ed8', border: '#1e3a8a' }
        };
      case 'citing':
        return {
          background: '#10b981',
          border: '#059669',
          highlight: { background: '#059669', border: '#047857' },
          hover: { background: '#059669', border: '#047857' }
        };
      case 'reference':
        return {
          background: '#f59e0b',
          border: '#d97706',
          highlight: { background: '#d97706', border: '#b45309' },
          hover: { background: '#d97706', border: '#b45309' }
        };
      default:
        return {
          background: '#6b7280',
          border: '#4b5563',
          highlight: { background: '#4b5563', border: '#374151' },
          hover: { background: '#4b5563', border: '#374151' }
        };
    }
  };

  if (!data || !data.nodes || data.nodes.length === 0) {
    return (
      <div className="citation-network-empty">
        <p>No citation network data available.</p>
        <p className="hint">This paper may not have citation data in OpenAlex.</p>
      </div>
    );
  }

  return (
    <div className="citation-network-container">
      <div className="network-legend">
        <div className="legend-item">
          <div className="legend-color" style={{ background: '#2563eb' }}></div>
          <span>This Paper (Seed)</span>
        </div>
        <div className="legend-item">
          <div className="legend-color" style={{ background: '#10b981' }}></div>
          <span>Citing Papers (Later Work)</span>
        </div>
        <div className="legend-item">
          <div className="legend-color" style={{ background: '#f59e0b' }}></div>
          <span>Referenced Papers (Earlier Work)</span>
        </div>
      </div>
      <div className="network-stats">
        <span>
          <strong>{data.nodes.length}</strong> papers
        </span>
        <span>
          <strong>{data.edges.length}</strong> connections
        </span>
        <span>
          <strong>{data.citations?.length || 0}</strong> citing papers
        </span>
        <span>
          <strong>{data.references?.length || 0}</strong> referenced papers
        </span>
      </div>
      <div ref={containerRef} className="network-canvas" />
      <div className="network-controls">
        <p className="hint">
          💡 Click and drag to pan • Scroll to zoom • Click nodes for details • Use navigation buttons
        </p>
      </div>
    </div>
  );
}
