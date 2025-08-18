"""
Client Agent implementation using LangGraph for A2A communication.

This client agent demonstrates how to use the A2A protocol to communicate
with our server agent, enabling agent-to-agent collaboration.
"""

import uuid
from typing import Dict, List, Any, Optional, TypedDict
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from .client_tools import call_a2a_server, discover_server_capabilities, format_multi_call_response


class ClientAgentState(TypedDict):
    """State for the client agent that manages A2A communication."""
    user_query: str                           # Original user request
    context_id: str                          # Unique context for this conversation
    server_responses: List[str]              # Responses from A2A server calls
    server_capabilities: Optional[str]       # Cached server capabilities
    routing_decision: Optional[str]          # How to route the query
    final_answer: str                        # Processed final response
    messages: List[BaseMessage]              # Conversation history
    call_count: int                         # Number of server calls made
    max_calls: int                          # Maximum allowed server calls


def query_router_node(state: ClientAgentState) -> ClientAgentState:
    """
    Analyze the user query and decide how to route it to the server.
    
    This node acts as an intelligent router that determines:
    - Whether to make single or multiple server calls
    - What type of information is needed
    - How to structure the queries for optimal results
    """
    user_query = state["user_query"]
    
    print(f"🧠 Client Agent: Analyzing query routing...")
    print(f"📝 Query: {user_query}")
    
    # Simple routing logic (can be enhanced with LLM-based analysis)
    routing_decision = "single_call"  # Default
    
    # Check for multi-part queries that might need multiple calls
    multi_indicators = [
        "and", "also", "compare", "both", "versus", "vs", 
        "contrast", "difference", "similar", "related"
    ]
    
    if any(indicator in user_query.lower() for indicator in multi_indicators):
        routing_decision = "multi_call"
        print("🔀 Routing Decision: Multiple calls needed")
    else:
        print("➡️ Routing Decision: Single call sufficient")
    
    return {
        **state,
        "routing_decision": routing_decision,
        "context_id": state.get("context_id", str(uuid.uuid4()))
    }


async def a2a_caller_node(state: ClientAgentState) -> ClientAgentState:
    """
    Make A2A protocol calls to the server agent.
    
    This node handles the actual communication with the server agent,
    managing context and collecting responses.
    """
    user_query = state["user_query"]
    routing_decision = state.get("routing_decision", "single_call")
    context_id = state["context_id"]
    call_count = state.get("call_count", 0)
    max_calls = state.get("max_calls", 3)
    
    print(f"📞 Client Agent: Making A2A server call(s)...")
    
    if call_count >= max_calls:
        print(f"⚠️ Maximum calls ({max_calls}) reached, stopping")
        return {
            **state,
            "server_responses": state.get("server_responses", []) + 
                              ["Maximum server calls reached"]
        }
    
    server_responses = state.get("server_responses", [])
    
    try:
        if routing_decision == "single_call":
            # Make a single comprehensive call
            response = await call_a2a_server.ainvoke({
                "query": user_query,
                "context_id": context_id
            })
            server_responses.append(response)
            
        elif routing_decision == "multi_call":
            # For demo, we'll make two related calls
            # In a real implementation, this would be more sophisticated
            
            # First call - general information
            response1 = await call_a2a_server.ainvoke({
                "query": f"Provide general information about: {user_query}",
                "context_id": context_id
            })
            server_responses.append(response1)
            
            # Second call - specific details or related information
            response2 = await call_a2a_server.ainvoke({
                "query": f"Provide additional details or related information about: {user_query}",
                "context_id": context_id
            })
            server_responses.append(response2)
            
    except Exception as e:
        error_response = f"Error calling server: {str(e)}"
        print(f"❌ {error_response}")
        server_responses.append(error_response)
    
    return {
        **state,
        "server_responses": server_responses,
        "call_count": call_count + 1
    }


