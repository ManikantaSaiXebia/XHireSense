import PyPDF2
from io import BytesIO
from typing import Optional, Tuple
import re

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

    @staticmethod
    def extract_contact_info(text: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        Extract name, email, and phone number from text

        Args:
            text: Extracted text from PDF

        Returns:
            Tuple of (name, email, phone)
        """
        name = None
        email = None
        phone = None

        lines = text.split('\n')
        # Assume first non-empty line is the name
        for line in lines:
            line = line.strip()
            if line and len(line) > 2 and not line.startswith('http') and '@' not in line and not re.match(r'\d{3}', line):
                name = line
                break

        # Email regex
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, text)
        if email_match:
            email = email_match.group()

        # Phone regex (simple pattern for US phones)
        phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
        phone_match = re.search(phone_pattern, text)
        if phone_match:
            phone = phone_match.group()

        return name, email, phone
