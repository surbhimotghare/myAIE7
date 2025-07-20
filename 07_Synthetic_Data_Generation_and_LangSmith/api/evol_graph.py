from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
import random
import uuid
import asyncio
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EvolState(TypedDict):
    """State for the Evol-Instruct graph"""
    documents: List[Dict[str, Any]]
    seed_questions: List[Dict[str, Any]]
    evolved_questions: List[Dict[str, Any]]
    question_answers: List[Dict[str, Any]]
    question_contexts: List[Dict[str, Any]]
    current_phase: str
    error: str

class EvolInstructGraph:
    """LangGraph implementation of Evol-Instruct methodology"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o-mini", 
            temperature=0.7,
            max_tokens=1000
        )
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(EvolState)
        
        # Add nodes for each phase
        workflow.add_node("generate_seeds", self.generate_seed_questions)
        workflow.add_node("simple_evolution", self.simple_evolution)
        workflow.add_node("multi_context_evolution", self.multi_context_evolution)
        workflow.add_node("reasoning_evolution", self.reasoning_evolution)
        workflow.add_node("generate_answers", self.generate_answers)
        workflow.add_node("extract_contexts", self.extract_contexts)
        
        # Define the flow
        workflow.set_entry_point("generate_seeds")
        workflow.add_edge("generate_seeds", "simple_evolution")
        workflow.add_edge("simple_evolution", "multi_context_evolution")
        workflow.add_edge("multi_context_evolution", "reasoning_evolution")
        workflow.add_edge("reasoning_evolution", "generate_answers")
        workflow.add_edge("generate_answers", "extract_contexts")
        workflow.set_finish_point("extract_contexts")
        
        return workflow.compile()

    def generate_seed_questions(self, state: EvolState) -> EvolState:
        """Generate initial seed questions from documents"""
        logger.info("Generating seed questions...")
        
        try:
            seed_questions = []
            
            # Generate questions from up to 3 documents to keep it manageable
            for i, doc in enumerate(state["documents"][:3]):
                content = doc["page_content"][:1500]  # Limit content length
                
                prompt = f"""Based on this document, generate one clear, specific question that can be answered using the information provided.

Document content:
{content}

Requirements:
- Question should be specific and answerable from the document
- Avoid yes/no questions
- Focus on key information or concepts
- Keep it concise but meaningful

Question:"""

                try:
                    response = self.llm.invoke(prompt)
                    question_text = response.content.strip()
                    
                    # Clean up the question
                    if question_text.startswith('"') and question_text.endswith('"'):
                        question_text = question_text[1:-1]
                    
                    seed_questions.append({
                        "id": f"seed_{i}",
                        "question": question_text,
                        "source_doc_index": i,
                        "metadata": doc.get("metadata", {})
                    })
                    
                    logger.info(f"Generated seed question {i+1}: {question_text[:50]}...")
                    
                except Exception as e:
                    logger.error(f"Error generating seed question {i}: {str(e)}")
                    continue
            
            state["seed_questions"] = seed_questions
            state["evolved_questions"] = []
            state["current_phase"] = "seeds_generated"
            
            logger.info(f"Generated {len(seed_questions)} seed questions")
            return state
            
        except Exception as e:
            logger.error(f"Error in generate_seed_questions: {str(e)}")
            state["error"] = f"Seed generation error: {str(e)}"
            return state

    def simple_evolution(self, state: EvolState) -> EvolState:
        """Apply simple evolution transformations"""
        logger.info("Applying simple evolution...")
        
        try:
            # Evol-Instruct simple evolution operations
            evolution_operations = [
                "Add specific constraints or conditions to make this question more challenging and detailed: {question}",
                "Deepen this question by asking for more comprehensive analysis and explanation: {question}",
                "Make this question more complex by incorporating multiple related aspects or variables: {question}",
                "Transform this question to require step-by-step reasoning or methodology: {question}",
                "Add real-world application context to make this question more practical: {question}"
            ]
            
            evolved_questions = []
            seeds_to_use = state["seed_questions"][:3]  # Use up to 3 seeds
            
            for i, seed in enumerate(seeds_to_use):
                try:
                    operation = random.choice(evolution_operations)
                    
                    prompt = f"""You are an expert at evolving questions to make them more sophisticated and challenging.

