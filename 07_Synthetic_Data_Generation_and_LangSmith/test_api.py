"""
Simple test script for the Evol-Instruct API
Run this locally to test the API before deployment
"""
import asyncio
import json
import sys
import os

# Add the current directory to the path so we can import our API
sys.path.append('.')

async def test_evol_graph():
    """Test the EvolInstructGraph directly"""
    try:
        from api.evol_graph import EvolInstructGraph
        
        # Sample test documents
        test_documents = [
            {
                "page_content": "Python is a high-level programming language that is widely used for web development, data analysis, artificial intelligence, and scientific computing. It was created by Guido van Rossum and first released in 1991.",
                "metadata": {"source": "python_basics.txt"}
            },
            {
                "page_content": "Machine learning is a subset of artificial intelligence that focuses on algorithms that can learn from and make predictions on data. Common types include supervised learning, unsupervised learning, and reinforcement learning.",
                "metadata": {"source": "ml_intro.txt"}
            }
        ]
        
        print("🧠 Testing Evol-Instruct Graph...")
        print(f"📄 Input: {len(test_documents)} test documents")
        
        # Initialize and run the graph
        evol_graph = EvolInstructGraph()
        result = await evol_graph.run(test_documents)
        
        # Display results
        print(f"✅ Generated {len(result['evolved_questions'])} evolved questions:")
        
        for i, question in enumerate(result['evolved_questions'], 1):
            print(f"\n{i}. [{question['evolution_type'].upper()}] {question['question'][:100]}...")
        
        print(f"\n📝 Generated {len(result['question_answers'])} answers")
        print(f"📚 Extracted {len(result['question_contexts'])} context sets")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing graph: {str(e)}")
        return False

def test_api_models():
    """Test the Pydantic models"""
    try:
        from api.models import EvolInstructRequest, Document
        
        print("\n🔧 Testing Pydantic Models...")
        
        # Test document model
        doc = Document(
            page_content="Test content",
            metadata={"source": "test.txt"}
        )
        
        # Test request model
        request = EvolInstructRequest(
            documents=[doc],
            target_questions=9
        )
        
        print(f"✅ Models work correctly")
        print(f"📄 Sample request: {len(request.documents)} documents, target: {request.target_questions}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing models: {str(e)}")
        return False

async def main():
    """Run all tests"""
    print("🚀 Starting Evol-Instruct API Tests\n")
    
    # Check environment
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY not found in environment")
        print("   Set it with: export OPENAI_API_KEY='your-key-here'")
        print("   Tests will fail without it.\n")
    
    # Test models
    models_ok = test_api_models()
    
    if not models_ok:
        print("❌ Model tests failed - stopping here")
        return
    
    # Test the graph (only if OpenAI key is available)
    if os.getenv("OPENAI_API_KEY"):
        graph_ok = await test_evol_graph()
        
        if graph_ok:
            print("\n🎉 All tests passed! API is ready for deployment.")
        else:
            print("\n❌ Graph tests failed - check your OpenAI API key and internet connection")
    else:
        print("\n⚠️  Skipped graph tests - no OpenAI API key provided")
        print("   Models are working correctly though!")

if __name__ == "__main__":
    asyncio.run(main()) 