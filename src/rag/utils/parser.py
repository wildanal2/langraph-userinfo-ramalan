from typing import List, Dict
from langchain_core.documents import Document
def document_parser(docs: List[Document]) -> str:
    return "\n\n".join(doc.page_content for doc in docs)