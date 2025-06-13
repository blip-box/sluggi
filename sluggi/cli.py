"""CLI for sluggi: Modern Python slugification tool.

Provides commands for single and batch slugification, with Unicode, emoji, and
parallel processing support.
"""

import json
import sys
from typing import Optional

import typer
from rich.console import Console

from . import __version__

app = typer.Typer(
    name="sluggi",
    help=(
        "sluggi: Modern, high-performance Python slugification CLI.\n\n"
        "Features:\n"
        "  • Unicode, emoji, and multilingual support\n"
        "  • Batch and parallel processing\n"
        "  • Custom character mappings\n"
        "  • Colorized, user-friendly output\n\n"
        "Examples:\n"
        "  sluggi slug 'Café déjà vu!'\n"
        "  sluggi slug 'Привет мир' --separator _\n"
        "  sluggi batch --input names.txt --output slugs.txt\n"
        "  echo 'emoji 🚀' | sluggi batch --parallel --mode process\n\n"
        "[Encoding]\n"
        "  Input and output files must be UTF-8 encoded.\n"
        "  On Windows, use a UTF-8 capable terminal or set PYTHONUTF8=1.\n\n"
        "Documentation: https://github.com/blip-box/sluggi"
    ),
)
app.name = "sluggi"  # Ensure compatibility with Click/Typer test runner
app.main = app  # Workaround for Click/Typer test runner expecting .main

console = Console()

single_separator = typer.Option(
    "-",
    "--separator",
    "-s",
    help="Separator for words in the slug (default: '-')",
)
single_stopwords = typer.Option(
    None,
    "--stopwords",
    help="Comma-separated words to exclude from slug (e.g. 'and,the,of').",
)
# trailing comma not needed here
single_custom_map = typer.Option(
    None,
    "--custom-map",
    help='Custom mapping as JSON, e.g. \'{"ä": "ae"}\'',
)

single_word_regex = typer.Option(
    None,
    "--word-regex",
    help=r"Custom regex pattern for word extraction (default: '\w+').",
)
single_max_length = typer.Option(
    None,
    "--max-length",
    "-m",
    help="Maximum length for the slug (truncate_slug, optional).",
)
single_word_boundary = typer.Option(
    True,
    "--word-boundary/--no-word-boundary",
    help="Truncate at word boundary (default: True).",
)
single_no_lowercase = typer.Option(
    False,
    "--no-lowercase",
    help="Preserve capitalization in the slug (default: False).",
)


