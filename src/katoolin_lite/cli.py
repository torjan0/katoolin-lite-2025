"""Command-line interface for katoolin-lite."""
from __future__ import annotations

import argparse
import json
import shutil
import sys
import textwrap
from typing import Iterable, List, Optional, Sequence

from . import __version__
from .apt import AptError, AptRunner, AptSourcesManager, get_installed_version, require_root
from .catalog import Category, Tool, get_category, iter_categories


RESET = "\033[0m"
PALETTE = {
    "accent": "\033[95m",
    "highlight": "\033[96m",
    "muted": "\033[90m",
    "success": "\033[92m",
    "warning": "\033[93m",
}


def colorize(text: str, tone: str, enabled: bool) -> str:
    """Apply an ANSI colour tone when enabled."""

    if not enabled:
        return text
    return f"{tone}{text}{RESET}"


def terminal_width() -> int:
    """Return the detected terminal width with sane fallbacks."""

    return max(70, shutil.get_terminal_size((100, 24)).columns)


def wrap_text(text: str, width: int) -> List[str]:
    """Wrap text without breaking long words unexpectedly."""

    if not text:
        return [""]
    return textwrap.wrap(text, width=width, break_long_words=False, break_on_hyphens=False)


def render_banner(color_enabled: bool) -> None:
    """Print a stylised banner for the CLI."""

    accent = PALETTE["accent"]
    highlight = PALETTE["highlight"]
    banner = [
        "╔═╗╔═╗╔╦╗╔═╗╔═╗╦  ╦╔═╗╦╔╦╗",
        "╠╣ ╠═╣ ║ ╠═╝║ ║║  ║║ ║║ ║ ",
        "╚  ╩ ╩ ╩ ╩  ╚═╝╩═╝╩╚═╝╩ ╩ ",
    ]
    for line in banner:
        print(colorize(line, accent, color_enabled))
    tagline = "Curated Kali tooling for Ubuntu • respect to torjan0"
    print(colorize(tagline, highlight, color_enabled))
    legend = "Legend: ✅ installed • ⬡ not installed • ⚙️ auto updates • 🛠 manual updates"
    print(colorize(legend, PALETTE["muted"], color_enabled))


def render_category_card(entry: dict, color_enabled: bool) -> None:
    """Render a single category with a bordered card layout."""

    width = min(terminal_width(), 110)
    inner_width = width - 2
    accent = PALETTE["accent"]

    top_border = "╭" + "─" * inner_width + "╮"
    mid_border = "├" + "─" * inner_width + "┤"
    bottom_border = "╰" + "─" * inner_width + "╯"
    print(colorize(top_border, accent, color_enabled))
    title = f" {entry['name']} [{entry['key']}] "
    title_line = title.center(inner_width)
    print(colorize(f"│{title_line}│", accent, color_enabled))
    print(colorize(mid_border, accent, color_enabled))

    for line in wrap_text(entry["description"], inner_width - 2):
        print(_box_line(f" {line}", inner_width, color_enabled))

    print(_box_line("", inner_width, color_enabled))

    for tool in entry["tools"]:
        packages = ", ".join(tool["packages"])
        status_icon = "✅" if tool["version"] else "⬡"
        updates_icon = "⚙️" if tool["updates"] == "auto" else "🛠"
        version_info = tool["version"] or "not installed"
        updates_label = f"{updates_icon} {tool['updates']} updates"
        header = f"{status_icon} {tool['name']} [{packages}]"
        for line in wrap_text(header, inner_width - 2):
            print(_box_line(f" {line}", inner_width, color_enabled))
        detail = f"↳ {tool['description']}"
        for line in wrap_text(detail, inner_width - 2):
            print(_box_line(f" {line}", inner_width, color_enabled))
        status = f"↳ {version_info} • {updates_label}"
        for line in wrap_text(status, inner_width - 2):
            print(_box_line(f" {line}", inner_width, color_enabled))
        print(_box_line("", inner_width, color_enabled))

    print(colorize(bottom_border, accent, color_enabled))


def _box_line(content: str, inner_width: int, color_enabled: bool) -> str:
    """Return a formatted line with coloured vertical borders."""

    padded = content.ljust(inner_width)
    left = colorize("│", PALETTE["accent"], color_enabled)
    right = colorize("│", PALETTE["accent"], color_enabled)
    return f"{left}{padded}{right}"


def render_fancy_list(payload: List[dict], color_enabled: bool) -> None:
    """Render the category list with banners and cards."""

    if not payload:
        render_banner(color_enabled)
        warning = "No tools match the current filters."
        print(colorize(warning, PALETTE["warning"], color_enabled))
        return

    render_banner(color_enabled)
    total_categories = len(payload)
    total_tools = sum(len(entry["tools"]) for entry in payload)
    summary = f"{total_categories} categories • {total_tools} curated tools"
    print(colorize(summary, PALETTE["highlight"], color_enabled))
    print()
    for index, entry in enumerate(payload):
        if index:
            print()
        render_category_card(entry, color_enabled)


