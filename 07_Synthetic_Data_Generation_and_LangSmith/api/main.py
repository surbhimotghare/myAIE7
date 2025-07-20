from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
import asyncio
import logging
import os
from typing import Dict, Any

from .models import (
    EvolInstructRequest, 
    EvolInstructResponse, 
    HealthResponse,
    ErrorResponse
)
from .evol_graph import get_evol_graph

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Evol-Instruct API",
    description="Generate synthetic data using Evol-Instruct methodology with LangGraph",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": f"Internal server error: {str(exc)}", "error_type": "server_error"}
    )

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize the application on startup"""
    logger.info("Starting Evol-Instruct API...")
    
    # Check for required environment variables
    if not os.getenv("OPENAI_API_KEY"):
        logger.warning("OPENAI_API_KEY not found in environment variables")
    
    logger.info("Evol-Instruct API startup completed")

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint - API information"""
    return {
        "message": "Evol-Instruct API is running!",
        "version": "1.0.0",
        "description": "Generate synthetic data using Evol-Instruct methodology with LangGraph",
        "endpoints": {
            "health": "/health",
            "generate": "/generate",
            "generate_demo": "/generate-demo",
            "docs": "/docs"
        }
    }

@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=time.time()
    )

@app.post("/generate", response_model=EvolInstructResponse, tags=["Generation"])
async def generate_synthetic_data(request: EvolInstructRequest):
    """
    Generate synthetic data using Evol-Instruct method
    
    This endpoint takes a list of documents and generates evolved questions using three types:
    - Simple Evolution: Add constraints, deepen, concretize
    - Multi-Context Evolution: Questions requiring multiple documents  
    - Reasoning Evolution: Questions requiring logical inference
    
    Returns evolved questions, answers, and relevant contexts.
    """
    start_time = time.time()
    
    try:
        logger.info(f"Received request with {len(request.documents)} documents, target: {request.target_questions}")
        
        # Validate input
        if len(request.documents) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one document is required"
            )
        
        # Check for empty documents
        valid_docs = [doc for doc in request.documents if doc.page_content.strip()]
        if len(valid_docs) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="All documents appear to be empty"
            )
        
        if len(valid_docs) < len(request.documents):
            logger.warning(f"Filtered out {len(request.documents) - len(valid_docs)} empty documents")
        
        # Convert Pydantic models to dicts for processing
        documents = [doc.dict() for doc in valid_docs]
        
        # Get the Evol-Instruct graph instance
        evol_graph = get_evol_graph()
        
        # Run the evolution process
        logger.info("Starting Evol-Instruct pipeline...")
        result = await evol_graph.run(documents)
        
        processing_time = time.time() - start_time
        
        # Validate results
        if not result.get("evolved_questions"):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="No questions were generated. Please check your documents and try again."
            )
        
        logger.info(f"Successfully generated {len(result['evolved_questions'])} questions in {processing_time:.2f}s")
        
        return EvolInstructResponse(
            evolved_questions=result["evolved_questions"],
            question_answers=result["question_answers"],
            question_contexts=result["question_contexts"],
            processing_time=processing_time,
            total_questions=len(result["evolved_questions"])
        )
    
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    
    except Exception as e:
        logger.error(f"Error in generate_synthetic_data: {str(e)}")
        processing_time = time.time() - start_time
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Processing error after {processing_time:.2f}s: {str(e)}"
        )

