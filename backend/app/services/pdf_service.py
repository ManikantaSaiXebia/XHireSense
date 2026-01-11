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

        # Clean and normalize text
        text = text.replace('\r', '\n').replace('\t', ' ')
        lines = [line.strip() for line in text.split('\n') if line.strip()]

        # Extract email first (more reliable)
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, text, re.IGNORECASE)
        if email_match:
            email = email_match.group().lower()

        # Extract phone number
        # More comprehensive phone patterns
        phone_patterns = [
            r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b',  # 123-456-7890, 123.456.7890, 123 456 7890
            r'\b\(\d{3}\)\s*\d{3}[-.\s]?\d{4}\b',  # (123) 456-7890
            r'\b\d{10}\b',  # 1234567890
            r'\+\d{1,3}[-.\s]?\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b'  # +1-123-456-7890
        ]

        for pattern in phone_patterns:
            phone_match = re.search(pattern, text)
            if phone_match:
                phone = phone_match.group()
                # Clean up the phone number
                phone = re.sub(r'[^\d+\-\(\)\.\s]', '', phone)
                break

        # Extract name - look for patterns that are likely to be names
        # Skip lines that are clearly not names
        skip_patterns = [
            r'^https?://',  # URLs
            r'^www\.',  # Websites
            r'^\d+$',  # Just numbers
            r'^[^\w\s]*$',  # Just symbols
            r'^\s*(email|phone|mobile|tel|cell|contact|address|linkedin|github|portfolio)\s*:?\s*$',  # Labels
            r'^\s*(objective|summary|experience|education|skills|projects|certifications)\s*:?\s*$',  # Section headers
        ]

        for line in lines[:10]:  # Check first 10 lines
            line_lower = line.lower()
            should_skip = False

            for pattern in skip_patterns:
                if re.search(pattern, line_lower, re.IGNORECASE):
                    should_skip = True
                    break

            if should_skip:
                continue

            # Check if line looks like a name (2-4 words, title case or mixed case)
            words = line.split()
            if 1 <= len(words) <= 4:
                # Check if it contains title case words (likely a name)
                has_title_case = any(word[0].isupper() and len(word) > 1 for word in words if word[0].isalpha())
                # Not all caps (likely headers)
                not_all_caps = not all(word.isupper() for word in words if len(word) > 1)
                # Not too short
                not_too_short = len(line) > 3

                if has_title_case and not_all_caps and not_too_short:
                    name = line
                    break

        return name, email, phone
