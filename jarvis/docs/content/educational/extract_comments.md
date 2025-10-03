---
title: "01_Learning notes: Extract Comments"
tags: [edu, auto-generated]
description: "01_Learning notes from extract_comments.py"
date: 2025-10-03
---

**Source File**: `jarvis/utils/extract_comments.py`

**Category**: Learning notes about computer science topics in general

---

<a id="general-1"></a>

Comments vs Docstrings - How this tool extracts tags

This tool ONLY extracts from COMMENT LINES (lines starting with #)

It does NOT extract from DOCSTRINGS (text in triple quotes """)

This WORKS (will be extracted):

  #EDU Python Classes - Blueprints for creating objects

  #EDU Classes are used to bundle data together.

This does NOT WORK (will be IGNORED by the extractor):

  """

  #EDU Python Classes - Blueprints for creating objects

  #EDU Classes are used to bundle data together.

  """

Why? Docstrings (""") are strings that Python keeps as documentation, not comments.

The tool searches for lines starting with '#' (see line 250: if not stripped.startswith('#'))

Tags inside docstrings will NOT be found during extraction.

Summary: Always use # for tagged comments if you want them extracted, never """ around tags

*[Source: extract_comments.py:34]*

---

<a id="general-2"></a>

Python Classes - Blueprints for creating objects

Classes are used to bundle data (attributes) and functionality (methods) together.

They let you create multiple objects (instances) with the same structure but different values.

Naming convention: Classes use PascalCase (CommentBlock, ExtractionResult, MyClass)

This distinguishes them from functions/variables which use snake_case.

Special methods (also called "dunder methods" - double underscore):

  __init__(self, ...):   Constructor - initializes a new instance with given values

                         Example: person = Person("Alice", 30)

  __repr__(self):        String representation for debugging/logging

                         Example: print(person)  # Person(name='Alice', age=30)

  __eq__(self, other):   Equality comparison - defines how instances are compared

                         Example: person1 == person2  # Compares their attributes

@dataclass decorator - Automatic boilerplate generation for Python classes

Without @dataclass:

  class Person:

      def __init__(self, name, age):

          self.name = name

          self.age = age

      def __repr__(self):

          return f"Person(name={self.name}, age={self.age})"

      def __eq__(self, other):

          return self.name == other.name and self.age == other.age

With @dataclass:

  @dataclass

  class Person:

      name: str

      age: int

The @dataclass decorator automatically generates __init__, __repr__, and __eq__ methods

based on the class attributes with type annotations. It eliminates ~15 lines of boilerplate.

Dunder methods vs Instance methods - When are they called?

Dunder methods (magic methods):

  - Called AUTOMATICALLY by Python when you perform specific operations

  - You don't call them directly in your code

  - Examples:

      comment = CommentBlock(...)     # Triggers __init__() automatically

      print(comment)                  # Triggers __repr__() automatically

      comment1 == comment2            # Triggers __eq__() automatically

Instance methods (regular methods):

  - Called EXPLICITLY by you in your code

  - You must write the method call yourself

  - Examples:

      comment.to_dict()               # You explicitly call this method

      comment.get_text()              # You explicitly call this method

Summary: Dunder methods = implicit/automatic, Instance methods = explicit/manual

Do classes have return statements?

Class definition - NO return, it's just a blueprint:

  class Person:

      name: str

      age: int

__init__ method - NO return (implicitly returns None):

  def __init__(self, name, age):

      self.name = name

      self.age = age

      # No return statement needed

Regular instance methods - CAN have return statements:

  def get_text(self) -> str:

      return '\n'.join(self.lines)    # Returns a string

  def to_dict(self) -> Dict:

      return asdict(self)             # Returns a dictionary

Summary: Class definition and __init__ don't return values, but regular methods can return

anything like normal functions.

*[Source: extract_comments.py:70]*

---

<a id="general-3"></a>

When to use @dataclass vs regular class?

@dataclass - Use for classes that primarily STORE DATA:

  - Main purpose is to bundle related fields together

  - Minimal logic, mostly just holding values

  - Examples: CommentBlock, ExtractionResult, Person, Config

  - Think of it as a simple data container

Regular class - Use for classes that primarily contain BEHAVIOR/LOGIC:

  - Main purpose is to perform operations and processing

  - Has complex methods and algorithms

  - Examples: CommentExtractor, Parser, DatabaseConnection, APIClient

  - Like traditional OOP classes with business logic

In this file:

  CommentBlock (dataclass)      → Data container: stores tag, lines, line_number

  ExtractionResult (dataclass)  → Data container: stores file_path, total_comments

  CommentExtractor (regular)    → Processing engine: extracts, parses, builds maps

Summary: @dataclass = data storage, Regular class = behavior/logic

*[Source: extract_comments.py:260]*

---

## class: CommentBlock

<a id="class:-commentblock-1"></a>

Example: Given this code with comments:

    #EDU Python Classes - Blueprints for creating objects

    #EDU

    #EDU Classes are used to bundle data and functionality together.

    @dataclass

    class CommentBlock:

What gets stored in ONE CommentBlock object:

    CommentBlock(

        tag="EDU",

        lines=[

            "Python Classes - Blueprints for creating objects",

            "",

            "Classes are used to bundle data and functionality together."

        ],

        line_number=49,

        file_path="/path/to/extract_comments.py",

        context=None (as it's outside any function/class)

    )

What to_dict() returns (for JSON serialization):

    {

        'tag': 'EDU',

        'lines': [

            'Python Classes - Blueprints for creating objects',

            '',

            'Classes are used to bundle data and functionality together.'

        ],

        'line_number': 49,

        'file_path': '/path/to/extract_comments.py',

        'context': None

    }

What get_text() returns (just the comment text joined with newlines):

    "Python Classes - Blueprints for creating objects\\n\\nClasses are used to bundle data and functionality together."

How many lines are in a CommentBlock?

A CommentBlock is a CONTINUOUS GROUP of tagged comment lines.

It can be 1 line or 1000 lines - there's no fixed size.

The block ENDS when one of these happens:

  1. Non-comment line appears (code, blank line without #)

  2. Different tag starts (switching from #EDU to #NOTE)

  3. File ends

Examples of CommentBlock boundaries:

  Single block (3 lines):

    #EDU Line 1

    #EDU Line 2

    #EDU Line 3

  Two blocks separated by code:

    #EDU Block 1 line 1

    #EDU Block 1 line 2

    def foo():          # ← Code ends block 1

        #EDU Block 2 line 1  # ← New block starts

  Two blocks with different tags:

    #EDU Block 1

    #NOTE Block 2       # ← Different tag = new block

  One block with continuation lines:

    #EDU This starts the block

    # This continues (no tag, but still a comment in the block)

The logic that determines block boundaries is in the CommentExtractor class:

  - extract_from_file() method (lines 269-364)

  - Lines 299-310: Detects non-comment lines and ends the current block

  - Lines 315-334: Detects tag changes and starts new blocks

  - Lines 336-350: Handles continuation lines within the same block

*[Source: extract_comments.py:154]*

---

## function: __init__

<a id="function:-__init__-1"></a>

Regex pattern for tag matching - How tags are detected

Pattern: rf'^\s*#\s*({tag_pattern})[\s:]*(.*)$'

Breaking down the regex:

  ^\s*        - Start of line, optional leading whitespace

  #           - The hash/pound symbol

  \s*         - Optional whitespace after #

  ({tag_pattern})  - Captures THE FIRST TAG (EDU, NOTE, TODO, etc.)

  [\s:]*      - Optional whitespace or colons after tag

  (.*)$       - Captures everything else as content (until end of line)

This pattern matches:

  #EDU content          → tag: "EDU", content: "content"

  # EDU content         → tag: "EDU", content: "content"

  #EDU: content         → tag: "EDU", content: "content"

  #  EDU  :  content    → tag: "EDU", content: "content"

IMPORTANT: Only the FIRST tag on a line is recognized!

If you write:  #EDU #NOTE some text

It becomes:    tag: "EDU", content: "#NOTE some text"

The "#NOTE" is treated as regular text, NOT a second tag.

Always use ONE tag per line to avoid confusion.

*[Source: extract_comments.py:293]*

---
