import json
from typing import Tuple, Dict, Any
from groq import Groq
from config import Config
import time


class LLMService:
    """Service for LLM integration with defensive error handling."""
    
    def __init__(self):
        """Initialize Groq client."""
        self.client = None
        if Config.GROQ_API_KEY:
            try:
                self.client = Groq(api_key=Config.GROQ_API_KEY)
            except Exception as e:
                print(f"Failed to initialize Groq client: {str(e)}")
    
    def generate_insights(self, summary: Dict[str, Any]) -> Tuple[bool, str, str]:
        """Generate insights from CSV summary.
        
        Args:
            summary: CSV summary dictionary
            
        Returns:
            Tuple of (success: bool, insights: str, error_message: str)
        """
        if not self.client:
            return False, "", "LLM service not initialized (API key missing or invalid)"
        
        # Validate summary
        from services.csv_service import CSVService
        if not CSVService.validate_summary(summary):
            return False, {}, "Invalid summary object"
        
        # Prepare prompt requesting structured JSON
        try:
            summary_text = json.dumps(summary, indent=2)
            prompt = f"""You are a senior data analyst generating a professional business report.
Analyze this CSV data and return ONLY valid JSON (no markdown, no code blocks).

Dataset Summary:
{summary_text}

STRICT INSTRUCTIONS:
1. Use ONLY the computed statistics provided.
2. Do NOT invent category counts or values.
3. If stating a category has the most products, verify using actual category counts.
4. Do NOT list only averages in the Executive Summary.
5. Avoid generic statements.
6. Interpret patterns instead of just ranking values.

STYLE REFERENCE (Use this tone):
- Executive Summary: "The dataset exhibits full-range distribution across sales (0–99), indicating broad variability. While average inventory appears proportionate, the wide spread suggests uneven dynamics requiring targeted management."
- Key Trends: "Preliminary analysis suggests variability in the relationship between pricing and sales. While higher discounts may coincide with stronger sales, a formal correlation analysis is recommended to validate this relationship."

Return JSON with this exact structure:
{{
  "summary": "High-level executive summary following the Style Reference above. Focus on distribution and variability.",
  "key_trends": ["Trend 1 (follow Style Reference)", "Trend 2", "Trend 3"],
  "outliers": ["List specific outliers with values"],
  "risks": ["Potential risks based on data (e.g. low stock)"],
  "recommendations": ["Actionable business recommendations"]
}}

Rules:
- If category counts are tied, clearly state they are tied.
- Do not fabricate product counts.
- Base all claims strictly on the dataset values provided.
- If no outliers/risks found, return empty arrays."""

            # Call Groq with timeout and token limit
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are a data analyst. Return only valid JSON, no markdown formatting."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                timeout=30
            )
            
            raw_content = response.choices[0].message.content.strip()
            
            # Parse JSON response
            try:
                # Remove markdown code blocks if present
                if raw_content.startswith("```"):
                    lines = raw_content.split("\n")
                    raw_content = "\n".join(lines[1:-1]) if len(lines) > 2 else raw_content
                    raw_content = raw_content.replace("```json", "").replace("```", "").strip()
                
                insights_data = json.loads(raw_content)
                
                # Validate required fields
                required_fields = ["summary", "key_trends", "outliers", "risks", "recommendations"]
                for field in required_fields:
                    if field not in insights_data:
                        insights_data[field] = [] if field != "summary" else "No summary available"
                
                # Validate types
                if not isinstance(insights_data["summary"], str):
                    insights_data["summary"] = str(insights_data["summary"])
                
                for field in ["key_trends", "outliers", "risks", "recommendations"]:
                    if not isinstance(insights_data[field], list):
                        insights_data[field] = []
                
                return True, insights_data, ""
                
            except json.JSONDecodeError as je:
                # Return fallback structured data
                return False, {}, f"LLM returned invalid JSON: {str(je)}"
            
        except Exception as e:
            error_msg = f"LLM API error: {str(e)}"
            return False, {}, error_msg
    
    def answer_with_context(self, question: str, context: str) -> Tuple[bool, str, str]:
        """Answer question using provided context string.
        
        Args:
            question: User's question
            context: Pre-formatted context string containing summary, history, etc.
            
        Returns:
            Tuple of (success: bool, answer: str, error_message: str)
        """
        if not self.client:
            return False, "", "LLM service not initialized"
        
        try:
            prompt = f"""Using the provided dataset context, answer the user's question.

Context:
{context}

User Question: {question}

Instructions:
- Answer ONLY using the provided information.
- Do not fabricate columns or values.
- If the answer cannot be determined from the context, state "Insufficient data in the dataset to answer this question."
- Keep the answer professional and concise.
"""

            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are a helpful data analyst. Answer strictly based on the provided data context."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                timeout=30
            )
            
            answer = response.choices[0].message.content
            return True, answer, ""
            
        except Exception as e:
            error_msg = f"LLM service error: {str(e)}"
            return False, "", error_msg

    def answer_question(self, summary: Dict[str, Any], insights: str, question: str) -> Tuple[bool, str, str]:
        """Legacy method for answering questions (kept for backward compatibility if needed)."""
        # ... logic ...
        return self.answer_with_context(question, f"Summary: {json.dumps(summary)}\nInsights: {insights}")
    
    def health_check(self) -> Tuple[bool, int, str]:
        """Perform health check on LLM service.
        
        Sends minimal test prompt: "Respond with OK only."
        Times out after 5 seconds.
        
        Returns:
            Tuple of (is_healthy: bool, response_time_ms: int, error_message: str)
        """
        if not self.client:
            return False, 0, "LLM client not initialized"
        
        try:
            start_time = time.time()
            
            response = self.client.chat.completions.create(
                model="mixtral-8x7b-32768",
                messages=[
                    {"role": "user", "content": "Respond with OK only."}
                ],
                max_tokens=5,
                timeout=5  # 5-second timeout
            )
            
            end_time = time.time()
            response_time_ms = int((end_time - start_time) * 1000)
            
            # Check if response is valid
            if response.choices and len(response.choices) > 0:
                return True, response_time_ms, ""
            else:
                return False, response_time_ms, "Invalid response from LLM"
                
        except Exception as e:
            # Sanitize error message - don't expose API keys
            return False, 0, "LLM API error (check credentials)"
        except Exception as e:
            return False, 0, "LLM connection timeout or error"
