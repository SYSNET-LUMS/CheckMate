# from langchain_core.pydantic_v1 import BaseModel, Field, validator
from pydantic import BaseModel, Field

# Making some output formats


class AnnotateData(BaseModel):
    approximation_description: str = Field("Describe what type of approximation can occur based on their function purpose and structure.")
    annotated_code: str = Field(
        description="Annotated code with comments where approximation can occur, code should be formated as corrently with '\n' and other spacings."
    )
    description: str = Field(description="Describe each approximation identifyied")


class ApproximatedData(BaseModel):
    approxmated_code: str = Field(
        description="Modifiyed function code with Approximation applied for each of the identified areas. Code should be formated as corrently with '\n' and other spacings."
    )
    knob_variables: str = Field(
        description="List of all the knob variables. Example format '['loop_skip', 'threshold', 'block_skip']'. If no knob variables then return an empty list []."
    )
    knob_ranges: str = Field(
        description="List of ranges of each knob variable in knob_variables list. Example format '[{'loop_skip': [1, 5]}, {'threshold': [8, 20]}, {'block_skip': [1, 5]}]'. If no knob variables then return an empty list []. Do NOT return a string as range point like this [{'loop_skip': [1, 'len']}]"
    )
    knob_increments: str = Field(
        description="This is the category of the step size of that the knob should use, it can either be Integer or Real. Example format '[{'loop_skip': 'Integer'}, {'threshold': 'Real'}, {'block_skip': 'Integer'}]' If no knob variables then return an empty list. []"
    )
    # description: str = Field(description="What changes have beeen made to the code and what would there effect be on the output of the function.")
