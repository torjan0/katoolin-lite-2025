# Katoolin Lite 2025

Katoolin Lite 2025 is a re-imagining of the classic Katoolin workflow for modern Ubuntu LTS releases. The CLI focuses on a curated, reproducible installation of commonly-used offensive security tooling without permanently pinning your system to Kali Linux repositories. The project is designed to be scriptable for unattended builds while remaining friendly for occasional, interactive usage on workstations and lab machines.

## Project goals

- Provide a safe way to install individual Kali Linux tools on Ubuntu without replacing core system packages.
- Keep the catalog of tooling up to date with minimal manual intervention and transparent automation.
- Offer a consistent CLI that works well for both single-run installations and automated provisioning pipelines.
- Encourage contributions from the security community with clear testing and review practices.

## Supported Ubuntu versions

Katoolin Lite 2025 actively supports the following Ubuntu releases:

- Ubuntu 22.04 LTS (Jammy Jellyfish)
- Ubuntu 24.04 LTS (Noble Numbat)

Other Debian-based distributions may work, but they are not part of the automated test matrix. When using a non-LTS release, verify the versions of third-party repositories and PPAs manually before installation.

## Installation

1. Ensure that you have `git`, `python3` (3.10 or newer), and `pipx` installed:

   ```bash
   sudo apt update
   sudo apt install -y git python3 python3-venv pipx
   pipx ensurepath
   ```

2. Clone this repository and install the CLI through `pipx`:

   ```bash
   git clone https://github.com/max/katoolin-lite-2025.git
   cd katoolin-lite-2025
   pipx install .
   ```

   Using `pipx` keeps the CLI isolated from your system interpreter while still exposing the `katoolin-lite` command on your `PATH`. You can alternatively install into a virtual environment with `pip install .` if you prefer manual environment management.

3. Verify the installation:

   ```bash
   katoolin-lite --version
   ```

## CLI usage examples

```bash
# View the catalog of available tools grouped by category
katoolin-lite list

# Install a single tool (and its dependencies) from the catalog
katoolin-lite install metasploit

# Install every tool within the "wireless" category
katoolin-lite install --category wireless

# Remove a previously-installed tool and clean related apt sources
katoolin-lite remove burpsuite

# Check for catalog and CLI updates
katoolin-lite check-updates

# Apply all pending catalog updates and refresh apt metadata
katoolin-lite update
```

Run `katoolin-lite --help` for the complete list of commands and flags. Every command supports the `--yes` flag for non-interactive usage in automation.

## Update-check mechanism

Katoolin Lite performs a lightweight update check to keep both the CLI and tool catalog current:

1. Each release bundles a signed `tool-manifest.yml` that describes the tool catalog and its last update timestamp.
2. When you run `katoolin-lite check-updates` (or any command that mutates the catalog), the CLI retrieves the latest manifest checksum from the GitHub Releases API.
3. The checksum is compared against the locally cached copy in `~/.cache/katoolin-lite/manifest.json`. If they differ, the CLI downloads the new manifest, verifies its signature, and prompts you to apply the update.
4. For offline environments you can skip remote checks with `--offline`. The CLI will fall back to the bundled manifest and emit a warning if it is older than 30 days.

The update mechanism intentionally avoids running `apt upgrade` for you. System package upgrades should continue to be handled with your normal OS workflows.

## Manual steps for specific tools

Some tools require additional setup after installation:

- **Metasploit Framework** – Initialize the PostgreSQL database once by running `msfdb init`. You may also want to enable the `msfdb` service to start automatically with `systemctl enable --now postgresql`.
- **Burp Suite Community** – The package installs the launcher, but you must accept the license agreement on first launch. Settings are stored in `~/.BurpSuite` and can be backed up for repeat deployments.
- **Nessus Essentials** – Tenable provides the `.deb` package. After installation, browse to `https://localhost:8834/` to complete setup and request an activation code.
- **Wireless drivers (aircrack-ng suite)** – Some chipsets require manual firmware or `dkms` driver installation. Review the output of `katoolin-lite install aircrack-ng` for chipset-specific guidance.

Refer to the catalog entry for each tool to see post-installation notes and links to upstream documentation.

## Contribution guidelines

We welcome contributions! To get started:

1. Fork the repository and create a feature branch (`git checkout -b feature/my-change`).
2. Install development dependencies into a virtual environment:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -e .[dev]
   ```

3. Run the formatting and linting checks before committing:

   ```bash
   ruff check .
   black .
   mypy src
   ```

4. Execute the test suite:

   ```bash
   pytest
   ```

5. Open a pull request that describes the motivation and testing performed. Include updates to documentation or manifests when you add or change tooling.

### Testing notes

- Use `pytest -m "not network"` when running in environments without internet access.
- For commands that interact with `apt`, rely on the `apt` mocks in `tests/fixtures` to avoid modifying the host system during testing.
- Continuous integration runs formatting, linting, and unit tests on Ubuntu 22.04 and 24.04. Make sure your changes pass locally to keep CI green.

## License

Katoolin Lite 2025 is distributed under the [MIT License](./LICENSE).
