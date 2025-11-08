"""Tests for PDF extraction service"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from backend.services.pdf_service import (
    extract_text_from_pdf,
    clean_extracted_text,
    extract_metadata_from_pdf,
    get_pdf_page_count
)


class TestPDFTextExtraction:
    """Test PDF text extraction"""

    @patch('backend.services.pdf_service.pymupdf')
    def test_extract_text_success(self, mock_pymupdf):
        """Test successful text extraction with PyMuPDF"""
        # Mock document
        mock_doc = MagicMock()
        mock_doc.__len__.return_value = 3

        # Mock pages
        mock_pages = [
            MagicMock(get_text=lambda: "Page 1 content"),
            MagicMock(get_text=lambda: "Page 2 content"),
            MagicMock(get_text=lambda: "Page 3 content")
        ]
        mock_doc.__getitem__ = lambda self, idx: mock_pages[idx]

        mock_pymupdf.open.return_value = mock_doc

        with patch('backend.services.pdf_service.Path.exists', return_value=True):
            text, page_count = extract_text_from_pdf("/fake/path.pdf")

        assert page_count == 3
        assert "Page 1 content" in text
        assert "Page 2 content" in text
        assert "Page 3 content" in text
        mock_doc.close.assert_called_once()

    def test_extract_text_file_not_found(self):
        """Test extraction with non-existent file"""
        with pytest.raises(FileNotFoundError):
            extract_text_from_pdf("/nonexistent/file.pdf")

    @patch('backend.services.pdf_service.pymupdf')
    def test_extract_text_empty_pdf(self, mock_pymupdf):
        """Test extraction from empty PDF"""
        mock_doc = MagicMock()
        mock_doc.__len__.return_value = 0
        mock_pymupdf.open.return_value = mock_doc

        with patch('backend.services.pdf_service.Path.exists', return_value=True):
            text, page_count = extract_text_from_pdf("/fake/empty.pdf")

        assert page_count == 0
        assert text == ""

    @patch('backend.services.pdf_service.pymupdf')
    def test_extract_text_single_page(self, mock_pymupdf):
        """Test extraction from single-page PDF"""
        mock_doc = MagicMock()
        mock_doc.__len__.return_value = 1
        mock_page = MagicMock(get_text=lambda: "Single page content")
        mock_doc.__getitem__ = lambda self, idx: mock_page
        mock_pymupdf.open.return_value = mock_doc

        with patch('backend.services.pdf_service.Path.exists', return_value=True):
            text, page_count = extract_text_from_pdf("/fake/single.pdf")

        assert page_count == 1
        assert "Single page content" in text

    @patch('backend.services.pdf_service.pymupdf', side_effect=ImportError)
    @patch('backend.services.pdf_service.PdfReader')
    def test_fallback_to_pypdf2(self, mock_reader_class, mock_pymupdf):
        """Test fallback to PyPDF2 when PyMuPDF not available"""
        mock_reader = MagicMock()
        mock_reader.pages = [
            MagicMock(extract_text=lambda: "Page 1"),
            MagicMock(extract_text=lambda: "Page 2")
        ]
        mock_reader.__len__ = lambda self: 2
        mock_reader_class.return_value = mock_reader

        text, page_count = extract_text_from_pdf("/fake/path.pdf")

        assert page_count == 2
        assert "Page 1" in text

    @patch('backend.services.pdf_service.pymupdf', side_effect=ImportError)
    def test_no_pdf_library_available(self, mock_pymupdf):
        """Test when neither PyMuPDF nor PyPDF2 is available"""
        with patch('backend.services.pdf_service.PdfReader', side_effect=ImportError):
            with pytest.raises(ImportError, match="Neither pymupdf nor PyPDF2"):
                extract_text_from_pdf("/fake/path.pdf")

    @patch('backend.services.pdf_service.pymupdf')
    def test_extract_text_with_unicode(self, mock_pymupdf):
        """Test extraction with unicode characters"""
        mock_doc = MagicMock()
        mock_doc.__len__.return_value = 1
        mock_page = MagicMock(get_text=lambda: "机器学习研究 α β γ")
        mock_doc.__getitem__ = lambda self, idx: mock_page
        mock_pymupdf.open.return_value = mock_doc

        with patch('backend.services.pdf_service.Path.exists', return_value=True):
            text, page_count = extract_text_from_pdf("/fake/unicode.pdf")

        assert "机器学习" in text
        assert "α" in text

    @patch('backend.services.pdf_service.pymupdf')
    def test_extract_text_large_document(self, mock_pymupdf):
        """Test extraction from large document"""
        mock_doc = MagicMock()
        mock_doc.__len__.return_value = 100
        mock_page = MagicMock(get_text=lambda: "Page content " * 100)
        mock_doc.__getitem__ = lambda self, idx: mock_page
        mock_pymupdf.open.return_value = mock_doc

        with patch('backend.services.pdf_service.Path.exists', return_value=True):
            text, page_count = extract_text_from_pdf("/fake/large.pdf")

        assert page_count == 100
        assert len(text) > 1000


class TestTextCleaning:
    """Test text cleaning utilities"""

    def test_clean_excessive_newlines(self):
        """Test removing excessive newlines"""
        text = "Line 1\n\n\n\nLine 2\n\n\n\n\n\nLine 3"
        cleaned = clean_extracted_text(text)

        assert "\n\n\n" not in cleaned
        assert "Line 1" in cleaned
        assert "Line 2" in cleaned

    def test_clean_page_numbers(self):
        """Test removing page numbers"""
        text = "Content 1\n\n1\n\nContent 2\n\n2\n\nContent 3"
        cleaned = clean_extracted_text(text)

        # Should remove standalone numbers
        assert cleaned.count("\n1\n") == 0

    def test_clean_excessive_spaces(self):
        """Test removing excessive spaces"""
        text = "Word1    Word2     Word3"
        cleaned = clean_extracted_text(text)

        assert "    " not in cleaned
        assert "Word1 Word2 Word3" in cleaned

    def test_clean_whitespace_edges(self):
        """Test trimming leading/trailing whitespace"""
        text = "\n\n   Content here   \n\n"
        cleaned = clean_extracted_text(text)

        assert cleaned == "Content here"

    def test_clean_empty_text(self):
        """Test cleaning empty text"""
        text = ""
        cleaned = clean_extracted_text(text)

        assert cleaned == ""

    def test_clean_whitespace_only(self):
        """Test cleaning whitespace-only text"""
        text = "   \n\n   \n   "
        cleaned = clean_extracted_text(text)

        assert cleaned == ""

    def test_clean_preserves_paragraphs(self):
        """Test that paragraph breaks are preserved"""
        text = "Paragraph 1\n\nParagraph 2\n\nParagraph 3"
        cleaned = clean_extracted_text(text)

        assert "Paragraph 1\n\nParagraph 2" in cleaned


class TestMetadataExtraction:
    """Test PDF metadata extraction"""

    @patch('backend.services.pdf_service.pymupdf')
    def test_extract_metadata_success(self, mock_pymupdf):
        """Test successful metadata extraction"""
        mock_doc = MagicMock()
        mock_doc.metadata = {
            'title': 'Test Paper',
            'author': 'John Doe',
            'subject': 'Machine Learning',
            'keywords': 'AI, ML, Deep Learning',
            'creator': 'LaTeX',
            'producer': 'pdfTeX',
            'creationDate': 'D:20230101',
            'modDate': 'D:20230102'
        }
        mock_pymupdf.open.return_value = mock_doc

        metadata = extract_metadata_from_pdf("/fake/path.pdf")

        assert metadata['title'] == 'Test Paper'
        assert metadata['author'] == 'John Doe'
        assert metadata['keywords'] == 'AI, ML, Deep Learning'

    @patch('backend.services.pdf_service.pymupdf')
    def test_extract_metadata_empty(self, mock_pymupdf):
        """Test extraction with empty metadata"""
        mock_doc = MagicMock()
        mock_doc.metadata = {}
        mock_pymupdf.open.return_value = mock_doc

        metadata = extract_metadata_from_pdf("/fake/path.pdf")

        assert metadata['title'] == ''
        assert metadata['author'] == ''

    @patch('backend.services.pdf_service.pymupdf', side_effect=ImportError)
    @patch('backend.services.pdf_service.PdfReader')
    def test_metadata_fallback_to_pypdf2(self, mock_reader_class, mock_pymupdf):
        """Test metadata extraction fallback to PyPDF2"""
        mock_reader = MagicMock()
        mock_reader.metadata = {
            '/Title': 'Test Title',
            '/Author': 'Test Author'
        }
        mock_reader_class.return_value = mock_reader

        metadata = extract_metadata_from_pdf("/fake/path.pdf")

        assert metadata['title'] == 'Test Title'
        assert metadata['author'] == 'Test Author'

    @patch('backend.services.pdf_service.pymupdf')
    def test_extract_metadata_error_handling(self, mock_pymupdf):
        """Test that errors return empty dict"""
        mock_pymupdf.open.side_effect = Exception("Error")

        metadata = extract_metadata_from_pdf("/fake/path.pdf")

        assert metadata == {}


class TestPageCount:
    """Test page count utility"""

    @patch('backend.services.pdf_service.pymupdf')
    def test_get_page_count_success(self, mock_pymupdf):
        """Test getting page count"""
        mock_doc = MagicMock()
        mock_doc.__len__.return_value = 42
        mock_pymupdf.open.return_value = mock_doc

        count = get_pdf_page_count("/fake/path.pdf")

        assert count == 42

    @patch('backend.services.pdf_service.pymupdf', side_effect=Exception)
    @patch('backend.services.pdf_service.PdfReader')
    def test_page_count_fallback(self, mock_reader_class, mock_pymupdf):
        """Test page count fallback to PyPDF2"""
        mock_reader = MagicMock()
        mock_reader.pages = [1, 2, 3, 4, 5]
        mock_reader.__len__ = lambda self: 5
        mock_reader_class.return_value = mock_reader

        count = get_pdf_page_count("/fake/path.pdf")

        assert count == 5

    @patch('backend.services.pdf_service.pymupdf', side_effect=Exception)
    def test_page_count_error(self, mock_pymupdf):
        """Test page count returns 0 on error"""
        with patch('backend.services.pdf_service.PdfReader', side_effect=Exception):
            count = get_pdf_page_count("/fake/path.pdf")
            assert count == 0

    @patch('backend.services.pdf_service.pymupdf')
    def test_page_count_zero(self, mock_pymupdf):
        """Test empty PDF"""
        mock_doc = MagicMock()
        mock_doc.__len__.return_value = 0
        mock_pymupdf.open.return_value = mock_doc

        count = get_pdf_page_count("/fake/path.pdf")

        assert count == 0


class TestEdgeCases:
    """Test edge cases in PDF processing"""

    @patch('backend.services.pdf_service.pymupdf')
    def test_corrupted_pdf_handling(self, mock_pymupdf):
        """Test handling of corrupted PDF"""
        mock_pymupdf.open.side_effect = Exception("Corrupted PDF")

        with pytest.raises(Exception, match="Failed to extract text"):
            extract_text_from_pdf("/fake/corrupted.pdf")

    @patch('backend.services.pdf_service.pymupdf')
    def test_pdf_with_images_only(self, mock_pymupdf):
        """Test PDF with only images (no text)"""
        mock_doc = MagicMock()
        mock_doc.__len__.return_value = 5
        mock_page = MagicMock(get_text=lambda: "")  # No text
        mock_doc.__getitem__ = lambda self, idx: mock_page
        mock_pymupdf.open.return_value = mock_doc

        with patch('backend.services.pdf_service.Path.exists', return_value=True):
            text, page_count = extract_text_from_pdf("/fake/images.pdf")

        assert page_count == 5
        assert text == ""

    def test_clean_text_with_special_formatting(self):
        """Test cleaning text with special formatting"""
        text = "Title\n\n\nAbstract: This is the abstract.\n\n1. Introduction\n\nContent here."
        cleaned = clean_extracted_text(text)

        assert "Title" in cleaned
        assert "Abstract:" in cleaned

    @patch('backend.services.pdf_service.pymupdf')
    def test_very_long_filename(self, mock_pymupdf):
        """Test with very long filename"""
        long_path = "/fake/" + "a" * 500 + ".pdf"
        mock_doc = MagicMock()
        mock_doc.__len__.return_value = 1
        mock_page = MagicMock(get_text=lambda: "Content")
        mock_doc.__getitem__ = lambda self, idx: mock_page
        mock_pymupdf.open.return_value = mock_doc

        with patch('backend.services.pdf_service.Path.exists', return_value=True):
            text, page_count = extract_text_from_pdf(long_path)

        assert "Content" in text
