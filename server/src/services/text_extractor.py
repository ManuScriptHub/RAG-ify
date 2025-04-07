import io
from bs4 import BeautifulSoup

def extract_text(file_type, file_bytes_or_url):
    """
    Extracts text from file bytes or a URL based on the file type.

    Parameters:
    - file_type: A string indicating the file type (e.g., 'pdf', 'docx', 'pptx', 'img', 'url').
    - file_bytes_or_url: The file content as bytes or a URL string.

    Returns:
    - A string containing the extracted text.
    """
    file_type = file_type.lower()

    if file_type == 'pdf':
        import pymupdf
        import pymupdf4llm

        bytes_io = io.BytesIO(file_bytes_or_url)
        doc = pymupdf.open(stream=bytes_io, filetype="pdf")
        md_text = pymupdf4llm.to_markdown(doc)
        return md_text

    elif file_type == 'docx':
        import docx
        bytes_io = io.BytesIO(file_bytes_or_url)
        doc = docx.Document(bytes_io)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text

    elif file_type in ['ppt', 'pptx']:
        from pptx import Presentation
        bytes_io = io.BytesIO(file_bytes_or_url)
        prs = Presentation(bytes_io)
        text_runs = []
        for slide in prs.slides:
            for shape in slide.shapes:
                if hasattr(shape, "text"):
                    text_runs.append(shape.text)
        return "\n".join(text_runs)

    elif file_type in ['img', 'jpeg', 'jpg', 'png']:
        from PIL import Image
        import pytesseract
        bytes_io = io.BytesIO(file_bytes_or_url)
        image = Image.open(bytes_io)
        text = pytesseract.image_to_string(image)
        return text

    elif file_type == 'url':
        import requests
        from bs4 import BeautifulSoup

        response = requests.get(file_bytes_or_url)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')
        for tag in soup(['script', 'style']):
            tag.decompose()
        
        text = soup.get_text(separator='\n')
        return '\n'.join(line.strip() for line in text.splitlines() if line.strip())

    else:
        raise ValueError("Unsupported file type")
