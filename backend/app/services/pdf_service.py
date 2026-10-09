import io
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class PDFService:
    def extract_text_and_metadata(self, file_bytes: bytes, filename: str) -> Dict[str, Any]:
        """
        Extracts page-by-page text content and metadata from a PDF file using PyMuPDF / pypdf.
        Enforces magic byte validation and detects scanned/zero-text PDFs.
        """
        # 1. Security Check: Magic Bytes signature check (%PDF-)
        if not file_bytes or not file_bytes.startswith(b'%PDF'):
            raise ValueError("File signature check failed. The file is not a valid PDF document.")

        pages: List[Dict[str, Any]] = []
        page_count = 0
        extraction_method = "pymupdf"

        # 2. Attempt PyMuPDF (fitz) primary extraction
        try:
            import fitz
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            page_count = doc.page_count
            
            for i in range(page_count):
                page = doc.load_page(i)
                text = page.get_text("text") or ""
                cleaned_text = text.strip()
                pages.append({
                    "page_number": i + 1,
                    "text": cleaned_text,
                    "char_count": len(cleaned_text)
                })
            doc.close()
        except Exception as err_fitz:
            logger.warning(f"PyMuPDF extraction note: {err_fitz}. Falling back to pypdf.")
            # Fallback to pypdf if fitz encounters non-standard stream
            try:
                import pypdf
                reader = pypdf.PdfReader(io.BytesIO(file_bytes))
                page_count = len(reader.pages)
                extraction_method = "pypdf"
                
                for i, page in enumerate(reader.pages):
                    text = page.extract_text() or ""
                    cleaned_text = text.strip()
                    pages.append({
                        "page_number": i + 1,
                        "text": cleaned_text,
                        "char_count": len(cleaned_text)
                    })
            except Exception as err_pypdf:
                logger.error(f"Failed to parse PDF with both PyMuPDF and pypdf: {err_pypdf}")
                raise ValueError("Could not parse PDF content. The file may be corrupt or encrypted.")

        # 3. Detect Scanned / Zero-Text PDFs
        total_chars = sum(p["char_count"] for p in pages)
        full_text = "\n".join([p["text"] for p in pages if p["text"]])

        if total_chars < 10:
            status = "NO_TEXT_EXTRACTED"
            summary = f"No extractable text found in '{filename}'. PDF may be a scanned image or empty file requiring OCR."
        else:
            status = "PROCESSED"
            summary = full_text[:250] + "..." if len(full_text) > 250 else full_text

        return {
            "filename": filename,
            "file_size": len(file_bytes),
            "page_count": max(page_count, 1),
            "pages": pages,
            "total_chars": total_chars,
            "summary": summary,
            "status": status,
            "extraction_method": extraction_method
        }

pdf_service = PDFService()
