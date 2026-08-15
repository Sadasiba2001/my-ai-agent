import argparse
import sys

from dotenv import load_dotenv

from my_ai_agent import __version__
from my_ai_agent.agent.engine import AgentEngine
from my_ai_agent.config import settings
from my_ai_agent.utils.logging import setup_logging

load_dotenv()


def main() -> None:
    
    parser = argparse.ArgumentParser(
        description="My AI Agent — Modular & Extensible Python AI Agent"
    )
    
    parser.add_argument(
        "-v", "--version", action="version", version=f"%(prog)s {__version__}"
    )
    
    parser.add_argument(
        "--prompt", type=str, help="Single query execution mode"
    )
    
    parser.add_argument(
        "--log-level",
        type=str,
        default=settings.log_level,
        help="Logging level (DEBUG, INFO, WARNING, ERROR)",
    )

    args = parser.parse_args()
    setup_logging(args.log_level)

    agent = AgentEngine(max_iterations=settings.agent_max_iterations)

    if args.prompt:
        response = agent.run(args.prompt)
        print(f"\nAgent:\n{response}")
        sys.exit(0)

    print(f"{settings.agent_name} (v{__version__})")
    print("=" * 40)
    print("Type 'exit' or 'quit' to exit.\n")

    while True:
        try:
            user_input = input("You: ")
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            break

        if user_input.lower().strip() in ["exit", "quit"]:
            print("Goodbye!")
            break

        if not user_input.strip():
            continue

        response = agent.run(user_input)
        print(f"\nAgent:\n{response}\n")


if __name__ == "__main__":
    main()
