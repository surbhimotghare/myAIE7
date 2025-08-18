"""
Test client for demonstrating A2A (Agent-to-Agent) communication.

This script demonstrates how the client agent communicates with the server agent
using the A2A protocol, showcasing agent-to-agent collaboration.
"""

import asyncio
import sys
from typing import List
from .client_agent import ClientAgent
from .client_tools import test_a2a_connection, discover_server_capabilities


async def test_server_connection():
    """Test if the A2A server is running and accessible."""
    print("🔍 Testing server connection...")
    
    is_connected = await test_a2a_connection()
    if is_connected:
        print("✅ Server is running and accessible!")
        return True
    else:
        print("❌ Server is not accessible. Please ensure the server is running on localhost:10000")
        print("💡 Run the server with: python -m app")
        return False


async def demonstrate_capabilities_discovery():
    """Demonstrate discovering server agent capabilities."""
    print("\n" + "="*60)
    print("🔍 DISCOVERING SERVER CAPABILITIES")
    print("="*60)
    
    try:
        capabilities = await discover_server_capabilities.ainvoke({})
        print("📋 Server Agent Capabilities:")
        print(capabilities)
        return True
    except Exception as e:
        print(f"❌ Failed to discover capabilities: {e}")
        return False


async def demonstrate_simple_query():
    """Demonstrate a simple single-query interaction."""
    print("\n" + "="*60)
    print("📞 SIMPLE A2A QUERY DEMONSTRATION")
    print("="*60)
    
    client = ClientAgent()
    query = "What are the latest developments in artificial intelligence?"
    
    print(f"🎯 Query: {query}")
    print("\n🔄 Processing...")
    
    try:
        response = await client.query(query)
        print(f"\n📄 Client Agent Response:")
        print("-" * 40)
        print(response)
        return True
    except Exception as e:
        print(f"❌ Error during simple query: {e}")
        return False


async def demonstrate_multi_part_query():
    """Demonstrate a multi-part query that requires multiple server calls."""
    print("\n" + "="*60)
    print("🔀 MULTI-PART A2A QUERY DEMONSTRATION")
    print("="*60)
    
    client = ClientAgent()
    query = "Compare recent AI research papers and current market trends in artificial intelligence"
    
    print(f"🎯 Complex Query: {query}")
    print("\n🔄 Processing (this may involve multiple server calls)...")
    
    try:
        response = await client.query(query)
        print(f"\n📄 Client Agent Synthesized Response:")
        print("-" * 50)
        print(response)
        return True
    except Exception as e:
        print(f"❌ Error during multi-part query: {e}")
        return False


async def demonstrate_specialized_queries():
    """Demonstrate different types of specialized queries."""
    print("\n" + "="*60)
    print("🎯 SPECIALIZED QUERY DEMONSTRATIONS")
    print("="*60)
    
    client = ClientAgent()
    
    specialized_queries = [
        {
            "name": "Academic Research Query",
            "query": "Find recent papers on transformer architecture improvements",
            "description": "This should trigger the ArXiv search capability"
        },
        {
            "name": "Web Search Query", 
            "query": "What are the current trends in AI startups and funding?",
            "description": "This should trigger web search capability"
        },
        {
            "name": "Technical Query",
            "query": "Explain the differences between GPT-4 and Claude-3 architectures",
            "description": "This might use multiple capabilities"
        }
    ]
    
    results = []
    
    for test_case in specialized_queries:
        print(f"\n📋 {test_case['name']}:")
        print(f"💡 {test_case['description']}")
        print(f"❓ Query: {test_case['query']}")
        print("\n🔄 Processing...")
        
        try:
            response = await client.query(test_case["query"])
            print(f"\n✅ Response received ({len(response)} chars)")
            print("📄 Preview:", response[:200] + "..." if len(response) > 200 else response)
            results.append(True)
        except Exception as e:
            print(f"❌ Error: {e}")
            results.append(False)
            
        print("-" * 50)
    
    return all(results)


