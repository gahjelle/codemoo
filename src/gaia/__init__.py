from gaia.chat.app import ChatApp
from gaia.chat.echo_bot import EchoBot
from gaia.chat.participant import HumanParticipant


def main() -> None:
    app = ChatApp(participants=[HumanParticipant(), EchoBot()])
    app.run()
