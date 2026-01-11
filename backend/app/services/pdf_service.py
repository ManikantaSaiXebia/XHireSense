import PyPDF2
from io import BytesIO
from typing import Optional

class PDFService:
    """Service for extracting text from PDF files"""
    
    @staticmethod
    def extract_text_from_pdf(file_content: bytes) -> Optional[str]:
        """
        Extract text from PDF file content
        
        Args:
            file_content: PDF file bytes
            
        Returns:
            Extracted text or None if extraction fails
        """
        try:
            pdf_file = BytesIO(file_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            text_parts = []
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text = page.extract_text()
                if text:
                    text_parts.append(text)
            
            extracted_text = "\n\n".join(text_parts)
            return extracted_text.strip() if extracted_text.strip() else None
            
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            return None
