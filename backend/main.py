"""FastAPI backend for Literature Search Application"""

from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from pathlib import Path
import json

from src.database.engine import get_db_session, init_db
from src.database import models as db_models
from src.models import SearchQuery as SearchQueryModel, Source
from src.search.orchestrator import SearchOrchestrator
from src.retrieval.pdf_retriever import PDFRetriever
from src.auth.ucsb_auth import UCSBAuth

from . import schemas
from .services import paper_service, pdf_service, visualization_service

# Initialize FastAPI
app = FastAPI(
    title="Literature Search API",
    description="API for academic literature search and management",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vite and React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()
    print("✓ FastAPI server started")


# =============================================================================
# SEARCH ENDPOINTS
# =============================================================================

@app.post("/api/search", response_model=schemas.SearchResultResponse)
async def search_papers(
    query: schemas.SearchRequest,
    db: Session = Depends(get_db_session)
):
    """Execute a literature search"""
    try:
        # Convert to internal search query
        search_query = SearchQueryModel(
            query=query.query,
            sources=[Source(s) for s in query.sources],
            max_results=query.max_results,
            year_start=query.year_start,
            year_end=query.year_end
        )

        # Try to load UCSB auth for enhanced access to Scholar and WoS
        ucsb_auth = UCSBAuth()
        ucsb_session = None
        if ucsb_auth.load_session():
            ucsb_session = ucsb_auth.get_session()

        # Execute search with UCSB session if available
        orchestrator = SearchOrchestrator(ucsb_session=ucsb_session)
        results = orchestrator.search(search_query)

        # Save to database
        saved_papers = []
        for paper in results.papers:
            db_paper = paper_service.save_paper(db, paper)
            saved_papers.append(db_paper)

        # Save search history
        search_history = db_models.SearchHistory(
            query=query.query,
            sources=json.dumps(query.sources),
            filters=json.dumps({
                "year_start": query.year_start,
                "year_end": query.year_end
            }),
            results_count=len(results.papers)
        )
        db.add(search_history)
        db.commit()

        return {
            "papers": [paper_service.paper_to_schema(p) for p in saved_papers],
            "total_found": results.total_found,
            "search_time": results.search_time,
            "sources_searched": [s.value for s in results.sources_searched],
            "statistics": results.get_statistics()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/search/history", response_model=List[schemas.SearchHistoryItem])
async def get_search_history(
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db_session)
):
    """Get search history"""
    history = db.query(db_models.SearchHistory)\
        .order_by(db_models.SearchHistory.searched_at.desc())\
        .limit(limit)\
        .all()

    return history


# =============================================================================
# PAPER ENDPOINTS
# =============================================================================

@app.get("/api/papers", response_model=schemas.PaperListResponse)
async def list_papers(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    collection_id: Optional[int] = None,
    tag: Optional[str] = None,
    year: Optional[int] = None,
    db: Session = Depends(get_db_session)
):
    """List papers with pagination and filters"""
    query = db.query(db_models.Paper)

    # Apply filters
    if collection_id:
        query = query.filter(db_models.Paper.collections.any(id=collection_id))
    if tag:
        query = query.filter(db_models.Paper.tags.any(name=tag))
    if year:
        query = query.filter(db_models.Paper.year == year)

    # Pagination
    total = query.count()
    papers = query.order_by(db_models.Paper.created_at.desc())\
        .offset((page - 1) * page_size)\
        .limit(page_size)\
        .all()

    return {
        "papers": [paper_service.paper_to_schema(p) for p in papers],
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": (total + page_size - 1) // page_size
    }


@app.get("/api/papers/{paper_id}", response_model=schemas.Paper)
async def get_paper(paper_id: int, db: Session = Depends(get_db_session)):
    """Get paper details"""
    paper = db.query(db_models.Paper).filter(db_models.Paper.id == paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    return paper_service.paper_to_schema(paper)


@app.delete("/api/papers/{paper_id}")
async def delete_paper(paper_id: int, db: Session = Depends(get_db_session)):
    """Delete a paper"""
    paper = db.query(db_models.Paper).filter(db_models.Paper.id == paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")

    db.delete(paper)
    db.commit()
    return {"message": "Paper deleted"}


@app.get("/api/papers/{paper_id}/pdf")
async def get_paper_pdf(paper_id: int, db: Session = Depends(get_db_session)):
    """Get paper PDF"""
    paper = db.query(db_models.Paper).filter(db_models.Paper.id == paper_id).first()
    if not paper or not paper.local_pdf_path:
        raise HTTPException(status_code=404, detail="PDF not found")

    pdf_path = Path(paper.local_pdf_path)
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="PDF file not found")

    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=pdf_path.name
    )


@app.post("/api/papers/{paper_id}/extract-text")
async def extract_pdf_text(paper_id: int, db: Session = Depends(get_db_session)):
    """Extract text from PDF"""
    paper = db.query(db_models.Paper).filter(db_models.Paper.id == paper_id).first()
    if not paper or not paper.local_pdf_path:
        raise HTTPException(status_code=404, detail="PDF not found")

    text, page_count = pdf_service.extract_text_from_pdf(paper.local_pdf_path)

    # Save to database
    pdf_content = db.query(db_models.PDFContent)\
        .filter(db_models.PDFContent.paper_id == paper_id)\
        .first()

    if pdf_content:
        pdf_content.full_text = text
        pdf_content.page_count = page_count
    else:
        pdf_content = db_models.PDFContent(
            paper_id=paper_id,
            full_text=text,
            page_count=page_count
        )
        db.add(pdf_content)

    db.commit()

    return {"message": "Text extracted", "page_count": page_count, "text_length": len(text)}


@app.get("/api/papers/search")
async def full_text_search(
    q: str = Query(..., min_length=1),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db_session)
):
    """Full-text search across papers and PDFs"""
    results = paper_service.full_text_search(db, q, limit)
    return {"results": [paper_service.paper_to_schema(p) for p in results]}


