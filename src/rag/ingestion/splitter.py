import re
import uuid
from collections import defaultdict
from typing import List, Dict, Tuple
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

class ParentChildSplitter:
    def __init__(self, parent_chunk_size: int, parent_chunk_overlap: int, child_chunk_size: int, child_chunk_overlap: int):
        self.parent_splitter = RecursiveCharacterTextSplitter(chunk_size=parent_chunk_size,
                                                            chunk_overlap=parent_chunk_overlap,
                                                            separators=["\n", ". ", ", ", " ", ""])
        self.child_splitter = RecursiveCharacterTextSplitter(chunk_size=child_chunk_size,
                                                            chunk_overlap=child_chunk_overlap,
                                                            separators=["\n\n", "\n", ". ", ", ", " ", ""])
                                                            
    def _preprocess_text(self, chunk_text: str) -> Tuple[str, List[str]]:
        text_clean = re.sub(r'\n{2,}', '\n', chunk_text)
        text_clean = re.sub(r'[ ]{2,}', ' ', text_clean)
        text_clean = re.sub(r'\n\s*\n+', '\n', text_clean)
        return text_clean.strip()

    def split_documents(self, documents: List[Document]) -> Dict[str, List[Document]]:
        docs_by_source = defaultdict(list)
        for doc in documents:
            source_key = doc.metadata.get("file_path")
            docs_by_source[source_key].append(doc)
        all_parent_docs = []
        all_child_docs = []
        for source_name, doc_group in docs_by_source.items():
            combined_text = "\n".join([d.page_content for d in doc_group])
            base_metadata = doc_group[0].metadata.copy() if doc_group else {}
            combined_doc = Document(page_content=combined_text, metadata=base_metadata)
            parent_chunks = self.parent_splitter.split_documents([combined_doc])
            for p_doc in parent_chunks:
                clean_text = self._preprocess_text(p_doc.page_content)
                parent_id = str(uuid.uuid4())
                parent_meta = p_doc.metadata.copy()
                parent_meta.update({
                    "doc_id": parent_id,
                    "type": "parent",
                    "source": source_name
                })
                final_parent_doc = Document(page_content=clean_text, metadata=parent_meta)
                all_parent_docs.append(final_parent_doc)
                child_texts = self.child_splitter.split_text(clean_text)
                for c_text in child_texts:
                    child_meta = {
                        "parent_id": parent_id,
                        "type": "child",
                        "source": source_name,
                    }
                    child_doc = Document(page_content=c_text, metadata=child_meta)
                    all_child_docs.append(child_doc)
        return {"parents": all_parent_docs,
                "children": all_child_docs}