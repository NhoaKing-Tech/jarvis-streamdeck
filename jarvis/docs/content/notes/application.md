---
title: "04_Implementation Notes: Application"
tags: [note, auto-generated]
description: "04_Implementation Notes from application.py"
date: 2025-10-03
---

# 04_Implementation Notes: Application

**Source File**: `jarvis/core/application.py`

**Category**: Important implementation details and considerations

---

<a id="general-1"></a>

This imports from the original Elgato StreamDeck repository in ../src/

 The StreamDeck library provides hardware abstraction for StreamDeck devices

 Original repository. The StreamDeck library provides hardware abstraction for StreamDeck devices.

 Installed inside my virtual environment in developer mode (pip install -e .). This ensures latest

 local changes are always used. Execute "pip install -e ." inside the repo directory to install

 in developer mode.

*[Source: application.py:45]*

---

<a id="general-2"></a>

KEYCODES dictionary has been moved to config/initialization.py

 for centralized configuration management

*[Source: application.py:216]*

---

## function: main

<a id="function:-main-1"></a>

This assumes only one StreamDeck is connected. For multiple devices,

 we would need to identify them by serial number or model

*[Source: application.py:301]*

---
