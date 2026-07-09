import sys
import os
import pytest
from datetime import datetime

# Add the backend to sys.path so we can import voxcore modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../backend')))

from voxcore.memory.composition.context_builder import ContextBuilder
from voxcore.contracts.storage.i_store import ConversationTurn

def create_turn(role: str, content: str = "", metadata: dict = None) -> ConversationTurn:
    return ConversationTurn(
        role=role,
        content=content,
        timestamp=datetime.now(),
        metadata=metadata
    )

def test_sliding_window_no_truncation():
    builder = ContextBuilder()
    history = [
        create_turn("user", "Hello"),
        create_turn("assistant", "Hi there!")
    ]
    
    # max_turns=5, history is 2, shouldn't truncate
    messages = builder.build(history, max_turns=5)
    
    # 1 system prompt + 2 messages
    assert len(messages) == 3
    assert messages[0]["role"] == "system"
    assert messages[1]["role"] == "user"
    assert messages[2]["role"] == "assistant"

def test_sliding_window_truncation_on_clean_boundary():
    builder = ContextBuilder()
    history = [
        create_turn("user", "1"),
        create_turn("assistant", "2"),
        create_turn("user", "3"),
        create_turn("assistant", "4"),
        create_turn("user", "5"),
        create_turn("assistant", "6")
    ]
    
    # max_turns=4. The last 4 messages are user(3), assistant(4), user(5), assistant(6).
    # It starts on a 'user' message, so it shouldn't pop anything extra.
    messages = builder.build(history, max_turns=4)
    
    assert len(messages) == 5 # 1 system + 4 history
    assert messages[1]["content"] == "3"
    assert messages[2]["content"] == "4"
    assert messages[3]["content"] == "5"
    assert messages[4]["content"] == "6"

def test_sliding_window_truncation_on_tool_boundary():
    builder = ContextBuilder()
    history = [
        create_turn("user", "What's the weather?"),  
        create_turn("assistant", "", metadata={"tool_calls": [{"id": "call_1", "type": "function", "function": {"name": "get_weather"}}]}),
        create_turn("tool", "Sunny", metadata={"tool_call_id": "call_1", "name": "get_weather"}),
        create_turn("assistant", "It is sunny."),
        create_turn("user", "Thank you."),
        create_turn("assistant", "You're welcome.")
    ]
    
    # max_turns=4. 
    # Last 4: tool("Sunny"), assistant("It is sunny"), user("Thank you"), assistant("You're welcome")
    # First is "tool", not "user". 
    # The while loop will pop "tool", then pop "assistant" ("It is sunny"), until it hits "user" ("Thank you").
    messages = builder.build(history, max_turns=4)
    
    assert len(messages) == 3 # 1 system + user("Thank you") + assistant("You're welcome")
    assert messages[1]["role"] == "user"
    assert messages[1]["content"] == "Thank you."
    assert messages[2]["role"] == "assistant"
    assert messages[2]["content"] == "You're welcome."
