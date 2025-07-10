# ZEUSNET Figma Handoff

This document outlines how to prepare and export the ZeusNet UI designs from Figma for developers.

## Layout & Spacing
- Base frame width: **1440 px** desktop.
- Use an **8 px** spacing grid for consistent padding and margins.
- Each tool module should follow a **Form on the Left, Output on the Right** layout.

## Components to Build
Create shared components in a Figma library so that screens can reuse them:
- **TopBar** – fixed header with mode toggle and quick stats.
- **SideNav** – collapsible navigation with icons and labels.
- **MainContentWrapper** – container for page modules.
- **LogConsole** – sticky footer that streams logs.
- **ModalTemplate** – generic dialog for confirmations and warnings.
- **FormFields** – consistent input styles.
- **StatusCards** – metric cards for interfaces or scans.
- **AttackFormLayout** – command inputs with progress feedback.

## Page Frames
Create separate frames named exactly as listed below:
- `Dashboard`
- `Scan`
- `Networks`
- `Devices`
- `Attack_Probe`
- `Attack_SYN`
- `Attack_Aire`
- `Alerts`
- `Export`
- `Settings`

These names will be used when exporting assets.

## Design Notes
- Include layers that respond to `ZEUSNET_MODE` to show disabled states when the application runs in **SAFE** mode.
- Enable **Dev Mode** in Figma so developers can read Tailwind-compatible class hints and CSS variables.

## Export Instructions
1. Export each frame as PNG/SVG and name the files to match the frame titles.
2. Publish shared components to the Figma Library for reuse.
3. Provide the team with the Figma link and ensure Dev Mode is enabled for inspection.

