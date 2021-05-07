from datetime import datetime
from urllib.parse import quote_plus
from typing import Optional, Tuple
from dataclasses import dataclass



@dataclass(init=True)
class SearchData(object):
    total: int
    results: list
    query: str

    @property
    def escaped_query(self):
        return quote_plus(self.query)


@dataclass(init=True)
class IssueData(object):
    name_with_owner: str
    author_name: str
    author_url: str
    author_avatar_url: str
    issue_type: str
    number: int
    title: str
    url: str
    body_text: str
    state: str
    labels: Tuple[str, ...]
    created_at: datetime
    is_draft: Optional[bool] = None
    mergeable_state: Optional[str] = None
    milestone: Optional[str] = None


@dataclass(init=True)
class IssueStateColour(object):
    OPEN: int = 0x6cc644
    CLOSED: int = 0xbd2c00
    MERGED: int = 0x6e5494