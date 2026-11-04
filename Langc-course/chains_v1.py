from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import (
    RunnableBranch,
    RunnableParallel, 
    RunnablePassthrough, 
    RunnableLambda, 
    RunnableBranch
    )
from langsmith import traceable
load_dotenv()

model = init_chat_model("gemini-3.5-flash-lite",
                        model_provider="google_genai",
                        temperature=0,
                        max_output_tokens=1500,
                        max_retries=3)

def demo_basic_chain():
    prompt = ChatPromptTemplate.from_template("Summarize the following text in one sentence: {text}")

    parser = StrOutputParser()

    chain = prompt | model | parser

    result = chain.invoke(
        {"text": "LangChain is a framework for developing applications powered by language models."}
    )
    print("Basic chain result:", result)

def demo_parallel_chain():
    summary_prompt = ChatPromptTemplate.from_template(
        "Summarize the following text in two sentence: {text}"
        )
    keywords_prompt = ChatPromptTemplate.from_template(
        "Extract the keywords from the following text: {text}\n Return as a comma-separated list."
    )
    sentiment_prompt = ChatPromptTemplate.from_template(
        "Analyze the sentiment of the following text: {text}"
    )

    parser = StrOutputParser()
    analysis_chain = RunnableParallel(
        summary = summary_prompt | model | parser,
        keyword = keywords_prompt | model | parser,
        sentiment = sentiment_prompt | model | parser
    )

    text = """
    The new AI features are absolutely amazing and will greatly enhance productivity.
    However, some have noted that prices for these features can be quite high.
    """
    result = analysis_chain.invoke({"text": text})
    print("Analysis chain result")
    print("Parallel chain result:", result)
    print(f".  Sentiment analysis result: {result['sentiment']}")
    print(f".  Keyword extraction result: {result['keyword']}")
    print(f".  Summary result: {result['summary']}")   

def demo_passthrough_chain():
    passthrough_chain = RunnablePassthrough()
    prompt = ChatPromptTemplate.from_template(
        "Original question: {question}\n" \
        "Context: {context}\n\n" \
        "Answer the question based on the context provided."
        )

    def fake_retriever(input_dict): 
        return " LangChain was created by Harrison Chase in 2022."

    chain = (
        RunnableParallel(
            context = RunnableLambda(fake_retriever), 
            question = RunnablePassthrough()
        ) 
        | RunnableLambda(lambda x: 
                {"context": x["context"], 
                "question": x["question"]["question"]}
        ) 
        | prompt 
        | model 
        | StrOutputParser()
    )


    result = chain.invoke({"question": {"question": "Who created LangChain?"}})
    print("Passthrough chain result:", result)

@traceable(name="demo_branching_chain", run_type="chain")
def demo_branching_chain():
    code_prompt = ChatPromptTemplate.from_template(
        "You are coding expert. Help with: {input}"
    )
    general_prompt = ChatPromptTemplate.from_template(
        "You are a helpful assistant. Answer the following question: {input}"
    )
    classifier_prompt = ChatPromptTemplate.from_template(
        "Classify this as 'code' or 'general': {input}\nReturn 'code' or 'general'."
    )

    classifier = classifier_prompt | model | StrOutputParser()
    @traceable(name="is_code_question", run_type="chain")
    def is_code_question(input_dict):
        classification = classifier.invoke(input_dict)
        return classification.lower() == "code"

    branc = RunnableBranch(
        (is_code_question, code_prompt | model | StrOutputParser()),
        general_prompt | model | StrOutputParser(),
    )

    questions = [
        "How do I create a Python function?",
        "What is the capital of France?"
    ]
    for q in questions:
        result = branc.invoke({"input": q})
        print(f"Question: {q}")
        print(f"Answer: {result[:100]}...\n")

def demo_debugging():
    prompt = ChatPromptTemplate.from_template(
        "Say hello to: {name}"
    )
    chain = prompt | model | StrOutputParser()

    print("Chain input schema:", chain.input_schema.model_json_schema())
    print("Chain output schema:", chain.output_schema.model_json_schema())


    result = chain.with_config(
        run_name="greeting chain"
    ).invoke({"name": "Jone"})
    
    print("Debugging chain result:", result)

    def log_step(x, step_name=""):
        print(f"Step '{step_name}' {type(x).__name__}: {str(x)[:100]}")
        return x

    debug_chain = (
        prompt
        | RunnableLambda(lambda x: log_step(x, "after prompt"))
        | model
        | RunnableLambda(lambda x: log_step(x, "after model"))
        | StrOutputParser()
    )
    debug_chain.invoke({"name": "Jone"})
    print("Debugging chain invoked.")
    print("Debugging chain completed.")

if __name__ == "__main__":
    #demo_basic_chain()  
    #demo_parallel_chain()
    #demo_passthrough_chain()
    #demo_branching_chain()
    demo_debugging()



