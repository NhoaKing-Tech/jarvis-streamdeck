---
title: "Performance Notes: Actions"
tags: [optimize, auto-generated]
description: "Performance Notes from actions.py"
date: 2025-10-03
---

# Performance Notes: Actions

**Source File**: `jarvis/actions/actions.py`

**Category**: Performance considerations and optimization opportunities

---

<a id="general-1"></a>

Cache Spotify running state to avoid repeated pgrep calls

Use D-Bus to communicate directly with Spotify (more efficient)

Implement timeout for Spotify launch detection

*[Source: actions.py:457]*

---

<a id="general-2"></a>

Hotkey simulation is faster than process discovery and launching

The desktop environment handles terminal selection and configuration

*[Source: actions.py:615]*

---

## function: open_obsidian

<a id="function:-open_obsidian-1"></a>

wmctrl window search typically <10ms

Could cache window list to avoid repeated wmctrl calls

*[Source: actions.py:848]*

---

## function: open_vscode

<a id="function:-open_vscode-1"></a>

Make delay configurable based on system performance

*[Source: actions.py:640]*

---

## function: type_snippet

<a id="function:-type_snippet-1"></a>

Could cache frequently used snippets in memory

*[Source: actions.py:774]*

---

## function: type_text

<a id="function:-type_text-1"></a>

For large text blocks, consider clipboard operations instead

*[Source: actions.py:699]*

---
