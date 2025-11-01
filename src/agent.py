"""
AI Agent for Hallucination Testing
Handles interactions with DeepSeek API and applies mitigation strategies
"""
import time
from typing import Dict, List, Optional, Tuple
from openai import OpenAI
from config import Config


class HallucinationTestAgent:
    """AI Agent for testing and mitigating hallucinations"""

    def __init__(self, api_key: Optional[str] = None,
                 model: Optional[str] = None,
                 temperature: Optional[float] = None,
                 max_tokens: Optional[int] = None):
        """
        Initialize the agent

        Args:
            api_key: DeepSeek API key (defaults to Config.DEEPSEEK_API_KEY)
            model: Model name (defaults to Config.MODEL_NAME)
            temperature: Temperature setting (defaults to Config.TEMPERATURE)
            max_tokens: Max tokens (defaults to Config.MAX_TOKENS)
        """
        self.api_key = api_key or Config.DEEPSEEK_API_KEY
        self.model = model or Config.MODEL_NAME
        self.temperature = temperature if temperature is not None else Config.TEMPERATURE
        self.max_tokens = max_tokens or Config.MAX_TOKENS

        if not self.api_key:
            raise ValueError("DeepSeek API key not provided")

        # Initialize OpenAI client with DeepSeek base URL
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.deepseek.com"
        )

    def query_baseline(self, prompt: str) -> Tuple[str, Dict]:
        """
        Query the model with no mitigation (baseline)

        Args:
            prompt: The user prompt

        Returns:
            Tuple of (response_text, metadata)
        """
        start_time = time.time()

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )

            elapsed_time = (time.time() - start_time) * 1000  # Convert to ms

            response_text = response.choices[0].message.content
            metadata = {
                'response_time_ms': elapsed_time,
                'tokens_used': response.usage.total_tokens,
                'prompt_tokens': response.usage.prompt_tokens,
                'completion_tokens': response.usage.completion_tokens,
                'model': self.model,
                'finish_reason': response.choices[0].finish_reason
            }

            return response_text, metadata

        except Exception as e:
            return f"ERROR: {str(e)}", {'error': str(e), 'response_time_ms': 0}

    def query_with_rag(self, prompt: str, context_documents: List[str]) -> Tuple[str, Dict]:
        """
        Query with Retrieval-Augmented Generation

        Args:
            prompt: The user prompt
            context_documents: List of retrieved relevant documents

        Returns:
            Tuple of (response_text, metadata)
        """
        # Build RAG prompt with context
        context_str = "\n\n".join([f"Document {i+1}: {doc}"
                                   for i, doc in enumerate(context_documents)])

        rag_prompt = f"""You are a helpful assistant. Use ONLY the information provided in the documents below to answer the question. If the answer is not in the documents, say "I don't have enough information to answer this question."

Documents:
{context_str}

Question: {prompt}

Answer based only on the documents above:"""

        start_time = time.time()

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": rag_prompt}
                ],
                temperature=0.3,  # Lower temperature for RAG to reduce hallucinations
                max_tokens=self.max_tokens
            )

            elapsed_time = (time.time() - start_time) * 1000

            response_text = response.choices[0].message.content
            metadata = {
                'response_time_ms': elapsed_time,
                'tokens_used': response.usage.total_tokens,
                'prompt_tokens': response.usage.prompt_tokens,
                'completion_tokens': response.usage.completion_tokens,
                'model': self.model,
                'retrieved_documents': context_documents,
                'num_documents': len(context_documents)
            }

            return response_text, metadata

        except Exception as e:
            return f"ERROR: {str(e)}", {'error': str(e), 'response_time_ms': 0}

    def query_with_constitutional_ai(self, prompt: str) -> Tuple[str, Dict]:
        """
        Query with Constitutional AI approach (self-critique)

        Args:
            prompt: The user prompt

        Returns:
            Tuple of (response_text, metadata)
        """
        start_time = time.time()

        try:
            # Step 1: Get initial response
            initial_response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )

            initial_answer = initial_response.choices[0].message.content

            # Step 2: Self-critique with constitutional principles
            critique_prompt = f"""Review the following response for factual accuracy and potential hallucinations.

Original Question: {prompt}

Response to Review: {initial_answer}

Constitutional Principles:
1. Only state facts you are certain about
2. Clearly distinguish between facts and speculation
3. Admit when you don't have information
4. Do not fabricate sources, citations, or entities
5. If uncertain, express uncertainty

Please review the response and provide:
1. Any potential factual errors or hallucinations
2. A revised, more accurate response

Format:
CRITIQUE: [your critique]
REVISED RESPONSE: [improved response]"""

            critique_response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": critique_prompt}
                ],
                temperature=0.3,  # Lower temperature for critique
                max_tokens=self.max_tokens
            )

            elapsed_time = (time.time() - start_time) * 1000

            final_response = critique_response.choices[0].message.content

            # Extract revised response if possible
            if "REVISED RESPONSE:" in final_response:
                revised = final_response.split("REVISED RESPONSE:")[1].strip()
            else:
                revised = final_response

            total_tokens = (initial_response.usage.total_tokens +
                          critique_response.usage.total_tokens)

            metadata = {
                'response_time_ms': elapsed_time,
                'tokens_used': total_tokens,
                'model': self.model,
                'initial_response': initial_answer,
                'critique_response': final_response,
                'num_critique_rounds': 1
            }

            return revised, metadata

        except Exception as e:
            return f"ERROR: {str(e)}", {'error': str(e), 'response_time_ms': 0}

    def query_with_chain_of_thought(self, prompt: str) -> Tuple[str, Dict]:
        """
        Query with Chain-of-Thought verification

        Args:
            prompt: The user prompt

        Returns:
            Tuple of (response_text, metadata)
        """
        start_time = time.time()

        cot_prompt = f"""{prompt}

Please answer this question using the following steps:
1. Break down what the question is asking
2. Think through what you know about this topic
3. Identify any facts you're uncertain about
4. Provide your answer, clearly marking any uncertain information
5. List any assumptions or limitations in your knowledge

Format your response as:
REASONING: [your step-by-step thinking]
ANSWER: [your final answer]
CONFIDENCE: [High/Medium/Low]
LIMITATIONS: [what you're uncertain about]"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": cot_prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )

            elapsed_time = (time.time() - start_time) * 1000

            response_text = response.choices[0].message.content
            metadata = {
                'response_time_ms': elapsed_time,
                'tokens_used': response.usage.total_tokens,
                'model': self.model,
                'finish_reason': response.choices[0].finish_reason
            }

            return response_text, metadata

        except Exception as e:
            return f"ERROR: {str(e)}", {'error': str(e), 'response_time_ms': 0}

    def query(self, prompt: str, mitigation_strategy: str = "baseline",
              **kwargs) -> Tuple[str, Dict]:
        """
        Universal query method that routes to appropriate mitigation strategy

        Args:
            prompt: The user prompt
            mitigation_strategy: One of: baseline, rag, constitutional_ai, chain_of_thought
            **kwargs: Additional arguments for specific strategies

        Returns:
            Tuple of (response_text, metadata)
        """
        if mitigation_strategy == "baseline":
            return self.query_baseline(prompt)

        elif mitigation_strategy == "rag":
            context_docs = kwargs.get('context_documents', [])
            if not context_docs:
                print("Warning: RAG strategy requires context_documents. Using baseline instead.")
                return self.query_baseline(prompt)
            return self.query_with_rag(prompt, context_docs)

        elif mitigation_strategy == "constitutional_ai":
            return self.query_with_constitutional_ai(prompt)

        elif mitigation_strategy == "chain_of_thought":
            return self.query_with_chain_of_thought(prompt)

        else:
            raise ValueError(f"Unknown mitigation strategy: {mitigation_strategy}")


if __name__ == "__main__":
    # Test agent
    print("Testing AI Agent...")
    try:
        agent = HallucinationTestAgent()
        response, metadata = agent.query_baseline("What is 2+2?")
        print(f"Response: {response}")
        print(f"Metadata: {metadata}")
    except ValueError as e:
        print(f"Error: {e}")
        print("Please set DEEPSEEK_API_KEY in .env file")
