#!/usr/bin/env bash

function print_help() {
    echo -e "USAGE:\n\033[31m  $0 \033[32m{OPTIONS}\n"

    echo -e "\033[0mOPTIONS:"
    echo -e "\033[32m  --install    \033[33mInstall all dependencies."
    echo -e "\033[32m  --reinstall  \033[33mRemove existing environment and reinstall dependencies."
    echo -e "\033[32m  --update     \033[33mEnsure packages are installed and update them."
    echo -e "\033[32m  --help       \033[33mDisplay this help message."
    echo -e "\033[0m"
}


# Check for flags
case $1 in
    --install)
        echo -e "\033[31m[Activating virtual environment]\033[0m"
        source ./.venv/bin/activate 2>/dev/null
        ;;

    --reinstall)
        echo -e "\033[31m[Removing existing virtual environment]\033[0m"
        rm -rf ./.venv

        echo -e "\033[31m[Creating a new virtual environment]\033[0m"
        python3 -m venv ./.venv

        echo -e "\033[31m[Installing requirements]\033[0m"
        source ./.venv/bin/activate
        python3 -m pip install -r ./src/requirements.txt
        ;;

    --update)
        if [ ! -d "./.venv" ]; then
            echo -e "\033[31m[Virtual environment not found. Creating it]\033[0m"
            python3 -m venv ./.venv

            echo -e "\033[31m[Installing requirements]\033[0m"
            source ./.venv/bin/activate
            python3 -m pip install -r ./src/requirements.txt
        else
            echo -e "\033[31m[Activating existing virtual environment]\033[0m"
            source ./.venv/bin/activate
        fi

        echo -e "\033[31m[Pulling updated git release]\033[0m"
        git pull

        echo -e "\033[31m[Updating installed packages]\033[0m"
        python3 -m pip install --upgrade -r ./src/requirements.txt
        ;;

    --help)
        print_help
        exit 0
        ;;
esac

# Run the main Python script
echo -e "\033[31m[Running GestureTracker]\033[0m"
python3 ./src/main.py

