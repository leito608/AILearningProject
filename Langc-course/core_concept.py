from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.chat_models import init_chat_model
load_dotenv()

def excercise_first_chain():
    """Exercise: create a chain that:
    1. Take a product name and target audience as input.
    2. Generate a marketing tagline
    3. Return just the tagline

    Test with: product="AI Course", audience="developers"
    """
    prompt = ChatPromptTemplate.from_template("Create a shortmarketing tagline for {product} targeting {audience}")
    llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite", temperature=0.4)
    parser = StrOutputParser()
    chain = prompt | llm | parser

    result = chain.invoke({"product": "AI Course", "audience": "developers"})
    print(f"Tagline: {result}")
    return chain

def new_way():
    """Demonstrate a new way to create a chain."""
    model = init_chat_model("gemini-3.5-flash-lite",
                            model_provider="google_genai",
                            temperature=0.4,
                            max_output_tokens=1500,
                            max_retries=3)
    
    prompt = ChatPromptTemplate.from_template("Create a short marketing tagline for {product} targeting {audience}")
    parser = StrOutputParser()
    chain = prompt | model | parser

    result = chain.invoke({"product": "AI Course", "audience": "developers"})
    print(f"Tagline: {result}")
    return chain

def demo_schema_inspection():
    """Demonstrate schema inspection for the chain."""
    prompt = ChatPromptTemplate.from_template("Summarize the following text: {text}")
    llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite", temperature=0.7)
    parser = StrOutputParser()
    chain = prompt | llm | parser

    #Inspect the schema of the chain
    input_schema = chain.input_schema.model_json_schema()
    print("Input schema:", input_schema)
    output_schema = chain.output_schema.model_json_schema()
    print("Output schema:", output_schema)


def demo_steaming():
    """Demonstrate streaming for real-time responses."""
    prompt = ChatPromptTemplate.from_template("Write haiku 20 lines about: {topic}")
    llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite", temperature=0.7, streaming=True)
    parser = StrOutputParser()
    chain = prompt | llm | parser

    print("Streaming response:")
    for chunk in chain.stream({"topic": "Nature"}):
        print(chunk, end="", flush=True)
    print()


def demo_batch_execution():
    """Demonstrate batch execution with the chain for multiple input questions."""
    prompt = ChatPromptTemplate.from_template("Translate to Thai: {text}")
    llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite", temperature=0.7)
    parser = StrOutputParser()
    chain = prompt | llm | parser

    inputs = [{"text": "Hello, how are you?"}, 
              {"text": "LangChain is a framework for building applications with LLMs."}, 
              {"text": "This is a test sentence."}]
    result = chain.batch(inputs)

    for text, res in zip(inputs, result):
        print(f"Input: {text['text']} => Output: {res}")




def demo_basic_chain():
    prompt = ChatPromptTemplate.from_template("You are helpful assistant. Answer in one sentence: {question}")
    llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite", temperature=0.7)
    parser = StrOutputParser()
    # Combine the prompt, LLM, and parser into a chain
    chain = prompt | llm | parser

    result = chain.invoke({"question": "What is LangChain?"})
    print(f"Response: {result}")

    return chain

def main():
    #demo_steaming()
    #demo_schema_inspection()
    #excercise_first_chain()
    new_way()

if __name__ == "__main__":
    main()
