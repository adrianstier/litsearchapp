"""Visualization data generation service"""

from collections import Counter, defaultdict
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
import json

from src.database import models as db_models
from backend import schemas


def get_timeline_data(db: Session, collection_id: Optional[int] = None) -> schemas.TimelineResponse:
    """
    Generate timeline data for papers by year

    Args:
        db: Database session
        collection_id: Optional collection to filter by

    Returns:
        Timeline data with papers grouped by year
    """
    query = db.query(
        db_models.Paper.year,
        func.count(db_models.Paper.id).label('count'),
        func.group_concat(db_models.Paper.id).label('paper_ids')
    )

    if collection_id:
        query = query.join(db_models.Paper.collections).filter(
            db_models.Collection.id == collection_id
        )

    query = query.filter(db_models.Paper.year.isnot(None))
    query = query.group_by(db_models.Paper.year)
    query = query.order_by(db_models.Paper.year)

    results = query.all()

    timeline_data = []
    for year, count, paper_ids_str in results:
        paper_ids = [int(pid) for pid in paper_ids_str.split(',')] if paper_ids_str else []
        timeline_data.append(schemas.TimelineDataPoint(
            year=year,
            count=count,
            papers=paper_ids
        ))

    # Get year range
    years = [d.year for d in timeline_data]
    year_range = (min(years), max(years)) if years else (2000, 2024)

    return schemas.TimelineResponse(
        data=timeline_data,
        year_range=year_range
    )


def get_citation_network(db: Session, collection_id: Optional[int] = None) -> schemas.NetworkResponse:
    """
    Generate citation network data

    Creates a network where:
    - Nodes are papers
    - Links are based on shared authors, citations, or similar topics

    Args:
        db: Database session
        collection_id: Optional collection to filter by

    Returns:
        Network data with nodes and links
    """
    query = db.query(db_models.Paper)

    if collection_id:
        query = query.join(db_models.Paper.collections).filter(
            db_models.Collection.id == collection_id
        )

    papers = query.limit(100).all()  # Limit for performance

    nodes = []
    links = []
    paper_map = {}

    # Create nodes
    for paper in papers:
        node_id = f"paper_{paper.id}"
        paper_map[paper.id] = node_id

        # Determine group based on year decade
        decade = (paper.year // 10 * 10) if paper.year else 2020

        nodes.append(schemas.NetworkNode(
            id=node_id,
            label=paper.title[:50] + "..." if len(paper.title) > 50 else paper.title,
            size=min(paper.citations / 10 + 5, 30),  # Scale by citations
            group=str(decade)
        ))

    # Create links based on shared authors
    author_papers = defaultdict(list)
    for paper in papers:
        for author in paper.authors:
            author_papers[author.id].append(paper.id)

    # Connect papers with shared authors
    link_strengths = Counter()
    for author_id, paper_ids in author_papers.items():
        if len(paper_ids) > 1:
            # Create links between all papers by this author
            for i, pid1 in enumerate(paper_ids):
                for pid2 in paper_ids[i+1:]:
                    link_key = tuple(sorted([pid1, pid2]))
                    link_strengths[link_key] += 1

    # Add links
    for (pid1, pid2), strength in link_strengths.items():
        if pid1 in paper_map and pid2 in paper_map:
            links.append(schemas.NetworkLink(
                source=paper_map[pid1],
                target=paper_map[pid2],
                weight=min(strength / 2.0, 5.0)
            ))

    return schemas.NetworkResponse(
        nodes=nodes,
        links=links
    )


def get_topic_clusters(db: Session, collection_id: Optional[int] = None) -> schemas.TopicResponse:
    """
    Generate topic clustering data

    Groups papers by similar keywords/topics

    Args:
        db: Database session
        collection_id: Optional collection to filter by

    Returns:
        Topic clusters
    """
    query = db.query(db_models.Paper)

    if collection_id:
        query = query.join(db_models.Paper.collections).filter(
            db_models.Collection.id == collection_id
        )

    papers = query.all()

    # Extract keywords
    keyword_papers = defaultdict(list)
    for paper in papers:
        keywords = json.loads(paper.keywords or "[]")
        for keyword in keywords:
            keyword = keyword.lower().strip()
            if keyword:
                keyword_papers[keyword].append(paper.id)

    # Create clusters from most common keywords
    common_keywords = sorted(keyword_papers.items(), key=lambda x: len(x[1]), reverse=True)

    clusters = []
    used_papers = set()

    for cluster_id, (keyword, paper_ids) in enumerate(common_keywords[:10], 1):
        # Only include papers not already in a cluster
        unique_paper_ids = [pid for pid in paper_ids if pid not in used_papers]

        if len(unique_paper_ids) >= 2:  # At least 2 papers
            clusters.append(schemas.TopicCluster(
                cluster_id=cluster_id,
                label=keyword.title(),
                papers=unique_paper_ids[:20],  # Limit per cluster
                size=len(unique_paper_ids),
                keywords=[keyword]
            ))

            used_papers.update(unique_paper_ids)

    # Add "Other" cluster for remaining papers
    if len(used_papers) < len(papers):
        other_papers = [p.id for p in papers if p.id not in used_papers]
        clusters.append(schemas.TopicCluster(
            cluster_id=len(clusters) + 1,
            label="Other",
            papers=other_papers[:20],
            size=len(other_papers),
            keywords=[]
        ))

    return schemas.TopicResponse(
        clusters=clusters
    )


def get_author_network(db: Session, collection_id: Optional[int] = None) -> schemas.NetworkResponse:
    """
    Generate author collaboration network

    Args:
        db: Database session
        collection_id: Optional collection to filter by

    Returns:
        Network of authors and their collaborations
    """
    query = db.query(db_models.Paper)

    if collection_id:
        query = query.join(db_models.Paper.collections).filter(
            db_models.Collection.id == collection_id
        )

    papers = query.all()

    nodes = []
    links = []
    author_map = {}
    author_paper_count = Counter()

    # Count papers per author
    for paper in papers:
        for author in paper.authors:
            author_paper_count[author.id] += 1

    # Create author nodes
    seen_authors = set()
    for paper in papers:
        for author in paper.authors:
            if author.id not in seen_authors and author_paper_count[author.id] >= 2:
                node_id = f"author_{author.id}"
                author_map[author.id] = node_id

                nodes.append(schemas.NetworkNode(
                    id=node_id,
                    label=author.name,
                    size=min(author_paper_count[author.id] * 3, 30),
                    group="author"
                ))

                seen_authors.add(author.id)

    # Create collaboration links
    collab_strengths = Counter()
    for paper in papers:
        author_ids = [a.id for a in paper.authors if a.id in author_map]

        if len(author_ids) > 1:
            # Create links between all co-authors on this paper
            for i, aid1 in enumerate(author_ids):
                for aid2 in author_ids[i+1:]:
                    link_key = tuple(sorted([aid1, aid2]))
                    collab_strengths[link_key] += 1

    # Add collaboration links
    for (aid1, aid2), strength in collab_strengths.items():
        if aid1 in author_map and aid2 in author_map:
            links.append(schemas.NetworkLink(
                source=author_map[aid1],
                target=author_map[aid2],
                weight=min(strength, 5.0)
            ))

    return schemas.NetworkResponse(
        nodes=nodes,
        links=links
    )