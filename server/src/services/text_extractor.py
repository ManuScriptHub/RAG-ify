import io

def extract_text(file_type, file_bytes):
    """
    Extracts text from file bytes based on the file type.

    Parameters:
    - file_type: A string indicating the file type (e.g., 'pdf', 'docx', 'pptx', 'img').
    - file_bytes: The file content as bytes.

    Returns:
    - A string containing the extracted text.
    """
    file_type = file_type.lower()

    if file_type == 'pdf':
        # For PDF files using PyPDF2
        from PyPDF2 import PdfReader
        bytes_io = io.BytesIO(file_bytes)
        reader = PdfReader(bytes_io)
        text = ""
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
        return text

    elif file_type == 'docx':
        # For DOCX files using python-docx
        import docx
        bytes_io = io.BytesIO(file_bytes)
        doc = docx.Document(bytes_io)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text

    elif file_type in ['ppt', 'pptx']:
        # For PowerPoint files using python-pptx
        from pptx import Presentation
        bytes_io = io.BytesIO(file_bytes)
        prs = Presentation(bytes_io)
        text_runs = []
        for slide in prs.slides:
            for shape in slide.shapes:
                if hasattr(shape, "text"):
                    text_runs.append(shape.text)
        return "\n".join(text_runs)

    elif file_type in ['img', 'jpeg', 'jpg', 'png']:
        # For images using pytesseract and Pillow
        from PIL import Image
        import pytesseract
        bytes_io = io.BytesIO(file_bytes)
        image = Image.open(bytes_io)
        text = pytesseract.image_to_string(image)
        return text

    else:
        raise ValueError("Unsupported file type")

# Example usage:
if __name__ == "__main__":
    # Let's assume 'file_bytes' is obtained from a file upload.
    # For demonstration, read a local file as bytes (replace with your actual file bytes).
    file_type = "pdf"
    try:
        with open(r"D:\Resources\Resume\Resu.pdf", "rb") as f:
            file_bytes = f.read()
        text_content = extract_text(file_type, file_bytes)
        print("Extracted text:\n", text_content)
    except Exception as e:
        print("An error occurred:", e)
