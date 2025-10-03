---
title: "04_Implementation Notes: Actions"
tags: [note, auto-generated]
description: "04_Implementation Notes from actions.py"
date: 2025-10-03
---

**Source File**: `jarvis/actions/actions.py`

**Category**: Important implementation details and considerations

---

<a id="general-1"></a>

Global Configuration with Dynamic Initialization chosen for:

 - Simple and straightforward for this hardware integration use case

 - Balances testability with StreamDeck API constraints

 - Provides clear error handling and initialization validation

*[Source: actions.py:182]*

---

## function: hk_terminal

<a id="function:-hk_terminal-1"></a>

This is preferred over direct terminal commands because it uses the

 desktop environment's configured default rather than hardcoding a

 specific terminal emulator.

*[Source: actions.py:577]*

---

## function: hot_keys

<a id="function:-hot_keys-1"></a>

Press keys in forward order

*[Source: actions.py:529]*

---

## function: spotify

<a id="function:-spotify-1"></a>

No lambda wrapper needed - this function doesn't take parameters and executes immediately,

 so it doesn't need the closure pattern used by parameterized functions.

*[Source: actions.py:393]*

---

## function: wrapper

<a id="function:-wrapper-1"></a>

Import render_keys here to avoid circular import

*[Source: actions.py:488]*

---

<a id="function:-wrapper-2"></a>

VSCode needs time to initialize

*[Source: actions.py:642]*

---

<a id="function:-wrapper-3"></a>

"--" prevents text starting with "-" being interpreted as flags

*[Source: actions.py:692]*

---

<a id="function:-wrapper-4"></a>

Auto-fix permissions if not executable

*[Source: actions.py:901]*

---

<a id="function:-wrapper-5"></a>

Resolve to absolute path for consistent window title matching

*[Source: actions.py:1011]*

---

<a id="function:-wrapper-6"></a>

Check multiple title formats for matching

*[Source: actions.py:1065]*

---
