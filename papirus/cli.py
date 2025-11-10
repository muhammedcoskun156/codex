"""Papirüs not defteri için komut satırı arayüzü."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Iterable

from .storage import PapirusStorage, get_default_storage
from .models import Note


def format_note(note: Note) -> str:
    """Notu okunabilir metne çevir."""

    created = note.created_at.strftime("%Y-%m-%d %H:%M")
    updated = note.updated_at.strftime("%Y-%m-%d %H:%M")
    header = f"{note.title} (id: {note.identifier})\nOluşturma: {created} | Güncelleme: {updated}"
    separator = "-" * len(note.title)
    return f"{separator}\n{header}\n{separator}\n{note.content}"


def _print_notes(notes: Iterable[Note]) -> None:
    printed = False
    for note in notes:
        printed = True
        print(format_note(note))
        print()
    if not printed:
        print("Herhangi bir not bulunamadı.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="papirus", description="Papirüs not defteri")
    parser.add_argument(
        "--storage",
        help="Notların tutulacağı dosya yolu. Boş bırakılırsa varsayılan konum kullanılır.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    add_parser = subparsers.add_parser("ekle", help="Yeni not oluştur")
    add_parser.add_argument("baslik", help="Not başlığı")
    add_parser.add_argument("icerik", help="Not içeriği")

    list_parser = subparsers.add_parser("liste", help="Tüm notları listele")
    list_parser.add_argument("--ara", dest="arama", help="Başlık veya içerikte arama yap")

    show_parser = subparsers.add_parser("goster", help="Belirli bir notu görüntüle")
    show_parser.add_argument("id", help="Notun benzersiz kimliği")

    delete_parser = subparsers.add_parser("sil", help="Bir notu sil")
    delete_parser.add_argument("id", help="Silinecek notun kimliği")

    update_parser = subparsers.add_parser("guncelle", help="Bir notu güncelle")
    update_parser.add_argument("id", help="Güncellenecek notun kimliği")
    update_parser.add_argument("--baslik", help="Yeni başlık")
    update_parser.add_argument("--icerik", help="Yeni içerik")

    return parser


def _resolve_storage(args: argparse.Namespace) -> PapirusStorage:
    if args.storage:
        return PapirusStorage(Path(args.storage))
    return get_default_storage()


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    storage = _resolve_storage(args)

    if args.command == "ekle":
        note = storage.add_note(args.baslik, args.icerik)
        print(f"Not oluşturuldu: {note.identifier}")
        return 0

    if args.command == "liste":
        if args.arama:
            notes = storage.search(args.arama)
        else:
            notes = storage.list_notes()
        _print_notes(notes)
        return 0

    if args.command == "goster":
        note = storage.get_note(args.id)
        if not note:
            print("Not bulunamadı.", file=sys.stderr)
            return 1
        print(format_note(note))
        return 0

    if args.command == "sil":
        success = storage.delete_note(args.id)
        if not success:
            print("Not bulunamadı.", file=sys.stderr)
            return 1
        print("Not silindi.")
        return 0

    if args.command == "guncelle":
        if not args.baslik and not args.icerik:
            print("Başlık veya içerikten en az biri sağlanmalı.", file=sys.stderr)
            return 2
        note = storage.update_note(args.id, title=args.baslik, content=args.icerik)
        if not note:
            print("Not bulunamadı.", file=sys.stderr)
            return 1
        print("Not güncellendi.")
        return 0

    parser.error("Geçersiz komut")
    return 2


if __name__ == "__main__":
    sys.exit(main())
