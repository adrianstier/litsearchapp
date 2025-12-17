"""LLM service for paper summarization and data extraction using Claude"""

import os
import json
import asyncio
from typing import List, Dict, Optional, Any
import anthropic
from pydantic import BaseModel

class LLMService:
    """Service for LLM-powered paper analysis using Claude"""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize with Anthropic API key"""
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self._client = None
        self._async_client = None

    @property
    def client(self) -> anthropic.Anthropic:
        """Get sync Anthropic client"""
        if self._client is None:
            if not self.api_key:
                raise ValueError("Anthropic API key not set. Set ANTHROPIC_API_KEY environment variable.")
            self._client = anthropic.Anthropic(api_key=self.api_key)
        return self._client

    @property
    def async_client(self) -> anthropic.AsyncAnthropic:
        """Get async Anthropic client"""
        if self._async_client is None:
            if not self.api_key:
                raise ValueError("Anthropic API key not set. Set ANTHROPIC_API_KEY environment variable.")
            self._async_client = anthropic.AsyncAnthropic(api_key=self.api_key)
        return self._async_client

    def summarize_paper(self, title: str, abstract: str,
                       max_tokens: int = 150) -> str:
        """
        Generate a concise summary of a paper

        Args:
            title: Paper title
            abstract: Paper abstract
            max_tokens: Maximum tokens in response

        Returns:
            2-3 sentence summary
        """
        prompt = f"""Summarize this academic paper in 2-3 sentences, focusing on the main finding and methodology. Be concise and specific.

Title: {title}

Abstract: {abstract}

Summary:"""

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text.strip()
        except Exception as e:
            print(f"⚠ Summarization failed: {e}")
            return ""

    async def summarize_paper_async(self, title: str, abstract: str,
                                   max_tokens: int = 150) -> str:
        """Async version of summarize_paper"""
        prompt = f"""Summarize this academic paper in 2-3 sentences, focusing on the main finding and methodology. Be concise and specific.

Title: {title}

Abstract: {abstract}

Summary:"""

        try:
            response = await self.async_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text.strip()
        except Exception as e:
            print(f"⚠ Async summarization failed: {e}")
            return ""

    async def summarize_papers_batch(self, papers: List[Dict],
                                    max_concurrent: int = 5) -> List[str]:
        """
        Summarize multiple papers concurrently

        Args:
            papers: List of papers with 'title' and 'abstract'
            max_concurrent: Max concurrent API calls

        Returns:
            List of summaries
        """
        semaphore = asyncio.Semaphore(max_concurrent)

        async def summarize_with_limit(paper):
            async with semaphore:
                return await self.summarize_paper_async(
                    paper.get('title', ''),
                    paper.get('abstract', '')
                )

        tasks = [summarize_with_limit(paper) for paper in papers]
        return await asyncio.gather(*tasks)

    def extract_structured_data(self, paper_text: str,
                               fields: List[str]) -> Dict[str, Any]:
        """
        Extract structured information from paper text

        Args:
            paper_text: Full paper text or abstract
            fields: List of fields to extract

        Returns:
            Dictionary with extracted values
        """
        # Build schema description
        field_descriptions = {
            "methodology": "Research methodology used (e.g., RCT, observational, meta-analysis)",
            "sample_size": "Number of participants/samples (integer)",
            "population": "Study population description",
            "intervention": "Intervention or treatment tested",
            "control": "Control condition",
            "outcomes": "Primary outcomes measured (list)",
            "main_finding": "Primary result or conclusion",
            "effect_size": "Effect size or key statistic",
            "limitations": "Study limitations (list)",
            "p_value": "Primary p-value reported",
            "confidence_interval": "Confidence interval if reported",
            "duration": "Study duration",
            "setting": "Study setting/location"
        }

        schema = {}
        for field in fields:
            if field in field_descriptions:
                schema[field] = field_descriptions[field]
            else:
                schema[field] = f"Extract: {field}"

        prompt = f"""Extract the following information from this research paper. Return ONLY valid JSON.
If information is not found, use null.

Fields to extract:
{json.dumps(schema, indent=2)}

Paper text:
{paper_text[:6000]}

