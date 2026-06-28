"""
Document ingestion: text extraction → chunking → embedding → store in pgvector.
"""
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

CHUNK_SIZE = 800
CHUNK_OVERLAP = 100

_EMBEDDING_MODEL = None


def _get_embedding_model():
    global _EMBEDDING_MODEL
    if _EMBEDDING_MODEL is None:
        from sentence_transformers import SentenceTransformer
        _EMBEDDING_MODEL = SentenceTransformer(
            'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
        )
    return _EMBEDDING_MODEL


def _ocr_pdf_with_vision(path: Path) -> str:
    """
    OCR fallback for scanned/image-based PDFs.
    Renders each page with PyMuPDF and sends to GPT-4o Vision to extract text.
    """
    import base64, os
    try:
        import fitz  # PyMuPDF
    except ImportError:
        logger.warning('PyMuPDF not installed — cannot OCR scanned PDF.')
        return ''

    try:
        from openai import OpenAI
        client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY', ''))
    except ImportError:
        logger.warning('openai package not available for Vision OCR.')
        return ''

    doc = fitz.open(str(path))
    all_text = []
    logger.info(f'OCR via GPT-4o Vision: {len(doc)} páginas em {path.name}')

    for page_num, page in enumerate(doc):
        try:
            # Render page at 150 DPI as PNG
            mat = fitz.Matrix(150 / 72, 150 / 72)
            pix = page.get_pixmap(matrix=mat, colorspace=fitz.csRGB)
            img_bytes = pix.tobytes('png')
            b64 = base64.b64encode(img_bytes).decode()

            response = client.chat.completions.create(
                model='gpt-4o',
                max_tokens=2000,
                messages=[{
                    'role': 'user',
                    'content': [
                        {
                            'type': 'text',
                            'text': (
                                'Extraia TODO o texto desta página de documento técnico industrial. '
                                'Preserve a estrutura (títulos, listas, tabelas). '
                                'Retorne somente o texto extraído, sem comentários.'
                            ),
                        },
                        {
                            'type': 'image_url',
                            'image_url': {'url': f'data:image/png;base64,{b64}', 'detail': 'high'},
                        },
                    ],
                }],
            )
            page_text = response.choices[0].message.content or ''
            all_text.append(f'--- Página {page_num + 1} ---\n{page_text}')
            logger.info(f'  Pág {page_num + 1}: {len(page_text)} chars extraídos')
        except Exception as e:
            logger.warning(f'  Pág {page_num + 1} OCR falhou: {e}')

    doc.close()
    return '\n\n'.join(all_text)


def extract_text(file_path: str) -> str:
    """Extract plain text from PDF, DOCX, or TXT. Falls back to Vision OCR for scanned PDFs."""
    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix == '.pdf':
        try:
            from PyPDF2 import PdfReader
            reader = PdfReader(str(path))
            pages = [p.extract_text() or '' for p in reader.pages]
            text = '\n'.join(pages).strip()
            # If fewer than 50 chars per page on average → scanned PDF, use OCR
            if len(text) < len(reader.pages) * 50:
                logger.info(f'Scanned PDF detected ({path.name}), switching to Vision OCR.')
                return _ocr_pdf_with_vision(path)
            return text
        except Exception as e:
            logger.warning(f'PyPDF2 failed for {path}: {e}')
            return _ocr_pdf_with_vision(path)

    elif suffix == '.docx':
        try:
            from docx import Document
            doc = Document(str(path))
            return '\n'.join(p.text for p in doc.paragraphs)
        except Exception as e:
            logger.warning(f'python-docx failed for {path}: {e}')
            return ''

    else:
        try:
            return path.read_text(encoding='utf-8')
        except Exception as e:
            logger.warning(f'Text read failed for {path}: {e}')
            return ''


def chunk_text(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list:
    """Sliding-window character-level chunking."""
    if not text.strip():
        return []
    chunks = []
    start = 0
    while start < len(text):
        end = start + size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= len(text):
            break
        start = end - overlap
    return chunks


def embed_texts(texts: list) -> list:
    """Embed a list of strings; returns list of float lists."""
    if not texts:
        return []
    model = _get_embedding_model()
    embeddings = model.encode(texts, show_progress_bar=False, batch_size=8)
    return [e.tolist() for e in embeddings]


def ingest_document(doc) -> int:
    """
    Extract → chunk → embed → store DocumentChunks for a KnowledgeDocument.
    Returns number of chunks created.
    """
    from .models import DocumentChunk

    # Delete existing chunks first (re-ingest idempotency)
    doc.chunks.all().delete()

    if not doc.file:
        logger.warning(f'Document {doc.pk} has no file; skipping.')
        return 0

    file_path = doc.file.path
    text = extract_text(file_path)
    if not text.strip():
        logger.warning(f'No text extracted from {file_path}')
        return 0

    chunks = chunk_text(text)
    if not chunks:
        return 0

    embeddings = embed_texts(chunks)

    to_create = []
    for idx, (content, emb) in enumerate(zip(chunks, embeddings)):
        to_create.append(
            DocumentChunk(
                document=doc,
                content=content,
                embedding=emb,
                chunk_index=idx,
            )
        )

    DocumentChunk.objects.bulk_create(to_create, batch_size=100)
    doc.is_ingested = True
    doc.save(update_fields=['is_ingested', 'updated_at'])

    return len(to_create)
