---
title: setup_config
tags:
  - jarvis
  - python
  - documentation
date: 2025-09-21
---

# setup_config

-- GENERAL INFORMATION --
AUTHOR: NhoaKing (pseudonym for privacy)
PROJECT: jarvis (personal assistant using ElGato StreamDeck XL)
NAME: setup_config.py
-- DESCRIPTION --
Setup script to create personalized configuration for Jarvis StreamDeck.

This script provides interactive configuration through prompts in terminal that helps users
set up their jarvis environment by creating a personalized config.env file. It handles path detection,
user inputs, and configuration file generation.

Purpose:
- Simplify initial jarvis setup for new users
- Generate properly formatted configuration files with sensible defaults according to user environment.
- Detect system-specific paths and tools
- Prevent common configuration errors

Usage:
Open a default terminal (CTRL+ALT+T) and run:
- python3 setup_config.py

Output:
- Creates config.env file in the jarvis directory with user-specific configuration

This first line of the script (#!/usr/bin/python3) is the 'shebang' line. 
It is a label that tells the system which interpreter to use to run the script.
In this case, it specifies to use the system default python 3 interpreter. 
This is important for scripts that are intended to be run directly from the command line.

In this way, it ensures that the script will use python 3 default installation.
New users probably do not have any virtual environment set up yet, so in this way 
we avoid using specific environment names. The purpose of this script is simply to create a config.env file, 
so no dependencies are needed as only standard modules are used.

## Functions

- [[#create_config|create_config()]]

## create_config

```python
def create_config():
```

Create a personalized config.env file through interactive prompts.

This function provides an interactive configuration menu that guides
users through setting up their jarvis environment. It provides a simple way
to collect user inputs for paths and generates a properly formatted configuration file
as the jarvis modules expect.

Process:
1. Checks for existing configuration and asks about overwriting
2. Prompts user for values
4. Generates properly formatted config.env file
5. Provides simple usage instructions and some warnings about security

Output:
Creates config.env with paths for ydotool, projects directory,
and obsidian vaults.

## Additional Code Context

Other contextual comments from the codebase:

- **Line 1:** !/usr/bin/python3
- **Line 38:** Modern path handling, more robust than os.path
- **Line 58:** Determine path for configuration file (same directory as this script)
- **Line 61:** Check if configuration already exists and asks user permission to overwrite
- **Line 66:** Exit without making changes
- **Line 71:** More reliable than os.path.expanduser('~'). It provides a path object. In this case it will be /home/username
- **Line 73:** ydotool path configuration
- **Line 84:** Projects directory configuration. The default is /home/username/projects
- **Line 89:** Obsidian vault configurations - multiple vaults with codenames
- **Line 90:** In my case I use two vaults, one for journaling and one for projects documentation and task management,
- **Line 91:** as I am using quartz to create my static website from my notes and host that through github pages later on.
- **Line 92:** You can customize these vaults for your use case. Use only one vault if you want, or more than two.
- **Line 93:** However, if you use more than two, please introduce the paths to the vaults directly manually inside
- **Line 94:** the config.env, and then refer to them with the codename after "OBISIDIAN_VAULT_" in the config.env file.
- **Line 95:** In the actions module you can then refer to them with the same codename to access the vault you want.
- ... and 8 more contextual comments
