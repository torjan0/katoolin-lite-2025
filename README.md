# katoolin-lite

> Crafted with pride by **torjan0**, the original creator.

A lightweight, safe-to-use reimplementation of the classic Katoolin workflow. The CLI allows you to list
Kali-inspired tool categories, enable the Kali rolling repository, and install or upgrade curated tools on
Ubuntu-based systems with minimal hassle.

## Prerequisites

Before you run katoolin-lite, make sure the following are true:

- You are on an Ubuntu or Ubuntu-based distribution with `apt` available.
- Python 3.9+ and `pip` are installed (`sudo apt install python3 python3-pip`).
- You have superuser (sudo) access for commands that interact with the system package manager.

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/torjan0/katoolin-lite-2025.git
   cd katoolin-lite-2025
   ```

2. Install the package. During development an editable install is convenient:

   ```bash
   pip install --upgrade pip
   pip install -e .
   ```

3. Confirm the CLI is on your PATH:

   ```bash
   katoolin-lite --help
   ```

   If the command is not found, ensure that your Python `bin` directory (for example,
   `~/.local/bin`) is present in your `PATH`.

## Using the CLI

The CLI is organised around **categories** of tools. Each subcommand includes friendly, colourised
output by default; append `--plain` if you prefer basic text.

### Explore the catalog

- View a quick summary of all categories:

  ```bash
  katoolin-lite list
  ```

- Inspect detailed metadata (version info, repository, manual upgrade notes) in JSON form:

  ```bash
  katoolin-lite list --json
  ```

### Manage the Kali repository

Some tools require the Kali rolling repository. Enable or disable it safely with:

```bash
sudo katoolin-lite repo enable    # backs up sources.list and adds the Kali entry
sudo katoolin-lite repo disable   # restores your previous sources.list
```

### Install tools by category

The installer resolves Ubuntu/Kali package names and can perform dry runs:

```bash
sudo katoolin-lite install recon          # install all reconnaissance tools
sudo katoolin-lite install web --tool wfuzz  # install a single tool from a category
sudo katoolin-lite install wireless --dry-run # preview actions without apt changes
```

### Check installed versions

Use the `versions` command to learn whether tools are installed, their available package versions,
and any manual upgrade requirements noted in the catalog:

```bash
katoolin-lite versions exploitation
```

Entries marked with "manual" in the output indicate that the upstream project requires
manual updates beyond `apt`. The CLI highlights these cases so that you can schedule follow-up
maintenance.

## Catalog overview

The curated catalog emphasises actively maintained, diverse tooling across offensive and defensive
disciplines. Categories currently include:

- Reconnaissance
- Web
- Exploitation
- Post-Exploitation
- Wireless
- Password Attacks
- Forensics
- Reverse Engineering

Run `katoolin-lite list --json` for the authoritative list of tools and metadata, including which
entries require manual upgrades. The human-friendly renderer adds colourful banners, emoji status
indicators, category summaries, and other flair when executed in a capable terminal.
