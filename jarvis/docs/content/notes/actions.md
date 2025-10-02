---
title: "Implementation Notes: Actions"
tags: [note, auto-generated]
description: "Implementation Notes from actions.py"
date: 2025-10-02
---

# Implementation Notes: Actions

**Source File**: `jarvis/actions/actions.py`

**Category**: Important implementation details and gotchas

---

<a id="general-1"></a>

render_keys import moved inside toggle_mic function to avoid circular import
This was: actions -> ui.render -> core.logic -> actions
Now render_keys is imported only when needed, breaking the cycle

*[Source: actions.py:78]*

---
