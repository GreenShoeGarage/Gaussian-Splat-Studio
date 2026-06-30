# Packaging

Maker Splat MVP includes packaging scaffolds for macOS, Windows, and Linux.

These are not signed production installers yet. They are starter scripts for repeatable packaging work.

## Targets

- macOS: `.app` / `.dmg` wrapper around Docker launch
- Windows: `.exe` / installer wrapper around Docker launch
- Linux: AppImage or `.deb` wrapper around Docker launch

## MVP packaging requirement

A non-technical user should be able to start Maker Splat without typing Docker commands manually.
