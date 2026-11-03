from langchain_core.prompts import ChatPromptTemplate
from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field
from typing import List, Optional
from dotenv import load_dotenv
from langsmith import traceable, Client
import os


load_dotenv()

if os.getenv("LANGSMITH_API_KEY"):
    os.environ["LANGSMITH_TRACING"] = "true"
    os.environ.setdefault("LANGSMITH_PROJECT_NAME", "Smart Q&A Bot Project")
    print(f"LANGSMITH_API_KEY is set and LANGSMITH_PROJECT_NAME is {os.environ['LANGSMITH_PROJECT_NAME']}")

class QAResponse(BaseModel):
    answer: str = Field( description="The answer to the question")
    confidence: str = Field(description="The confidence level of the answer")
    reasoning: str = Field(description="The reasoning behind the answer")
    follow_up_question: List[str] = Field(
        description="The list of follow-up questions related to the topic",
        default_factory=list
    )
    source_needed: bool = Field(
        description="Indicates whether the source is needed for the answer",
        default=False
    )

class SmartQABot:
    def __init__(
        self,
        model_name: str="gemini-3.5-flash-lite",
        model_provider: str="google_genai",
        temperature: float = 0.3
    ):
        self.chat_model = init_chat_model(
            model=model_name,
            model_provider=model_provider,
            temperature=temperature
        ).with_structured_output(QAResponse)

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a knowledgeable assistant who provides accurate and detailed answers to questions.
            Your guidelines:
            - Answer questions accurately and concisely.
            - Be honest about uncertainty - set confidence to 'low' if unsure.
            - Provide clear reasoning for your answers.
            - Suggest follow-up questions if applicable.
            - Indicate if sources are needed for the answer.

            Always respond with accurate, helpful information.
            """),
            ("human", "{question}")
        ])

        self.chain = self.prompt | self.chat_model

    @traceable(name="ask_question", run_type="chain")
    def ask_question(self, question: str) -> QAResponse:
        try:
            response = self.chain.invoke({"question": question})
            return response
        except Exception as e:
            print(f"Error occurred: {e}")
            return QAResponse(
                answer="I'm sorry, I couldn't provide an answer.",
                confidence="low",
                reasoning=str(e),
                follow_up_question=["Could you please try again later?"],
                source_needed=True
            )

    @traceable(name="ask_batch", run_type="chain")
    def ask_batch(self, questions: List[str]) -> List[QAResponse]:
        """Ask multiple questions in parallel and return their responses"""
        inputs = [{"question": q} for q in questions]
        return self.chain.batch(inputs)

    

@traceable(name="demo_qa_bot", run_type="chain")
def demo_qa_bot():
    bot = SmartQABot()
    question = ["What is the capital of France?",
                "Explain the theory of relativity?",
                "How does photosynthesis work?"]
    print("=" * 60)
    print("SMART QA BOT DEMO")
    print("=" * 60)

    for question in question:
        print(f"\nQuestion: {question}")
        print("-" * 40)
        response = bot.ask_question(question)
        print(f"Answer: {response.answer}")
        print(f"Confidence: {response.confidence}")
        print(f"Reasoning: {response.reasoning}")
        print(f"Follow-up Questions: {response.follow_up_question}")
        print(f"Source Needed: {response.source_needed}")
        print("-" * 40)
        print("\n")

@traceable(name="demo_error_handling", run_type="chain")
def demo_error_handling():
    bot = SmartQABot()
    long_question = "What is" + "very" * 100 + "important?"
    print("=" * 60)
    print("SMART QA BOT ERROR HANDLING DEMO")
    print("=" * 60)
    response = bot.ask_question(long_question)
    print(f"Answer: {response.answer}")
    print(f"Confidence: {response.confidence}")
    print(f"Reasoning: {response.reasoning}")
    print(f"Follow-up Questions: {response.follow_up_question}")
    print(f"Source Needed: {response.source_needed}")
    print("-" * 40)

@traceable(name="demo_batch_questions", run_type="chain")
def demo_batch_questions():
    bot = SmartQABot()
    questions = ["What is Python?",
                 "What is Java?",
                 "What is Ruby?"]
    print("=" * 60)
    print("SMART QA BOT BATCH QUESTIONS DEMO")
    print("=" * 60)
    responses = bot.ask_batch(questions)
    for i, response in enumerate(responses):
        print(f"\nQuestion: {questions[i]}")
        print("-" * 40)
        print(f"Answer: {response.answer}")
        print(f"Confidence: {response.confidence}")
        print(f"Reasoning: {response.reasoning}")
        print(f"Follow-up Questions: {response.follow_up_question}")
        print(f"Source Needed: {response.source_needed}")
        print("-" * 40)
        print("\n")

if __name__ == "__main__":
    try:
        demo_qa_bot()
        demo_error_handling()
        demo_batch_questions()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        pass
        #Client().flush() # Flush any pending telemetry data to the client
