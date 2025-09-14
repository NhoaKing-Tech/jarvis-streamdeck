"""
UI logic for StreamDeck event handling and layout management.
This module handles user input events and layout switching logic.
"""

from .render import render_layout

# Global state - will be set by the main module
current_layout = None
layouts = None
deck = None

def initialize_logic(deck_instance, layouts_dict, initial_layout="main"):
    """Initialize the UI logic module with required state."""
    global deck, layouts, current_layout
    deck = deck_instance
    layouts = layouts_dict
    current_layout = initial_layout

def switch_layout(layout_name):
    """
    I created this function as a function that returns a wrapper function (accomplishes the same as a lambda function
    declared inline when building the layout dictionary, but cleaner and easier to read).
    When I call this function with a layout_name, it doesn't immediately switch the deck layout. Instead,
    I return a nested function (wrapper) that, when called later, will switch to the specified layout in layout_name.
    This is useful in my StreamDeck layout because I can call switch_layout('home') during layout definition,
    and it returns a function that can be executed when the button is pressed.
    This eliminates the need for me to write lambda expressions in my layout dictionaries, keeping the code cleaner.
    The wrapper function uses the global current_layout variable to track state and
    calls render_layout to actually display the new deck layout.
    """
    def wrapper():
        global current_layout
        current_layout = layout_name
        render_layout(deck, layouts[layout_name])
    return wrapper

def switch_layout_lambda_in_layout(layout_name):
    """
    I designed this function first to be called directly when I want to switch deck layouts.
    Unlike the switch_layout function above, this one switches to the specified deck layout right away
    when called, since it takes an argument (layout_name). Therefore I needed to write a lambda expression when using
    it in my layout dictionaries, like: lambda: switch_layout_lambda_in_layout('main').
    At the beginning, I had lambda expressions in my layout definitions, but I wanted to avoid that for cleaner code.
    It also makes easier to build the dictionary, as I could have forgotten to add the lambda in some places. ._.

    """
    global current_layout
    current_layout = layout_name
    render_layout(deck, layouts[layout_name])

def key_change(deck_instance, key, state):
    """
    Event handler for deck key presses
    Arguments:
    deck_instance: the stream deck
    key: what key was pressed. In my case from 0 to 31 (the stream deck XL from elgato has 32 keys)
    state: true if key is pressed, and false when it is release.
    """
    if state and key in layouts[current_layout]:
        # when a key is pressed and the key exists in the current layout
        try:
            # executes the action assigned to the key
            layouts[current_layout][key]["action"]()
        except:
            pass # ignore silently