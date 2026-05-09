def greet_user() -> None:
    seen_users: set[str] = set()

    while True:
        try:
            name = input("What is your name? (or type 'exit' to quit) ").strip()
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break

        if not name:
            print("Please enter a name.")
            continue

        if name.lower() == "exit":
            print("Goodbye!")
            break

        first_name = name.split()[0].capitalize()
        key = first_name.lower()

        if key in seen_users:
            print(f"Welcome back, {first_name}!")
        else:
            print(f"Hello, {first_name}! Welcome to Python programming.")
            seen_users.add(key)


greet_user()