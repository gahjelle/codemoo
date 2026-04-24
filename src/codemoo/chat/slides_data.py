"""Static demo metadata: bot one-liners and source file mappings."""

from codemoo.core.bots.agent_bot import AgentBot
from codemoo.core.bots.chat_bot import ChatBot
from codemoo.core.bots.echo_bot import EchoBot
from codemoo.core.bots.file_bot import FileBot
from codemoo.core.bots.llm_bot import LlmBot
from codemoo.core.bots.shell_bot import ShellBot
from codemoo.core.bots.system_bot import SystemBot
from codemoo.core.bots.tool_bot import ToolBot

BOT_DESCRIPTIONS: dict[type, str] = {
    EchoBot: "Repeat your message verbatim — no LLM, just a mirror.",
    LlmBot: "Call the LLM once and forget the conversation immediately after.",
    ChatBot: "Keep the full conversation history, remember what you said.",
    SystemBot: "Add a system prompt to shape the LLM's persona and behavior.",
    ToolBot: "Call a tool before replying — the first step toward doing things.",
    FileBot: "Read files from disk to answer questions about your code.",
    ShellBot: "Execute shell commands — now it can run code, not just read it.",
    AgentBot: "Loop tool calls until done — pursue goals, not single commands.",
}

BOT_SOURCES: dict[type, list[str]] = {
    EchoBot: ["echo_bot.py"],
    LlmBot: ["llm_bot.py"],
    ChatBot: ["chat_bot.py"],
    SystemBot: ["system_bot.py"],
    ToolBot: ["tool_bot.py", "general_tool_bot.py"],
    FileBot: ["file_bot.py", "general_tool_bot.py"],
    ShellBot: ["shell_bot.py", "general_tool_bot.py"],
    AgentBot: ["agent_bot.py"],
}
