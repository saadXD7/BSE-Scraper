import pymupdf  # Updated to the modern PyMuPDF import
from abc import ABC, abstractmethod
import os
from groq import Groq

# ==========================================
# 1. THE LLM FACTORY PATTERN (Provider-Agnostic)
# ==========================================
class LLMProvider(ABC):
    """Abstract base class dictating how all LLMs must behave."""
    @abstractmethod
    def ask(self, context: str, question: str) -> str:
        pass

class MockLLM(LLMProvider):
    """A local mock provider to test the engine without needing API keys."""
    def ask(self, context: str, question: str) -> str:
        return f"[Mock LLM] I successfully read {len(context)} characters from the PDF. You asked: '{question}'"

class GroqLLM(LLMProvider):
    """Concrete implementation for Groq API."""
    def __init__(self, api_key: str):
        self.client = Groq(api_key=api_key)
        
    def ask(self, context: str, question: str) -> str:
        prompt = f"Using the following document context, answer the question.\n\nContext: {context}\n\nQuestion: {question}"
        
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="openai/gpt-oss-20b", 
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            return f"API Error: {e}"

class LLMFactory:
    """The Factory that instantiates the correct LLM based on configuration."""
    @staticmethod
    def get_provider(provider_type: str, api_key: str = None) -> LLMProvider:
        if provider_type.lower() == "mock":
            return MockLLM()
        elif provider_type.lower() == "groq":
            if not api_key or api_key == "your_api_key_here":
                raise ValueError("A valid Groq API key is required to use the Groq provider.")
            return GroqLLM(api_key)
        else:
            raise ValueError(f"Unsupported LLM provider: {provider_type}")

# ==========================================
# 2. THE PyMuPDF EXTRACTION ENGINE
# ==========================================
class PDFKnowledgeEngine:
    def __init__(self, pdf_path: str, llm_provider: LLMProvider):
        self.pdf_path = pdf_path
        self.llm = llm_provider
        self.context = self._extract_text()

    def _extract_text(self) -> str:
        """Extracts raw text from the PDF using PyMuPDF."""
        try:
            doc = pymupdf.open(self.pdf_path)
            text = ""
            for page in doc:
                text += page.get_text("text") + "\n"
            return text.strip()
        except Exception as e:
            return f"Error reading PDF: {e}"

    def query(self, question: str) -> str:
        """Sends the extracted PDF context and the user query to the LLM."""
        if not self.context:
            return "No content extracted from PDF."
        
        # Truncate context to avoid token limits on standard tiers
        snippet = self.context[:4000] 
        return self.llm.ask(snippet, question)

# ==========================================
# 3. EXECUTION
# ==========================================
if __name__ == "__main__":
    # 1. Auto-generate a dummy Annual Report PDF so the script works instantly
    test_pdf = "annual_report.pdf"
    if not os.path.exists(test_pdf):
        doc = pymupdf.open()
        page = doc.new_page()
        page.insert_text((50, 50), "BSE Annual Report 2024: Overall market revenue increased by 15% due to AI automation.")
        doc.save(test_pdf)
    
    # 2. Initialize the architecture using the Factory Pattern
    GROQ_API_KEY = "your_api_key_here" # Evaluator: Please paste your Groq API key here to test
    
    # Instantiate the provider
    provider = LLMFactory.get_provider("groq", api_key=GROQ_API_KEY)
    
    # 3. Run the Engine
    engine = PDFKnowledgeEngine(test_pdf, provider)
    
    print("\n--- 📄 PDF Knowledge Engine Initialized ---")
    print(f"Target File: {test_pdf}")
    print("-------------------------------------------")
    
    question = "What drove the revenue increase in 2024?"
    print(f"Q: {question}")
    
    answer = engine.query(question)
    print(f"A: {answer}\n")