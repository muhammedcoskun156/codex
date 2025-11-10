"""Papirüs için veri modelleri."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict


@dataclass
class Note:
    """Tek bir notu temsil eden veri sınıfı."""

    title: str
    content: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    identifier: str | None = None

    def to_dict(self) -> Dict[str, Any]:
        """Notu JSON uyumlu bir sözlüğe dönüştür."""

        return {
            "id": self.identifier,
            "title": self.title,
            "content": self.content,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Note":
        """Bir sözlükten :class:`Note` örneği oluştur."""

        return cls(
            title=data["title"],
            content=data["content"],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            identifier=data.get("id"),
        )

    def update_content(self, new_title: str | None = None, new_content: str | None = None) -> None:
        """Not başlığını ve/veya içeriğini güncelle."""

        if new_title is not None:
            self.title = new_title
        if new_content is not None:
            self.content = new_content
        self.updated_at = datetime.utcnow()