@app.command()
def slug(
    text: str = typer.Argument(
        None,
        help="Text to slugify. If omitted, reads from stdin or --input file.",
    ),
    input: Optional[str] = typer.Option(
        None, "--input", "-i", help="Input file (overrides text/stdin)"
    ),
    output: Optional[str] = typer.Option(
        None, "--output", "-o", help="Output file (writes slug result)"
    ),
    process_emoji: bool = typer.Option(
        False,
        "--process-emoji/--no-process-emoji",
        help="Enable emoji-to-name conversion (default: off)",
    ),
    separator: str = single_separator,
    max_length: Optional[int] = single_max_length,
    word_boundary: bool = single_word_boundary,
    stopwords: Optional[str] = single_stopwords,
    regex: Optional[str] = typer.Option(
        None, "--regex", help="Custom regex for word extraction"
    ),
    no_lowercase: bool = single_no_lowercase,
    custom_map: Optional[str] = typer.Option(
        None, "--custom-map", help='Custom mapping as JSON, e.g. \'{"ä": "ae"}\''
    ),
    decode_entities: bool = typer.Option(
        True,
        "--decode-entities/--no-decode-entities",
        help="Decode HTML entities (default: on)",
    ),
    decode_decimal: bool = typer.Option(
        True,
        "--decode-decimal/--no-decode-decimal",
        help="Decode decimal numeric refs (default: on)",
    ),
    decode_hexadecimal: bool = typer.Option(
        True,
        "--decode-hexadecimal/--no-decode-hexadecimal",
        help="Decode hexadecimal numeric refs (default: on)",
    ),
):
    """Slugify a single string and print the result.

    Args:
        text (str): The input string to slugify.
        input (str, optional): Input file (overrides text/stdin).
        output (str, optional): Output file (writes slug result).
        process_emoji (bool, optional): Enable emoji-to-name conversion (default: off).
        transliterate (bool, optional): Enable transliteration (default: on).
        separator (str, optional): Separator for words in the slug (default: '-').
        max_length (int, optional): Maximum length for the slug (truncate_slug).
        word_boundary (bool, optional): Truncate at word boundary (default: True).
        save_order (bool, optional): Preserve word order when truncating.
        stopwords (str, optional): Comma-separated words to exclude from slug.
        regex (str, optional): Custom regex for allowed characters.
        no_lowercase (bool, optional): Preserve capitalization in the slug
            (default: False).
        replacements (str, optional): Custom replacements, e.g. 'old1:new1,old2:new2'.
        allow_unicode (bool, optional): Allow unicode in output.
        custom_map (str, optional): Custom mapping as JSON, e.g. '{"ä": "ae"}'.
        decode_decimal (bool, optional): Decode decimal numeric refs (default: on).
        decode_entities (bool, optional): Decode HTML entities (default: on).
        decode_hexadecimal (bool, optional): Decode hexadecimal numeric refs
            (default: on).

    Examples:
        sluggi slug "Café déjà vu!"
        sluggi slug "Привет мир" --separator _
        sluggi slug "ä ö ü" --custom-map '{"ä": "ae", "ö": "oe", "ü": "ue"}'
        sluggi slug "the quick brown fox" --stopwords "the,fox"
        sluggi slug "long example sentence" --max-length 15 \
            --word-boundary --no-save-order

    """
    # Determine input text
    if input:
        with open(input, encoding="utf-8") as f:
            text = f.read().strip()
    elif text is None:
        text = sys.stdin.read().strip()

    # Parse stopwords
    stopwords_list = (
        [w.strip() for w in stopwords.split(",") if w.strip()] if stopwords else None
    )
    cmap = None
    if custom_map:
        import json

        try:
            cmap = json.loads(custom_map)
        except Exception as e:
            console.print(f"[bold red]Invalid JSON for custom_map: {e}[/bold red]")
            raise typer.Exit(1) from e

    # Call slugify with only valid arguments
    from . import slugify as _slugify

    result = _slugify(
        text,
        separator=separator,
        custom_map=cmap,
        stopwords=stopwords_list,
        lowercase=not no_lowercase,
        word_regex=regex,
        decode_entities=decode_entities,
        decode_decimal=decode_decimal,
        decode_hexadecimal=decode_hexadecimal,
        max_length=max_length,
        word_boundary=word_boundary,
        process_emoji=process_emoji,
    )
    if output:
        with open(output, "w", encoding="utf-8") as f:
            f.write(result + "\n")
    else:
        console.print(result)


@app.command()
def bench():
    """Run benchmarking tests for slugify."""
    # TODO: implement benchmarking tests
    console.print("Benchmarking tests not implemented yet.")


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        is_eager=True,
        help="Show version and exit.",
    ),
):
    """Modern Python CLI for generating clean, URL-safe slugs from text or files.

    Use `sluggi --help` or `sluggi <command> --help` for detailed usage.
    """
    if version:
        typer.echo(f"slugify v{__version__}")
        raise typer.Exit(code=0)
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit(code=0)


@app.command()
def version():
    """Show the installed sluggi version and exit."""
    typer.echo(f"slugify v{__version__}")


