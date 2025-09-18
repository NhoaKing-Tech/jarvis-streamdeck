# Actions Package Initialization
# This file makes the actions directory a Python package and provides access to action functions

# Import the actions module to make it available as actions.actions
# This allows: from actions import actions OR import actions; actions.actions.some_function()
from . import actions

# PACKAGE STRUCTURE:
# actions/
# ├── __init__.py     (this file - package initialization)
# └── actions.py      (all action functions for StreamDeck keys)
#
# DESIGN RATIONALE:
# The actions package currently contains only one module (actions.py), but using
# a package structure provides several benefits:
#
# 1. FUTURE EXPANSION: Easy to add specialized action modules later
#    - actions/system.py (system control actions)
#    - actions/media.py (media control actions)
#    - actions/development.py (development workflow actions)
#
# 2. NAMESPACE ORGANIZATION: Clear separation of action-related code
#    from other jarvis components
#
# 3. IMPORT CONSISTENCY: Follows same pattern as ui package for
#    consistent codebase structure
#
# 4. DEPENDENCY ISOLATION: Actions can have their own dependencies
#    without affecting other parts of jarvis
#
# USAGE IN JARVIS:
# The main application imports actions like this:
#   from actions import actions
#   actions.initialize_actions(...)
#   layout_key["action"] = actions.open_vscode("/path/to/project")
#
# This provides clear namespacing while keeping imports simple and readable.

# ALTERNATIVE STRUCTURES CONSIDERED:
#
# 1. Single actions.py file in jarvis root:
#    - Simpler structure but less organized
#    - Harder to expand with additional action categories
#    - No clear separation of concerns
#
# 2. Individual action files in actions/ package:
#    - actions/applications.py, actions/system.py, etc.
#    - More modular but current codebase doesn't justify this complexity
#    - Could be adopted later if action categories grow significantly
#
# 3. Class-based action organization:
#    - ActionManager class with methods for different actions
#    - More OOP approach but adds complexity without clear benefits
#    - Current function-based approach is simpler and more direct
#
# The current structure strikes a good balance between simplicity and
# future expandability.