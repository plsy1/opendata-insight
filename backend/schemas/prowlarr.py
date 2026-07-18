from typing import Optional

from pydantic import BaseModel


class ProwlarrSearchResultOut(BaseModel):
    indexer: Optional[str] = None
    title: Optional[str] = None
    size: Optional[int] = None
    seeders: Optional[int] = None
    leechers: Optional[int] = None
    publishDate: Optional[str] = None
    infoUrl: Optional[str] = None
    downloadUrl: Optional[str] = None
    magnetUrl: Optional[str] = None
    resolution: Optional[str] = None
    codec: Optional[str] = None

    # Prowlarr may add fields as indexers and releases evolve. Keep the complete
    # upstream object while documenting the fields currently used by the UI.
    model_config = {"extra": "allow"}
