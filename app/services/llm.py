from typing import List, Dict, Any, Optional
from groq import Groq
import logging
from tenacity import retry, stop_after_attempt, wait_exponential
from ..config import settings

logger = logging.getLogger(__name__)

class LLMService:
    """Service for generating answers using Groq's LLM."""
    
    def __init__(self):
        self.client = Groq(api_key=settings.groq_api_key)
        self.model = settings.llm_model
    
    @retry(
        stop=stop_after_attempt(settings.max_retries),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def generate_answer(self, query: str, context_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate an answer based on query and context chunks."""
        try:
            # Build context from chunks
            context = self._build_context(context_chunks)
            
            # Create prompt
            prompt = self._create_prompt(query, context)
            
            # Generate answer using Groq
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1024,
                top_p=1,
                stream=False,  # For simplicity, we'll use non-streaming
                stop=None,
            )
            
            answer_text = response.choices[0].message.content
            
            # Extract citations and confidence
            citations = self._extract_citations(answer_text, context_chunks)
            confidence = self._calculate_confidence(context_chunks)
            
            return {
                "answer": answer_text,
                "citations": citations,
                "confidence": confidence
            }
            
        except Exception as e:
            logger.error(f"Failed to generate answer: {e}")
            raise
    
    def _build_context(self, chunks: List[Dict[str, Any]]) -> str:
        """Build context string from chunks."""
        context_parts = []
        for i, chunk in enumerate(chunks):
            metadata = chunk.get("metadata", {})
            source_info = f"[Source {i+1}: {metadata.get('journal_name', 'Unknown')} ({metadata.get('year', 'Unknown')})]"
            context_parts.append(f"{source_info}\n{chunk['text']}\n")
        
        return "\n".join(context_parts)
    
    def _create_prompt(self, query: str, context: str) -> str:
        """Create prompt for the LLM."""
        return f"""
Based on the following research context, please answer the question. 
If the context doesn't contain enough information to answer the question, please say so.
Always cite your sources using the format [Source X] when referencing information.

Context:
{context}

Question: {query}

Answer:
"""
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for the LLM."""
        return """
You are a helpful research assistant that provides accurate, well-cited answers based on scientific literature.

Guidelines:
1. Only answer based on the provided context
2. Always cite sources using [Source X] format
3. If information is insufficient, say so clearly
4. Be concise but comprehensive
5. Maintain scientific accuracy
6. If multiple sources agree, mention that
7. If sources disagree, mention the disagreement
"""
    
    def _extract_citations(self, answer: str, chunks: List[Dict[str, Any]]) -> List[str]:
        """Extract citations from the answer."""
        citations = []
        for i, chunk in enumerate(chunks):
            if f"[Source {i+1}]" in answer:
                metadata = chunk.get("metadata", {})
                citation = f"{metadata.get('journal_name', 'Unknown')} ({metadata.get('year', 'Unknown')})"
                if citation not in citations:
                    citations.append(citation)
        
        return citations
    
    def _calculate_confidence(self, chunks: List[Dict[str, Any]]) -> float:
        """Calculate confidence score based on context quality."""
        if not chunks:
            return 0.0
        
        # Simple confidence calculation based on:
        # - Number of chunks
        # - Average similarity score
        # - Presence of high-quality sources
        
        avg_similarity = sum(chunk.get("similarity_score", 0) for chunk in chunks) / len(chunks)
        chunk_count_factor = min(len(chunks) / 5, 1.0)  # Normalize to 5 chunks
        
        confidence = (avg_similarity * 0.7) + (chunk_count_factor * 0.3)
        return min(confidence, 1.0)