def render_plain_list(payload: List[dict]) -> None:
    """Render a simplified list output (legacy style)."""

    for entry in payload:
        print(f"[{entry['key']}] {entry['name']} - {entry['description']}")
        for tool in entry["tools"]:
            version_info = tool["version"] or "not installed"
            update_label = "automatic" if tool["updates"] == "auto" else "manual"
            print(
                f"  - {tool['name']} ({', '.join(tool['packages'])})"
                f" :: {tool['description']} :: {version_info} :: {update_label} updates"
            )


def render_versions_table(headers: Sequence[str], rows: List[Sequence[str]], color_enabled: bool) -> None:
    """Render versions in a boxed table layout."""

    accent = PALETTE["accent"]
    widths = [len(header) for header in headers]
    for row in rows:
        widths = [max(width, len(cell)) for width, cell in zip(widths, row)]

    def border(left: str, fill: str, sep: str, right: str) -> str:
        segments = [colorize(fill * (width + 2), accent, color_enabled) for width in widths]
        left_col = colorize(left, accent, color_enabled)
        right_col = colorize(right, accent, color_enabled)
        sep_col = colorize(sep, accent, color_enabled)
        return left_col + sep_col.join(segments) + right_col

    def row_line(cells: Sequence[str]) -> str:
        parts = []
        for cell, width in zip(cells, widths):
            parts.append(f" {cell.ljust(width)} ")
        border_piece = colorize("│", accent, color_enabled)
        return border_piece + border_piece.join(parts) + border_piece

    header_border = border("┏", "━", "┯", "┓")
    row_border = border("┠", "─", "┼", "┨")
    footer_border = border("┗", "━", "┷", "┛")
    print(header_border)

    header_cells = [header.center(width) for header, width in zip(headers, widths)]
    header_cells = [colorize(cell, PALETTE["highlight"], color_enabled) for cell in header_cells]
    print(row_line(header_cells))
    print(row_border)

    for row in rows:
        padded = [cell.ljust(width) for cell, width in zip(row, widths)]
        print(row_line(padded))

    print(footer_border)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="katoolin-lite",
        description="Manage Kali tooling categories on Ubuntu safely.",
    )
    parser.add_argument("--version", action="version", version=f"katoolin-lite {__version__}")
    parser.add_argument("--dry-run", action="store_true", help="Print actions without executing apt commands")
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable ANSI colour output even when the terminal supports it",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", help="List available categories and tools")
    list_parser.add_argument(
        "category",
        nargs="?",
        help="If provided, list only this category and its tools",
    )
    list_parser.add_argument(
        "--json",
        action="store_true",
        help="Output the listing as JSON for automation",
    )
    list_parser.add_argument(
        "--only-installed",
        action="store_true",
        help="Only display tools with an installed version",
    )
    list_parser.add_argument(
        "--plain",
        action="store_true",
        help="Disable the stylised renderer and use legacy text output",
    )

    install_parser = subparsers.add_parser("install", help="Install all tools for a category")
    install_parser.add_argument("category", help="Category key to install")
    install_parser.add_argument(
        "--upgrade",
        action="store_true",
        help="Attempt an in-place upgrade when tools are already installed",
    )

    repo_parser = subparsers.add_parser("repo", help="Manage Kali repository sources")
    repo_sub = repo_parser.add_subparsers(dest="repo_command", required=True)
    repo_enable = repo_sub.add_parser("enable", help="Enable the Kali rolling repository")
    repo_enable.add_argument(
        "--disable",
        action="store_true",
        help="Disable instead of enable (useful for toggling quickly)",
    )
    repo_sub.add_parser("status", help="Show whether the Kali repository is configured")

    version_parser = subparsers.add_parser("versions", help="Show installed versions for tools in a category")
    version_parser.add_argument("category", nargs="?", help="Category key to inspect")
    version_parser.add_argument(
        "--plain",
        action="store_true",
        help="Disable the stylised table output",
    )

    return parser


def list_categories(
    *,
    category: Optional[str],
    only_installed: bool,
    as_json: bool,
    fancy: bool,
    color_enabled: bool,
) -> int:
    categories: Iterable[Category]
    if category:
        try:
            categories = [get_category(category)]
        except KeyError as exc:
            print(str(exc), file=sys.stderr)
            return 1
    else:
        categories = iter_categories()

    payload = []
    for cat in categories:
        tools_payload = []
        for tool in cat.tools:
            version = resolve_tool_version(tool)
            if only_installed and version is None:
                continue
            tools_payload.append(
                {
                    "name": tool.name,
                    "packages": tool.packages,
                    "description": tool.description,
                    "updates": tool.labels(),
                    "version": version,
                }
            )
        if only_installed and not tools_payload:
            continue
        payload.append(
            {
                "key": lookup_category_key(cat),
                "name": cat.name,
                "description": cat.description,
                "tools": tools_payload,
            }
        )

    if as_json:
        json.dump(payload, sys.stdout, indent=2)
        sys.stdout.write("\n")
    else:
        if not payload:
            message = "No tools match the current filters."
            if fancy:
                render_fancy_list([], color_enabled)
            else:
                print(message)
            return 0
        if fancy:
            render_fancy_list(payload, color_enabled)
        else:
            render_plain_list(payload)
    return 0