# =============================================================================
# DOWNLOAD ENDPOINTS
# =============================================================================

@app.post("/api/download/{paper_id}")
async def download_paper(paper_id: int, db: Session = Depends(get_db_session)):
    """Download PDF for a paper"""
    paper_db = db.query(db_models.Paper).filter(db_models.Paper.id == paper_id).first()
    if not paper_db:
        raise HTTPException(status_code=404, detail="Paper not found")

    # Convert to Paper model
    paper = paper_service.db_to_paper_model(paper_db)

    # Try to load UCSB auth
    ucsb_auth = UCSBAuth()
    ucsb_session = None
    if ucsb_auth.load_session():
        ucsb_session = ucsb_auth.get_session()

    # Download
    retriever = PDFRetriever(ucsb_session=ucsb_session)
    success, result = retriever.download_paper(paper)

    if success:
        # Update database
        paper_db.local_pdf_path = result
        db.commit()
        return {"success": True, "path": result}
    else:
        return {"success": False, "error": result}


@app.post("/api/download/batch")
async def batch_download(
    paper_ids: List[int],
    db: Session = Depends(get_db_session)
):
    """Batch download PDFs"""
    papers = db.query(db_models.Paper).filter(db_models.Paper.id.in_(paper_ids)).all()

    # Convert to Paper models
    paper_models = [paper_service.db_to_paper_model(p) for p in papers]

    # Try to load UCSB auth
    ucsb_auth = UCSBAuth()
    ucsb_session = None
    if ucsb_auth.load_session():
        ucsb_session = ucsb_auth.get_session()

    # Download
    retriever = PDFRetriever(ucsb_session=ucsb_session)
    results = retriever.download_papers(paper_models)

    # Update database
    for item in results['successful']:
        paper_db = next((p for p in papers if p.title == item['paper'].title), None)
        if paper_db:
            paper_db.local_pdf_path = item['filepath']

    db.commit()

    return {
        "successful": len(results['successful']),
        "failed": len(results['failed']),
        "total": len(paper_ids)
    }


