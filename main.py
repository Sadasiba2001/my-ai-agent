# from tools.filesystem import list_files


# def main():
#     print("Testing filesystem tool")
#     print("-" * 40)

#     result = list_files(".")

#     print(result)


# if __name__ == "__main__":
#     main()









from agent.llm import ask_llm


def main():
    print("My AI Agent")
    print("-" * 40)

    while True:
        user_input = input("\nYou: ")

        if user_input.lower() in ["exit", "quit"]:
            break

        response = ask_llm(user_input)

        print("\nAgent:")
        print(response)


if __name__ == "__main__":
    main()