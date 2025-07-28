import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--bot', action='store_true', help='Run trading bot')
    args = parser.parse_args()

    if args.bot:
        from src.bot.bot_main import run_bot
        run_bot()
    else:
        print("Specify --bot to run trading bot.")

if __name__ == "__main__":
    main()
