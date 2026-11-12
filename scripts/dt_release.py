#!/usr/bin/env python3
"""Keep the dt-puya version in the docs in step with pyproject.toml, and check it before a release.

Usage:
  python scripts/dt_release.py update        rewrite the docs for the pyproject.toml version
  python scripts/dt_release.py check [tag]   fail if the stubs, uv.lock, docs or tag disagree

The version is <puya version>+dt.<x.y.z> in pyproject.toml (a PEP 440 local version, which the
wheels carry) and <puya version>-dt.<x.y.z> everywhere else: the tag (v5.10.1-dt.1.0.0), the
binaries' names, `puya --version` and the docs. The stubs (algorand-python) keep their own
version with the same +dt.<x.y.z>.

Needs only the standard library, so it runs before `uv sync`.
"""

import re
import sys
import tomllib
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
_DOCS = ("README.md", "DTPUYA.md")
_FORMAT = "<puya version>+dt.<x.y.z>"
_VERSION = re.compile(r"^(\d+\.\d+\.\d+)\+dt\.(\d+\.\d+\.\d+)$")
# The tag v5.10.1-dt.1.0.0 and the binary puya-5.10.1-dt.1.0.0-linux_x64.tar.gz in the docs
# (not other dt versions, such as @d13co/dt-puya-ts@1.3.1-dt.1.0.0)
_RELEASE_REF = re.compile(r"(?:\bv|\bpuya-)(\d+\.\d+\.\d+-dt\.\d+\.\d+\.\d+)(?!\.?\d)")
# puyapy-5.10.1+dt.1.0.0-py3-none-any.whl and algorand_python-4.0.0+dt.1.0.0-... in the docs
_WHEEL_REF = re.compile(r"\b(puyapy|algorand_python)-(\d+\.\d+\.\d+\+dt\.\d+\.\d+\.\d+)-")


def _project_version(path: str) -> str:
    data = tomllib.loads((_ROOT / path).read_text("utf8"))
    version = data["project"]["version"]
    assert isinstance(version, str)
    return version


def _locked_version(name: str) -> str | None:
    lock = tomllib.loads((_ROOT / "uv.lock").read_text("utf8"))
    for package in lock["package"]:
        if package["name"] == name:
            version = package.get("version")
            return version if isinstance(version, str) else None
    return None


def _update(release: str, wheels: dict[str, str]) -> None:
    for doc in _DOCS:
        path = _ROOT / doc
        text = path.read_text("utf8")
        updated = _RELEASE_REF.sub(lambda m: m[0].replace(m[1], release), text)
        updated = _WHEEL_REF.sub(lambda m: f"{m[1]}-{wheels[m[1]]}-", updated)
        path.write_text(updated, "utf8")
        print(f"{doc}: {'unchanged' if text == updated else 'updated'}")
    print(f"dt-puya {release}")


def _check(release: str, wheels: dict[str, str], tag: str | None) -> list[str]:
    errors = []
    for name, version in (
        ("puyapy", wheels["puyapy"]),
        ("algorand-python", wheels["algorand_python"]),
    ):
        locked = _locked_version(name)
        if locked != version:
            errors.append(f"uv.lock has {name} {locked}, not {version}: run `uv lock`")
    if tag and tag != f"v{release}":
        errors.append(f"tag {tag} is not v{release}")
    for doc in _DOCS:
        text = (_ROOT / doc).read_text("utf8")
        errors.extend(
            f"{doc}: {found} is not {release}"
            for found in _RELEASE_REF.findall(text)
            if found != release
        )
        errors.extend(
            f"{doc}: {name}-{found} is not {name}-{wheels[name]}"
            for name, found in _WHEEL_REF.findall(text)
            if found != wheels[name]
        )
    return errors


def main() -> None:
    mode, *rest = sys.argv[1:] or [""]
    tag = rest[0] if rest and rest[0] else None
    if mode not in ("update", "check") or len(rest) > 1 or (mode == "update" and rest):
        sys.exit("Usage: dt_release.py update | check [tag]")

    version = _project_version("pyproject.toml")
    stubs_version = _project_version("stubs/pyproject.toml")
    matched = _VERSION.match(version)
    if not matched:
        sys.exit(f"pyproject.toml version {version} is not {_FORMAT}")
    base, dt = matched.groups()
    release = f"{base}-dt.{dt}"
    wheels = {"puyapy": version, "algorand_python": stubs_version}

    errors = []
    stubs_matched = _VERSION.match(stubs_version)
    if not stubs_matched or stubs_matched[2] != dt:
        errors.append(
            f"stubs/pyproject.toml version {stubs_version} is not <stubs version>+dt.{dt}"
        )
    if mode == "update":
        if errors:
            sys.exit("\n".join(errors))
        _update(release, wheels)
        return

    errors.extend(_check(release, wheels, tag))
    if errors:
        print("\n".join(errors), file=sys.stderr)
        sys.exit("Set the versions, run `uv lock`, then `python scripts/dt_release.py update`")
    print(f"dt-puya {release} is consistent{f' with {tag}' if tag else ''}")


if __name__ == "__main__":
    main()
