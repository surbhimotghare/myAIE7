# Evol-Instruct Synthetic Data Generation App

<p align="center">
  <img src="https://img.shields.io/badge/FastAPI-0.116.1-009688?style=for-the-badge&logo=fastapi" alt="FastAPI">
  <img src="https://img.shields.io/badge/LangGraph-0.5.4-FF6B6B?style=for-the-badge&logo=python" alt="LangGraph">
  <img src="https://img.shields.io/badge/OpenAI-GPT--4o--mini-412991?style=for-the-badge&logo=openai" alt="OpenAI">
  <img src="https://img.shields.io/badge/React-Modern%20UI-61DAFB?style=for-the-badge&logo=react" alt="Modern UI">
</p>

## 🚀 Overview

A sophisticated synthetic data generation application built with **Evol-Instruct methodology** from the WizardLM paper. This app uses LangGraph to orchestrate complex AI workflows that generate high-quality question-answer pairs through multiple evolution types.

### ✨ Key Features

- **🎯 Evol-Instruct Pipeline**: Advanced synthetic data generation using LangGraph
- **🌐 Modern Web Interface**: LinkedIn-inspired, professional UI with real-time progress
- **📁 Multi-File Support**: Upload and process `.txt`, `.pdf`, and `.csv` files
- **🔑 OpenAI Integration**: User-configurable API keys with secure storage
- **📊 Real-Time Progress**: Server-Sent Events (SSE) for live progress updates
- **📚 Comprehensive API**: Full REST API with interactive documentation
- **⚡ FastAPI Backend**: High-performance async API server
- **🎨 Responsive Design**: Works seamlessly on desktop and mobile

## 🏗️ Architecture

### System Architecture

![System Architecture Diagram](https://github.com/user-attachments/assets/your-image-url-here)

*Clean, organized view of the Evol-Instruct synthetic data generation pipeline showing data flow from frontend to output generation*

```mermaid
graph TB
    subgraph "Frontend Layer"
        UI[Modern Web UI<br/>LinkedIn-inspired Design]
        FileUpload[File Upload<br/>Drag & Drop Interface]
        Progress[Real-time Progress<br/>SSE Updates]
        Results[Results Display<br/>Tabbed Interface]
    end

    subgraph "API Layer"
        FastAPI[FastAPI Server<br/>Port 8000]
        Auth[OpenAI Key<br/>Authentication]
        SSE[Server-Sent Events<br/>Progress Streaming]
    end

    subgraph "Processing Layer"
        LangGraph[LangGraph Workflow<br/>Evol-Instruct Pipeline]
        LLM[OpenAI GPT-4o-mini<br/>Question Generation]
        Embeddings[OpenAI Embeddings<br/>Context Extraction]
    end

    subgraph "File Processing"
        PDF[PDF.js<br/>Client-side PDF parsing]
        CSV[Papa Parse<br/>CSV processing]
        TXT[Text processing<br/>Direct content]
    end

    subgraph "Evolution Pipeline"
        Seeds[Seed Questions<br/>Initial generation]
        Simple[Simple Evolution<br/>Enhanced detail]
        Multi[Multi-Context<br/>Cross-document]
        Reasoning[Reasoning Evolution<br/>Logical analysis]
    end

    subgraph "Output Generation"
        Questions[Evolved Questions<br/>3 types × 3 each]
        Answers[Generated Answers<br/>Comprehensive responses]
        Contexts[Relevant Contexts<br/>Document sections]
    end

    %% User Flow
    UI --> FileUpload
    FileUpload --> PDF
    FileUpload --> CSV
    FileUpload --> TXT
    
    %% API Flow
    PDF --> FastAPI
    CSV --> FastAPI
    TXT --> FastAPI
    
    %% Processing Flow
    FastAPI --> LangGraph
    LangGraph --> Seeds
    Seeds --> Simple
    Simple --> Multi
    Multi --> Reasoning
    
    %% AI Integration
    LangGraph --> LLM
    LangGraph --> Embeddings
    
    %% Output Flow
    Reasoning --> Questions
    Reasoning --> Answers
    Reasoning --> Contexts
    
    %% Progress Updates
    LangGraph --> SSE
    SSE --> Progress
    
    %% Results Display
    Questions --> Results
    Answers --> Results
    Contexts --> Results
    
    %% Authentication
    Auth --> LLM
    Auth --> Embeddings

    %% Styling
    classDef frontend fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef api fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef processing fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px
    classDef files fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef evolution fill:#fce4ec,stroke:#880e4f,stroke-width:2px
    classDef output fill:#f1f8e9,stroke:#33691e,stroke-width:2px

    class UI,FileUpload,Progress,Results frontend
    class FastAPI,Auth,SSE api
    class LangGraph,LLM,Embeddings processing
    class PDF,CSV,TXT files
    class Seeds,Simple,Multi,Reasoning evolution
    class Questions,Answers,Contexts output
```

### Evolution Types

1. **Simple Evolution** 🎯
   - Enhances questions with more detail and complexity
   - Maintains core meaning while adding sophistication

2. **Multi-Context Evolution** 🔗
   - Creates questions spanning multiple documents
   - Enables comprehensive cross-document analysis

3. **Reasoning Evolution** 🧠
   - Generates questions requiring logical reasoning
   - Promotes analytical thinking and problem-solving

### Tech Stack

- **Backend**: FastAPI + Uvicorn + LangGraph + LangChain
- **Frontend**: Modern HTML/CSS/JavaScript with Font Awesome
- **AI**: OpenAI GPT-4o-mini for question generation
- **File Processing**: PDF.js + Papa Parse for client-side parsing
- **Deployment**: Vercel-ready configuration

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- OpenAI API key (optional - server has default key)

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd s07-bonus-evol-instruct-app
   ```