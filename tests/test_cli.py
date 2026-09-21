"""The command-line tools are the contributor's interface; exercise them.

Each test calls the same `main()` CI calls, so a broken exit code or a renamed
flag fails here rather than in somebody's pull request.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

from rsi.paths import ROOT

SCRIPTS = ROOT / "scripts"


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"cli_{name}", SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def validate_cli():
    return _load("validate")


@pytest.fixture(scope="module")
def format_cli():
    return _load("format")


@pytest.fixture(scope="module")
def build_cli():
    return _load("build")


def test_validate_passes_on_the_committed_corpus(validate_cli, capsys):
    assert validate_cli.main(["--no-color"]) == 0
    assert "OK" in capsys.readouterr().out


def test_validate_fails_on_a_broken_entry(validate_cli, make_entry, capsys):
    broken = make_entry(contribution="benchmark")  # E151
    assert validate_cli.main(["--no-color", str(broken)]) == 1
    assert "E151" in capsys.readouterr().out


def test_validate_accepts_specific_files(validate_cli, capsys):
    from rsi.entries import entry_files

    assert validate_cli.main(["--no-color", str(entry_files()[0])]) == 0
    assert "1 entry checked" in capsys.readouterr().out


def test_format_check_is_clean(format_cli):
    assert format_cli.main(["--check"]) == 0


def test_format_rewrites_a_scruffy_file(format_cli, tmp_path: Path, capsys):
    path = tmp_path / "scruffy-2024.yaml"
    path.write_text(
        "title: Scruffy Loop\n"
        "id: scruffy-2024\n"
        "tags: [rejection-sampling, distillation]\n"
        "domain: [math, code]\n",
        encoding="utf-8",
    )
    assert format_cli.main([str(path)]) == 0
    text = path.read_text(encoding="utf-8")
    assert text.startswith("id: scruffy-2024\n"), "keys were not reordered"
    assert "tags: [distillation, rejection-sampling]" in text, "tags were not sorted"
    assert "domain: [code, math]" in text, "axis values are not in taxonomy order"


def test_build_check_reports_no_drift(build_cli):
    assert build_cli.main(["--check", "--no-figures"]) == 0