Return JSON only, no markdown or explanation:"""

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )

            # Extract JSON from response
            response_text = response.content[0].text.strip()
            # Handle potential markdown code blocks
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]
                response_text = response_text.strip()

            result = json.loads(response_text)
            return result

        except Exception as e:
            print(f"⚠ Extraction failed: {e}")
            return {field: None for field in fields}

    def extract_custom_column(self, papers: List[Dict],
                             column_name: str,
                             column_description: str) -> List[str]:
        """
        Extract custom column data from multiple papers

        Args:
            papers: List of papers
            column_name: Name for the column
            column_description: Description of what to extract

        Returns:
            List of extracted values
        """
        results = []

        prompt_template = f"""Extract the following information from this paper:
{column_description}

Title: {{title}}
Abstract: {{abstract}}

Extracted value for "{column_name}" (be concise, max 50 words):"""

        for paper in papers:
            prompt = prompt_template.format(
                title=paper.get('title', ''),
                abstract=paper.get('abstract', '')
            )

            try:
                response = self.client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=100,
                    messages=[{"role": "user", "content": prompt}]
                )
                results.append(response.content[0].text.strip())
            except Exception as e:
                print(f"⚠ Column extraction failed: {e}")
                results.append("Error extracting")

        return results

    def verify_claim(self, paper_text: str, claim: str) -> Dict[str, Any]:
        """
        Verify if a claim is supported by the paper text

        Args:
            paper_text: Paper text to check against
            claim: Claim to verify

        Returns:
            Dict with verification result and evidence
        """
        prompt = f"""Is the following claim directly supported by the paper text? Respond with JSON only:
{{
  "verdict": "SUPPORTED" | "NOT_SUPPORTED" | "PARTIALLY_SUPPORTED",
  "confidence": 0-100,
  "evidence": "relevant quote or explanation",
  "reasoning": "brief explanation"
}}

Claim: {claim}

Paper excerpt:
{paper_text[:3000]}

Return JSON only, no markdown:"""

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=300,
                messages=[{"role": "user", "content": prompt}]
            )

            response_text = response.content[0].text.strip()
            # Handle potential markdown code blocks
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]
                response_text = response_text.strip()

            return json.loads(response_text)

        except Exception as e:
            print(f"⚠ Verification failed: {e}")
            return {
                "verdict": "ERROR",
                "confidence": 0,
                "evidence": "",
                "reasoning": str(e)
            }

    def generate_research_questions(self, topic: str, num_questions: int = 5) -> List[str]:
        """
        Generate research questions for a topic

        Args:
            topic: Research topic
            num_questions: Number of questions to generate

        Returns:
            List of research questions
        """
        prompt = f"""Generate {num_questions} specific, answerable research questions about:
{topic}

Make questions:
- Specific and focused
- Empirically testable
- Relevant to academic research

Return as JSON object with a "questions" key containing an array of strings:"""

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )

            response_text = response.content[0].text.strip()
            # Handle potential markdown code blocks
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]
                response_text = response_text.strip()

            result = json.loads(response_text)
            if isinstance(result, dict):
                # Handle {"questions": [...]} format
                return result.get("questions", [])
            return result

        except Exception as e:
            print(f"⚠ Question generation failed: {e}")
            return []

    def compare_papers(self, papers: List[Dict], aspect: str = "findings") -> str:
        """
        Compare multiple papers on a specific aspect

        Args:
            papers: List of papers to compare
            aspect: Aspect to compare (findings, methodology, etc.)

        Returns:
            Comparison summary
        """
        paper_summaries = []
        for i, paper in enumerate(papers[:5]):  # Limit to 5 papers
            paper_summaries.append(f"""Paper {i+1}: {paper.get('title', 'Untitled')}
Abstract: {paper.get('abstract', 'No abstract')[:500]}
""")

        prompt = f"""Compare these papers focusing on their {aspect}:

{chr(10).join(paper_summaries)}

Provide a structured comparison highlighting:
1. Common themes
2. Key differences
3. Contradictions (if any)
4. Gaps in the research

Comparison:"""

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=800,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text.strip()

        except Exception as e:
            print(f"⚠ Comparison failed: {e}")
            return f"Error comparing papers: {e}"


# Global instance
_llm_service = None

def get_llm_service() -> LLMService:
    """Get or create LLM service singleton"""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service
