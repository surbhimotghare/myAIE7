<p align = "center" draggable=”false” ><img src="https://github.com/AI-Maker-Space/LLM-Dev-101/assets/37101144/d1343317-fa2f-41e1-8af1-1dbb18399719" 
     width="200px"
     height="auto"/>
</p>

## <h1 align="center" id="heading">Session 14: Build & Serve Agentic Graphs with LangGraph</h1>

| 🤓 Pre-work | 📰 Session Sheet | ⏺️ Recording     | 🖼️ Slides        | 👨‍💻 Repo         | 📝 Homework      | 📁 Feedback       |
|:-----------------|:-----------------|:-----------------|:-----------------|:-----------------|:-----------------|:-----------------|
| [Session 14: Pre-Work](https://www.notion.so/Session-14-Deploying-Agents-to-Production-21dcd547af3d80aba092fcb6c649c150?source=copy_link#247cd547af3d80709683ff380f4cba62)| [Session 14: Deploying Agents to Production](https://www.notion.so/Session-14-Deploying-Agents-to-Production-21dcd547af3d80aba092fcb6c649c150) | [Recording!](https://us02web.zoom.us/rec/share/1YepNUK3kqQnYLY8InMfHv84JeiOMyjMRWOZQ9jfjY86dDPvHMhyoz5Zo04w_tn-.91KwoSPyP6K6u0DC)  (@@5J6DVQ)| [Session 14 Slides](https://www.canva.com/design/DAGvVPg7-mw/IRwoSgDXPEqU-PKeIw8zLg/edit?utm_content=DAGvVPg7-mw&utm_campaign=designshare&utm_medium=link2&utm_source=sharebutton) | You are here! | [Session 14 Assignment: Production Agents](https://forms.gle/nZ7ugE4W9VsC1zXE8) | [AIE7 Feedback 8/7](https://forms.gle/juo8SF5y5XiojFyC9)

# Build 🏗️

Run the repository and complete the following:

- 🤝 Breakout Room Part #1 — Building and serving your LangGraph Agent Graph
  - Task 1: Getting Dependencies & Environment
    - Configure `.env` (OpenAI, Tavily, optional LangSmith)
  - Task 2: Serve the Graph Locally
    - `uv run langgraph dev` (API on http://localhost:2024)
  - Task 3: Call the API
    - `uv run test_served_graph.py` (sync SDK example)
  - Task 4: Explore assistants (from `langgraph.json`)
    - `agent` → `simple_agent` (tool-using agent)
    - `agent_helpful` → `agent_with_helpfulness` (separate helpfulness node)

- 🤝 Breakout Room Part #2 — Using LangGraph Studio to visualize the graph
  - Task 1: Open Studio while the server is running
    - https://smith.langchain.com/studio?baseUrl=http://localhost:2024
  - Task 2: Visualize & Stream
    - Start a run and observe node-by-node updates
  - Task 3: Compare Flows
    - Contrast `agent` vs `agent_helpful` (tool calls vs helpfulness decision)

<details>
<summary>🚧 Advanced Build 🚧 (OPTIONAL - <i>open this section for the requirements</i>)</summary>

- Create and deploy a locally hosted MCP server with FastMCP.
- Extend your tools in `tools.py` to allow your LangGraph to consume the MCP Server.
</details>

# Ship 🚢

- Running local server (`langgraph dev`)
- Short demo showing both assistants responding

# Share 🚀
- Walk through your graph in Studio
- Share 3 lessons learned and 3 lessons not learned


#### ❓ Question:

What is the purpose of the `chunk_overlap` parameter when using `RecursiveCharacterTextSplitter` to prepare documents for RAG, and what trade-offs arise as you increase or decrease its value?

#### ✅ Answer:
The `chunk_overlap` parameter in `RecursiveCharacterTextSplitter` controls how much text is shared between consecutive chunks when splitting documents for RAG.

**Purpose**: It ensures context continuity between chunks by allowing adjacent chunks to share some text.

**Trade-offs**:

- **Increasing overlap**:
  - ✅ Better context preservation across chunk boundaries
  - ✅ Reduces risk of losing important information at chunk edges
  - ❌ More storage/memory usage
  - ❌ Potential redundancy in retrieved content

- **Decreasing overlap**:
  - ✅ More efficient storage and retrieval
  - ✅ Less duplicate content
  - ❌ Risk of losing context at chunk boundaries
  - ❌ May break up coherent ideas or sentences

In this project, `chunk_overlap=0` means no overlap between chunks, which is memory-efficient but could lose context at chunk boundaries. For financial aid documents with complex regulations, some overlap (like 50-100 tokens) might improve answer quality by maintaining context continuity.


#### ❓ Question:

Your retriever is configured with `search_kwargs={"k": 5}`. How would adjusting `k` likely affect RAGAS metrics such as Context Precision and Context Recall in practice, and why?

#### ✅ Answer:

The `k=5` parameter in `search_kwargs` controls how many document chunks the retriever returns for each query.

**Impact on RAGAS metrics**:

- **Context Precision**: 
  - Lower `k` (e.g., 3) → Higher precision (more relevant chunks)
  - Higher `k` (e.g., 10) → Lower precision (more irrelevant chunks included)

- **Context Recall**:
  - Lower `k` → Lower recall (might miss relevant chunks)
  - Higher `k` → Higher recall (more likely to capture all relevant information)

**Why this happens**:
- With `k=5`, we're getting the top 5 most similar chunks
- If relevant information is spread across more than 5 chunks, we'll miss some (low recall)
- If the top 5 chunks are highly relevant, precision stays high
- Increasing `k` trades precision for recall by including more chunks, some of which may be less relevant

**Practical consideration**: For financial aid documents with complex, interconnected regulations, `k=5` might be too low to capture all relevant context, suggesting a higher value could improve recall while maintaining acceptable precision.


#### ❓ Question:

Compare the `agent` and `agent_helpful` assistants defined in `langgraph.json`. Where does the helpfulness evaluator fit in the graph, and under what condition should execution route back to the agent vs. terminate?

#### ✅ Answer:

1. **simple_agent**:
- Basic tool-using agent
- Flow: 
`User Input → Agent (with tools) → Tool Execution (if needed) → Response → End`


2. **agent_with_helpfulness**:
- Enhanced agent with helpfulness evaluation loops
- Flow:
`User Input → Agent → Tool Execution (if needed) → Helpfulness Check → Loop or End`

The helpfulness agent includes a sophisticated evaluation loop that:

- Assesses response quality after each iteration
- Continues improving responses until deemed helpful
- Has built-in loop limits to prevent infinite execution

**Where helpfulness evaluator fits**:
The helpfulness node sits **after** the agent responds (when no tools are needed) and **before** termination.

**Routing conditions**:
- **Route back to agent**: When helpfulness evaluator returns "N" (not helpful) - allows the agent to improve its response
- **Terminate**: When helpfulness evaluator returns "Y" (helpful) or when loop limit (10 messages) is exceeded

**Key difference**: 

The simple agent terminates immediately after responding, while the helpful agent can loop back multiple times to refine responses until they meet helpfulness criteria or hit the safety limit.
