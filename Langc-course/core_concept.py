from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()



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
    demo_schema_inspection()

if __name__ == "__main__":
    main()

