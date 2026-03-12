from docling.document_converter import DocumentConverter
from docling_core.transforms.chunker import HierarchicalChunker


def merge_consecutive_chunks(chunks):
    if not chunks:
        return []
    
    merged = []
    current_chunk = chunks[0]

    for next_chunk in chunks[1:]:
        # On compare les titres associés (headings)
        if current_chunk.meta.headings == next_chunk.meta.headings and len(current_chunk.text) + len(next_chunk.text) < 2500:
            # Fusion du texte
            current_chunk.text += " " + next_chunk.text
        else:
            merged.append(current_chunk)
            current_chunk = next_chunk
            
    merged.append(current_chunk)
    return merged

converter = DocumentConverter()
result = converter.convert("documents/image_processing.pdf")
chunker = HierarchicalChunker(max_chars=2500)

chunks = list(chunker.chunk(result.document))

final_chunks = merge_consecutive_chunks(chunks)
