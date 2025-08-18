"""
Client tools for A2A (Agent-to-Agent) communication.

This module provides tools for the client agent to communicate with the server agent
using the A2A protocol over HTTP, leveraging the official A2A library.
"""

import asyncio
import json
import uuid
from typing import Dict, Any, Optional
from uuid import uuid4
import httpx
from langchain_core.tools import tool

from a2a.client import A2ACardResolver, A2AClient
from a2a.types import (
    MessageSendParams,
    SendMessageRequest,
)
from a2a.utils.constants import AGENT_CARD_WELL_KNOWN_PATH


@tool
async def call_a2a_server(
    query: str, 
    context_id: Optional[str] = None,
    task_id: Optional[str] = None,
    server_url: str = "http://localhost:10000"
) -> str:
    """
    Call the A2A server with a query and return the response.
    
    This tool implements the A2A protocol to communicate with our server agent
    using the official A2A library for proper protocol compliance.
    
    Args:
        query: The user query to send to the server agent
        context_id: Optional context ID for multi-turn conversations
        task_id: Optional task ID for multi-turn conversations
        server_url: The URL of the A2A server (default: localhost:10000)
        
    Returns:
        The server's response as a string
    """
    try:
        print(f"🔄 Client → Server: Sending query via A2A protocol")
        print(f"📝 Query: {query[:100]}{'...' if len(query) > 100 else ''}")
        
        async with httpx.AsyncClient(timeout=60.0) as httpx_client:
            # Initialize A2A Card Resolver and Client
            resolver = A2ACardResolver(
                httpx_client=httpx_client,
                base_url=server_url,
            )
            
            # Get the agent card
            agent_card = await resolver.get_agent_card()
            
            # Initialize A2A Client
            client = A2AClient(
                httpx_client=httpx_client, 
                agent_card=agent_card
            )
            
            # Prepare message payload
            message_data = {
                'role': 'user',
                'parts': [
                    {'kind': 'text', 'text': query}
                ],
                'message_id': uuid4().hex,
            }
            
            # Add context/task IDs if provided for multi-turn conversations
            if context_id:
                message_data['context_id'] = context_id
            if task_id:
                message_data['task_id'] = task_id
            
            send_message_payload = {
                'message': message_data,
            }
            
            # Create and send request
            request = SendMessageRequest(
                id=str(uuid4()), 
                params=MessageSendParams(**send_message_payload)
            )
            
            response = await client.send_message(request)
            
            # Extract response content
            if hasattr(response, 'root') and hasattr(response.root, 'result'):
                result = response.root.result
                if hasattr(result, 'content'):
                    server_response = result.content
                elif hasattr(result, 'parts') and result.parts:
                    # Handle parts-based response
                    server_response = ""
                    for part in result.parts:
                        if hasattr(part, 'text'):
                            server_response += part.text
                        elif hasattr(part, 'content'):
                            server_response += part.content
                else:
                    server_response = str(result)
            else:
                server_response = str(response)
            
            print(f"✅ Server → Client: Received response")
            print(f"📄 Response length: {len(server_response)} characters")
            
            return server_response
            
    except Exception as e:
        error_msg = f"A2A communication error: {str(e)}"
        print(f"❌ {error_msg}")
        return f"Error: {error_msg}"


@tool
async def discover_server_capabilities(server_url: str = "http://localhost:10000") -> str:
    """
    Discover what capabilities the A2A server offers.
    
    This tool queries the server's AgentCard to understand what skills and
    capabilities are available for the client to use.
    
    Args:
        server_url: The URL of the A2A server
        
    Returns:
        JSON string describing the server's capabilities
    """
    try:
        print(f"🔍 Discovering server capabilities at {server_url}")
        
        async with httpx.AsyncClient(timeout=30.0) as httpx_client:
            # Use proper A2A library to get agent card
            resolver = A2ACardResolver(
                httpx_client=httpx_client,
                base_url=server_url,
            )
            
            agent_card = await resolver.get_agent_card()
            
            # Convert to dict for easier handling
            agent_card_dict = agent_card.model_dump() if hasattr(agent_card, 'model_dump') else dict(agent_card)
            
            # Extract key information for the client
            capabilities_summary = {
                "name": agent_card_dict.get("name", "Unknown Agent"),
                "description": agent_card_dict.get("description", ""),
                "skills": [
                    {
                        "id": skill.get("id"),
                        "name": skill.get("name"),
                        "description": skill.get("description")
                    }
                    for skill in agent_card_dict.get("skills", [])
                ],
                "capabilities": agent_card_dict.get("capabilities", {}),
                "version": agent_card_dict.get("version", "unknown")
            }
            
            print(f"✅ Discovered server: {capabilities_summary['name']}")
            print(f"📋 Available skills: {len(capabilities_summary['skills'])}")
            
            return json.dumps(capabilities_summary, indent=2)
            
    except Exception as e:
        error_msg = f"Failed to discover server capabilities: {str(e)}"
        print(f"❌ {error_msg}")
        return f"Error: {error_msg}"


@tool 
def format_multi_call_response(responses: list, query: str) -> str:
    """
    Format multiple server responses into a coherent answer.
    
    When the client makes multiple calls to the server, this tool
    helps synthesize the responses into a single, coherent answer.
    
    Args:
        responses: List of server responses to combine
        query: The original user query for context
        
    Returns:
        A formatted, synthesized response
    """
    if not responses:
        return "No responses received from server."
        
    if len(responses) == 1:
        return responses[0]
        
    # Multi-response synthesis
    synthesized = f"Based on multiple queries to the server agent, here's a comprehensive response to: '{query}'\n\n"
    
    for i, response in enumerate(responses, 1):
        synthesized += f"## Part {i}:\n{response}\n\n"
        
    synthesized += "---\n*This response was synthesized from multiple server agent calls.*"
    
    return synthesized


# Utility function for testing
async def test_a2a_connection(server_url: str = "http://localhost:10000") -> bool:
    """Test if the A2A server is reachable and responsive."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as httpx_client:
            resolver = A2ACardResolver(
                httpx_client=httpx_client,
                base_url=server_url,
            )
            agent_card = await resolver.get_agent_card()
            return agent_card is not None
    except:
        return False