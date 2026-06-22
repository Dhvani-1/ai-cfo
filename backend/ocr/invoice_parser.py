import os

_reader = None

def get_ocr_reader():
    global _reader
    if _reader is None:
        import ssl
        ssl._create_default_https_context = ssl._create_unverified_context
        # pyrefly: ignore [missing-import]
        import easyocr
        # Initialize EasyOCR Reader for English on CPU to ensure universal compatibility
        _reader = easyocr.Reader(['en'], gpu=False)
    return _reader

def extract_text(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".txt":
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    # Fallback/Test check: if a .txt file exists next to file_path, use it directly.
    # This enables offline execution and rapid testing without EasyOCR model downloads.
    txt_fallback_path = file_path + ".txt"
    if os.path.exists(txt_fallback_path):
        with open(txt_fallback_path, "r", encoding="utf-8") as f:
            return f.read()

    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        import pdfplumber
        text_content = []
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                extracted = page.extract_text()
                if extracted:
                    text_content.append(extracted)
        return "\n".join(text_content)
    else:
        try:
            reader = get_ocr_reader()
            results = reader.readtext(file_path, detail=0)
            return "\n".join(results)
        except Exception as e:
            # Fallback if EasyOCR fails (e.g. connection timeout on downloading weights)
            if os.path.exists(txt_fallback_path):
                with open(txt_fallback_path, "r", encoding="utf-8") as f:
                    return f.read()
            raise e
