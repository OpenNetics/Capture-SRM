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
        echo -e "\033[31mActivating virtual environment...\033[0m"
        source ./.venv/bin/activate 2>/dev/null
        ;;

    --reinstall)
        echo -e "\033[31mRemoving existing virtual environment...\033[0m"
        rm -rf ./.venv

        echo -e "\033[31mCreating a new virtual environment...\033[0m"
        python3 -m venv ./.venv

        echo -e "\033[31mInstalling requirements...\033[0m"
        source ./.venv/bin/activate
        python3 -m pip install -r ./requirements.txt
        ;;

    --update)
        if [ ! -d "./.venv" ]; then
            echo -e "\033[31mVirtual environment not found. Creating it...\033[0m"
            python3 -m venv ./.venv

            echo -e "\033[31mInstalling requirements...\033[0m"
            source ./.venv/bin/activate
            python3 -m pip install -r ./requirements.txt
        else
            echo -e "\033[31mActivating existing virtual environment...\033[0m"
            source ./.venv/bin/activate
        fi

        echo -e "\033[31mPulling updated git release...\033[0m"


        echo -e "\033[31mUpdating installed packages...\033[0m"
        python3 -m pip install --upgrade -r ./requirements.txt
        ;;

    --help)
        print_help
        exit 0
        ;;
esac

# Run the main Python script
echo -e "\033[31mRunning main script...\033[0m"
python3 ./src/main.py