# =============================================================================
# COLLECTIONS ENDPOINTS
# =============================================================================

@app.get("/api/collections", response_model=List[schemas.Collection])
async def list_collections(db: Session = Depends(get_db_session)):
    """List all collections"""
    collections = db.query(db_models.Collection).all()
    return collections


@app.post("/api/collections", response_model=schemas.Collection)
async def create_collection(
    collection: schemas.CollectionCreate,
    db: Session = Depends(get_db_session)
):
    """Create a new collection"""
    db_collection = db_models.Collection(
        name=collection.name,
        description=collection.description
    )
    db.add(db_collection)
    db.commit()
    db.refresh(db_collection)
    return db_collection


@app.post("/api/collections/{collection_id}/papers/{paper_id}")
async def add_paper_to_collection(
    collection_id: int,
    paper_id: int,
    db: Session = Depends(get_db_session)
):
    """Add paper to collection"""
    collection = db.query(db_models.Collection).filter(db_models.Collection.id == collection_id).first()
    paper = db.query(db_models.Paper).filter(db_models.Paper.id == paper_id).first()

    if not collection or not paper:
        raise HTTPException(status_code=404, detail="Collection or paper not found")

    if paper not in collection.papers:
        collection.papers.append(paper)
        db.commit()

    return {"message": "Paper added to collection"}


# =============================================================================
# VISUALIZATION ENDPOINTS
# =============================================================================

@app.get("/api/visualize/timeline")
async def get_timeline_data(
    collection_id: Optional[int] = None,
    db: Session = Depends(get_db_session)
):
    """Get timeline visualization data"""
    return visualization_service.get_timeline_data(db, collection_id)


@app.get("/api/visualize/network")
async def get_citation_network(
    collection_id: Optional[int] = None,
    db: Session = Depends(get_db_session)
):
    """Get citation network data"""
    return visualization_service.get_citation_network(db, collection_id)


@app.get("/api/visualize/topics")
async def get_topic_clusters(
    collection_id: Optional[int] = None,
    db: Session = Depends(get_db_session)
):
    """Get topic clustering data"""
    return visualization_service.get_topic_clusters(db, collection_id)


# =============================================================================
# AUTH ENDPOINTS
# =============================================================================

@app.post("/api/auth/import-cookies")
async def import_cookies(file: UploadFile = File(...)):
    """Import UCSB cookies"""
    import tempfile

    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = Path(tmp.name)

    try:
        ucsb_auth = UCSBAuth()
        success = ucsb_auth.import_cookies_netscape(tmp_path)

        return {
            "success": success,
            "message": "Cookies imported successfully" if success else "Failed to import cookies"
        }
    finally:
        tmp_path.unlink()


@app.get("/api/auth/status")
async def auth_status():
    """Get UCSB authentication status"""
    ucsb_auth = UCSBAuth()
    ucsb_auth.load_session()
    return ucsb_auth.get_status()


@app.delete("/api/auth/clear")
async def clear_auth():
    """Clear UCSB authentication"""
    ucsb_auth = UCSBAuth()
    ucsb_auth.clear_session()
    return {"message": "Authentication cleared"}


# =============================================================================
# STATS ENDPOINT
# =============================================================================

@app.get("/api/stats")
async def get_stats(db: Session = Depends(get_db_session)):
    """Get application statistics"""
    total_papers = db.query(db_models.Paper).count()
    total_pdfs = db.query(db_models.Paper).filter(db_models.Paper.local_pdf_path.isnot(None)).count()
    total_collections = db.query(db_models.Collection).count()
    total_searches = db.query(db_models.SearchHistory).count()

    return {
        "total_papers": total_papers,
        "total_pdfs": total_pdfs,
        "total_collections": total_collections,
        "total_searches": total_searches,
        "pdf_percentage": (total_pdfs / total_papers * 100) if total_papers > 0 else 0
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)