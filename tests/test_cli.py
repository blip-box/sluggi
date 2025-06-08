"""CLI tests for the sluggi library."""

import json
import re

import pytest
from click.testing import CliRunner

from sluggi.cli import app


def strip_ansi(text):
    """Remove ANSI escape sequences from the given string."""
    ansi_escape = re.compile(r"\x1b\[[0-9;]*[mGKHF]")
    return ansi_escape.sub("", text)


runner = CliRunner()


def extract_slug(line):
    """Extract the slug from a CLI output line.

    Handles the special separator if present.
    """
    if "̔" in line:
        return line.split("̔", 1)[1].strip()
    return line.strip()


def test_single_basic():
    """Test single command with basic input."""
    result = runner.invoke(app, ["slug", "Hello, world!"])
    assert result.exit_code == 0
    slug = extract_slug(result.output)
    assert slug == "hello-world"


def test_single_stopwords():
    """Test single command with stopwords option."""
    result = runner.invoke(
        app, ["slug", "The quick brown fox jumps", "--stopwords", "the,fox"]
    )
    assert result.exit_code == 0
    slug = extract_slug(result.output)
    assert slug == "quick-brown-jumps"


def test_single_separator():
    """Test single command with custom separator."""
    result = runner.invoke(app, ["slug", "Hello, world!", "--separator", "_"])
    assert result.exit_code == 0
    slug = extract_slug(result.output)
    assert slug == "hello_world"


def test_single_custom_map():
    """Test single command with custom map."""
    cmap = json.dumps({"ä": "ae", "ö": "oe", "ü": "ue"})
    result = runner.invoke(app, ["slug", "ä ö ü", "--custom-map", cmap])
    assert result.exit_code == 0
    slug = extract_slug(result.output)
    assert slug == "ae-oe-ue"


def test_single_word_regex_capitalized():
    """Test single command with regex option to extract capitalized words."""
    result = runner.invoke(
        app,
        ["slug", "The Quick Brown Fox", "--regex", r"[A-Z][a-z]+", "--no-lowercase"],
    )
    assert (
        result.exit_code == 0
    ), f"Exit code: {result.exit_code}, Output: {result.output}"
    slug = extract_slug(result.output)
    assert slug == "The-Quick-Brown-Fox"


def test_single_word_regex_default():
    """Test single command with default word-regex behavior."""
    result = runner.invoke(app, ["slug", "Hello, world!"])
    assert result.exit_code == 0
    slug = extract_slug(result.output)
    assert slug == "hello-world"


def test_batch_stdin():
    """Test batch slug generation from standard input (should print error if no input).

    Accept both exit codes 0 and 1 due to Click/Typer runner behavior.
    Assert error message in output.
    """
    result = runner.invoke(app, ["batch"], input="")
    assert result.exit_code in (0, 1)
    output = result.output or ""
    assert (
        "No input provided" in output or "Aborted." in output
    ), f"Unexpected output: {output!r}"


def test_batch_file(tmp_path):
    """Test batch slug generation from file.

    Verifies that the batch command works correctly with a file input.
    """
    file = tmp_path / "input.txt"
    file.write_text("Hello, world!\nPrivet mir\n")
    result = runner.invoke(app, ["batch", "--input", str(file)])
    assert result.exit_code == 0
    output = strip_ansi(result.output)
    lines = [
        line
        for line in output.strip().splitlines()
        if line.strip() and all(c.isalnum() or c in "-_" for c in line.strip())
    ]
    slugs = [extract_slug(line) for line in lines]
    assert "hello-world" in slugs
    assert "privet-mir" in slugs


def test_batch_file_stopwords(tmp_path):
    """Test batch CLI with --stopwords option."""
    file = tmp_path / "input.txt"
    file.write_text("the quick brown fox\njump over the lazy dog\n")
    result = runner.invoke(
        app, ["batch", "--input", str(file), "--stopwords", "the,fox,dog"]
    )
    assert result.exit_code == 0
    lines = [line for line in result.output.strip().splitlines() if line.strip()]
    slugs = [extract_slug(line) for line in lines]
    assert "quick-brown" in slugs
    assert "jump-over-lazy" in slugs


def test_batch_file_stopwords_separator(tmp_path):
    """Test batch CLI with --stopwords and --separator together."""
    file = tmp_path / "input.txt"
    file.write_text("the quick brown fox\njump over the lazy dog\n")
    result = runner.invoke(
        app,
        [
            "batch",
            "--input",
            str(file),
            "--stopwords",
            "the,fox,dog",
            "--separator",
            "_",
        ],
    )
    assert result.exit_code == 0
    lines = [line for line in result.output.strip().splitlines() if line.strip()]
    slugs = [extract_slug(line) for line in lines]
    assert "quick_brown" in slugs
    assert "jump_over_lazy" in slugs


