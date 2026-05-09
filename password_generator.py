import random
import string

def generate_password(length: int) -> str:
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ""

    for _ in range(length):
        password += random.choice(characters)

    return password


def main():
    print("🔐 Password Generator")

    try:
        length = int(input("Enter password length: "))
    except ValueError:
        print("Please enter a valid number.")
        return

    password = generate_password(length)
    print(f"Your password: {password}")


if __name__ == "__main__":
    main()