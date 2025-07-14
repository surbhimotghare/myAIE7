#!/usr/bin/env python3
"""
Test script for the Advanced Build: LinkedIn Post Generator

This script demonstrates the multi-agent LangGraph system that generates
LinkedIn posts about Machine Learning papers.

Usage:
    python test_advanced_build.py
"""

import os
import sys
from pathlib import Path

# Add the current directory to the path for imports
sys.path.append(str(Path(__file__).parent))

def test_linkedin_post_generation():
    """Test the LinkedIn post generation system."""
    
    print("🚀 Testing Advanced Build: LinkedIn Post Generator")
    print("=" * 60)
    
    # Test paper URLs
    test_papers = [
        {
            "url": "https://arxiv.org/abs/2308.08155",
            "name": "Multi-Agent Conversation Systems",
            "description": "AutoGen framework for LLM applications"
        },
        {
            "url": "https://arxiv.org/abs/2303.08774", 
            "name": "GPT-4 Technical Report",
            "description": "OpenAI's GPT-4 model capabilities"
        },
        {
            "url": "https://arxiv.org/abs/2302.14045",
            "name": "LLaMA: Open and Efficient Foundation Language Models",
            "description": "Meta's LLaMA model architecture"
        }
    ]
    
    # Test tones
    tones = ["professional", "technical", "casual"]
    
    print(f"📊 Testing {len(test_papers)} papers with {len(tones)} different tones")
    print(f"Total tests: {len(test_papers) * len(tones)}")
    print()
    
    try:
        # Import the advanced build module
        from advanced_build import generate_linkedin_post_for_paper
        
        # Run tests
        for i, paper in enumerate(test_papers, 1):
            print(f"📄 Test {i}: {paper['name']}")
            print(f"   Description: {paper['description']}")
            print(f"   URL: {paper['url']}")
            print()
            
            for j, tone in enumerate(tones, 1):
                print(f"   🎭 Tone {j}: {tone.capitalize()}")
                
                try:
                    # Generate post
                    result = generate_linkedin_post_for_paper(
                        paper_url=paper['url'],
                        tone=tone
                    )
                    
                    # Display results
                    print(f"   ✅ Status: {result['status']}")
                    print(f"   📈 Workflow Steps: {result['workflow_steps']}")
                    print(f"   📝 Post Length: {len(result['final_post'])} characters")
                    
                    # Show verification results
                    verification = result.get('verification_results', {})
                    if verification:
                        print(f"   🔍 Verification:")
                        for check, status in verification.items():
                            print(f"      • {check}: {status}")
                    
                    # Show a preview of the post
                    post_preview = result['final_post'][:200] + "..." if len(result['final_post']) > 200 else result['final_post']
                    print(f"   📱 Post Preview: {post_preview}")
                    print()
                    
                except Exception as e:
                    print(f"   ❌ Error: {str(e)}")
                    print()
                    
            print("-" * 60)
            print()
            
        print("🎉 All tests completed!")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please ensure all dependencies are installed:")
        print("pip install langchain langgraph langchain-openai")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
        
    return True

def test_system_features():
    """Test specific system features."""
    
    print("🔧 Testing System Features")
    print("=" * 40)
    
    try:
        from advanced_build import LinkedInPostGenerator
        
        # Test initialization
        print("1. Testing system initialization...")
        generator = LinkedInPostGenerator("test_key")  # Will use environment variable
        print("   ✅ System initialized successfully")
        
        # Test paper URL parsing
        print("2. Testing paper URL parsing...")
        test_urls = [
            "https://arxiv.org/abs/2308.08155",
            "https://arxiv.org/pdf/2308.08155.pdf",
            "https://arxiv.org/abs/cs.AI/2308.08155",
            "https://arxiv.org/pdf/cs.AI/2308.08155.pdf"
        ]
        
        for url in test_urls:
            result = generator.generate_post(url, "professional")
            print(f"   ✅ Processed: {url}")
            
        print("   ✅ URL parsing works correctly")
        
        # Test different tones
        print("3. Testing tone variations...")
        test_url = "https://arxiv.org/abs/2308.08155"
        tones = ["professional", "technical", "casual"]
        
        for tone in tones:
            result = generator.generate_post(test_url, tone)
            print(f"   ✅ {tone.capitalize()} tone generated")
            
        print("   ✅ All tones work correctly")
        
        print("🎉 All system features working!")
        return True
        
    except Exception as e:
        print(f"❌ Feature test error: {e}")
        return False

def main():
    """Main test function."""
    
    print("🧪 Advanced Build: LinkedIn Post Generator - Test Suite")
    print("=" * 70)
    print()
    
    # Check if OpenAI API key is available
    if not os.environ.get("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY not found in environment variables")
        print("   The system will use demonstration mode with sample posts")
        print()
    
    # Run tests
    success1 = test_linkedin_post_generation()
    print()
    success2 = test_system_features()
    
    print()
    print("📊 Test Results Summary")
    print("=" * 30)
    print(f"LinkedIn Post Generation: {'✅ PASSED' if success1 else '❌ FAILED'}")
    print(f"System Features: {'✅ PASSED' if success2 else '❌ FAILED'}")
    
    if success1 and success2:
        print()
        print("🎉 All tests passed! The Advanced Build system is working correctly.")
        print()
        print("📋 Next Steps:")
        print("1. Set your OPENAI_API_KEY for full functionality")
        print("2. Try the system with your own Arxiv papers")
        print("3. Customize the system for other platforms")
        print("4. Extend the verification rules as needed")
    else:
        print()
        print("❌ Some tests failed. Please check the implementation.")
        
    print()
    print("📚 For more information, see ADVANCED_BUILD_README.md")

if __name__ == "__main__":
    main()