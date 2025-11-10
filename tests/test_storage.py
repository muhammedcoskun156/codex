from pathlib import Path

import json

from papirus.storage import PapirusStorage


def create_storage(tmp_path: Path) -> PapirusStorage:
    return PapirusStorage(tmp_path / "notes.json")


def test_add_and_list(tmp_path: Path) -> None:
    storage = create_storage(tmp_path)
    storage.add_note("Başlık", "İçerik")
    notes = storage.list_notes()
    assert len(notes) == 1
    assert notes[0].title == "Başlık"
    assert notes[0].content == "İçerik"


def test_get_and_update(tmp_path: Path) -> None:
    storage = create_storage(tmp_path)
    note = storage.add_note("Eski", "İçerik")
    updated = storage.update_note(note.identifier, title="Yeni", content="Yeni içerik")
    assert updated is not None
    assert updated.title == "Yeni"
    fetched = storage.get_note(note.identifier)
    assert fetched is not None
    assert fetched.title == "Yeni"


def test_delete(tmp_path: Path) -> None:
    storage = create_storage(tmp_path)
    note = storage.add_note("Silinecek", "İçerik")
    assert storage.delete_note(note.identifier)
    assert storage.list_notes() == []


def test_search(tmp_path: Path) -> None:
    storage = create_storage(tmp_path)
    storage.add_note("Alışveriş", "Elma, armut")
    storage.add_note("Toplantı", "Proje planı")
    results = list(storage.search("elma"))
    assert len(results) == 1
    assert results[0].title == "Alışveriş"


def test_invalid_json_is_recovered(tmp_path: Path) -> None:
    storage_file = tmp_path / "notes.json"
    storage_file.write_text("bozuk")
    storage = PapirusStorage(storage_file)
    assert storage.list_notes() == []
    data = json.loads(storage_file.read_text())
    assert "notes" in data
