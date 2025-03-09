from datetime import datetime
from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class Location(BaseModel):
    x: float = Field(..., description="Left coordinate (x-axis)", ge=0)
    y: float = Field(..., description="Top coordinate (y-axis)", ge=0)
    width: float = Field(..., description="Width of text block", gt=0)
    height: float = Field(..., description="Height of text block", gt=0)
    page: int = Field(..., description="Page number where text appears", ge=1)


class TextSummary(BaseModel):
    """Represents a processed text block with normalized values."""

    block_id: int = Field(..., description="Unique identifier for the text block")
    text: str = Field(..., description="Original text content")
    confidence: float = Field(
        ..., description="Normalized confidence score (0.0-1.0)", ge=0.0, le=1.0
    )
    location: Location = Field(..., description="Standardized position in the document")
    summary: Optional[str] = Field(
        default=None, description="Summarized version of the text, if available"
    )
    content_type: Literal["text", "heading", "list", "table"] = Field(
        default="text", description="Type of content in the block"
    )


class DocumentSummary(BaseModel):
    """Represents a summarized document with processed text blocks."""

    blocks: List[TextSummary] = Field(
        ..., description="List of text blocks in the document"
    )
    document_name: str = Field(..., description="Name of the document")
    document_id: str = Field(..., description="Unique identifier for the document")
    created_at: datetime = Field(
        default_factory=datetime.now, description="When the summary was created"
    )
    total_blocks: Optional[int] = None
    metadata: Dict = Field(
        default_factory=dict, description="Additional document metadata"
    )
