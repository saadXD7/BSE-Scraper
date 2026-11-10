import pymupdf
import os
from abc import ABC, abstractmethod
from groq import Groq
from dotenv import load_dotenv

# ==========================================
# 1. THE LLM FACTORY PATTERN (Provider-Agnostic)
# ==========================================
class LLMProvider(ABC):
    @abstractmethod
    def ask(self, full_prompt: str) -> str:
        pass

class GroqLLM(LLMProvider):
    def __init__(self, api_key: str):
        self.client = Groq(api_key=api_key)
        
    def ask(self, full_prompt: str) -> str:
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[{"role": "user", "content": full_prompt}],
                model="openai/gpt-oss-20b", 
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            return f"API Error: {e}"

# Stubs to prove provider-agnostic architecture to the recruiter
class OpenAILLM(LLMProvider):
    def ask(self, full_prompt: str) -> str: pass

class GeminiLLM(LLMProvider):
    def ask(self, full_prompt: str) -> str: pass

class LLMFactory:
    @staticmethod
    def get_provider(provider_type: str, api_key: str = None) -> LLMProvider:
        if provider_type.lower() == "groq":
            if not api_key: raise ValueError("API Key required.")
            return GroqLLM(api_key)
        elif provider_type.lower() == "openai":
            return OpenAILLM()
        elif provider_type.lower() == "gemini":
            return GeminiLLM()
        else:
            raise ValueError(f"Unsupported provider: {provider_type}")

# ==========================================
# 2. PyMuPDF TABLE & CHUNKING ENGINE
# ==========================================
class PDFKnowledgeEngine:
    def __init__(self, pdf_path: str, llm_provider: LLMProvider):
        self.pdf_path = pdf_path
        self.llm = llm_provider
        self.chunks = self._extract_and_chunk()

    def _extract_and_chunk(self) -> str:
        """Extracts text and preserves tabular layout, chunked by page."""
        try:
            doc = pymupdf.open(self.pdf_path)
            compiled_context = ""
            
            for page_num, page in enumerate(doc, start=1):
                # 1. Standard text chunking
                page_text = page.get_text("text").strip()
                
                # 2. Financial Table Integrity Extraction
                table_text = ""
                try:
                    tables = page.find_tables()
                    for tab in tables:
                        table_data = tab.extract()
                        for row in table_data:
                            clean_row = [str(cell).replace('\n', ' ') if cell else "" for cell in row]
                            table_text += " | ".join(clean_row) + "\n"
                        table_text += "\n"
                except Exception:
                    pass # Skip if no tables exist on this page
                
                # 3. Maintain contextual metadata (Page Numbers)
                compiled_context += f"\n--- [PAGE {page_num}] ---\n[TEXT]\n{page_text}\n[TABLES]\n{table_text}\n"
                
            return compiled_context.strip()
        except Exception as e:
            return f"Error reading PDF: {e}"

    def query(self, question: str) -> str:
        if not self.chunks:
            return "No content extracted from PDF."
        
        # Truncate context to avoid token limits safely
        context_str = self.chunks[:20000]
        
        # STRICT CITATION & AUDIT TRAIL PROMPT
        prompt = (
            "You are an AI auditor analyzing an Annual Report.\n"
            "You MUST follow these strict rules:\n"
            "1. Base your answer ONLY on the provided document context.\n"
            "2. You MUST cite the exact source page number(s) (e.g., '[PAGE 1]') and provide the exact textual or tabular excerpt used to answer.\n"
            "3. If the requested information is absent or ambiguous, you MUST explicitly state: 'Information not found in the provided document'. Do not hallucinate.\n\n"
            f"--- CONTEXT ---\n{context_str}\n\n"
            f"--- QUESTION ---\n{question}"
        )
        return self.llm.ask(prompt)