#!/usr/bin/env bash

#- Helper Functions --------------------------------------------------------------------------------

function print_help() {
    echo -e "USAGE:\n\033[31m  $0 \033[32m{OPTIONS}\n"

    echo -e "\033[0mOPTIONS:"
    echo -e "\033[32m  --install    \033[33mInstall all dependencies."
    echo -e "\033[32m  --reinstall  \033[33mRemove existing environment and reinstall dependencies."
    echo -e "\033[32m  --update     \033[33mEnsure packages are installed and update them."
    echo -e "\033[32m  --help       \033[33mDisplay this help message."
    echo -e "\033[0m"
}

function create_virtual_env() {
    echo -e "\033[33m[Creating a new virtual environment]\033[0m"
    python3 -m venv ./.venv

    echo -e "\033[33m[Installing requirements]\033[0m"
    source ./.venv/bin/activate
    python3 -m pip install -r ./src/requirements.txt
}

function delete_virtual_env() {
    echo -e "\033[31m[Removing existing virtual environment]\033[0m"
    rm -rf ./.venv
}


#- Check for Flags ---------------------------------------------------------------------------------

case $1 in
    --install)
        create_virtual_env
        ;;

    --reinstall)
        delete_virtual_env
        create_virtual_env
        ;;

    --update)
        # pull new release
        echo -e "\033[33m[Pulling updated git release]\033[0m"
        git pull

        # activate virtual-environment
        if [ ! -d "./.venv" ]; then
            echo -e "\033[31m[Virtual environment not found]\033[0m"
            create_virtual_env

        else
            echo -e "\033[33m[Activating existing virtual environment]\033[0m"
            source ./.venv/bin/activate
        fi

        # update all packages
        echo -e "\033[33m[Updating installed packages]\033[0m"
        python3 -m pip install --upgrade -r ./src/requirements.txt
        ;;

    --help)
        print_help
        ;;
esac


#- Run GestureTracker ------------------------------------------------------------------------------

# Run the main script when no --args are added
if [ -z "$1" ]; then
    echo -e "\033[33m[Activating virtual environment]\033[0m"
    if [ ! -d "./.venv" ]; then
        echo -e "\033[31m[Virtual environment not found]\033[0m"
        create_virtual_env
    fi
    source ./.venv/bin/activate 2>/dev/null

    echo -e "\033[1;33m[Running GestureTracker]\033[0m"
    python3 ./src/main.py
fi