batch_input_file = typer.Option(
    None,
    "--input",
    "-i",
    help="Input file (one string per line, UTF-8). Reads from stdin if omitted.",
)
batch_separator = typer.Option(
    "-",
    "--separator",
    "-s",
    help="Separator for words in the slug (default: '-')",
)
batch_stopwords = typer.Option(
    None,
    "--stopwords",
    help="Comma-separated words to exclude from slug (e.g. 'and,the,of').",
)
batch_custom_map = typer.Option(
    None,
    "--custom-map",
    help='Custom mapping as JSON, e.g. \'{"ä": "ae"}\'',
)
batch_output = typer.Option(
    None,
    "--output",
    "-o",
    help="Output file for slugs (one per line, UTF-8 encoded).",
)
batch_dry_run = typer.Option(
    False,
    "--dry-run",
    help="Show what would be written, but do not write output file.",
)
batch_quiet = typer.Option(
    False,
    "--quiet",
    help="Suppress preview output to terminal.",
)
batch_parallel = typer.Option(
    False,
    "--parallel",
    help="Enable parallel processing for batch slugification.",
)
batch_workers = typer.Option(
    None,
    "--workers",
    help=(
        "Number of parallel workers (default: min(32, cpu_count+4)). "
        "Only used if --parallel is set."
    ),
)
batch_mode = typer.Option(
    "thread",
    "--mode",
    help=(
        "Parallel mode: 'thread' (default), 'process', or 'serial'. "
        "Use 'process' for true CPU parallelism."
    ),
)


def _validate_mode(mode: str) -> None:
    """Validate that the mode is one of the supported options.

    Args:
        mode (str): The mode to validate ('thread', 'process', or 'serial').

    Raises:
        typer.Exit: If the mode is invalid.

    """
    valid_modes = {"thread", "process", "serial"}
    if mode not in valid_modes:
        console.print(
            f"[red]Error: --mode must be one of {valid_modes}, got '{mode}'.[/red]",
        )
        raise typer.Exit(1)


def _parse_custom_map(custom_map: Optional[str]) -> Optional[dict]:
    """Parse a custom mapping string as JSON, or return None if not provided.

    Args:
        custom_map (str, optional): JSON string mapping characters.

    Returns:
        dict or None: The parsed mapping or None.

    Raises:
        typer.Exit: If the JSON is invalid.

    """
    cmap = None
    if custom_map:
        try:
            cmap = json.loads(custom_map)
        except Exception as e:
            console.print(f"[bold red]Invalid JSON for custom_map: {e}[/bold red]")
            raise typer.Exit(1) from e
    return cmap


def _read_input_lines(input_file: Optional[typer.FileText]) -> list[str]:
    """Read lines from the input file or stdin.

    Args:
        input_file (typer.FileText, optional): File object to read from.

    Returns:
        list[str]: List of input lines.

    Raises:
        typer.Exit: If the file cannot be read.

    """
    lines = []
    if input_file:
        try:
            lines = [line.rstrip("\n") for line in input_file]
        except Exception as e:
            console.print(f"[bold red]Could not read input file: {e}[/bold red]")
            raise typer.Exit(1) from e
    else:
        if not batch_quiet:
            console.print("[cyan]Enter lines to slugify (Ctrl-D to end):[/cyan]")
        lines = [line.rstrip("\n") for line in sys.stdin]
    return lines


def _write_output_file(output: str, results: list[str], dry_run: bool) -> None:
    """Write slugified results to the output file if not a dry run.

    Args:
        output (str): Path to the output file.
        results (list[str]): List of slugified strings.
        dry_run (bool): If True, do not write output file.

    Raises:
        typer.Exit: If the file cannot be written.

    """
    if output and not dry_run:
        try:
            with open(output, "w", encoding="utf-8") as f:
                for slug in results:
                    f.write(slug + "\n")
        except Exception as e:
            console.print(f"[bold red]Could not write to output file: {e}[/bold red]")
            raise typer.Exit(1) from e


