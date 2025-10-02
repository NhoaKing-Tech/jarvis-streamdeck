---
title: "Educational Content: Actions"
tags: [edu, auto-generated]
description: "Educational Content from actions.py"
date: 2025-10-02
---

# Educational Content: Actions

**Source File**: `jarvis/actions/actions.py`

**Category**: Computer science concepts, design patterns, and learning material

---

<a id="general-1"></a>

=====================================================================================
COMPUTER SCIENCE EDUCATION: DESIGN PATTERNS COMPARISON
=====================================================================================
WHAT WE'RE ACTUALLY USING: Global Configuration with Dynamic Initialization
===========================================================================
Our pattern stores configuration in module-level global variables that are set at runtime.
This approach provides:
1. TESTABILITY: Easy to mock configuration by setting globals for unit tests
2. FLEXIBILITY: Can be configured differently for different environments
3. PERFORMANCE: Configuration accessed directly without repeated file reads or imports
4. ERROR HANDLING: Can detect and report missing configuration with None checks
HOW OUR PATTERN WORKS:
1. Declare global variables as None (creates module attributes)
2. At startup, init_module() uses setattr() to set real values
3. Functions access these globals directly: if YDOTOOL_PATH is None: ...
4. Configuration is "injected" into the module, not into individual functions

*[Source: actions.py:109]*

---

<a id="general-2"></a>

WHAT IS TRUE DEPENDENCY INJECTION? (Computer Science Definition)
================================================================
Dependency Injection (DI) is a design pattern where an object's dependencies
are provided (injected) to it from external sources rather than the object
creating or finding them itself.
KEY PRINCIPLE: "Don't call us, we'll call you" (Inversion of Control)
- Dependencies are PASSED IN as parameters to functions/constructors
- The function/object doesn't know HOW to create its dependencies
- An external "injector" provides the dependencies
TRUE DEPENDENCY INJECTION EXAMPLE:
def hot_keys(ydotool_path: str, keycodes: Dict, *keys: str) -> None:
"""Dependencies are INJECTED as parameters - this is true DI"""
sequence = []
for key in keys:
if key not in keycodes:  # EDU: Uses injected dependency
raise ValueError(f"Unknown key: {key}")
sequence.append(f"{keycodes[key]}:1")
subprocess.run([ydotool_path, "key"] + sequence)  # EDU: Uses injected dependency
HOW YOU WOULD CALL IT:
hot_keys("/usr/bin/ydotool", KEYCODES_DICT, "CTRL", "C")  # EDU: Dependencies passed in
OUR CURRENT APPROACH (Global Configuration):
def hot_keys(*keys: str) -> None:
"""Dependencies accessed from global state - NOT dependency injection"""
if KEYCODES is None or YDOTOOL_PATH is None:  # EDU: Accesses global variables
raise RuntimeError("Module not initialized")
sequence = []
for key in keys:
if key not in KEYCODES:  # EDU: Uses global variable
raise ValueError(f"Unknown key: {key}")
sequence.append(f"{KEYCODES[key]}:1")
subprocess.run([YDOTOOL_PATH, "key"] + sequence)  # EDU: Uses global variable
HOW YOU CALL IT:
hot_keys("CTRL", "C")  # EDU: No dependencies passed - function finds them globally
KEY DIFFERENCES EXPLAINED:
==========================
1. WHERE DEPENDENCIES COME FROM:
- TRUE DI: Dependencies passed as function parameters
- OUR APPROACH: Dependencies accessed from module-level globals
2. FUNCTION SIGNATURES:
- TRUE DI: Functions declare what they need as parameters
- OUR APPROACH: Functions have simpler signatures, find dependencies internally
3. CALLER RESPONSIBILITY:
- TRUE DI: Caller must provide all dependencies when calling function
- OUR APPROACH: Caller just calls function, dependencies already available globally
4. COUPLING:
- TRUE DI: Functions are decoupled from specific dependency sources
- OUR APPROACH: Functions are coupled to specific global variable names
5. TESTING:
- TRUE DI: Pass mock objects as parameters: hot_keys(mock_path, mock_codes, "A")
- OUR APPROACH: Set global variables before test: YDOTOOL_PATH = mock_path
DEV: WHY WE CHOSE OUR APPROACH INSTEAD OF TRUE DEPENDENCY INJECTION:
DEV: ==============================================================
1. STREAMDECK CONSTRAINT: StreamDeck library calls our functions with fixed signatures
- StreamDeck expects: key_pressed(deck, key_number)
- Can't change to: key_pressed(deck, key_number, ydotool_path, keycodes, ...)
2. SIMPLICITY: Fewer parameters to pass around in every function call
- Our way: hot_keys("CTRL", "C")
- DI way: hot_keys(ydotool_path, keycodes, "CTRL", "C")
3. PERFORMANCE: No need to pass the same config objects repeatedly
- Configuration set once at startup, accessed directly when needed
4. STREAMDECK INTEGRATION: Hardware callbacks can't receive arbitrary parameters
- Hardware events trigger callbacks with predetermined signatures
- Global state allows callbacks to access needed configuration
ALTERNATIVE PATTERNS WE COULD HAVE USED:
========================================
1. SERVICE LOCATOR: Functions call a service to get dependencies
config = ConfigService.get_config(); config.ydotool_path
2. SINGLETON: Global configuration object
Config.instance().ydotool_path
3. CLOSURE WITH DEPENDENCY INJECTION: Factory functions that capture dependencies
def create_hotkey_function(ydotool_path, keycodes):
def hot_keys(*keys): # Uses captured dependencies
return hot_keys
OUR CHOICE: Global Configuration with Dynamic Initialization
- Simple and straightforward for this hardware integration use case
- Balances testability with StreamDeck API constraints
- Provides clear error handling and initialization validation

*[Source: actions.py:128]*

---
