"""Command-line interface for katoolin-lite."""
from __future__ import annotations

import argparse
import json
import sys
from typing import Iterable, List, Optional

from . import __version__
from .apt import AptError, AptRunner, AptSourcesManager, get_installed_version, require_root
from .catalog import Category, Tool, get_category, iter_categories


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="katoolin-lite",
        description="Manage Kali tooling categories on Ubuntu safely.",
    )
    parser.add_argument("--version", action="version", version=f"katoolin-lite {__version__}")
    parser.add_argument("--dry-run", action="store_true", help="Print actions without executing apt commands")

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

    return parser


def list_categories(
    *,
    category: Optional[str],
    only_installed: bool,
    as_json: bool,
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
        for entry in payload:
            print(f"[{entry['key']}] {entry['name']} - {entry['description']}")
            for tool in entry["tools"]:
                version_info = tool["version"] or "not installed"
                update_label = "automatic" if tool["updates"] == "auto" else "manual"
                print(
                    f"  - {tool['name']} ({', '.join(tool['packages'])})"
                    f" :: {tool['description']}"
                    f" :: {version_info} :: {update_label} updates"
                )
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


def handle_versions(category: Optional[str]) -> int:
    categories: Iterable[Category]
    if category:
        try:
            categories = [get_category(category)]
        except KeyError as exc:
            print(str(exc), file=sys.stderr)
            return 1
    else:
        categories = iter_categories()

    for cat in categories:
        print(f"[{lookup_category_key(cat)}] {cat.name}")
        for tool in cat.tools:
            version = resolve_tool_version(tool) or "not installed"
            update_policy = "automatic" if tool.auto_updates else "manual"
            print(f"  - {tool.name}: {version} ({update_policy} updates)")
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "list":
        return list_categories(
            category=args.category,
            only_installed=args.only_installed,
            as_json=args.json,
        )
    if args.command == "install":
        return handle_install(args.category, upgrade=args.upgrade, dry_run=args.dry_run)
    if args.command == "repo":
        if args.repo_command == "enable":
            return handle_repo("enable", toggle_disable=args.disable, dry_run=args.dry_run)
        if args.repo_command == "status":
            return handle_repo("status", toggle_disable=False, dry_run=args.dry_run)
    if args.command == "versions":
        return handle_versions(args.category)

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
