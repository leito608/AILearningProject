from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage
from os import getenv

load_dotenv()


def demo_init_chat_no_model():
    if not getenv("GEMINI_API_KEY"):
        print("GEMINI_API_KEY is not set.")
        return

    chat_model = init_chat_model(
        model="gemini-3.5-flash-lite",
        model_provider="google_genai",
        max_retries=3,
        streaming=True,
    )
    response = chat_model.invoke("What is the capital of France? Answer in one word.")
    print(f"Response: {response.text}")

def demo_model_comparison():
    if not getenv("GEMINI_API_KEY"):
        print("GEMINI_API_KEY is not set.")
        return
    prompt = "Explain recursion in one sentence."
    models = ["gemini-3.5-flash-lite", "gemini-3.5-flash"]
    print(f"Prompt: {prompt}")

    for model in models:
        chat_model = init_chat_model(
            model=model,
            model_provider="google_genai",
            max_retries=3,
            streaming=True,
        )
        response = chat_model.invoke(prompt)
        print(f"Model: {model}, Response: {response.text}")
    
def demo_message():
    if not getenv("GEMINI_API_KEY"):
        print("GEMINI_API_KEY is not set.")
        return

    chat_model = init_chat_model(
        model="gemini-3.5-flash-lite",
        model_provider="google_genai",
        max_retries=3,
        streaming=True,
    )
    messages = []
    messages.append(SystemMessage(content="You are a pirate. Answer like a pirate."))
    messages.append(HumanMessage(content="What is the weather today"))
    response = chat_model.invoke(messages)
    print(f"Response: {response.text}")

    messages.append(response)
    #print(f"Continue conversation with the pirate.")
    #print(messages)
    messages.append(HumanMessage(content="And what about tomorrow?"))
    response = chat_model.invoke(messages)
    print(f"Folow-up Response: {response.text}")

def exercise_multi_models():
    if not getenv("GEMINI_API_KEY"):
        print("GEMINI_API_KEY is not set.")
        return

    def get_response(question: str, model_names: list[str]) -> dict[str, str]:
        responses = {}
        for model in model_names:
            chat_model = init_chat_model(
                model=model,
                model_provider="google_genai",
                max_retries=3,
                streaming=True,
                temperature=0.7,
            )
            response = chat_model.invoke(question)
            responses[model] = response.text
        return responses

    # Test the function
    question = "What is the AI? Answer in one sentence."
    model_names = ["gemini-3.5-flash-lite", "gemini-3.5-flash"]
    responses = get_response(question, model_names)
    for model, response in responses.items():
        print(f"Model: {model}, Response: {response}")


if __name__ == "__main__":
    #demo_init_chat_no_model()
    #demo_model_comparison()
    #demo_message()
    exercise_multi_models()
