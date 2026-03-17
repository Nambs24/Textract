from pathlib import Path
from typing import Optional

import docx
from PyPDF2 import PdfReader


def load_file(file_path: str) -> Optional[str]:
    """
    Detect file type and extract raw text.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    suffix = path.suffix.lower()

    if suffix == ".pdf":
        return load_pdf(path)

    elif suffix == ".docx":
        return load_docx(path)

    elif suffix == ".txt":
        return load_txt(path)

    else:
        raise ValueError(f"Unsupported file type: {suffix}")


# =========================
# 📄 PDF
# =========================
def load_pdf(path: Path) -> str:
    reader = PdfReader(str(path))
    text = []

    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text.append(extracted)

    return "\n".join(text)


# =========================
# 📝 DOCX
# =========================
def load_docx(path: Path) -> str:
    doc = docx.Document(str(path))
    return "\n".join([para.text for para in doc.paragraphs])


# =========================
# 📃 TXT
# =========================
def load_txt(path: Path) -> str:
    return path.read_text(encoding="utf-8")
