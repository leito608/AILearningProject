from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_ollama import OllamaEmbeddings
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import (
    HumanMessage,
    AIMessage,
    SystemMessage,
    trim_messages
)

from langchain_core.chat_history import (
    InMemoryChatMessageHistory,
    BaseChatMessageHistory,
)
from langchain_core.runnables.history import RunnableWithMessageHistory

from langchain_core.output_parsers import StrOutputParser
from typing import Dict
from dotenv import load_dotenv

load_dotenv()

llm = init_chat_model("gemini-3.5-flash-lite",
                    model_provider="google_genai",
                    max_retries=3)

def demo_basic_memory():
    print("=" * 60)

    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content="You are a helpful assistant."),
        MessagesPlaceholder(variable_name="history"),
        HumanMessage(content="{input}")
    ])
    chain = prompt | llm | StrOutputParser()

    store: Dict[str, InMemoryChatMessageHistory] = {}

    def get_session_history(session_id: str) -> BaseChatMessageHistory:
        if session_id not in store:
            store[session_id] = InMemoryChatMessageHistory()
        return store[session_id]

    chain_with_history = RunnableWithMessageHistory(
        chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="history",
    )

    config = {
        "configurable" : {"session_id": "user_123"}
    }

    messages = [
        "Hi! My name is John.",
        "I'm learning about conversation memory.",
        "What is my name and what am I learning about?"
    ]

    print("Conversation with memory:")
    for msg in messages:
        print(f"\nUser: {msg}")
        response = chain_with_history.invoke({"input": msg}, config=config)
        print(f"AI: {response}")


    print(f"\n--- Store history ({len(store['user_123'].messages)} messages) ---")
    for msg in store['user_123'].messages:
        role = "Human" if isinstance(msg, HumanMessage) else "AI"
        print(f"{role}: {msg.content[:50]}")

def demo_multiple_sessions():
    print("=" * 60)

    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content="You are a helpful assistant."),
        MessagesPlaceholder(variable_name="history"),
        HumanMessage(content="{input}")
    ])
    chain = prompt | llm | StrOutputParser()

    store: Dict[str, InMemoryChatMessageHistory] = {}

    def get_session_history(session_id: str) -> BaseChatMessageHistory:
        if session_id not in store:
            store[session_id] = InMemoryChatMessageHistory()
        return store[session_id]

    chain_with_history = RunnableWithMessageHistory(
        chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="history",
    )

    config_user_123 = {
        "configurable" : {"session_id": "user_123"}
    }

    config_user_456 = {
        "configurable" : {"session_id": "user_456"}
    }

    messages_user_123 = [
        "Hi! My name is John.",
        "I'm learning about conversation memory.",
        "What is my name and what am I learning about?"
    ]

    messages_user_456 = [
        "Hello! My name is Alice.",
        "I am exploring chat history.",
        "Can you tell me my name and what I am doing?"
    ]

    print("Conversation with memory for user_123:")
    for msg in messages_user_123:
        print(f"\nUser: {msg}")
        response = chain_with_history.invoke({"input": msg}, config=config_user_123)
        print(f"AI: {response}")

    print("Conversation with memory for user_456:")
    for msg in messages_user_456:
        print(f"\nUser: {msg}")
        response = chain_with_history.invoke({"input": msg}, config=config_user_456)
        print(f"AI: {response}")

    print(f"\n--- Store history for user_123 ({len(store['user_123'].messages)} messages) ---")
    for msg in store['user_123'].messages:
        role = "Human" if isinstance(msg, HumanMessage) else "AI"
        print(f"{role}: {msg.content[:50]}")

    print(f"\n--- Store history for user_456 ({len(store['user_456'].messages)} messages) ---")
    for msg in store['user_456'].messages:
        role = "Human" if isinstance(msg, HumanMessage) else "AI"
        print(f"{role}: {msg.content[:50]}") 


def demo_message_trimming():
    print("=" * 60)
    print("MESSAGE TRIMMING")
    print("Keep conversation within token limits")
    print("=" * 60)

    # Simulate a long conversation
    messages = [
        SystemMessage(content="You are a helpful coding assistant."),
        HumanMessage(content="What is Python?"),
        AIMessage(
            content="Python is a high-level programming language known for readability and versatility. It's used in web development, data science, AI, and automation."
        ),
        HumanMessage(content="How do I install it?"),
        AIMessage(
            content="You can install Python from python.org or use package managers like apt, brew, or chocolatey. I recommend Python 3.12+ for new projects."
        ),
        HumanMessage(content="What about pip?"),
        AIMessage(
            content="Pip is Python's package installer. It comes with Python 3.4+. Use 'pip install package_name' to install packages. Consider using virtual environments with venv or uv."
        ),
        HumanMessage(content="Can you summarize everything we discussed?"),
    ]

    print(f"\nOriginal: {len(messages)} messages")

    trimmed = trim_messages(
        messages,
        max_tokens=60,
        strategy="last",
        token_counter=llm,
        include_system=True,
        allow_partial=False,
    )

    print(f"Trimmed: {len(trimmed)} messages")
    for msg in trimmed:
        role = type(msg).__name__.replace("Message", "")
        print(f"{role}: {msg.content[:50]}...")

def demo_windowed_memory():
    print("=" * 60)
    print("WINDOWED MEMORY")
    print("Keep only the last N messages in memory")
    print("=" * 60)

    class WindowedChatHistory(InMemoryChatMessageHistory):
        """Chat history that keeps only last k message pairs."""

        k: int = 3  # Pydantic field - number of exchange pairs to keep

        def add_messages(self, messages):
            super().add_messages(messages)
            # Keep only last k pairs (2k messages: human + ai)
            if len(self.messages) > self.k * 2:
                self.messages = self.messages[-(self.k * 2) :]

    store: Dict[str, WindowedChatHistory] = {}

    def get_session_history(session_id: str) -> WindowedChatHistory:
        if session_id not in store:
            store[session_id] = WindowedChatHistory()
        return store[session_id]

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a helpful coding assistant."),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}"),
        ]
    )
    chain = prompt | llm | StrOutputParser()

    chain_with_history = RunnableWithMessageHistory(
        chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="history"
    )

    config = {"configurable" : {"session_id" : "windowed_test"}}

        # Simulate a conversation with more than 2 pairs
    exchanges = [
        "My name is Paulo",
        "I live in Seattle",
        "I work as an AI engineer",
        "I have 2 cats",
        "What do you remember about me?",
    ]

    print("\nConversation with k=2 window")
    for i, msg in enumerate(exchanges):
        print(f"User: {msg}")
        response = chain_with_history.invoke(
            {"input": msg}, config = config
        )
        print(f"AI: {response}")

        history = store["windowed_test"].messages
        print(f" [Window: {len(history)} messages]", end="")
        facts_in_memory = [
            m.content[:40] for m in history if isinstance(m, HumanMessage)
        ]
        print(f" [Remembers: {facts_in_memory}]")

    

if __name__ == "__main__":
    #demo_basic_memory()
    #demo_multiple_sessions()
    #demo_message_trimming()
    demo_windowed_memory()