def _display_results(
    lines: list[str],
    results: list[str],
    output: str,
    quiet: bool,
    dry_run: bool,
    output_format: str = None,
    display_output: bool = False,
) -> None:
    """Display the slugification results in the terminal.

    Args:
        lines (list[str]): Original input lines.
        results (list[str]): Corresponding slugified results.
        output (str): Output file path (if any).
        quiet (bool): If True, suppress terminal output.
        dry_run (bool): If True, do not write output file.
        output_format (str, optional): Custom output format string.
        display_output (bool, optional): Display as rich table.

    """
    if quiet:
        return
    if display_output:
        from rich.table import Table

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Original", style="yellow")
        table.add_column("Slug", style="green")
        for orig, slug in zip(lines, results):
            table.add_row(orig, slug)
        console.print(table)
        console.print(
            f"[bold blue]Processed {len(lines)} line"
            f"{'s' if len(lines) != 1 else ''}.[/bold blue]",
        )
        # Always print these status messages, even if quiet is True,
        # to match test expectations
    if output:
        if dry_run:
            console.print(f"Dry-run: Output would be written to {output}")
        else:
            console.print(f"Slugs written to {output}")
    elif output_format:
        for i, (orig, slug) in enumerate(zip(lines, results), 1):
            out = output_format.format(slug=slug, original=orig, line_num=i)
            console.print(out)
    elif not quiet:
        for slug in results:
            console.print(slug)


batch_word_regex = typer.Option(
    None,
    "--word-regex",
    help="Custom regex pattern for word extraction (default: '\\w+').",
)

batch_max_length = typer.Option(
    None,
    "--max-length",
    "-m",
    help="Maximum length for each slug (truncate_slug, optional).",
)

batch_word_boundary = typer.Option(
    True,
    "--word-boundary/--no-word-boundary",
    help="Truncate at word boundary (default: True).",
)

batch_output_format = typer.Option(
    None,
    "--output-format",
    help=(
        "Custom output format using {slug}, {original}, {line_num}. "
        "Default: just the slug."
    ),
)

batch_display_output = typer.Option(
    False,
    "--display-output",
    help="Display results as a rich table in the console after batch processing.",
)

batch_no_lowercase = typer.Option(
    False,
    "--no-lowercase",
    help="Preserve capitalization in the slug (default: False).",
)

batch_process_emoji = typer.Option(
    False,
    "--process-emoji/--no-process-emoji",
    help="Enable emoji-to-name conversion (default: off)",
)


@app.command()
def batch(
    input_file: Optional[typer.FileText] = batch_input_file,
    separator: str = batch_separator,
    custom_map: Optional[str] = batch_custom_map,
    stopwords: Optional[str] = batch_stopwords,
    output: Optional[str] = batch_output,
    dry_run: bool = batch_dry_run,
    quiet: bool = batch_quiet,
    parallel: bool = batch_parallel,
    workers: Optional[int] = batch_workers,
    mode: str = batch_mode,
    word_regex: Optional[str] = batch_word_regex,
    max_length: Optional[int] = batch_max_length,
    word_boundary: bool = batch_word_boundary,
    no_lowercase: bool = batch_no_lowercase,
    output_format: Optional[str] = batch_output_format,
    display_output: bool = batch_display_output,
    process_emoji: bool = batch_process_emoji,
) -> None:
    r"""Slugify many strings from a file or stdin, with optional output and
    parallel processing.

    Args:
        input_file (file, optional): File with one string per line (UTF-8).
            Reads from stdin if omitted.
        separator (str, optional): Separator for words in the slug (default: '-').
        custom_map (str, optional): Custom mapping as JSON, e.g. '{"ä": "ae"}'.
        stopwords (str, optional): Comma-separated words to exclude from slug.
        output (str, optional): Output file for slugs.
        dry_run (bool, optional): If True, do not write output file.
        quiet (bool, optional): Suppress terminal output.
        parallel (bool, optional): Enable parallel processing.
        workers (int, optional): Number of parallel workers.
        mode (str, optional): 'thread', 'process', or 'serial'.
        word_regex (str, optional): Custom regex pattern for word extraction
            (default: '\w+').
        max_length (int, optional): Maximum length for each slug (truncate_slug).
        word_boundary (bool, optional): Truncate at word boundary (default: True).
        no_lowercase (bool, optional): Preserve capitalization in the slug
            (default: False).
        output_format (str, optional): Custom output format using {slug},
            {original}, {line_num}.
        display_output (bool, optional): Display results as a rich table in the
            console after batch processing.
        process_emoji (bool, optional): Enable emoji-to-name conversion
            (default: False).

    Returns:
        None

    """
    _validate_mode(mode)
    cmap = _parse_custom_map(custom_map)
    # Read input lines
    lines = _read_input_lines(input_file)
    import sys

    print(f"DEBUG: lines={lines!r}", file=sys.stderr)
    if not lines or all(not line.strip() for line in lines):
        import sys

        sys.stderr.write("No input provided\n")
        sys.exit(1)
    stopwords_list = (
        [w.strip() for w in stopwords.split(",") if w.strip()] if stopwords else None
    )
    from . import batch_slugify as _batch_slugify

    results = _batch_slugify(
        lines,
        separator=separator,
        stopwords=stopwords_list,
        word_regex=word_regex,
        lowercase=not no_lowercase,
        max_length=max_length,
        word_boundary=word_boundary,
        process_emoji=process_emoji,
        custom_map=cmap,
        parallel=parallel,
        workers=workers,
        mode=mode,
    )
    _display_results(
        lines,
        results,
        output,
        quiet,
        dry_run,
        output_format=output_format,
        display_output=display_output,
    )

    if output and not dry_run:
        _write_output_file(output, results, dry_run)
        if display_output:
            from rich.table import Table

            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Original", style="yellow")
            table.add_column("Slug", style="green")
            for orig, slug in zip(lines, results):
                table.add_row(orig, slug)
            console.print(table)
            console.print(
                f"[bold blue]Processed {len(lines)} line"
                f"{'s' if len(lines) != 1 else ''}.[/bold blue]",
            )


