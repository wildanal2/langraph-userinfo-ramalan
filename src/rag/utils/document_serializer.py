from typing import Any
from langchain_core.documents import Document
from langchain_core.load import dumps, loads

def encode(doc: Document) -> bytes:
    return dumps(doc).encode("utf-8")

def decode(data: bytes) -> Document:
    if isinstance(data, str):
        data = data.encode("utf-8")
    return loads(data.decode("utf-8"))

def encode_key(key: Any) -> str:
    if isinstance(key, bytes):
        return key.decode("utf-8")
    return str(key)