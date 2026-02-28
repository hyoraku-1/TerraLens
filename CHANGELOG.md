# Changelog

All notable changes to TerraLens are documented here.

---

## [0.1.3] - 2026-02-28

### Fixed
- Removed duplicate `main()` function at the top of `cli.py` that was shadowing the correct one at the bottom of the file
- Eliminated stale `from insight_tf.app import InsightTFApp` import that referenced a non-existent module
- Resolved `NameError: name 'InsightTFApp' is not defined` crash on binary startup — the CLI and binary now correctly launch the full `InsightTF` app with state file support

---

## [0.1.2] - 2026-02-27

### Fixed
- Fixed `ParserError: Missing expression after unary operator '--'` on Windows builds caused by PowerShell not supporting `\` line continuation
- Added `shell: bash` to the Build Binary step in the GitHub Actions workflow so both Ubuntu and Windows runners use the same shell
- Resolved Windows binary build failures — `insight-tf-windows-latest.exe` now builds and runs correctly

---

## [0.1.1] - 2026-02-27

### Fixed
- Fixed `ModuleNotFoundError: No module named 'rich._unicode_data.unicode17-0-0'` crash on startup
- Added `--collect-submodules rich` and `--collect-submodules textual` to PyInstaller build flags to ensure all lazy-loaded submodules are bundled into the binary
- Added `--hidden-import rich._unicode_data` to force inclusion of unicode data files that `rich` loads at runtime — resolves crashes on Arch Linux and other non-Ubuntu distributions

---

## [0.1.0] - 2026-02-26

### Added
- Initial public release of TerraLens (formerly Insight-TF)
- **Overview tab** — displays Terraform version, state serial, total resource count, provider count, and a full resource summary table
- **Manage tab** — interactive resource tree grouped by type with full attribute inspector
- **Plan** — streams real `terraform plan` output line-by-line into the terminal
- **Apply Now** — runs `terraform apply -auto-approve` and auto-reloads state on success
- **Cost Estimate** — Infracost-powered breakdown with per-resource monthly costs and totals
- **Drift Detection** — runs `terraform plan -refresh-only -detailed-exitcode` and reports drifted resources with status
- **Add Resource wizard** — 3-step flow: select provider → browse 334 AWS resources across 20 categories → configure fields and preview generated HCL
- **Destroy** — targeted destroy with confirmation modal before execution
- **State Reload** — press `r` at any time to reload state from disk without restarting
- Pre-built binaries available for Linux (Ubuntu/Arch/Fedora) and Windows
- Published to PyPI as `insight-tf`

---
