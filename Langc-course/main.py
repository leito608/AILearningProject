from  dotenv import load_dotenv
from importlib.metadata import version

load_dotenv()

from langchain_core import __version__ as core_version
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI

lg_version = version("langgraph")

print(f"Langchain Core Version: {core_version}, Langgraph Version: {lg_version}")
print(f"Langchain OpenAI Version: {version('langchain_openai')}, Langchain Google Generative AI Version: {version('langchain_google_genai')}")

def main():
    print("Hello, Langc-course!")
    llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite", temperature=0)
    response = llm.invoke("Hello, how are you?")
    print(f"Response from AI : {response}")

if __name__ == "__main__":
    main()



    