def response_processor_node(state: ClientAgentState) -> ClientAgentState:
    """
    Process and synthesize responses from the server agent.
    
    This node takes the raw server responses and formats them into
    a coherent, user-friendly final answer.
    """
    user_query = state["user_query"]
    server_responses = state.get("server_responses", [])
    
    print(f"🔄 Client Agent: Processing server responses...")
    print(f"📊 Number of responses: {len(server_responses)}")
    
    if not server_responses:
        final_answer = "I wasn't able to get a response from the server agent. Please try again."
    else:
        # Use our formatting tool to synthesize responses
        final_answer = format_multi_call_response.invoke({
            "responses": server_responses,
            "query": user_query
        })
    
    # Add client agent signature
    final_answer += "\n\n---\n*Response generated via A2A protocol by Client Agent*"
    
    return {
        **state,
        "final_answer": final_answer,
        "messages": state.get("messages", []) + [
            AIMessage(content=final_answer)
        ]
    }


def should_continue(state: ClientAgentState) -> str:
    """
    Decide whether to continue processing or end.
    
    This conditional edge determines if we need more server calls
    or if we can proceed to the final response.
    """
    call_count = state.get("call_count", 0)
    max_calls = state.get("max_calls", 3)
    server_responses = state.get("server_responses", [])
    
    # Simple logic: if we have responses and haven't exceeded limits, process them
    if server_responses and call_count > 0:
        return "process_response"
    elif call_count >= max_calls:
        return "process_response"
    else:
        return "make_call"


def build_client_agent_graph() -> StateGraph:
    """
    Build the LangGraph for the client agent.
    
    This creates a graph that can intelligently route queries to the server
    agent and process the responses.
    """
    # Initialize the graph
    graph = StateGraph(ClientAgentState)
    
    # Add nodes
    graph.add_node("query_router", query_router_node)
    graph.add_node("a2a_caller", a2a_caller_node)
    graph.add_node("response_processor", response_processor_node)
    
    # Set entry point
    graph.set_entry_point("query_router")
    
    # Add edges
    graph.add_edge("query_router", "a2a_caller")
    graph.add_conditional_edges(
        "a2a_caller",
        should_continue,
        {
            "process_response": "response_processor",
            "make_call": "a2a_caller"  # Allow for multiple calls if needed
        }
    )
    graph.add_edge("response_processor", END)
    
    return graph.compile()


class ClientAgent:
    """
    High-level client agent class for easy interaction.
    
    This class provides a simple interface for using the client agent
    to communicate with the server agent via A2A protocol.
    """
    
    def __init__(self, server_url: str = "http://localhost:10000", max_calls: int = 3):
        self.server_url = server_url
        self.max_calls = max_calls
        self.graph = build_client_agent_graph()
        
    async def query(self, user_query: str, context_id: Optional[str] = None) -> str:
        """
        Send a query to the server agent and get a processed response.
        
        Args:
            user_query: The user's question or request
            context_id: Optional context ID for conversation continuity
            
        Returns:
            The processed response from the server agent
        """
        initial_state: ClientAgentState = {
            "user_query": user_query,
            "context_id": context_id or str(uuid.uuid4()),
            "server_responses": [],
            "server_capabilities": None,
            "routing_decision": None,
            "final_answer": "",
            "messages": [HumanMessage(content=user_query)],
            "call_count": 0,
            "max_calls": self.max_calls
        }
        
        print(f"🚀 Client Agent: Starting A2A communication...")
        print(f"🎯 User Query: {user_query}")
        
        # Run the graph
        final_state = await self.graph.ainvoke(initial_state)
        
        return final_state["final_answer"]
    
    async def discover_capabilities(self) -> str:
        """Discover what the server agent can do."""
        return await discover_server_capabilities.ainvoke({"server_url": self.server_url})


# Convenience function for quick testing
async def quick_client_test(query: str) -> str:
    """Quick test function for the client agent."""
    client = ClientAgent()
    return await client.query(query)


if __name__ == "__main__":
    import asyncio
    
    async def main():
        client = ClientAgent()
        
        # Test queries
        test_queries = [
            "What are the latest developments in AI?",
            "Compare machine learning and deep learning approaches",
            "Find recent papers on transformer architectures"
        ]
        
        for query in test_queries:
            print(f"\n{'='*60}")
            print(f"Testing: {query}")
            print('='*60)
            
            response = await client.query(query)
            print(f"\nFinal Response:\n{response}")
    
    asyncio.run(main())
