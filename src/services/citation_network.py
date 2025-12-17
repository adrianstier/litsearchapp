"""Citation network analysis service"""

import networkx as nx
from typing import List, Dict, Any, Optional, Tuple
import json

class CitationNetworkService:
    """Service for building and analyzing citation networks"""

    def __init__(self):
        """Initialize citation network service"""
        pass

    def build_network(self, papers: List[Dict],
                     citations_data: Dict[str, List[str]],
                     references_data: Dict[str, List[str]]) -> nx.DiGraph:
        """
        Build a citation network from papers and their citations/references

        Args:
            papers: List of paper dictionaries with 'id' or 'paper_id'
            citations_data: Dict mapping paper_id to list of citing paper_ids
            references_data: Dict mapping paper_id to list of reference paper_ids

        Returns:
            NetworkX directed graph
        """
        G = nx.DiGraph()

        # Add all papers as nodes
        for paper in papers:
            paper_id = paper.get('id') or paper.get('paper_id')
            G.add_node(paper_id, **{
                'title': paper.get('title', 'Unknown'),
                'year': paper.get('year'),
                'citations': paper.get('citations', 0),
                'authors': paper.get('authors', []),
            })

        # Add citation edges (paper -> cited_by)
        for paper_id, citing_ids in citations_data.items():
            for citing_id in citing_ids:
                G.add_edge(citing_id, paper_id)  # citing -> cited

        # Add reference edges (paper -> references)
        for paper_id, ref_ids in references_data.items():
            for ref_id in ref_ids:
                G.add_edge(paper_id, ref_id)  # paper -> reference

        return G

    def get_network_stats(self, G: nx.DiGraph) -> Dict[str, Any]:
        """
        Calculate network statistics

        Args:
            G: NetworkX graph

        Returns:
            Dict with network statistics
        """
        if len(G.nodes()) == 0:
            return {
                'nodes': 0,
                'edges': 0,
                'density': 0,
                'components': 0
            }

        stats = {
            'nodes': G.number_of_nodes(),
            'edges': G.number_of_edges(),
            'density': nx.density(G),
            'components': nx.number_weakly_connected_components(G),
        }

        # Degree statistics
        in_degrees = [d for n, d in G.in_degree()]
        out_degrees = [d for n, d in G.out_degree()]

        if in_degrees:
            stats['avg_in_degree'] = sum(in_degrees) / len(in_degrees)
            stats['max_in_degree'] = max(in_degrees)

        if out_degrees:
            stats['avg_out_degree'] = sum(out_degrees) / len(out_degrees)
            stats['max_out_degree'] = max(out_degrees)

        return stats

    def find_key_papers(self, G: nx.DiGraph, top_k: int = 10) -> List[Tuple[str, float]]:
        """
        Find key papers using PageRank

        Args:
            G: NetworkX graph
            top_k: Number of top papers to return

        Returns:
            List of (paper_id, pagerank_score) tuples
        """
        if len(G.nodes()) == 0:
            return []

        try:
            pagerank = nx.pagerank(G)
            sorted_papers = sorted(pagerank.items(), key=lambda x: x[1], reverse=True)
            return sorted_papers[:top_k]
        except Exception as e:
            print(f"⚠ PageRank calculation failed: {e}")
            return []

    def find_clusters(self, G: nx.DiGraph) -> List[List[str]]:
        """
        Find paper clusters using community detection

        Args:
            G: NetworkX graph

        Returns:
            List of clusters (each cluster is list of paper_ids)
        """
        if len(G.nodes()) == 0:
            return []

        try:
            # Convert to undirected for community detection
            G_undirected = G.to_undirected()

            # Use greedy modularity
            from networkx.algorithms.community import greedy_modularity_communities
            communities = greedy_modularity_communities(G_undirected)

            return [list(c) for c in communities]
        except Exception as e:
            print(f"⚠ Clustering failed: {e}")
            return []

    def get_paper_context(self, G: nx.DiGraph, paper_id: str,
                        depth: int = 1) -> Dict[str, Any]:
        """
        Get citation context for a paper

        Args:
            G: NetworkX graph
            paper_id: Paper to analyze
            depth: How many hops to include

        Returns:
            Dict with papers that cite this one and papers it cites
        """
        if paper_id not in G:
            return {'cites': [], 'cited_by': [], 'co_cited': []}

        # Papers this one cites (references)
        cites = list(G.successors(paper_id))

        # Papers that cite this one
        cited_by = list(G.predecessors(paper_id))

        # Co-cited papers (papers that appear together in references)
        co_cited = set()
        for citing_paper in cited_by:
            # Other papers cited by the same citing paper
            other_refs = set(G.successors(citing_paper))
            other_refs.discard(paper_id)
            co_cited.update(other_refs)

        return {
            'cites': cites,
            'cited_by': cited_by,
            'co_cited': list(co_cited)
        }

    def to_d3_format(self, G: nx.DiGraph,
                    include_all_nodes: bool = False) -> Dict[str, Any]:
        """
        Convert graph to D3.js format for visualization

        Args:
            G: NetworkX graph
            include_all_nodes: Include nodes without edges

        Returns:
            Dict with 'nodes' and 'links' for D3
        """
        nodes = []
        links = []

        # Collect nodes with edges or all nodes
        if include_all_nodes:
            node_ids = set(G.nodes())
        else:
            node_ids = set()
            for u, v in G.edges():
                node_ids.add(u)
                node_ids.add(v)

        # Build node list
        for node_id in node_ids:
            node_data = G.nodes.get(node_id, {})
            nodes.append({
                'id': node_id,
                'title': node_data.get('title', 'Unknown'),
                'year': node_data.get('year'),
                'citations': node_data.get('citations', 0),
                'in_degree': G.in_degree(node_id),
                'out_degree': G.out_degree(node_id),
            })

        # Build link list
        for source, target in G.edges():
            if source in node_ids and target in node_ids:
                links.append({
                    'source': source,
                    'target': target
                })

        return {
            'nodes': nodes,
            'links': links
        }

    def get_citation_path(self, G: nx.DiGraph,
                         source_id: str, target_id: str) -> List[str]:
        """
        Find citation path between two papers

        Args:
            G: NetworkX graph
            source_id: Starting paper
            target_id: Target paper

        Returns:
            List of paper_ids in the path
        """
        try:
            path = nx.shortest_path(G, source_id, target_id)
            return path
        except nx.NetworkXNoPath:
            return []
        except Exception as e:
            print(f"⚠ Path finding failed: {e}")
            return []

    def get_temporal_analysis(self, G: nx.DiGraph) -> Dict[str, Any]:
        """
        Analyze citation network over time

        Args:
            G: NetworkX graph

        Returns:
            Dict with temporal statistics
        """
        papers_by_year = {}

        for node_id in G.nodes():
            year = G.nodes[node_id].get('year')
            if year:
                if year not in papers_by_year:
                    papers_by_year[year] = []
                papers_by_year[year].append(node_id)

        # Calculate citations per year
        citations_by_year = {}
        for year, paper_ids in papers_by_year.items():
            total_citations = sum(
                G.in_degree(pid) for pid in paper_ids
            )
            citations_by_year[year] = {
                'papers': len(paper_ids),
                'citations': total_citations,
                'avg_citations': total_citations / len(paper_ids) if paper_ids else 0
            }

        return {
            'by_year': citations_by_year,
            'years': sorted(papers_by_year.keys())
        }

    def find_bridge_papers(self, G: nx.DiGraph, top_k: int = 5) -> List[Tuple[str, float]]:
        """
        Find papers that bridge different research areas

        Args:
            G: NetworkX graph
            top_k: Number of bridge papers to return

        Returns:
            List of (paper_id, betweenness_score) tuples
        """
        if len(G.nodes()) < 3:
            return []

        try:
            betweenness = nx.betweenness_centrality(G)
            sorted_papers = sorted(betweenness.items(), key=lambda x: x[1], reverse=True)
            return sorted_papers[:top_k]
        except Exception as e:
            print(f"⚠ Betweenness calculation failed: {e}")
            return []


# Global instance
_network_service = None

def get_network_service() -> CitationNetworkService:
    """Get or create citation network service singleton"""
    global _network_service
    if _network_service is None:
        _network_service = CitationNetworkService()
    return _network_service
