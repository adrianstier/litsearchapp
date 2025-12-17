/**
 * D3.js Citation Network Visualization Component
 */

import React, { useEffect, useRef, useState } from 'react';
import { networkAPI } from '../services/api';
import './CitationNetworkD3.css';

export function CitationNetworkD3({ paperId, width = 800, height = 600 }) {
  const svgRef = useRef(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [networkData, setNetworkData] = useState(null);
  const [selectedNode, setSelectedNode] = useState(null);

  useEffect(() => {
    if (!paperId) return;

    const loadNetwork = async () => {
      setLoading(true);
      setError(null);

      try {
        const response = await networkAPI.getD3Network(paperId);
        setNetworkData(response.data);
      } catch (err) {
        setError('Failed to load citation network');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    loadNetwork();
  }, [paperId]);

  useEffect(() => {
    if (!networkData || !svgRef.current) return;

    // Clear previous visualization
    const svg = svgRef.current;
    while (svg.firstChild) {
      svg.removeChild(svg.firstChild);
    }

    // Create the visualization
    renderNetwork(svg, networkData, width, height, setSelectedNode);
  }, [networkData, width, height]);

  if (loading) {
    return (
      <div className="citation-network-loading">
        <div className="loading-spinner" />
        <p>Loading citation network...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="citation-network-error">
        <p>{error}</p>
      </div>
    );
  }

  if (!networkData) {
    return null;
  }

  return (
    <div className="citation-network-d3">
      <div className="network-header">
        <h3>Citation Network</h3>
        <div className="network-stats">
          <span>{networkData.stats?.total_nodes || 0} papers</span>
          <span>{networkData.stats?.total_links || 0} connections</span>
        </div>
      </div>

      <div className="network-legend">
        <div className="legend-item">
          <span className="legend-dot seed" />
          <span>Selected Paper</span>
        </div>
        <div className="legend-item">
          <span className="legend-dot citing" />
          <span>Citing Papers</span>
        </div>
        <div className="legend-item">
          <span className="legend-dot reference" />
          <span>References</span>
        </div>
      </div>

      <div className="network-container">
        <svg
          ref={svgRef}
          width={width}
          height={height}
          viewBox={`0 0 ${width} ${height}`}
        />
      </div>

      {selectedNode && (
        <div className="node-details">
          <h4>{selectedNode.title}</h4>
          <p>Citations: {selectedNode.citations}</p>
          <p>Type: {selectedNode.type}</p>
        </div>
      )}
    </div>
  );
}

function renderNetwork(svg, data, width, height, onNodeSelect) {
  const { nodes, links } = data;

  if (!nodes || nodes.length === 0) return;

  // Create SVG groups
  const ns = 'http://www.w3.org/2000/svg';

  // Defs for arrow markers
  const defs = document.createElementNS(ns, 'defs');
  const marker = document.createElementNS(ns, 'marker');
  marker.setAttribute('id', 'arrowhead');
  marker.setAttribute('viewBox', '-0 -5 10 10');
  marker.setAttribute('refX', 20);
  marker.setAttribute('refY', 0);
  marker.setAttribute('orient', 'auto');
  marker.setAttribute('markerWidth', 6);
  marker.setAttribute('markerHeight', 6);

  const path = document.createElementNS(ns, 'path');
  path.setAttribute('d', 'M 0,-5 L 10,0 L 0,5');
  path.setAttribute('fill', 'var(--color-border)');
  marker.appendChild(path);
  defs.appendChild(marker);
  svg.appendChild(defs);

  // Create groups for links and nodes
  const linkGroup = document.createElementNS(ns, 'g');
  linkGroup.setAttribute('class', 'links');
  svg.appendChild(linkGroup);

  const nodeGroup = document.createElementNS(ns, 'g');
  nodeGroup.setAttribute('class', 'nodes');
  svg.appendChild(nodeGroup);

  // Simple force-directed layout simulation
  const nodePositions = {};
  const centerX = width / 2;
  const centerY = height / 2;

  // Position nodes
  nodes.forEach((node, i) => {
    if (node.type === 'seed') {
      nodePositions[node.id] = { x: centerX, y: centerY };
    } else if (node.type === 'citing') {
      const angle = (i / nodes.filter(n => n.type === 'citing').length) * Math.PI;
      const radius = 150;
      nodePositions[node.id] = {
        x: centerX + Math.cos(angle - Math.PI / 2) * radius,
        y: centerY + Math.sin(angle - Math.PI / 2) * radius - 50
      };
    } else {
      const angle = (i / nodes.filter(n => n.type === 'reference').length) * Math.PI;
      const radius = 150;
      nodePositions[node.id] = {
        x: centerX + Math.cos(angle + Math.PI / 2) * radius,
        y: centerY + Math.sin(angle + Math.PI / 2) * radius + 50
      };
    }
  });

  // Draw links
  links.forEach(link => {
    const source = nodePositions[link.source];
    const target = nodePositions[link.target];

    if (source && target) {
      const line = document.createElementNS(ns, 'line');
      line.setAttribute('x1', source.x);
      line.setAttribute('y1', source.y);
      line.setAttribute('x2', target.x);
      line.setAttribute('y2', target.y);
      line.setAttribute('class', 'network-link');
      line.setAttribute('marker-end', 'url(#arrowhead)');
      linkGroup.appendChild(line);
    }
  });

  // Draw nodes
  nodes.forEach(node => {
    const pos = nodePositions[node.id];
    if (!pos) return;

    const group = document.createElementNS(ns, 'g');
    group.setAttribute('class', `network-node ${node.type}`);
    group.setAttribute('transform', `translate(${pos.x}, ${pos.y})`);

    // Circle
    const circle = document.createElementNS(ns, 'circle');
    const radius = node.type === 'seed' ? 15 : 10;
    circle.setAttribute('r', radius);
    circle.setAttribute('class', `node-circle ${node.type}`);
    group.appendChild(circle);

    // Label
    const text = document.createElementNS(ns, 'text');
    text.setAttribute('dy', radius + 12);
    text.setAttribute('text-anchor', 'middle');
    text.setAttribute('class', 'node-label');
    text.textContent = node.title.substring(0, 20) + (node.title.length > 20 ? '...' : '');
    group.appendChild(text);

    // Click handler
    group.addEventListener('click', () => {
      onNodeSelect(node);
    });

    // Hover effect
    group.addEventListener('mouseenter', () => {
      circle.setAttribute('r', radius + 3);
    });

    group.addEventListener('mouseleave', () => {
      circle.setAttribute('r', radius);
    });

    nodeGroup.appendChild(group);
  });
}

export default CitationNetworkD3;
