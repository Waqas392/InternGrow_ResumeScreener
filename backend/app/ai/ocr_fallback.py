import fitz
import pytesseract
from PIL import Image
from app.core.exceptions import ProcessingException

def extract_text_with_ocr(pdf_bytes: bytes) -> str:
    try:
        document = fitz.open(stream=pdf_bytes, filetype="pdf")
        extracted_pages = []

        for page_index in range(document.page_count):
            page = document.load_page(page_index)
            page_text = page.get_text("text")

            if len(page_text.strip()) < 20:
                zoom = 200 / 72
                matrix = fitz.Matrix(zoom, zoom)
                pixmap = page.get_pixmap(matrix=matrix)
                image_mode = "RGBA" if pixmap.alpha else "RGB"
                image = Image.frombytes(image_mode, [pixmap.width, pixmap.height], pixmap.samples)
                page_text = pytesseract.image_to_string(image, lang="eng")

            extracted_pages.append(page_text)

        document.close()
        return "\n".join(extracted_pages)
    except Exception as error:
        raise ProcessingException(detail=f"OCR extraction failed: {str(error)}")