def test_batch_file_word_regex_capitalized(tmp_path):
    """Test batch CLI with --word-regex option to extract capitalized words."""
    file = tmp_path / "input.txt"
    file.write_text("The Quick Brown Fox\nJump Over The Lazy Dog\n")
    result = runner.invoke(
        app,
        [
            "batch",
            "--input",
            str(file),
            "--word-regex",
            r"[A-Z][a-z]+",
            "--no-lowercase",
        ],
    )
    assert result.exit_code == 0
    lines = [line for line in result.output.strip().splitlines() if line.strip()]
    slugs = [extract_slug(line) for line in lines]
    assert "The-Quick-Brown-Fox" in slugs
    assert "Jump-Over-The-Lazy-Dog" in slugs


def test_batch_file_word_regex_default(tmp_path):
    """Test batch CLI with default word-regex behavior."""
    file = tmp_path / "input.txt"
    file.write_text("Hello, world!\nPrivet mir\n")
    result = runner.invoke(app, ["batch", "--input", str(file)])
    assert result.exit_code == 0
    lines = [
        line
        for line in result.output.strip().splitlines()
        if line.strip() and all(c.isalnum() or c in "-_" for c in line.strip())
    ]
    slugs = [extract_slug(line) for line in lines]
    assert "hello-world" in slugs
    assert "privet-mir" in slugs


def test_batch_display_output_table(tmp_path):
    """Test batch display output in table format."""
    input_file = tmp_path / "input.txt"
    input_file.write_text("Alpha Beta\nGamma Delta\n")
    result = runner.invoke(
        app, ["batch", "--input", str(input_file), "--display-output"]
    )
    out = result.stdout
    headers_present = ("original" in out.lower() and "slug" in out.lower()) or (
        "┏" in out and "┓" in out and "┃" in out
    )
    assert headers_present
    assert "Alpha Beta" in out and "alpha-beta" in out
    assert "Gamma Delta" in out and "gamma-delta" in out


def test_batch_output_file(tmp_path):
    """Test batch slug generation with output file."""
    infile = tmp_path / "in.txt"
    outfile = tmp_path / "out.txt"
    infile.write_text("foo\nbar\n")
    result = runner.invoke(
        app, ["batch", "--input", str(infile), "--output", str(outfile)]
    )
    assert result.exit_code == 0
    assert outfile.read_text().strip().splitlines() == ["foo", "bar"]
    assert "Slugs written to" in result.output


def test_batch_dry_run(tmp_path):
    """Test batch slug generation with dry-run option."""
    infile = tmp_path / "in.txt"
    outfile = tmp_path / "out.txt"
    infile.write_text("baz\nbat\n")
    result = runner.invoke(
        app, ["batch", "--input", str(infile), "--output", str(outfile), "--dry-run"]
    )
    assert result.exit_code == 0
    assert not outfile.exists()
    assert "Dry-run" in result.output


def test_batch_quiet(tmp_path):
    """Test batch slug generation with quiet option."""
    infile = tmp_path / "in.txt"
    outfile = tmp_path / "out.txt"
    infile.write_text("a\nb\n")
    result = runner.invoke(
        app, ["batch", "--input", str(infile), "--output", str(outfile), "--quiet"]
    )
    assert result.exit_code == 0
    assert outfile.read_text().strip().splitlines() == ["a", "b"]
    assert "→" not in result.output


@pytest.mark.parametrize("mode", ["serial", "thread", "process"])
def test_batch_file_modes(tmp_path, mode):
    """Test batch CLI with --mode for all parallelization backends."""
    file = tmp_path / "input.txt"
    file.write_text("Hello, world!\nPrivet mir\n")
    result = runner.invoke(
        app, ["batch", "--input", str(file), "--mode", mode, "--parallel"]
    )
    assert result.exit_code == 0
    assert "hello-world" in result.output
    assert "privet-mir" in result.output


@pytest.mark.parametrize(
    "mode,workers",
    [
        ("thread", 2),
        ("process", 2),
    ],
)
def test_batch_file_workers(tmp_path, mode, workers):
    """Test batch CLI with --mode and --workers."""
    file = tmp_path / "input.txt"
    file.write_text("foo\nbar\n")
    result = runner.invoke(
        app,
        [
            "batch",
            "--input",
            str(file),
            "--mode",
            mode,
            "--parallel",
            "--workers",
            str(workers),
        ],
    )
    assert result.exit_code == 0
    assert "foo" in result.output
    assert "bar" in result.output


