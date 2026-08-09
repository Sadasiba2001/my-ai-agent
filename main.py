# from tools.filesystem import list_files


# def main():
#     print("Testing filesystem tool")
#     print("-" * 40)

#     result = list_files(".")

#     print(result)


# if __name__ == "__main__":
#     main()









# from agent import ask_llm


# def main():
#     print("My AI Agent")
#     print("-" * 40)

#     while True:
#         user_input = input("\nYou: ")

#         if user_input.lower() in ["exit", "quit"]:
#             break

#         response = ask_llm(user_input)

#         print("\nAgent:")
#         print(response)


# if __name__ == "__main__":
#     main()







import os

from dotenv import load_dotenv

from agent.engine import AgentEngine


load_dotenv()


def main():

    agent_name = os.getenv(
        "AGENT_NAME",
        "My AI Agent"
    )

    max_iterations = int(
        os.getenv(
            "AGENT_MAX_ITERATIONS",
            "10"
        )
    )

    agent = AgentEngine(
        max_iterations=max_iterations
    )

    print(agent_name)
    print("-" * 40)

    while True:

        user_input = input("\nYou: ")

        if user_input.lower() in [
            "exit",
            "quit"
        ]:
            break

        if not user_input.strip():
            continue

        response = agent.run(
            user_input
        )

        print("\nAgent:")
        print(response)


if __name__ == "__main__":
    main()