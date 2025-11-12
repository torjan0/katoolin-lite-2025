"""Catalog definitions for katoolin-lite."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List


@dataclass(frozen=True)
class Tool:
    """Represents an installable tool entry."""

    name: str
    packages: List[str]
    description: str
    auto_updates: bool = True

    def labels(self) -> str:
        """Return a short label to describe update behaviour."""

        return "auto" if self.auto_updates else "manual"


@dataclass(frozen=True)
class Category:
    """Represents a tool category."""

    name: str
    tools: List[Tool]
    description: str

    def tool_names(self) -> Iterable[str]:
        return (tool.name for tool in self.tools)


CATALOG: Dict[str, Category] = {
    "recon": Category(
        name="Reconnaissance",
        description="Network and host discovery tooling.",
        tools=[
            Tool(
                name="nmap",
                packages=["nmap"],
                description="Versatile network scanner",
            ),
            Tool(
                name="masscan",
                packages=["masscan"],
                description="Mass IP port scanner",
            ),
            Tool(
                name="dnsenum",
                packages=["dnsenum"],
                description="DNS enumeration utility",
            ),
            Tool(
                name="amass",
                packages=["amass"],
                description="In-depth attack surface mapping suite",
            ),
            Tool(
                name="theharvester",
                packages=["theharvester"],
                description="Search engine and OSINT harvester",
            ),
            Tool(
                name="recon-ng",
                packages=["recon-ng"],
                description="Modular OSINT reconnaissance framework",
            ),
            Tool(
                name="sublist3r",
                packages=["python3-sublist3r"],
                description="Fast subdomain enumeration tool",
            ),
            Tool(
                name="dnsrecon",
                packages=["dnsrecon"],
                description="DNS reconnaissance utility with brute forcing",
            ),
        ],
    ),
    "web": Category(
        name="Web",
        description="Web vulnerability analysis and exploitation.",
        tools=[
            Tool(
                name="nikto",
                packages=["nikto"],
                description="Web server scanner",
            ),
            Tool(
                name="wfuzz",
                packages=["wfuzz"],
                description="Web application brute forcer",
            ),
            Tool(
                name="burpsuite",
                packages=["burpsuite"],
                description="Integrated web security testing platform",
                auto_updates=False,
            ),
            Tool(
                name="gobuster",
                packages=["gobuster"],
                description="Directory and DNS brute forcing utility",
            ),
            Tool(
                name="ffuf",
                packages=["ffuf"],
                description="Fast web fuzzer for content discovery",
            ),
            Tool(
                name="dirsearch",
                packages=["dirsearch"],
                description="Command-line brute forcing of web paths",
            ),
            Tool(
                name="owasp-zap",
                packages=["owasp-zap"],
                description="OWASP Zed Attack Proxy web scanner",
                auto_updates=False,
            ),
            Tool(
                name="whatweb",
                packages=["whatweb"],
                description="Next generation web scanner and fingerprinting",
            ),
        ],
    ),
    "exploitation": Category(
        name="Exploitation",
        description="Exploitation frameworks and helpers.",
        tools=[
            Tool(
                name="metasploit-framework",
                packages=["metasploit-framework"],
                description="Metasploit penetration testing framework",
            ),
            Tool(
                name="sqlmap",
                packages=["sqlmap"],
                description="Automated SQL injection tool",
            ),
            Tool(
                name="searchsploit",
                packages=["exploitdb"],
                description="Local exploit database copies",
                auto_updates=False,
            ),
        ],
    ),
    "post": Category(
        name="Post-Exploitation",
        description="Privilege escalation and persistence utilities.",
        tools=[
            Tool(
                name="beef-xss",
                packages=["beef-xss"],
                description="Browser exploitation framework",
                auto_updates=False,
            ),
            Tool(
                name="responder",
                packages=["responder"],
                description="LLMNR, NBT-NS and MDNS poisoning tool",
            ),
        ],
    ),
    "wireless": Category(
        name="Wireless",
        description="Wireless auditing toolset.",
        tools=[
            Tool(
                name="aircrack-ng",
                packages=["aircrack-ng"],
                description="Wi-Fi network cracking suite",
            ),
            Tool(
                name="bettercap",
                packages=["bettercap"],
                description="Network capture and MITM framework",
            ),
            Tool(
                name="kismet",
                packages=["kismet"],
                description="Wireless network detector, sniffer, and IDS",
            ),
            Tool(
                name="reaver",
                packages=["reaver"],
                description="WPS brute force attack tool",
            ),
            Tool(
                name="hcxdumptool",
                packages=["hcxdumptool"],
                description="Captures wireless traffic for hash cracking",
            ),
            Tool(
                name="wifite",
                packages=["wifite"],
                description="Automated wireless attack toolkit",
            ),
            Tool(
                name="mdk4",
                packages=["mdk4"],
                description="Wi-Fi network stress testing tool",
            ),
        ],
    ),
    "passwords": Category(
        name="Password Attacks",
        description="Wordlist generation and password cracking suites.",
        tools=[
            Tool(
                name="hashcat",
                packages=["hashcat"],
                description="GPU-accelerated password cracker",
            ),
            Tool(
                name="john",
                packages=["john"],
                description="John the Ripper password cracking framework",
            ),
            Tool(
                name="hydra",
                packages=["hydra"],
                description="Parallelized login brute forcer",
            ),
            Tool(
                name="cewl",
                packages=["cewl"],
                description="Custom wordlist generator from web content",
            ),
            Tool(
                name="crunch",
                packages=["crunch"],
                description="Flexible wordlist generation utility",
            ),
        ],
    ),
    "forensics": Category(
        name="Forensics",
        description="File system, memory, and artifact analysis tools.",
        tools=[
            Tool(
                name="autopsy",
                packages=["autopsy"],
                description="Digital forensics platform and graphical interface",
                auto_updates=False,
            ),
            Tool(
                name="sleuthkit",
                packages=["sleuthkit"],
                description="File system forensic analysis toolkit",
            ),
            Tool(
                name="binwalk",
                packages=["binwalk"],
                description="Firmware analysis tool for binary images",
            ),
            Tool(
                name="foremost",
                packages=["foremost"],
                description="File carving utility",
            ),
            Tool(
                name="bulk-extractor",
                packages=["bulk-extractor"],
                description="Scans disk images, files, and directories for features",
            ),
        ],
    ),
}


def iter_categories() -> Iterable[Category]:
    """Iterate over the catalog categories."""

    return CATALOG.values()


def get_category(name: str) -> Category:
    """Return a category by its key, raising KeyError if not found."""

    key = name.strip().lower()
    if key not in CATALOG:
        raise KeyError(f"Unknown category '{name}'. Available: {', '.join(sorted(CATALOG))}")
    return CATALOG[key]
