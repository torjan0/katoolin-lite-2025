"""Abstractions for interacting with apt safely."""
from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional

APT_SOURCES_DIR = Path("/etc/apt/sources.list.d")
KALI_SOURCE_FILE = APT_SOURCES_DIR / "katoolin-kali.list"
KALI_SOURCE_SNIPPET = "deb http://http.kali.org/kali kali-rolling main contrib non-free non-free-firmware\n"


class AptError(RuntimeError):
    """Raised when apt operations fail."""


@dataclass
class AptCommandResult:
    """Represents the result of a command execution."""

    command: List[str]
    returncode: int
    stdout: str
    stderr: str

    @property
    def succeeded(self) -> bool:
        return self.returncode == 0


class AptRunner:
    """Wraps subprocess calls to apt, enabling dry-run support."""

    def __init__(self, dry_run: bool = False) -> None:
        self.dry_run = dry_run

    def run(self, command: Iterable[str], check: bool = True) -> AptCommandResult:
        cmd = list(command)
        if self.dry_run:
            return AptCommandResult(cmd, 0, "", "")
        completed = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        if check and completed.returncode != 0:
            raise AptError(f"Command {' '.join(cmd)} failed: {completed.stderr.strip()}")
        return AptCommandResult(cmd, completed.returncode, completed.stdout, completed.stderr)

    # Convenience wrappers -------------------------------------------------

    def ensure_updated(self) -> AptCommandResult:
        return self.run(["sudo", "apt-get", "update"])

    def install_packages(self, packages: Iterable[str]) -> AptCommandResult:
        return self.run(["sudo", "apt-get", "install", "-y", *packages])

    def upgrade_packages(self, packages: Iterable[str]) -> AptCommandResult:
        return self.run(["sudo", "apt-get", "install", "--only-upgrade", "-y", *packages])


class AptSourcesManager:
    """Manage Kali repository sources safely."""

    def __init__(self, runner: Optional[AptRunner] = None) -> None:
        self.runner = runner or AptRunner()

    def source_exists(self) -> bool:
        return KALI_SOURCE_FILE.exists()

    def read_source(self) -> str:
        if not self.source_exists():
            return ""
        return KALI_SOURCE_FILE.read_text(encoding="utf-8")

    def enable_source(self, dry_run: Optional[bool] = None) -> None:
        dry = self.runner.dry_run if dry_run is None else dry_run
        if dry:
            return
        APT_SOURCES_DIR.mkdir(parents=True, exist_ok=True)
        KALI_SOURCE_FILE.write_text(KALI_SOURCE_SNIPPET, encoding="utf-8")

    def disable_source(self, dry_run: Optional[bool] = None) -> None:
        dry = self.runner.dry_run if dry_run is None else dry_run
        if dry:
            return
        if self.source_exists():
            KALI_SOURCE_FILE.unlink()

    def ensure_source(self, enable: bool) -> bool:
        """Ensure the Kali source file matches the *enable* flag.

        Returns True if a change was required.
        """

        currently_enabled = self.source_exists()
        if enable and not currently_enabled:
            self.enable_source()
            return True
        if not enable and currently_enabled:
            self.disable_source()
            return True
        return False


def get_installed_version(package: str) -> Optional[str]:
    """Return the installed version string for *package*, if any."""

    try:
        result = subprocess.run(
            ["dpkg-query", "-W", "-f=${Version}", package],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
    except FileNotFoundError as exc:  # pragma: no cover - dpkg-query unavailable
        raise AptError("dpkg-query command not found") from exc

    if result.returncode != 0:
        return None
    return result.stdout.strip() or None


def require_root() -> None:
    """Raise AptError if the current process lacks root privileges."""

    if os.geteuid() != 0:
        raise AptError("This operation requires root privileges. Re-run with sudo.")
