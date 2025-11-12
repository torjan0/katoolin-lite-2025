# katoolin-lite


A lightweight, safe-to-use reimplementation of the classic Katoolin workflow. The CLI allows you to list
Kali-inspired tool categories, enable the Kali rolling repository, and install or upgrade curated tools on
Ubuntu-based systems with minimal hassle.

## Usage

Install the package (editable install recommended during development):

```bash
pip install -e .
```

Then invoke the CLI:

```bash
katoolin-lite list
katoolin-lite repo enable
katoolin-lite install recon
katoolin-lite versions web
```

Use the `--dry-run` flag during installation commands to preview actions without executing `apt`.

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
