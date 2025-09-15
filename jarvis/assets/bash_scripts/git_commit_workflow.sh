#!/bin/bash

# Get PROJECTS_DIR from first parameter
PROJECTS_DIR="$1"

gnome-terminal -- bash -l -c "
    # Function to handle CTRL+C
    cleanup() {
        echo \"\"
        echo \"Script interrupted by user. Exiting...\"
        exit 1
    }

    # Set up trap for CTRL+C
    trap cleanup SIGINT

    echo \"=== Git Commit Workflow ===\"
    echo \"\"
    echo \"Projects directory: $PROJECTS_DIR\"
    echo \"\"

    # Prompt for project name
    echo \"Enter project name (or press CTRL+C to exit):\"
    read -r PROJECT_NAME

    if [ -z \"\$PROJECT_NAME\" ]; then
        echo \"No project name provided. Exiting...\"
        exit 1
    fi

    PROJECT_PATH=\"$PROJECTS_DIR/\$PROJECT_NAME\"

    if [ ! -d \"\$PROJECT_PATH\" ]; then
        echo \"Project directory '\$PROJECT_PATH' does not exist. Exiting...\"
        exit 1
    fi

    echo \"Changing to project directory: \$PROJECT_PATH\"
    cd \"\$PROJECT_PATH\" || {
        echo \"Failed to change to project directory. Exiting...\"
        exit 1
    }
    echo \"\"

    # Step 1: git status
    echo \"Step 1: Checking git status...\"
    git status
    echo \"\"

    # Prompt for continuation
    echo \"Do you want to continue? Press Enter to proceed or CTRL+C to exit.\"
    read -r

    # Step 2: git add .
    echo \"\"
    echo \"Step 2: Adding all changes...\"
    git add .
    echo \"Files added to staging area.\"
    echo \"\"

    # Prompt for continuation
    echo \"Do you want to continue with commit? Press Enter to proceed or CTRL+C to exit.\"
    read -r

    # Step 3: git commit
    echo \"\"
    echo \"Step 3: Creating commit...\"
    git commit
    echo \"\"
    echo \"Commit workflow completed!\"
    echo \"Press Enter to close this terminal...\"
    read -r
"