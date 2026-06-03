"""Whoami — a daily-seeded famous-person guessing game for the RetryBot demo.

Run with no arguments to get an introduction from the mystery guest.
Run with one argument to ask the mystery guest a question.
If your argument contains the person's name (or close enough), they reveal themselves.

The API key is intentionally wrong (MISTAKE_API_KEY instead of MISTRAL_API_KEY).
This is a deliberate demo bug — do not fix it.
"""

import datetime
import os
import random
import sys

from openai import OpenAI

_FAMOUS_PEOPLE = [
    "Albert Einstein",
    "Marie Curie",
    "Leonardo da Vinci",
    "Nikola Tesla",
    "Ada Lovelace",
    "Alan Turing",
    "Grace Hopper",
    "Cleopatra",
    "William Shakespeare",
    "Charles Darwin",
    "Isaac Newton",
    "Frida Kahlo",
    "Socrates",
    "Napoleon Bonaparte",
    "David Attenborough",
    "Rosalind Franklin",
    "Galileo Galilei",
    "Maya Angelou",
]

_SYSTEM_PROMPT = (
    "You are {person}. Never reveal any part of your name or any information that"
    " directly identifies you. The user will ask you questions to guess who you are."
    " Answer all questions concisely and truthfully (but don't reveal any part of"
    " your name) while in character."
    " If the user's guess is very close to your name — including minor spelling"
    " errors or using only your first or last name — confirm enthusiastically"
    " that they have identified you correctly."
)

_REVEAL_MESSAGE = (
    "The user has guessed your identity correctly. Confirm enthusiastically"
    " that you are {person} and say something memorable in character."
)


def _pick_person() -> str:
    random.seed(datetime.date.today().toordinal())
    return random.choice(_FAMOUS_PEOPLE)  # noqa: S311


def _is_name_guess(arg: str, person: str) -> bool:
    """Return True if any word (≥4 chars) from arg appears in the person's name."""
    person_lower = person.lower()
    return any(word in person_lower and len(word) >= 4 for word in arg.lower().split())


def main() -> None:
    person = _pick_person()
    client = OpenAI(
        api_key=os.environ["MISTRAL_API_KEY"], base_url="https://api.mistral.ai/v1"
    )
    system = _SYSTEM_PROMPT.format(person=person)

    if len(sys.argv) == 1:
        user_message = "Greet the user, and ask them to guess your identity."
    else:
        arg = sys.argv[1]
        if _is_name_guess(arg, person):
            user_message = _REVEAL_MESSAGE.format(person=person)
        else:
            user_message = arg

    response = client.chat.completions.create(
        model="mistral-small-latest",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user_message},
        ],
    )
    print(response.choices[0].message.content)


if __name__ == "__main__":
    main()
