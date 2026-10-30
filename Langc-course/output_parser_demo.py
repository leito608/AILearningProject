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
from langchain_core.output_parsers import JsonOutputParser
#from langchain_core.output_parsers import StructuredOutputParser

from langchain.chat_models import init_chat_model
from dotenv import load_dotenv


load_dotenv()

parser = StrOutputParser()
prompt = ChatPromptTemplate.from_template("wire a short story about {topic}")
llm = init_chat_model(
    model="gemini-3.5-flash-lite",
    model_provider="google_genai",
    max_retries=3,
    streaming=True,
)
chain = prompt | llm | parser
response  = chain.invoke({"topic": "a brave knight"})
print(type(response))

# JSON output parser example
parser = JsonOutputParser()
prompt = ChatPromptTemplate.from_template("Return a JSON object with 'name' and 'age' for: {description}")
chain = prompt | llm | parser
response = chain.invoke({"description": "John Doe 25 years old"})
print(response)


#Pydantic output parser example
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

class Person(BaseModel):
    name: str = Field(description="The person's full name")
    age: int = Field(description="The person's age")
    occupation: str = Field(description="The person's occupation")

parser = PydanticOutputParser(pydantic_object=Person)
prompt = ChatPromptTemplate.from_template(
    "Return a JSON object with 'name', 'age', and 'occupation' for: {description}"
).partial(format_instructions=parser.get_format_instructions())

chain = prompt | llm | parser
response = chain.invoke({"description": "Artist John Doe 25 years old"})
print(f"Prompt: {prompt}")
print(f"Response: {response}")

#structured output parser example


class MovieReview(BaseModel):
    title: str = Field(description="The title of the movie")
    review: str = Field(description="The review of the movie")
    rating: int = Field(description="The rating of the movie")


structured_model = llm.with_structured_output(MovieReview)
prompt = ChatPromptTemplate.from_template("Review movie: {movie_title}")

result = structured_model.invoke("Review: Inception is a mind-bending thriller with stunning visuals. 9/10")
print(f"Result: {result}")

chain = prompt | structured_model
result = chain.invoke({"movie_title": "Dune"})
print(f"Result from template: {result.rating}")


class CompanyInfo(BaseModel):
    name: str = Field(description="The name of the company")
    industry: str = Field(description="The industry the company operates in")
    employees: int = Field(description="The number of employees in the company")
    headquarters: str = Field(description="The location of the company's headquarters")
    directors: str = Field(description="The directors of the company")

company_model = llm.with_structured_output(CompanyInfo)
prompt = ChatPromptTemplate.from_template("Provide information for company: {company_name}")

chain = prompt | company_model
result = chain.invoke({"company_name": "OpenAI"})
print(f"Company Info: {result}")
print(f"Company Name: {result.name}")
print(f"Industry: {result.industry}")
print(f"Employees: {result.employees}")
print(f"Headquarters: {result.headquarters}")
print(f"Directors: {result.directors}")
