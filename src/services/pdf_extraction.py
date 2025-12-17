"""Enhanced PDF text extraction service"""

import io
import os
import re
from pathlib import Path
from typing import Optional, Dict, Any
import requests
from pypdf import PdfReader

class PDFExtractionService:
    """Service for extracting text from PDFs with multiple methods"""

    def __init__(self):
        """Initialize PDF extraction service"""
        self._marker_available = False
        self._check_marker()

    def _check_marker(self):
        """Check if marker-pdf is available"""
        try:
            from marker.convert import convert_single_pdf
            self._marker_available = True
            print("✓ marker-pdf available for enhanced extraction")
        except ImportError:
            self._marker_available = False
            print("⚠ marker-pdf not available, using pypdf fallback")

    def extract_from_file(self, pdf_path: str, use_marker: bool = True) -> Dict[str, Any]:
        """
        Extract text from a PDF file

        Args:
            pdf_path: Path to PDF file
            use_marker: Use marker-pdf if available (better quality)

        Returns:
            Dict with extracted text and metadata
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        if use_marker and self._marker_available:
            return self._extract_with_marker(pdf_path)
        else:
            return self._extract_with_pypdf(pdf_path)

    def extract_from_url(self, url: str, use_marker: bool = True,
                        session: Optional[requests.Session] = None) -> Dict[str, Any]:
        """
        Download and extract text from PDF URL

        Args:
            url: URL to PDF
            use_marker: Use marker-pdf if available
            session: Optional requests session with auth

        Returns:
            Dict with extracted text and metadata
        """
        # Download PDF
        try:
            if session:
                response = session.get(url, timeout=60)
            else:
                response = requests.get(url, timeout=60, headers={
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'
                })

            response.raise_for_status()
            pdf_content = response.content

        except Exception as e:
            raise Exception(f"Failed to download PDF: {e}")

        # Save temporarily if using marker
        if use_marker and self._marker_available:
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
                f.write(pdf_content)
                temp_path = f.name

            try:
                result = self._extract_with_marker(temp_path)
            finally:
                os.unlink(temp_path)

            return result
        else:
            return self._extract_with_pypdf_bytes(pdf_content)

    def _extract_with_pypdf(self, pdf_path: str) -> Dict[str, Any]:
        """Extract using pypdf"""
        try:
            reader = PdfReader(pdf_path)
            text = ""
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n\n"

            # Clean up text
            text = self._clean_text(text)

            return {
                "text": text,
                "pages": len(reader.pages),
                "method": "pypdf",
                "metadata": reader.metadata if reader.metadata else {}
            }

        except Exception as e:
            raise Exception(f"pypdf extraction failed: {e}")

    def _extract_with_pypdf_bytes(self, pdf_bytes: bytes) -> Dict[str, Any]:
        """Extract from bytes using pypdf"""
        try:
            pdf_file = io.BytesIO(pdf_bytes)
            reader = PdfReader(pdf_file)

            text = ""
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n\n"

            text = self._clean_text(text)

            return {
                "text": text,
                "pages": len(reader.pages),
                "method": "pypdf",
                "metadata": reader.metadata if reader.metadata else {}
            }

        except Exception as e:
            raise Exception(f"pypdf extraction failed: {e}")

    def _extract_with_marker(self, pdf_path: str) -> Dict[str, Any]:
        """Extract using marker-pdf (better quality)"""
        try:
            from marker.convert import convert_single_pdf
            from marker.models import load_all_models

            # Load models (cached after first load)
            model_lst = load_all_models()

            # Convert PDF
            full_text, images, metadata = convert_single_pdf(
                pdf_path,
                model_lst
            )

            # Clean text
            text = self._clean_text(full_text)

            return {
                "text": text,
                "pages": metadata.get("pages", 0),
                "method": "marker",
                "metadata": metadata,
                "images": len(images) if images else 0
            }

        except Exception as e:
            print(f"⚠ marker extraction failed, falling back to pypdf: {e}")
            return self._extract_with_pypdf(pdf_path)

    def _clean_text(self, text: str) -> str:
        """Clean extracted text"""
        # Remove excessive whitespace
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r' {2,}', ' ', text)

        # Remove page numbers
        text = re.sub(r'\n\d+\n', '\n', text)

        # Fix common OCR issues
        text = text.replace('ﬁ', 'fi')
        text = text.replace('ﬂ', 'fl')
        text = text.replace('ﬀ', 'ff')

        # Remove headers/footers (common patterns)
        lines = text.split('\n')
        cleaned_lines = []
        for line in lines:
            # Skip very short lines that are likely headers/footers
            if len(line.strip()) < 3:
                continue
            # Skip lines that are just numbers
            if line.strip().isdigit():
                continue
            cleaned_lines.append(line)

        return '\n'.join(cleaned_lines).strip()

    def extract_sections(self, text: str) -> Dict[str, str]:
        """
        Extract common paper sections from text

        Args:
            text: Full paper text

        Returns:
            Dict mapping section names to content
        """
        sections = {}

        # Common section patterns
        section_patterns = [
            (r'(?i)abstract[:\s]*\n', 'abstract'),
            (r'(?i)introduction[:\s]*\n', 'introduction'),
            (r'(?i)methods?[:\s]*\n|(?i)materials?\s+and\s+methods?', 'methods'),
            (r'(?i)results?[:\s]*\n', 'results'),
            (r'(?i)discussion[:\s]*\n', 'discussion'),
            (r'(?i)conclusion[s]?[:\s]*\n', 'conclusion'),
            (r'(?i)references?[:\s]*\n|(?i)bibliography', 'references'),
        ]

        # Find section boundaries
        boundaries = []
        for pattern, name in section_patterns:
            match = re.search(pattern, text)
            if match:
                boundaries.append((match.start(), match.end(), name))

        # Sort by position
        boundaries.sort(key=lambda x: x[0])

        # Extract section content
        for i, (start, end, name) in enumerate(boundaries):
            # End of section is start of next section or end of text
            if i + 1 < len(boundaries):
                section_end = boundaries[i + 1][0]
            else:
                section_end = len(text)

            section_text = text[end:section_end].strip()

            # Clean up section text
            section_text = re.sub(r'\n{3,}', '\n\n', section_text)

            sections[name] = section_text

        return sections

    def get_paper_info(self, text: str) -> Dict[str, Any]:
        """
        Extract paper metadata from text

        Args:
            text: Full paper text

        Returns:
            Dict with title, authors, etc.
        """
        info = {}

        # Try to extract title (usually first substantial line)
        lines = text.split('\n')
        for line in lines[:10]:
            line = line.strip()
            if len(line) > 20 and not line.isupper():
                info['title'] = line
                break

        # Extract DOI
        doi_match = re.search(r'10\.\d{4,}/[^\s]+', text)
        if doi_match:
            info['doi'] = doi_match.group(0).rstrip('.,;')

        # Extract year
        year_match = re.search(r'\b(19|20)\d{2}\b', text[:2000])
        if year_match:
            info['year'] = int(year_match.group(0))

        return info


# Global instance
_pdf_service = None

def get_pdf_service() -> PDFExtractionService:
    """Get or create PDF extraction service singleton"""
    global _pdf_service
    if _pdf_service is None:
        _pdf_service = PDFExtractionService()
    return _pdf_service
