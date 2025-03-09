from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class Location(BaseModel):
    x: float = Field(..., description="Left coordinate (x-axis)")
    y: float = Field(..., description="Top coordinate (y-axis)")
    width: float = Field(..., description="Width of text block")
    height: float = Field(..., description="Height of text block")


class TextSummary(BaseModel):
    location: Location = Field(..., description="Standardized position in the document")
    summary: Optional[str] = Field(
        ..., description="Summarized version of the text, if available"
    )
    content_type: Literal["paragraph", "heading"] = Field(
        default="paragraph", description="Type of content in the block"
    )


class Page(BaseModel):
    page_number: int = Field(..., description="Page number")
    blocks: List[TextSummary] = Field(
        default_factory=list, description="List of text blocks on this page"
    )


class DocumentSummary(BaseModel):
    pages: List[Page] = Field(..., description="List of pages in the document")
    document_name: str = Field(..., description="Name of the document")
    number_of_pages: int = Field(
        ..., description="Total number of pages in the document"
    )