def lookup_category_key(category: Category) -> str:
    for key, value in iter_categories_with_keys():
        if value is category:
            return key
    raise ValueError("Category not found in catalog")


def iter_categories_with_keys():
    from .catalog import CATALOG

    return CATALOG.items()


def resolve_tool_version(tool: Tool) -> Optional[str]:
    versions: List[str] = []
    for package in tool.packages:
        version = get_installed_version(package)
        if version:
            versions.append(version)
    if not versions:
        return None
    return ", ".join(sorted(set(versions)))


def handle_install(category_key: str, *, upgrade: bool, dry_run: bool) -> int:
    try:
        category = get_category(category_key)
    except KeyError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    runner = AptRunner(dry_run=dry_run)
    sources = AptSourcesManager(runner=runner)

    try:
        require_root()
        if not sources.source_exists():
            print("Kali repository is not enabled. Use 'katoolin-lite repo enable' first.", file=sys.stderr)
            return 2
    except AptError as exc:
        print(exc, file=sys.stderr)
        return 1

    packages = sorted({pkg for tool in category.tools for pkg in tool.packages})
    versions_before = {pkg: get_installed_version(pkg) for pkg in packages}

    runner.ensure_updated()
    if upgrade:
        runner.upgrade_packages(packages)
    else:
        runner.install_packages(packages)

    for tool in category.tools:
        version = resolve_tool_version(tool)
        upgrade_label = "automatic" if tool.auto_updates else "manual"
        prev_versions = {versions_before[pkg] for pkg in tool.packages}
        if None in prev_versions:
            prev_versions.discard(None)
        prev_display = ", ".join(sorted(prev_versions)) or "not installed"
        print(
            f"{tool.name}: {prev_display} -> {version or 'not installed'} ({upgrade_label} updates)"
        )
    return 0


def handle_repo(command: str, *, toggle_disable: bool, dry_run: bool) -> int:
    runner = AptRunner(dry_run=dry_run)
    sources = AptSourcesManager(runner=runner)

    if command == "status":
        state = "enabled" if sources.source_exists() else "disabled"
        print(f"Kali repository is {state}.")
        return 0

    target_state = not toggle_disable
    try:
        require_root()
    except AptError as exc:
        print(exc, file=sys.stderr)
        return 1

    changed = sources.ensure_source(target_state)
    label = "enabled" if target_state else "disabled"
    if changed:
        print(f"Kali repository {label}.")
    else:
        print(f"Kali repository already {label}.")
    return 0


def handle_versions(
    category: Optional[str], *, fancy: bool, color_enabled: bool
) -> int:
    categories: Iterable[Category]
    if category:
        try:
            categories = [get_category(category)]
        except KeyError as exc:
            print(str(exc), file=sys.stderr)
            return 1
    else:
        categories = iter_categories()

    categories = list(categories)

    rows: List[Sequence[str]] = []
    plain_payload = []
    for cat in categories:
        key = lookup_category_key(cat)
        tools_payload = []
        for tool in cat.tools:
            version = resolve_tool_version(tool) or "not installed"
            update_policy = "automatic" if tool.auto_updates else "manual"
            rows.append((key, tool.name, version, update_policy))
            tools_payload.append((tool.name, version, update_policy))
        plain_payload.append((key, cat.name, tools_payload))

    if fancy:
        if rows:
            render_versions_table(("Category", "Tool", "Version", "Updates"), rows, color_enabled)
        else:
            warning = "No tools available for the requested category."
            print(colorize(warning, PALETTE["warning"], color_enabled))
    else:
        for key, name, tools in plain_payload:
            print(f"[{key}] {name}")
            for tool_name, version, update_policy in tools:
                print(f"  - {tool_name}: {version} ({update_policy} updates)")
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    color_enabled = not args.no_color and sys.stdout.isatty()

    if args.command == "list":
        return list_categories(
            category=args.category,
            only_installed=args.only_installed,
            as_json=args.json,
            fancy=not args.plain and not args.json,
            color_enabled=color_enabled,
        )
    if args.command == "install":
        return handle_install(args.category, upgrade=args.upgrade, dry_run=args.dry_run)
    if args.command == "repo":
        if args.repo_command == "enable":
            return handle_repo("enable", toggle_disable=args.disable, dry_run=args.dry_run)
        if args.repo_command == "status":
            return handle_repo("status", toggle_disable=False, dry_run=args.dry_run)
    if args.command == "versions":
        return handle_versions(
            args.category,
            fancy=not args.plain,
            color_enabled=color_enabled,
        )

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
