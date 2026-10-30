from langchain_core.prompts import (
    ChatPromptTemplate,
    FewShotChatMessagePromptTemplate,
    MessagesPlaceholder
)
from langchain_core.messages import (
    HumanMessage, 
    SystemMessage, 
    AIMessage
)

from langchain_core.output_parsers import StrOutputParser
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv


load_dotenv()

model = init_chat_model(
    model="gemini-3.5-flash-lite",
    model_provider="google_genai",
    max_retries=3,
    streaming=True,
)

def demo_basic_template():
    simple = ChatPromptTemplate.from_template("Translate '{text}' to '{language}'")

    messages = simple.format_messages(text="Hello", language="French")
    print("Simple template output:")
    print(messages)

    multi = ChatPromptTemplate.from_messages([
        SystemMessage(content="You are a translator."),
        HumanMessage(content="Translate '{text}' to '{language}'")
    ])

    messages_multi = multi.format_messages(text="Hello", language="French")
    print("Multi-message template output:")
    for msg in messages_multi:
        print(f" {type(msg).__name__}: {msg.content}")

def demo_message_types():

    model = init_chat_model(
        model="gemini-3.5-flash-lite",
        model_provider="google_genai",
        max_retries=3,
        streaming=True,
    )
    messages = [
        SystemMessage(content="You are a math tutor."),
        HumanMessage(content="What is 5*5?"),
        AIMessage(content="The answer is 25."),
        HumanMessage(content="And if I multiply by 2?"),
    ]
    response = model.invoke(messages)
    print("Message types demo output:", response.text)

def demo_message_placeholders():
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant."),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{question}'"),
    ])

    history = [
        HumanMessage(content="My name is John."),
        AIMessage(content="Hello John."),
    ]
    messages = prompt.format_messages(question="What is my name?", history=history)
    print("Message placeholders demo output:")
    for msg in messages:
        print(f" {type(msg).__name__}: {msg.content[:50]}...")

    model = init_chat_model(
        model="gemini-3.5-flash",
        model_provider="google_genai",
        max_retries=3,
        streaming=True,
    )

    response = model.invoke(messages)   
    print("Message placeholders demo model output:", response.text)

    chain = prompt | model
    response = chain.invoke({"history": history, "question": "What is my name?"})
    print("Message placeholders demo model output with chain:", response.text)

    parser = StrOutputParser()
    chain = prompt | model | parser
    response = chain.invoke({"history": history, "question": "What is my name?"})
    print("Message placeholders demo model output with chain and parser:", response)




if __name__ == "__main__":
    #demo_basic_template()
    #demo_message_types()
    demo_message_placeholders()

