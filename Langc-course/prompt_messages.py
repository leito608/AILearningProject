from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain.chat_models import init_chat_model

load_dotenv()

prompt = ChatPromptTemplate.from_template("Tell me a {adjective} joke about {topic}")

messages = prompt.format_messages(adjective="funny", topic="chickens")

print(f"Messages: {messages}")

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant that translates {input_language} to {output_language}"),
        ("human", "Translate the following text: {text}")
    ]
)
messages = prompt.format_messages(
    input_language="English",
    output_language="French",
    text="I love programming"
)

model = init_chat_model(  
    model="gemini-3.5-flash-lite",
    model_provider="google_genai",
    max_retries=3,
    streaming=True,
)
response = model.invoke(messages)
print(f"Response: {response.text}")


messages = [
    SystemMessage(content="You are a helpful assistant that translates English to French"),
    HumanMessage(content="Hello"),
    AIMessage(content="Hi there! How can I assist you today?"),
    HumanMessage(content="Translate: I enjoy learning languages."),
]

response = model.invoke(messages)
print(f"Response: {response.text}")

from langchain_core.prompts import FewShotChatMessagePromptTemplate

examples = [
    {"input": "happy", "output": "joyful"},
    {"input": "sad", "output": "unhappy"},
    {"input": "angry", "output": "mad"},
    {"input": "excited", "output": "thrilled"}
]

example_prompt = ChatPromptTemplate.from_messages(
    [
        ("human", "{input}"),
        ("ai", "{output}"),
    ]
)

examples_few_shot_prompt = FewShotChatMessagePromptTemplate(
    examples=examples,
    example_prompt=example_prompt,
)

final_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant that converts emotions to synonyms"),
        examples_few_shot_prompt,
        ("human", "{input}"),
    ]
)

response = model.invoke(final_prompt.format_messages(input="happy"))
print(f"Response: {response.text}")


system_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a {role}")
    ]
)
user_prompt = ChatPromptTemplate.from_messages(
    [
        ("human", "{question}")
    ]
)
full_prompt = system_prompt + user_prompt
response = model.invoke(full_prompt.format_messages(role="helpful assistant", question="What is the capital of France?"))
print(f"Response: {response.text}")

