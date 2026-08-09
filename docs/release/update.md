# Signed updates

Configure `AUTHTWIN_RELEASE_MANIFEST_URL` and `AUTHTWIN_RELEASE_PUBLIC_KEY`, or pass `--manifest` and `--public-key` explicitly.

```bash
authtwin update --check
authtwin update
authtwin update --force
```

`authtwin update --check` verifies signed release metadata and reports availability without installing. `authtwin update` installs a newer trusted release selected by the manifest. `authtwin update --force` explicitly reinstalls the selected signed release even when that exact version is already installed; the updater invokes pip with `--force-reinstall` after signature and SHA-256 verification.

`--force` never permits a downgrade, including a prerelease replacing a stable release with the same numeric core version. `--check` and `--force` are mutually exclusive. State is backed up before installation, normal upgrades require verified rollback metadata, and same-version forced reinstalls use the verified target wheel as the package recovery artifact.

Only Ed25519-signed manifests and hash-matching wheel artifacts are accepted. HTTP update sources, unsigned downloads, and blind `git pull` updates are rejected. Until the official release signing channel and public trust root are published, the manifest and trusted public key must be configured explicitly.
