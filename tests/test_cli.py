from pathlib import Path

from papirus import cli


def run_cli(tmp_path: Path, *args: str) -> int:
    storage = tmp_path / "notes.json"
    argv = ["--storage", str(storage), *args]
    return cli.main(list(argv))


def test_cli_add_and_list(tmp_path: Path, capsys) -> None:
    code = run_cli(tmp_path, "ekle", "Deneme", "İçerik")
    assert code == 0
    code = run_cli(tmp_path, "liste")
    assert code == 0
    out = capsys.readouterr().out
    assert "Deneme" in out
    assert "İçerik" in out


def test_cli_show_unknown(tmp_path: Path, capsys) -> None:
    code = run_cli(tmp_path, "goster", "yok")
    assert code == 1
    err = capsys.readouterr().err
    assert "Not bulunamadı" in err


def test_cli_update_requires_changes(tmp_path: Path, capsys) -> None:
    code = run_cli(tmp_path, "guncelle", "id")
    assert code == 2
    err = capsys.readouterr().err
    assert "en az biri" in err
