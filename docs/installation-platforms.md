# Installation and uninstallation

| Platform | Install | Uninstall |
|---|---|---|
| Linux / Termux | `sh scripts/install-linux.sh` | `sh scripts/uninstall-linux.sh` |
| Windows | `scripts\install-windows.cmd` | `scripts\uninstall-windows.cmd` |

The Windows uninstaller removes the `authtwin.cmd` shim and isolated AuthTwin venv, while preserving workspaces, configuration and authorization evidence. It leaves the shared `%USERPROFILE%\.local\bin` PATH entry untouched so sibling Sentinel Forge tools are not broken. Linux uses the same preservation policy.
