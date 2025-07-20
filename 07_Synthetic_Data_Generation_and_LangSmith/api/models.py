from typing import List, Dict, Optional, Literal
from pydantic import BaseModel, Field

class Document(BaseModel):
    """Input document model"""
    page_content: str = Field(..., description="The content of the document")
    metadata: Dict = Field(default_factory=dict, description="Document metadata")

class EvolvedQuestion(BaseModel):
    """Evolved question with tracking information"""
    id: str = Field(..., description="Unique question identifier")
    question: str = Field(..., description="The evolved question text")
    evolution_type: Literal["simple", "multi_context", "reasoning"] = Field(
        ..., description="Type of evolution applied"
    )
    parent_id: Optional[str] = Field(None, description="ID of the parent/seed question")

class QuestionAnswer(BaseModel):
    """Answer corresponding to an evolved question"""
    question_id: str = Field(..., description="ID of the question this answers")
    answer: str = Field(..., description="Generated answer based on document context")

class QuestionContext(BaseModel):
    """Relevant contexts for an evolved question"""
    question_id: str = Field(..., description="ID of the question")
    contexts: List[str] = Field(..., description="List of relevant document excerpts")

class EvolInstructRequest(BaseModel):
    """Request model for evolution generation"""
    documents: List[Document] = Field(..., min_length=1, description="Input documents to generate questions from")
    target_questions: int = Field(default=9, ge=3, le=15, description="Target number of evolved questions (3 per type)")

    model_config = {
        "json_schema_extra": {
            "example": {
                "documents": [
                    {
                        "page_content": "Student loans are financial aid that help students pay for college expenses. Federal loans offer better terms than private loans.",
                        "metadata": {"source": "loan_basics.pdf", "page": 1}
                    },
                    {
                        "page_content": "To qualify for federal student loans, students must complete the FAFSA form and demonstrate financial need for subsidized loans.",
                        "metadata": {"source": "fafsa_guide.pdf", "page": 3}
                    }
                ],
                "target_questions": 9
            }
        }
    }

class EvolInstructResponse(BaseModel):
    """Response model containing all generated synthetic data"""
    evolved_questions: List[EvolvedQuestion] = Field(..., description="List of evolved questions with metadata")
    question_answers: List[QuestionAnswer] = Field(..., description="Answers for each evolved question")
    question_contexts: List[QuestionContext] = Field(..., description="Relevant contexts for each question")
    processing_time: float = Field(..., description="Time taken to process the request in seconds")
    total_questions: int = Field(..., description="Total number of questions generated")

class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="API status")
    timestamp: float = Field(..., description="Current timestamp")
    
class ErrorResponse(BaseModel):
    """Error response model"""
    detail: str = Field(..., description="Error details")
    error_type: str = Field(..., description="Type of error") 