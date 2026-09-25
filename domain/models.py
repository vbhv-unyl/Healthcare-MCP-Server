from dataclasses import dataclass

@dataclass
class RetrievedChunk:
    text: str
    section: str
    page_start: int
    page_end: int
    low_confidence: bool
    score: int
    source_type: str = "text"