def test_batch_file_custom_map_process(tmp_path):
    """Test batch CLI with --mode process and --custom-map."""
    file = tmp_path / "input.txt"
    file.write_text("ae oe ue\nGeia sou Kosme\n")
    cmap = '{"ä": "ae", "ö": "oe", "ü": "ue"}'
    result = runner.invoke(
        app,
        [
            "batch",
            "--input",
            str(file),
            "--mode",
            "process",
            "--parallel",
            "--custom-map",
            cmap,
        ],
    )
    assert result.exit_code == 0
    assert "ae-oe-ue" in result.output
    assert "geia" in result.output


def test_batch_file_invalid_mode(tmp_path):
    """Test batch CLI with invalid mode."""
    file = tmp_path / "input.txt"
    file.write_text("foo\n")
    result = runner.invoke(
        app, ["batch", "--input", str(file), "--mode", "invalid", "--parallel"]
    )
    assert result.exit_code != 0
    assert "Invalid value" in result.output or "Error" in result.output


def test_invalid_custom_map():
    """Test CLI with invalid custom map argument."""
    result = runner.invoke(app, ["slug", "foo", "--custom-map", "notjson"])
    assert result.exit_code != 0
    assert "Invalid JSON" in result.output or "Expecting value" in result.output


def test_single_unicode():
    """Test CLI slugifies Unicode input (accented letters)."""
    result = runner.invoke(app, ["slug", "Café au lait"])
    assert result.exit_code == 0
    slug = extract_slug(result.output)
    assert slug == "cafe-au-lait"


def test_single_emoji():
    """Test CLI slugifies emoji input."""
    result = runner.invoke(app, ["slug", "💡 emoji test"])
    assert result.exit_code == 0
    slug = extract_slug(result.output)
    assert slug == "emoji-test"


def test_version():
    """Test CLI version command."""
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "slugify" in result.output


def test_cli_no_args():
    """Test CLI with no arguments (should show help and exit)."""
    result = runner.invoke(app, [])
    assert result.exit_code == 0
    assert "Usage" in result.output or "Help" in result.output


def test_invalid_custom_map_json():
    """Test CLI with invalid custom map JSON (should print error and exit)."""
    result = runner.invoke(app, ["slug", "foo", "--custom-map", "notjson"])
    assert result.exit_code != 0
    assert "Invalid JSON" in result.output or "Expecting value" in result.output


def test_parse_custom_map_empty():
    """Test _parse_custom_map returns None for empty input."""
    from sluggi.cli import _parse_custom_map

    assert _parse_custom_map(None) is None
    assert _parse_custom_map("") is None


def test_batch_file_notfound(monkeypatch, tmp_path):
    """Test batch CLI with input file that raises FileNotFoundError."""
    from sluggi.cli import app as cli_app

    class DummyFile:
        name = "dummy.txt"

        def __iter__(self):
            raise FileNotFoundError("dummy")

    result = runner.invoke(
        cli_app, ["batch", "--input", "dummy.txt"], obj={"input_file": DummyFile()}
    )
    assert result.exit_code != 0
    assert (
        "Input file not found" in result.output
        or "Could not read input file" in result.output
        or "Error" in result.output
    )


def test_batch_file_generic_exception(monkeypatch, tmp_path):
    """Test batch CLI with input file that raises generic Exception."""
    from sluggi.cli import app as cli_app

    class DummyFile:
        name = "dummy.txt"

        def __iter__(self):
            raise Exception("fail")

    result = runner.invoke(
        cli_app, ["batch", "--input", "dummy.txt"], obj={"input_file": DummyFile()}
    )
    assert result.exit_code != 0
    assert "Could not read input file" in result.output or "Error" in result.output


def test_batch_missing_input_file():
    """Test batch CLI with missing input file (should print error and exit)."""
    result = runner.invoke(app, ["batch", "--input", "doesnotexist.txt"])
    assert result.exit_code != 0
    assert "Error" in result.output or result.output.strip() != ""


def test_batch_unwritable_output_file(tmp_path):
    """Test batch CLI with unwritable output file (should print error and exit)."""
    infile = tmp_path / "in.txt"
    outfile = tmp_path / "out.txt"
    infile.write_text("foo\nbar\n")
    outfile.write_text("")
    outfile.chmod(0o400)  # Read-only
    result = runner.invoke(
        app,
        ["batch", "--input", str(infile), "--output", str(outfile)],
    )
    assert result.exit_code != 0
    assert "Could not write to output file" in result.output


def test_batch_empty_input():
    """Test batch CLI with empty stdin input (should print error and exit).

    Accept both exit codes 0 and 1 due to Click/Typer runner behavior.
    Assert error message in output.
    """
    result = runner.invoke(app, ["batch"], input="")
    assert result.exit_code in (0, 1)
    output = result.output or ""
    assert (
        "No input provided" in output or "Aborted." in output
    ), f"Unexpected output: {output!r}"
