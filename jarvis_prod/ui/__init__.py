# UI Package Initialization
# This file makes the ui directory a Python package and controls what gets imported
# when someone does "from ui import ..." or "import ui"

# Import the render module to make it available as ui.render
# This allows: from ui import render OR import ui; ui.render.some_function()
from . import render

# PACKAGE DESIGN DECISIONS:
#
# 1. Explicit imports instead of __all__:
#    We explicitly import render rather than using __all__ = ['render', 'logic', 'lifecycle']
#    because we want to control exactly what's exposed at the package level.
#
# 2. Module imports instead of function imports:
#    We import modules (from . import render) rather than specific functions
#    (from .render import render_layout) to maintain clear namespacing and
#    avoid naming conflicts.
#
# 3. Relative imports:
#    Using relative imports (from . import) instead of absolute imports
#    makes the package self-contained and easier to move or rename.
#
# USAGE PATTERNS:
# This allows consumers to use the ui package in several ways:
#
# 1. Direct module access:
#    from ui import render
#    render.render_layout(deck, layout)
#
# 2. Package import with dot notation:
#    import ui
#    ui.render.render_layout(deck, layout)
#
# 3. Specific function imports (if needed):
#    from ui.render import render_layout
#    render_layout(deck, layout)
#
# The current approach (option 1) is used throughout jarvis for consistency.

# PACKAGE STRUCTURE OVERVIEW:
# ui/
# ├── __init__.py     (this file - package initialization)
# ├── render.py       (visual rendering and layout management)
# ├── logic.py        (event handling and layout switching)
# └── lifecycle.py    (cleanup and shutdown management)
#
# Each module has a specific responsibility:
# - render: StreamDeck visual output and layout definitions
# - logic: User input processing and application flow control
# - lifecycle: Resource management and graceful shutdown