import logging
import time
from typing import Dict, Any, List, Optional
import json
import asyncio
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import ValidationError

from .models import EvolInstructRequest, EvolInstructResponse, HealthResponse, ErrorResponse, Document
from .evol_graph import EvolInstructGraph

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Evol-Instruct API",
    description="Advanced synthetic data generation using LangGraph and Evol-Instruct methodology",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Global variable to store progress updates
current_progress = {
    "session_id": None,
    "steps": [],
    "current_step": "",
    "completed": False,
    "error": None
}

# Progress callback function
def progress_callback(step_info: Dict[str, Any]):
    """Callback function to receive progress updates from the graph"""
    global current_progress
    current_progress["steps"].append(step_info)
    current_progress["current_step"] = step_info.get("message", "")
    
    # Log the progress
    logger.info(f"Progress Update: {step_info}")

@app.get("/", tags=["Root"])
async def root():
    """Serve the main frontend page"""
    return FileResponse("static/index.html")

@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint"""
    try:
        # Try to initialize the graph to check if everything is working
        graph = EvolInstructGraph()
        graph_status = "initialized"
    except Exception as e:
        logger.error(f"Graph initialization failed: {str(e)}")
        graph_status = f"error: {str(e)}"
    
    return HealthResponse(
        status="healthy",
        timestamp=time.time(),
        graph_status=graph_status
    )

@app.post("/generate", response_model=EvolInstructResponse, tags=["Generation"])
async def generate_questions(request: EvolInstructRequest):
    """Generate evolved questions from documents"""
    try:
        logger.info(f"Received request with {len(request.documents)} documents, target: {request.target_questions}")
        
        # Reset progress tracking
        global current_progress
        current_progress = {
            "session_id": f"session_{int(time.time())}",
            "steps": [],
            "current_step": "Initializing...",
            "completed": False,
            "error": None
        }
        
        start_time = time.time()
        
        # Initialize the graph with progress callback
        graph = EvolInstructGraph()
        
        # Run the pipeline
        result = await graph.run(
            request.documents, 
            target_questions=request.target_questions,
            progress_callback=progress_callback
        )
        
        processing_time = time.time() - start_time
        
        # Mark progress as completed
        current_progress["completed"] = True
        current_progress["current_step"] = "✅ Pipeline completed successfully!"
        
        response = EvolInstructResponse(
            **result,
            processing_time=processing_time
        )
        
        logger.info(f"Successfully generated {result['total_questions']} questions in {processing_time:.2f}s")
        return response
        
    except ValidationError as e:
        logger.error(f"Validation error: {str(e)}")
        current_progress["error"] = f"Validation error: {str(e)}"
        current_progress["completed"] = True
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid request data: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error in question generation: {str(e)}")
        current_progress["error"] = str(e)
        current_progress["completed"] = True
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Question generation failed: {str(e)}"
        )

@app.post("/generate-demo", response_model=EvolInstructResponse, tags=["Demo"])
async def generate_demo():
    """Generate demo questions using sample documents"""
    try:
        # Create sample documents for demo
        demo_docs = [
            Document(
                page_content="FastAPI is a modern, fast (high-performance), web framework for building APIs with Python 3.6+ based on standard Python type hints. It provides automatic interactive API documentation, automatic data validation, serialization and deserialization.",
                metadata={"source": "demo_doc_1.txt"}
            ),
            Document(
                page_content="Machine Learning is a subset of artificial intelligence that focuses on algorithms that can learn from data. It includes supervised learning, unsupervised learning, and reinforcement learning approaches.",
                metadata={"source": "demo_doc_2.txt"}
            )
        ]
        
        logger.info("Starting demo Evol-Instruct pipeline...")
        start_time = time.time()
        
        # Initialize the graph
        graph = EvolInstructGraph()
        
        # Run the pipeline
        result = await graph.run(demo_docs, target_questions=9, progress_callback=progress_callback)
        
        processing_time = time.time() - start_time
        
        # Mark progress as completed
        global current_progress
        current_progress["completed"] = True
        
        response = EvolInstructResponse(
            **result,
            processing_time=processing_time
        )
        
        logger.info(f"Successfully generated {result['total_questions']} demo questions in {processing_time:.2f}s")
        return response
        
    except Exception as e:
        logger.error(f"Error in demo generation: {str(e)}")
        current_progress["error"] = str(e)
        current_progress["completed"] = True
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Demo generation failed: {str(e)}"
        )

@app.get("/progress-stream", tags=["Progress"])
async def progress_stream():
    """Server-Sent Events endpoint for real-time progress updates"""
    async def event_generator():
        global current_progress
        last_step_count = 0
        
        while not current_progress["completed"] and current_progress["error"] is None:
            # Send new steps if any
            if len(current_progress["steps"]) > last_step_count:
                for step in current_progress["steps"][last_step_count:]:
                    yield f"data: {json.dumps(step)}\n\n"
                last_step_count = len(current_progress["steps"])
            
            # Send current status
            status_data = {
                "type": "status",
                "current_step": current_progress["current_step"],
                "total_steps": len(current_progress["steps"]),
                "completed": current_progress["completed"]
            }
            yield f"data: {json.dumps(status_data)}\n\n"
            
            await asyncio.sleep(0.5)  # Update every 500ms
        
        # Send final completion or error
        if current_progress["error"]:
            final_data = {
                "type": "error",
                "message": current_progress["error"]
            }
        else:
            final_data = {
                "type": "completed",
                "message": "✅ All questions generated successfully!",
                "total_steps": len(current_progress["steps"])
            }
        
        yield f"data: {json.dumps(final_data)}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control"
        }
    )

# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            detail=exc.detail,
            timestamp=time.time()
        ).dict()
    )

@app.exception_handler(ValidationError)
async def validation_exception_handler(request, exc: ValidationError):
    """Handle Pydantic validation errors"""
    return JSONResponse(
        status_code=422,
        content=ErrorResponse(
            detail=f"Validation error: {str(exc)}",
            timestamp=time.time()
        ).dict()
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            detail=f"Internal server error: {str(exc)}",
            timestamp=time.time()
        ).dict()
    ) 