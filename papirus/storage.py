"""Papirüs uygulaması için depolama katmanı."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, List, Optional
import json
import uuid

from .models import Note


class PapirusStorage:
    """Notları JSON dosyasında tutan basit depolama sınıfı."""

    def __init__(self, storage_path: Path) -> None:
        self.storage_path = storage_path
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.storage_path.exists():
            self._write_raw({"notes": []})

    def _write_raw(self, data: Dict[str, List[Dict]]) -> None:
        self.storage_path.write_text(json.dumps(data, ensure_ascii=False, indent=2))

    def _read_raw(self) -> Dict[str, List[Dict]]:
        if not self.storage_path.exists():
            data: Dict[str, List[Dict]] = {"notes": []}
            self._write_raw(data)
            return data

        text = self.storage_path.read_text() or "{}"
        rewrite = False
        try:
            data = json.loads(text)
            if not isinstance(data, dict):
                data = {"notes": []}
                rewrite = True
        except json.JSONDecodeError:
            data = {"notes": []}
            rewrite = True

        notes = data.get("notes")
        if not isinstance(notes, list):
            data["notes"] = []
            rewrite = True

        if rewrite:
            self._write_raw({"notes": data.get("notes", [])})
            return {"notes": data.get("notes", [])}

        return {"notes": notes}

    def list_notes(self) -> List[Note]:
        return [Note.from_dict(item) for item in self._read_raw()["notes"]]

    def add_note(self, title: str, content: str) -> Note:
        note = Note(title=title, content=content, identifier=str(uuid.uuid4()))
        notes = self._read_raw()["notes"]
        notes.append(note.to_dict())
        self._write_raw({"notes": notes})
        return note

    def get_note(self, identifier: str) -> Optional[Note]:
        for raw in self._read_raw()["notes"]:
            if raw.get("id") == identifier:
                return Note.from_dict(raw)
        return None

    def update_note(self, identifier: str, *, title: Optional[str] = None, content: Optional[str] = None) -> Optional[Note]:
        data = self._read_raw()
        notes = data["notes"]
        for index, raw in enumerate(notes):
            if raw.get("id") == identifier:
                note = Note.from_dict(raw)
                note.update_content(new_title=title, new_content=content)
                notes[index] = note.to_dict()
                self._write_raw({"notes": notes})
                return note
        return None

    def delete_note(self, identifier: str) -> bool:
        data = self._read_raw()
        notes = data["notes"]
        new_notes = [raw for raw in notes if raw.get("id") != identifier]
        if len(new_notes) == len(notes):
            return False
        self._write_raw({"notes": new_notes})
        return True

    def search(self, keyword: str) -> Iterable[Note]:
        lowered = keyword.lower()
        for raw in self._read_raw()["notes"]:
            if lowered in raw.get("title", "").lower() or lowered in raw.get("content", "").lower():
                yield Note.from_dict(raw)


def get_default_storage() -> PapirusStorage:
    """Kullanıcının ev dizininde varsayılan depolama nesnesi döndür."""

    home = Path.home()
    storage_file = home / ".papirus" / "notes.json"
    return PapirusStorage(storage_file)