@app.command()
def info():
    """Display package and environment info with a stylish ASCII logo."""
    import platform

    from rich.table import Table

    from . import __version__

    ascii_logo = """

███████╗██╗     ██╗   ██╗ ██████╗  ██████╗ ██╗
██╔════╝██║     ██║   ██║██╔════╝ ██╔════╝ ██║
███████╗██║     ██║   ██║██║  ███╗██║  ███╗██║
╚════██║██║     ██║   ██║██║   ██║██║   ██║██║
███████║███████╗╚██████╔╝╚██████╔╝╚██████╔╝██║
╚══════╝╚══════╝ ╚═════╝  ╚═════╝  ╚═════╝ ╚═╝

"""

    console.print(ascii_logo, style="bright_green")

    info_table = Table(show_header=False, box=None, pad_edge=False)
    info_table.add_row("[bold]Version[/bold]", f"[cyan]{__version__}[/cyan]")
    info_table.add_row(
        "[bold]Python[/bold]", f"[cyan]{platform.python_version()}[/cyan]"
    )
    info_table.add_row(
        "[bold]Platform[/bold]",
        f"[cyan]{platform.system()} {platform.release()}[/cyan]",
    )
    info_table.add_row("[bold]Emoji support[/bold]", "[green]Yes[/green]")
    info_table.add_row("[bold]Transliteration[/bold]", "[green]Yes[/green]")
    console.print(info_table)

    console.print("\n")

    # Shell completion info as a Rich Table
    completion_table = Table(
        title="Shell Completion",
        show_header=True,
        header_style="bold yellow",
    )
    completion_table.add_column("Shell", style="cyan", no_wrap=True)
    completion_table.add_column("Command", style="green")
    completion_table.add_row(
        "bash",
        'eval "$(_SLUGIFY_COMPLETE=bash_source slugify)"',
    )
    completion_table.add_row(
        "zsh",
        'eval "$(_SLUGIFY_COMPLETE=zsh_source slugify)"',
    )
    completion_table.add_row(
        "fish",
        "eval (env _SLUGIFY_COMPLETE=fish_source slugify)",
    )
    console.print(completion_table)
    console.print(
        "\n[dim]See Typer docs for more: https://typer.tiangolo.com/tutorial/commands/completion/[/dim]\n"
    )


if __name__ == "__main__":
    app()