Original question: {seed['question']}

Task: {operation.format(question=seed['question'])}

Requirements:
- The evolved question should still be answerable from the original document context
- Make it more sophisticated but not impossible to answer
- Maintain clarity while adding complexity
- Don't change the core topic, just make it more challenging

Evolved question:"""

                    response = self.llm.invoke(prompt)
                    evolved_text = response.content.strip()
                    
                    # Clean up the response
                    if evolved_text.startswith('"') and evolved_text.endswith('"'):
                        evolved_text = evolved_text[1:-1]
                    
                    evolved_questions.append({
                        "id": f"simple_{i}",
                        "question": evolved_text,
                        "evolution_type": "simple",
                        "parent_id": seed["id"],
                        "source_doc_index": seed["source_doc_index"]
                    })
                    
                    logger.info(f"Simple evolution {i+1}: {evolved_text[:50]}...")
                    
                except Exception as e:
                    logger.error(f"Error in simple evolution {i}: {str(e)}")
                    continue
            
            state["evolved_questions"].extend(evolved_questions)
            state["current_phase"] = "simple_evolution_complete"
            
            logger.info(f"Generated {len(evolved_questions)} simple evolution questions")
            return state
            
        except Exception as e:
            logger.error(f"Error in simple_evolution: {str(e)}")
            state["error"] = f"Simple evolution error: {str(e)}"
            return state

    def multi_context_evolution(self, state: EvolState) -> EvolState:
        """Create questions requiring multiple document contexts"""
        logger.info("Applying multi-context evolution...")
        
        try:
            if len(state["documents"]) < 2:
                logger.warning("Not enough documents for multi-context evolution, using single document")
                # Fallback to creating complex single-document questions
                return self._single_doc_multi_aspect_evolution(state)
            
            evolved_questions = []
            seeds_to_use = state["seed_questions"][:3]
            
            for i, seed in enumerate(seeds_to_use):
                try:
                    # Get content from multiple documents
                    doc_contents = []
                    for j, doc in enumerate(state["documents"][:3]):
                        content_preview = doc["page_content"][:800]
                        doc_contents.append(f"Document {j+1}: {content_preview}")
                    
                    combined_context = "\n\n".join(doc_contents)
                    
                    prompt = f"""You are creating questions that require synthesizing information from multiple documents.

Base question: {seed['question']}

Available document contexts:
{combined_context}

Create a new question that:
- Requires information from at least 2 different documents
- Asks for comparison, connection, or synthesis across documents
- Is more complex than the original question
- Can still be answered using the provided documents

Examples of multi-context questions:
- "How do the requirements in Document 1 relate to the processes described in Document 2?"
- "Compare and contrast the approaches described in Documents 1 and 2"
- "What are the implications of Document 1's policies for the scenarios in Document 2?"

Multi-context question:"""

                    response = self.llm.invoke(prompt)
                    evolved_text = response.content.strip()
                    
                    if evolved_text.startswith('"') and evolved_text.endswith('"'):
                        evolved_text = evolved_text[1:-1]
                    
                    evolved_questions.append({
                        "id": f"multi_context_{i}",
                        "question": evolved_text,
                        "evolution_type": "multi_context",
                        "parent_id": seed["id"],
                        "source_doc_index": "multiple"
                    })
                    
                    logger.info(f"Multi-context evolution {i+1}: {evolved_text[:50]}...")
                    
                except Exception as e:
                    logger.error(f"Error in multi-context evolution {i}: {str(e)}")
                    continue
            
            state["evolved_questions"].extend(evolved_questions)
            state["current_phase"] = "multi_context_evolution_complete"
            
            logger.info(f"Generated {len(evolved_questions)} multi-context questions")
            return state
            
        except Exception as e:
            logger.error(f"Error in multi_context_evolution: {str(e)}")
            state["error"] = f"Multi-context evolution error: {str(e)}"
            return state

    def _single_doc_multi_aspect_evolution(self, state: EvolState) -> EvolState:
        """Fallback for multi-context when only one document is available"""
        evolved_questions = []
        seeds_to_use = state["seed_questions"][:3]
        
        for i, seed in enumerate(seeds_to_use):
            try:
                prompt = f"""Create a more complex question that examines multiple aspects of the topic.

