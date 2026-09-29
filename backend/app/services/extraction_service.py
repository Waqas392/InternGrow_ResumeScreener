import io
import fitz
from docx import Document
from app.core.exceptions import ProcessingException, ValidationException
from app.ai.ocr_fallback import extract_text_with_ocr
from app.ai.nlp_extractor import NLPExtractor

class ExtractionService:
    def __init__(self):
        self.extractor = NLPExtractor()

    def extract_text(self, filename: str, content: bytes) -> str:
        lowered_name = filename.lower()

        if lowered_name.endswith(".pdf"):
            return self.extract_pdf_text(content)

        if lowered_name.endswith(".docx"):
            return self.extract_docx_text(content)

        raise ValidationException(detail="Only PDF and DOCX files are supported")

    def extract_pdf_text(self, content: bytes) -> str:
        try:
            document = fitz.open(stream=content, filetype="pdf")
            text_parts = []

            for page_index in range(document.page_count):
                page = document.load_page(page_index)
                text_parts.append(page.get_text("text"))

            document.close()
            full_text = "\n".join(text_parts)

            if len(full_text.strip()) < 50:
                return extract_text_with_ocr(content)

            return full_text
        except ProcessingException:
            raise
        except Exception as error:
            raise ProcessingException(detail=f"PDF extraction failed: {str(error)}")

    def extract_docx_text(self, content: bytes) -> str:
        try:
            document = Document(io.BytesIO(content))
            paragraphs = [paragraph.text for paragraph in document.paragraphs if paragraph.text.strip()]
            return "\n".join(paragraphs)
        except Exception as error:
            raise ProcessingException(detail=f"DOCX extraction failed: {str(error)}")

    def extract_resume(self, filename: str, content: bytes) -> tuple[str, dict]:
        raw_text = self.extract_text(filename, content)

        if not raw_text.strip():
            raise ProcessingException(detail="No readable text found in resume")

        profile = self.extractor.extract_profile(raw_text)
        return raw_text, profile
