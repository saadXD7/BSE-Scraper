# Technical Assessment: Market Scraper & PDF Knowledge Engine

This monorepo contains two backend projects demonstrating real-time data extraction, API development, and Large Language Model (LLM) integration using modern Python design patterns.

## 📁 Repository Structure

* **`Project1_Market_Scraper/`**: A real-time web scraper built with FastAPI and Playwright.
* **`Project2_PDF_Engine/`**: An LLM-powered document QA engine using PyMuPDF and the Groq API.

---

## 🚀 Project 1: Live Market Scraper

A high-performance web scraping API that extracts real-time market data and serves it via a Jinja2 frontend.

* **Tech Stack:** FastAPI, Playwright, Uvicorn, Jinja2
* **Features:**
  * Asynchronous browser automation for dynamic content extraction.
  * REST API endpoints for seamless data consumption.
  * Modular HTML templating for immediate data visualization.

## 🧠 Project 2: PDF Knowledge Engine

An intelligent document extraction tool that parses unstructured PDF data and queries an LLM to answer contextual questions.

* **Tech Stack:** Python, PyMuPDF, Groq API (GPT-OSS-20b)
* **Architecture:** Implements the **Factory Design Pattern** to ensure the LLM provider is decoupled and easily interchangeable (e.g., swapping between Groq, OpenAI, or local Mock instances) without altering the core extraction logic.
* **Features:**
  * High-speed text extraction using modern `pymupdf`.
  * Context-aware prompt engineering to bypass token limits.
  * Built-in dummy data generation for immediate local testing.

---

## ⚙️ Local Setup & Execution

### 1. Install Dependencies
Ensure you have Python installed, then run:
```bash
pip install -r requirements.txt