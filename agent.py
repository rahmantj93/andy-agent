"""Agent loop - handles Claude API calls and tool execution."""
from anthropic import Anthropic
from tools import run_tool, TOOL_SCHEMAS
from prompts import SYSTEM_PROMPT

client = Anthropic()
MODEL = "claude-haiku-4-5"


def step(messages: list) -> None:
    """
    Run one full agent turn:
    - Send messages to Claude
    - If Claude wants tools, run them and loop until Claude is done
    - Mutates `messages` in place (appends Claude's responses and tool results)
    - Prints Andy's final text reply when stop_reason is end_turn
    """
    while True:
        response = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            tools=TOOL_SCHEMAS,
            messages=messages
        )

        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "end_turn":
            for block in response.content:
                if block.type == "text":
                    print(f"🤖 Andy: {block.text}\n")
            return

        if response.stop_reason == "tool_use":
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    result = run_tool(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result
                    })
            messages.append({"role": "user", "content": tool_results})
            # loop again with the tool results added to the conversation