Original question: {seed['question']}

Transform this into a question that:
- Examines multiple facets or aspects of the topic
- Requires connecting different concepts within the document
- Is more comprehensive and analytical

Multi-aspect question:"""

                response = self.llm.invoke(prompt)
                evolved_text = response.content.strip()
                
                if evolved_text.startswith('"') and evolved_text.endswith('"'):
                    evolved_text = evolved_text[1:-1]
                
                evolved_questions.append({
                    "id": f"multi_context_{i}",
                    "question": evolved_text,
                    "evolution_type": "multi_context",
                    "parent_id": seed["id"],
                    "source_doc_index": seed["source_doc_index"]
                })
                
            except Exception as e:
                logger.error(f"Error in single-doc multi-aspect evolution {i}: {str(e)}")
                continue
        
        state["evolved_questions"].extend(evolved_questions)
        return state

    def reasoning_evolution(self, state: EvolState) -> EvolState:
        """Create questions requiring logical reasoning and inference"""
        logger.info("Applying reasoning evolution...")
        
        try:
            evolved_questions = []
            seeds_to_use = state["seed_questions"][:3]
            
            for i, seed in enumerate(seeds_to_use):
                try:
                    prompt = f"""Transform this question to require logical reasoning, cause-effect analysis, or inferential thinking.

Original question: {seed['question']}

Create a reasoning question that:
- Requires "if-then" logical analysis
- Asks for cause and effect relationships
- Involves problem-solving or strategic thinking
- Requires inference beyond direct facts
- Uses scenario-based reasoning

Examples:
- "If [condition X] occurs, what would be the implications for [outcome Y], and how should one respond?"
- "Given [constraints A and B], what approach would you recommend for [situation C] and why?"
- "What are the potential consequences of [action X], and how might they affect [stakeholder Y]?"

Reasoning question:"""

                    response = self.llm.invoke(prompt)
                    evolved_text = response.content.strip()
                    
                    if evolved_text.startswith('"') and evolved_text.endswith('"'):
                        evolved_text = evolved_text[1:-1]
                    
                    evolved_questions.append({
                        "id": f"reasoning_{i}",
                        "question": evolved_text,
                        "evolution_type": "reasoning",
                        "parent_id": seed["id"],
                        "source_doc_index": seed.get("source_doc_index", 0)
                    })
                    
                    logger.info(f"Reasoning evolution {i+1}: {evolved_text[:50]}...")
                    
                except Exception as e:
                    logger.error(f"Error in reasoning evolution {i}: {str(e)}")
                    continue
            
            state["evolved_questions"].extend(evolved_questions)
            state["current_phase"] = "reasoning_evolution_complete"
            
            logger.info(f"Generated {len(evolved_questions)} reasoning questions")
            return state
            
        except Exception as e:
            logger.error(f"Error in reasoning_evolution: {str(e)}")
            state["error"] = f"Reasoning evolution error: {str(e)}"
            return state

    def generate_answers(self, state: EvolState) -> EvolState:
        """Generate answers for all evolved questions"""
        logger.info("Generating answers...")
        
        try:
            answers = []
            all_content = "\n\n".join([
                f"Document {i+1}:\n{doc['page_content'][:2000]}" 
                for i, doc in enumerate(state["documents"])
            ])
            
            for question in state["evolved_questions"]:
                try:
                    prompt = f"""Answer the following question based on the provided document context. Be comprehensive, accurate, and well-structured.

Context:
{all_content}

Question: {question['question']}

Instructions:
- Answer based only on the information provided in the context
- Be thorough and provide detailed explanations
- If the question requires reasoning, show your logical steps
- If information is not available, state that clearly
- Structure your answer clearly with appropriate paragraphs