async def demonstrate_conversation_context():
    """Demonstrate maintaining context across multiple interactions."""
    print("\n" + "="*60)
    print("💬 CONVERSATION CONTEXT DEMONSTRATION")
    print("="*60)
    
    client = ClientAgent()
    context_id = "demo_conversation_001"
    
    conversation_flow = [
        "What is machine learning?",
        "How does it relate to artificial intelligence?",
        "Can you give me some practical applications?"
    ]
    
    print(f"🗣️ Simulating conversation with context ID: {context_id}")
    
    try:
        for i, query in enumerate(conversation_flow, 1):
            print(f"\n📞 Turn {i}: {query}")
            response = await client.query(query, context_id=context_id)
            print(f"✅ Response: {response[:150]}{'...' if len(response) > 150 else ''}")
        
        return True
    except Exception as e:
        print(f"❌ Error in conversation: {e}")
        return False


async def run_comprehensive_demo():
    """Run the complete A2A demonstration."""
    print("🚀 A2A PROTOCOL DEMONSTRATION")
    print("=" * 80)
    print("This demo shows how a client agent communicates with a server agent")
    print("using the A2A (Agent-to-Agent) protocol for collaborative AI.")
    print("=" * 80)
    
    # Track test results
    test_results = []
    
    # 1. Test server connection
    test_results.append(await test_server_connection())
    if not test_results[-1]:
        print("\n❌ Cannot proceed without server connection. Exiting.")
        return False
    
    # 2. Discover capabilities
    test_results.append(await demonstrate_capabilities_discovery())
    
    # 3. Simple query
    test_results.append(await demonstrate_simple_query())
    
    # 4. Multi-part query
    test_results.append(await demonstrate_multi_part_query())
    
    # 5. Specialized queries
    test_results.append(await demonstrate_specialized_queries())
    
    # 6. Conversation context
    test_results.append(await demonstrate_conversation_context())
    
    # Summary
    print("\n" + "="*60)
    print("📊 DEMONSTRATION SUMMARY")
    print("="*60)
    
    test_names = [
        "Server Connection",
        "Capabilities Discovery", 
        "Simple Query",
        "Multi-part Query",
        "Specialized Queries",
        "Conversation Context"
    ]
    
    for name, result in zip(test_names, test_results):
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{name:.<30} {status}")
    
    success_rate = sum(test_results) / len(test_results) * 100
    print(f"\nOverall Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print("🎉 A2A Protocol demonstration completed successfully!")
        print("✨ Client-Server agent collaboration is working!")
    else:
        print("⚠️ Some issues were encountered during the demonstration.")
        print("💡 Check server status and configuration.")
    
    return success_rate >= 80


async def interactive_mode():
    """Run in interactive mode for manual testing."""
    print("\n🎮 INTERACTIVE A2A CLIENT MODE")
    print("="*50)
    print("Type your queries to test the A2A protocol.")
    print("Type 'done', 'quit', 'exit', or 'q' to exit, 'help' for commands.")
    print("="*50)
    
    client = ClientAgent()
    context_id = "interactive_session"
    
    while True:
        try:
            query = input("\n💬 Your query: ").strip()
            
            if query.lower() in ['quit', 'exit', 'q', 'done', 'end', 'bye']:
                print("👋 Goodbye! Thanks for testing the A2A protocol!")
                break
                
            if query.lower() == 'help':
                print("\n📚 Available commands:")
                print("  - Any question: Send to server agent via A2A")
                print("  - 'capabilities': Show server capabilities")
                print("  - 'quit', 'exit', 'q', 'done', 'end', 'bye': Exit interactive mode")
                print("  - 'help': Show this help message")
                continue
                
            if query.lower() == 'capabilities':
                caps = await client.discover_capabilities()
                print(f"\n📋 Server Capabilities:\n{caps}")
                continue
                
            if not query:
                continue
                
            print("🔄 Processing via A2A protocol...")
            response = await client.query(query, context_id=context_id)
            print(f"\n🤖 Response:\n{response}")
            
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "interactive":
        asyncio.run(interactive_mode())
    else:
        asyncio.run(run_comprehensive_demo())