@app.post("/generate-demo", response_model=EvolInstructResponse, tags=["Demo"])
async def generate_demo():
    """
    Demo endpoint with sample loan documents for testing
    
    This endpoint uses pre-defined sample documents about student loans to demonstrate
    the Evol-Instruct methodology. Perfect for testing without providing your own documents.
    """
    
    try:
        # Sample loan documents for demonstration
        sample_docs = [
            {
                "page_content": """Student loans are financial aid that help students pay for college expenses including tuition, books, and living costs. There are two main types: federal student loans and private student loans. Federal loans typically offer better terms, including fixed interest rates, income-driven repayment options, and potential loan forgiveness programs. Students must complete the Free Application for Federal Student Aid (FAFSA) to be considered for federal aid.""",
                "metadata": {"source": "loan_basics.pdf", "page": 1, "section": "introduction"}
            },
            {
                "page_content": """Direct Subsidized Loans are available to undergraduate students with demonstrated financial need. The government pays the interest while students are in school at least half-time, during grace periods, and during authorized periods of deferment. Direct Unsubsidized Loans are available to undergraduate and graduate students regardless of financial need. Interest accrues from the time the loan is disbursed until it's paid in full.""",
                "metadata": {"source": "federal_loans.pdf", "page": 2, "section": "loan_types"}
            },
            {
                "page_content": """To qualify for federal student aid, students must meet eligibility requirements including being a U.S. citizen or eligible non-citizen, having a valid Social Security number, and maintaining satisfactory academic progress. Students must also complete the FAFSA annually and may need to provide additional documentation for verification. The Expected Family Contribution (EFC) calculated from FAFSA determines aid eligibility.""",
                "metadata": {"source": "eligibility.pdf", "page": 3, "section": "requirements"}
            }
        ]
        
        # Create request object
        demo_request = EvolInstructRequest(
            documents=sample_docs,
            target_questions=9  # 3 per evolution type
        )
        
        logger.info("Processing demo request with sample loan documents")
        
        # Process using the main generation endpoint
        return await generate_synthetic_data(demo_request)
    
    except Exception as e:
        logger.error(f"Error in generate_demo: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Demo generation error: {str(e)}"
        )

@app.get("/status", tags=["Status"])
async def get_status():
    """Get detailed API status information"""
    try:
        # Check if OpenAI API key is available
        openai_key_status = "configured" if os.getenv("OPENAI_API_KEY") else "missing"
        
        # Try to get the graph instance to check initialization
        try:
            evol_graph = get_evol_graph()
            graph_status = "initialized"
        except Exception as e:
            graph_status = f"error: {str(e)}"
        
        return {
            "api_status": "running",
            "timestamp": time.time(),
            "environment": {
                "openai_key": openai_key_status,
                "evol_graph": graph_status
            },
            "endpoints": {
                "generate": "Available for custom documents",
                "generate_demo": "Available with sample data",
                "health": "Health check endpoint"
            }
        }
    
    except Exception as e:
        logger.error(f"Error in get_status: {str(e)}")
        return {
            "api_status": "error",
            "error": str(e),
            "timestamp": time.time()
        }

# Additional utility endpoints
@app.get("/evolution-types", tags=["Info"])
async def get_evolution_types():
    """Get information about the three evolution types"""
    return {
        "evolution_types": {
            "simple": {
                "description": "Basic evolutions that add constraints, deepen analysis, or increase complexity",
                "examples": [
                    "Add specific constraints to make question more challenging",
                    "Transform to require step-by-step reasoning",
                    "Add real-world application context"
                ]
            },
            "multi_context": {
                "description": "Questions that require information from multiple documents or sources",
                "examples": [
                    "Compare information across different documents",
                    "Synthesize concepts from multiple sources",
                    "Analyze relationships between different document sections"
                ]
            },
            "reasoning": {
                "description": "Questions requiring logical inference, cause-effect analysis, or strategic thinking",
                "examples": [
                    "If-then conditional analysis",
                    "Cause and effect relationships",
                    "Problem-solving scenarios"
                ]
            }
        },
        "methodology": "Based on Evol-Instruct from WizardLM paper (https://arxiv.org/pdf/2304.12244)",
        "implementation": "LangGraph-based agent workflow"
    }

# Development/debugging endpoints
@app.get("/debug/sample-request", tags=["Debug"])
async def get_sample_request():
    """Get a sample request format for testing"""
    return {
        "sample_request": {
            "documents": [
                {
                    "page_content": "Your document content here. This should be substantial text that contains information suitable for question generation.",
                    "metadata": {
                        "source": "document1.pdf",
                        "page": 1,
                        "section": "introduction"
                    }
                },
                {
                    "page_content": "Additional document content. Multiple documents enable multi-context evolution questions.",
                    "metadata": {
                        "source": "document2.pdf", 
                        "page": 1,
                        "section": "details"
                    }
                }
            ],
            "target_questions": 9
        },
        "note": "Use POST /generate with this format, or try GET /generate-demo for a working example"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 