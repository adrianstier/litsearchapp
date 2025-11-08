"""PDF text extraction service"""

from pathlib import Path
from typing import Tuple
import re


def extract_text_from_pdf(pdf_path: str) -> Tuple[str, int]:
    """
    Extract text from PDF file

    Args:
        pdf_path: Path to PDF file

    Returns:
        Tuple of (extracted_text, page_count)
    """
    try:
        import pymupdf  # PyMuPDF (fitz)

        pdf_file = Path(pdf_path)
        if not pdf_file.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        doc = pymupdf.open(pdf_file)
        text_parts = []
        page_count = len(doc)

        for page_num in range(page_count):
            page = doc[page_num]
            text = page.get_text()
            text_parts.append(text)

        doc.close()

        # Combine all pages
        full_text = "\n\n".join(text_parts)

        # Clean up text
        full_text = clean_extracted_text(full_text)

        return full_text, page_count

    except ImportError:
        # Fallback to PyPDF2 if pymupdf not available
        try:
            from PyPDF2 import PdfReader

            reader = PdfReader(pdf_path)
            text_parts = []
            page_count = len(reader.pages)

            for page in reader.pages:
                text = page.extract_text()
                text_parts.append(text)

            full_text = "\n\n".join(text_parts)
            full_text = clean_extracted_text(full_text)

            return full_text, page_count

        except ImportError:
            raise ImportError("Neither pymupdf nor PyPDF2 is installed. Install with: pip install pymupdf")

    except Exception as e:
        raise Exception(f"Failed to extract text from PDF: {e}")


def clean_extracted_text(text: str) -> str:
    """
    Clean extracted text

    Args:
        text: Raw extracted text

    Returns:
        Cleaned text
    """
    # Remove excessive whitespace
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)

    # Remove page numbers (common pattern)
    text = re.sub(r'\n\s*\d+\s*\n', '\n', text)

    # Remove excessive spaces
    text = re.sub(r' +', ' ', text)

    # Strip leading/trailing whitespace
    text = text.strip()

    return text


def extract_metadata_from_pdf(pdf_path: str) -> dict:
    """
    Extract metadata from PDF

    Args:
        pdf_path: Path to PDF file

    Returns:
        Dictionary of metadata
    """
    try:
        import pymupdf

        doc = pymupdf.open(pdf_path)
        metadata = doc.metadata

        doc.close()

        return {
            'title': metadata.get('title', ''),
            'author': metadata.get('author', ''),
            'subject': metadata.get('subject', ''),
            'keywords': metadata.get('keywords', ''),
            'creator': metadata.get('creator', ''),
            'producer': metadata.get('producer', ''),
            'creation_date': metadata.get('creationDate', ''),
            'mod_date': metadata.get('modDate', '')
        }

    except ImportError:
        try:
            from PyPDF2 import PdfReader

            reader = PdfReader(pdf_path)
            metadata = reader.metadata

            return {
                'title': metadata.get('/Title', ''),
                'author': metadata.get('/Author', ''),
                'subject': metadata.get('/Subject', ''),
                'keywords': metadata.get('/Keywords', ''),
                'creator': metadata.get('/Creator', ''),
                'producer': metadata.get('/Producer', ''),
                'creation_date': metadata.get('/CreationDate', ''),
                'mod_date': metadata.get('/ModDate', '')
            }

        except ImportError:
            return {}

    except Exception:
        return {}


def get_pdf_page_count(pdf_path: str) -> int:
    """Get number of pages in PDF"""
    try:
        import pymupdf
        doc = pymupdf.open(pdf_path)
        count = len(doc)
        doc.close()
        return count
    except:
        try:
            from PyPDF2 import PdfReader
            reader = PdfReader(pdf_path)
            return len(reader.pages)
        except:
            return 0