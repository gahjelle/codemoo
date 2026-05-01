"""Greet each bot by name."""


def load_names(path: str) -> list[str]:
    with open(path, mode="r", encoding="ascii") as f:
        return [line.strip() for line in f if line.strip()]


def greet(name: str) -> str:
    return f"Hello, {name}!"


def main() -> None:
    names = load_names("names.txt")
    for name in names:
        print(greet(name))


if __name__ == "__main__":
    main()
