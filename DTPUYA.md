# dt-puya: differences from puya

`dt-puya` is [puya](https://github.com/algorandfoundation/puya), the Algorand Python compiler (`puyapy`) and the compiler backend shared with Algorand TypeScript (`puya`), for [dt-algorand](https://github.com/d13co/dt-algorand/tree/dtalgorand), the time-travel fork of go-algorand, released on GitHub with the binaries [dt-puya-ts](https://github.com/d13co/dt-puya-ts) downloads. Everything else is upstream's: code that compiles with puya compiles with dt-puya to the same output.

It is built on puya 5.10.1. Source and issues: [d13co/dt-puya](https://github.com/d13co/dt-puya) (branch `dtalgorand`).

- [Changes](#changes)
- [Installing](#installing)
- [Versions](#versions)
- [Releasing dt-puya](#releasing-dt-puya)

## Changes

| Area                | puya                    | dt-puya                                                         |
| ------------------- | ----------------------- | --------------------------------------------------------------- |
| `puya --version`    | `puya 5.10.1`           | `puya <version>`, with the `-dt.<x.y.z>` form of the version    |
| Releases            | PyPI and GitHub, signed | GitHub only, unsigned, with a SHA-256 checksum for each binary |

## Installing

### Algorand TypeScript

Use [dt-puya-ts](https://github.com/d13co/dt-puya-ts). It downloads the matching dt-puya binary from this repository's releases on first use, the way puya-ts downloads puya's.

### The puya binary

Each release has `puya-<version>-<os>_<arch>.tar.gz` and its `.sha256.txt` for `linux_x64`, `linux_arm64`, `macos_x64`, `macos_arm64` and `windows_x64`, e.g. [puya-5.10.1-dt.1.0.0-linux_x64.tar.gz](https://github.com/d13co/dt-puya/releases/download/v5.10.1-dt.1.0.0/puya-5.10.1-dt.1.0.0-linux_x64.tar.gz). The binaries are not code signed. On macOS, a binary downloaded with a browser needs `xattr -d com.apple.quarantine puya` first; puya-ts's download doesn't.

```shell
curl -LO https://github.com/d13co/dt-puya/releases/download/v5.10.1-dt.1.0.0/puya-5.10.1-dt.1.0.0-linux_x64.tar.gz
curl -LO https://github.com/d13co/dt-puya/releases/download/v5.10.1-dt.1.0.0/puya-5.10.1-dt.1.0.0-linux_x64.sha256.txt
sha256sum -c puya-5.10.1-dt.1.0.0-linux_x64.sha256.txt
mkdir puya && tar -xzf puya-5.10.1-dt.1.0.0-linux_x64.tar.gz -C puya
./puya/puya --version
```

To use it from upstream puya-ts, pass `--puya-path ./puya/puya`.

### Algorand Python

dt-puya is not on PyPI. Install the compiler and the stubs from the release's wheels, under their upstream names `puyapy` and `algorand-python`, so that tools that look for them find them:

```shell
uv add --dev "puyapy @ https://github.com/d13co/dt-puya/releases/download/v5.10.1-dt.1.0.0/puyapy-5.10.1+dt.1.0.0-py3-none-any.whl"
uv add "algorand-python @ https://github.com/d13co/dt-puya/releases/download/v5.10.1-dt.1.0.0/algorand_python-4.0.0+dt.1.0.0-py3-none-any.whl"
```

With pip, `pip install <url>` for each. Then compile with `puyapy <path>`. The `algorand-python` wheel gives your editor and type checker the fork's stubs.

## Versions

A release is `<puya version>-dt.<x.y.z>`, such as `5.10.1-dt.1.0.0`:

- the puya version the code is built on; change it when merging a new upstream release;
- the fork's own release, `x.y.z`: bump `x` for a breaking change to what the fork adds, `y` for features and `z` for fixes. It never starts again: when the puya version changes, it keeps counting from the last release, bumped as the change calls for.

That form is the tag (`v5.10.1-dt.1.0.0`), the binaries' names and what `puya --version` prints. Python versions can't have a `-dt.` suffix, so `pyproject.toml` has the PEP 440 local version `5.10.1+dt.1.0.0`, which the `puyapy` wheel carries. The stubs keep their own version with the same suffix: `algorand-python` `4.0.0+dt.1.0.0`.

## Releasing dt-puya

GitHub Actions releases dt-puya, with [`.github/workflows/dt-puya.yml`](.github/workflows/dt-puya.yml). On every push and pull request to `dtalgorand` it runs pre-commit (ruff, mypy), checks the generated code and the typeshed, runs the tests (with LocalNet) and compiles all the examples and test cases at `-O0`, `-O1` and `-O2`, checking the output against the committed one. The `Test` job passes when all of these do. On a `v<version>` tag it also builds the puya binaries for the five platforms with upstream's `build-binaries.yaml` (unsigned, smoke tested on each platform and on older Linux distributions) and the wheels, and creates a GitHub release with them. Upstream's workflows that release, publish docs or comment on pull requests (`cd.yaml`, `prerelease.yaml`, `gh-pages.yaml`, `publish-devportal-docs.yml`, `check-python.yaml`) don't run on the fork.

1. Choose the version (see [Versions](#versions)).
2. Set it in `pyproject.toml` (`<puya version>+dt.<x.y.z>`) and `stubs/pyproject.toml` (`<stubs version>+dt.<x.y.z>`), run `uv lock`, then `python scripts/dt_release.py update`. The script sets the version in the tags, binary and wheel names in `README.md` and this file.
3. `poe gen`, `pre-commit run --all-files` and `pytest`.
4. Commit and push `dtalgorand`, then tag the commit and push the tag: `git tag v<version>` and `git push d13co v<version>`.
5. The workflow checks that the tag is on `dtalgorand` and matches the versions in `pyproject.toml`, `stubs/pyproject.toml`, `uv.lock` and the docs (`python scripts/dt_release.py check v<version>` runs the same check locally), and that `puya --version` prints the version. After the tests and the binaries, the `release` job waits for approval, then creates the release. If the release already exists, it is left as it is.
6. Point dt-puya-ts at the new version (its `targetedPuyaVersion`) and release it.

### One-time setup

- **Default branch.** Set it to `dtalgorand` (Settings → General). The guards that keep upstream's workflows off the fork exist only on this branch, and the repository page then shows this branch's README.
- **Environment.** The `release` job runs in the GitHub environment `release`: give it required reviewers to approve each release, and a deployment policy that admits only `v*-dt.*` tags.
