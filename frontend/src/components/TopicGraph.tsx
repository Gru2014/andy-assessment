import { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';
import type { TopicGraph, TopicNode } from '../api/client';

interface TopicGraphProps {
  graph: TopicGraph;
  onNodeClick: (nodeId: string) => void;
  width?: number;
  height?: number;
}

type SimulationNode = TopicNode & d3.SimulationNodeDatum;
interface SimulationEdge {
  source: SimulationNode;
  target: SimulationNode;
  weight: number;
  type: string;
}

export const TopicGraphComponent: React.FC<TopicGraphProps> = ({
  graph,
  onNodeClick,
  width = 1200,
  height = 800,
}) => {
  const svgRef = useRef<SVGSVGElement>(null);
  const [selectedNode, setSelectedNode] = useState<string | null>(null);

  useEffect(() => {
    if (!svgRef.current || !graph.nodes.length) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();

    const nodes: SimulationNode[] = graph.nodes.map((node) => ({ ...node }));
    const nodeMap = new Map<string, SimulationNode>(nodes.map((n) => [n.id, n]));
    const edges: SimulationEdge[] = graph.edges
      .map((edge) => {
        const source = nodeMap.get(edge.source);
        const target = nodeMap.get(edge.target);
        if (!source || !target) return null;
        return {
          source,
          target,
          weight: edge.weight,
          type: edge.type,
        } as SimulationEdge;
      })
      .filter((edge): edge is SimulationEdge => edge !== null);

    const simulation = d3
      .forceSimulation<SimulationNode>(nodes)
      .force(
        'link',
        d3
          .forceLink<SimulationNode, SimulationEdge>(edges)
          .id((d) => d.id)
          .distance((d) => 200 - d.weight * 100)
      )
      .force('charge', d3.forceManyBody<SimulationNode>().strength(-300))
      .force('center', d3.forceCenter<SimulationNode>(width / 2, height / 2))
      .force('collision', d3.forceCollide<SimulationNode>().radius(50));

    // Create links
    const link = svg
      .append('g')
      .attr('class', 'links')
      .selectAll<SVGLineElement, SimulationEdge>('line')
      .data(edges)
      .enter()
      .append('line')
      .attr('stroke', '#999')
      .attr('stroke-opacity', 0.6)
      .attr('stroke-width', (d) => Math.sqrt(d.weight) * 3);

    // Create nodes
    const node = svg
      .append('g')
      .attr('class', 'nodes')
      .selectAll<SVGCircleElement, SimulationNode>('circle')
      .data(nodes)
      .enter()
      .append('circle')
      .attr('r', (d) => 10 + d.size_score * 20)
      .attr('fill', (d) => d.color || '#3498db')
      .attr('stroke', '#fff')
      .attr('stroke-width', 2)
      .style('cursor', 'pointer')
      .on('click', (_, d) => {
        setSelectedNode(d.id);
        onNodeClick(d.id);
      })
      .call(
        d3
          .drag<SVGCircleElement, SimulationNode>()
          .on('start', (event, d) => {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
          })
          .on('drag', (event, d) => {
            d.fx = event.x;
            d.fy = event.y;
          })
          .on('end', (event, d) => {
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
          })
      );

    // Add labels
    const labels = svg
      .append('g')
      .attr('class', 'labels')
      .selectAll<SVGTextElement, SimulationNode>('text')
      .data(nodes)
      .enter()
      .append('text')
      .text((d) => d.label)
      .attr('font-size', '12px')
      .attr('dx', 15)
      .attr('dy', 4)
      .style('pointer-events', 'none')
      .style('fill', '#333');

    // Update positions on simulation tick
    simulation.on('tick', () => {
      link
        .attr('x1', (d) => {
          const source = d.source as SimulationNode;
          return source.x ?? 0;
        })
        .attr('y1', (d) => {
          const source = d.source as SimulationNode;
          return source.y ?? 0;
        })
        .attr('x2', (d) => {
          const target = d.target as SimulationNode;
          return target.x ?? 0;
        })
        .attr('y2', (d) => {
          const target = d.target as SimulationNode;
          return target.y ?? 0;
        });

      node
        .attr('cx', (d) => d.x ?? 0)
        .attr('cy', (d) => d.y ?? 0);

      labels
        .attr('x', (d) => d.x ?? 0)
        .attr('y', (d) => d.y ?? 0);
    });

    // Highlight selected node
    if (selectedNode) {
      node
        .filter((d) => d.id === selectedNode)
        .attr('stroke', '#ff6b6b')
        .attr('stroke-width', 4);
    }

    return () => {
      simulation.stop();
    };
  }, [graph, width, height, selectedNode, onNodeClick]);

  return (
    <div className="w-full h-full border border-gray-300 rounded-lg overflow-hidden bg-white">
      <svg ref={svgRef} width={width} height={height}></svg>
    </div>
  );
};