Answer:"""

                    response = self.llm.invoke(prompt)
                    answer_text = response.content.strip()
                    
                    answers.append({
                        "question_id": question["id"],
                        "answer": answer_text
                    })
                    
                    logger.info(f"Generated answer for {question['id']}")
                    
                except Exception as e:
                    logger.error(f"Error generating answer for {question['id']}: {str(e)}")
                    # Add placeholder answer
                    answers.append({
                        "question_id": question["id"],
                        "answer": "Unable to generate answer due to processing error."
                    })
                    continue
            
            state["question_answers"] = answers
            state["current_phase"] = "answers_generated"
            
            logger.info(f"Generated {len(answers)} answers")
            return state
            
        except Exception as e:
            logger.error(f"Error in generate_answers: {str(e)}")
            state["error"] = f"Answer generation error: {str(e)}"
            return state

    def extract_contexts(self, state: EvolState) -> EvolState:
        """Extract relevant contexts for each question"""
        logger.info("Extracting contexts...")
        
        try:
            contexts = []
            
            for question in state["evolved_questions"]:
                try:
                    relevant_contexts = []
                    
                    if question.get("source_doc_index") == "multiple":
                        # Multi-context question - include multiple document excerpts
                        for doc in state["documents"][:3]:
                            if len(doc["page_content"]) > 100:
                                context_chunk = doc["page_content"][:600]
                                relevant_contexts.append(context_chunk)
                    else:
                        # Single document question
                        doc_index = question.get("source_doc_index", 0)
                        if doc_index < len(state["documents"]):
                            doc = state["documents"][doc_index]
                            context_chunk = doc["page_content"][:800]
                            relevant_contexts.append(context_chunk)
                        
                        # Add a second context if available for more comprehensive coverage
                        if len(state["documents"]) > 1:
                            other_doc_index = (doc_index + 1) % len(state["documents"])
                            other_doc = state["documents"][other_doc_index]
                            if len(other_doc["page_content"]) > 100:
                                other_context = other_doc["page_content"][:400]
                                relevant_contexts.append(other_context)
                    
                    contexts.append({
                        "question_id": question["id"],
                        "contexts": relevant_contexts
                    })
                    
                    logger.info(f"Extracted {len(relevant_contexts)} contexts for {question['id']}")
                    
                except Exception as e:
                    logger.error(f"Error extracting context for {question['id']}: {str(e)}")
                    # Add placeholder context
                    contexts.append({
                        "question_id": question["id"],
                        "contexts": ["Context extraction failed."]
                    })
                    continue
            
            state["question_contexts"] = contexts
            state["current_phase"] = "contexts_extracted"
            
            logger.info(f"Extracted contexts for {len(contexts)} questions")
            return state
            
        except Exception as e:
            logger.error(f"Error in extract_contexts: {str(e)}")
            state["error"] = f"Context extraction error: {str(e)}"
            return state

    async def run(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute the full Evol-Instruct pipeline"""
        logger.info("Starting Evol-Instruct pipeline...")
        
        initial_state: EvolState = {
            "documents": documents,
            "seed_questions": [],
            "evolved_questions": [],
            "question_answers": [],
            "question_contexts": [],
            "current_phase": "initialized",
            "error": ""
        }
        
        try:
            # Run the graph
            final_state = await self.graph.ainvoke(initial_state)
            
            if final_state.get("error"):
                raise Exception(f"Pipeline error: {final_state['error']}")
            
            logger.info("Evol-Instruct pipeline completed successfully")
            
            return {
                "evolved_questions": final_state["evolved_questions"],
                "question_answers": final_state["question_answers"],
                "question_contexts": final_state["question_contexts"],
                "seed_questions": final_state["seed_questions"]  # For debugging
            }
            
        except Exception as e:
            logger.error(f"Error running Evol-Instruct pipeline: {str(e)}")
            raise Exception(f"Pipeline execution failed: {str(e)}")

# Global instance for reuse
evol_graph_instance = None

def get_evol_graph() -> EvolInstructGraph:
    """Get singleton instance of EvolInstructGraph"""
    global evol_graph_instance
    if evol_graph_instance is None:
        evol_graph_instance = EvolInstructGraph()
    return evol_graph_instance 