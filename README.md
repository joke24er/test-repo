# Document Analysis Workflow System

A comprehensive agentic workflow system for document analysis with selectable personas, built using LangGraph, LangChain, and FastAPI.

## 🚀 Features

- **Selectable Personas**: Choose from predefined personas or create custom ones for different types of analysis
- **Workflow Creation**: Build custom workflows by combining multiple personas
- **LangGraph Integration**: Uses LangGraph for orchestrated workflow execution
- **Agent vs Prompt Decision**: Automatically determines whether to use agents or prompts based on complexity
- **Interactive Chat**: Chat with your analysis results for deeper insights
- **REST API**: Full REST API for integration with other systems
- **Web Interface**: Streamlit-based frontend for easy interaction

## 🏗️ Architecture

### Core Components

1. **Persona Manager** (`src/personas.py`)
   - Manages predefined and custom personas
   - Determines persona type (Agent vs Prompt)
   - Handles persona creation and deletion

2. **Workflow Engine** (`src/workflow_engine.py`)
   - LangGraph-based workflow execution
   - Orchestrates persona analysis
   - Handles both simple prompts and complex agents

3. **Chat System** (`src/chat_system.py`)
   - Interactive chat with analysis results
   - Conversation memory and history
   - Analysis summaries and comparisons

4. **API Layer** (`src/api.py`)
   - FastAPI-based REST API
   - Complete CRUD operations
   - File upload and processing

5. **Frontend** (`frontend/app.py`)
   - Streamlit-based web interface
   - Intuitive workflow creation
   - Real-time analysis and chat

## 📋 Predefined Personas

### Agent Personas (Complex Analysis)
- **Contract Review Specialist**: Legal contract analysis with risk assessment
- **Financial Analyst**: Financial statement analysis with ratios and trends
- **Risk Management Specialist**: Comprehensive risk evaluation and mitigation
- **Market Intelligence Analyst**: Market analysis and competitive intelligence

### Prompt Personas (Simple Analysis)
- **Technical Reviewer**: Technical document review and feasibility
- **Compliance Officer**: Regulatory compliance and governance analysis

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd document-analysis-workflow
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your OpenAI API key
   ```

4. **Run the API server**
   ```bash
   python app.py
   ```

5. **Run the frontend** (in a new terminal)
   ```bash
   cd frontend
   streamlit run app.py
   ```

## 🚀 Quick Start

1. **Start the system**
   - API will be available at `http://localhost:8000`
   - Frontend will be available at `http://localhost:8501`

2. **Create a workflow**
   - Go to the "Workflows" page
   - Select personas for your analysis
   - Save the workflow

3. **Run analysis**
   - Upload a document or paste content
   - Select your workflow
   - Execute the analysis

4. **Chat with results**
   - Go to the "Chat" page
   - Select your analysis
   - Ask questions about the results

## 📚 API Documentation

### Personas
- `GET /personas` - Get all personas
- `GET /personas/{id}` - Get specific persona
- `POST /personas` - Create custom persona
- `DELETE /personas/{id}` - Delete custom persona

### Workflows
- `GET /workflows` - Get all workflows
- `GET /workflows/{id}` - Get specific workflow
- `POST /workflows` - Create new workflow

### Analysis
- `POST /analysis/execute` - Execute workflow with document
- `GET /analysis/{id}` - Get analysis result
- `GET /analysis/user/{user_id}` - Get user's analyses

### Chat
- `POST /chat/send` - Send chat message
- `GET /chat/{analysis_id}/history` - Get chat history
- `DELETE /chat/{analysis_id}/history` - Clear chat history
- `GET /chat/{analysis_id}/summary` - Get analysis summary

## 🔧 Configuration

### Environment Variables
```bash
OPENAI_API_KEY=your_openai_api_key
HOST=0.0.0.0
PORT=8000
DEBUG=False
```

### Persona Types

The system automatically determines whether to use an **Agent** or **Prompt** based on complexity:

**Agent Personas** (Complex Analysis):
- Contract Review: Multi-step legal analysis
- Financial Analysis: Complex calculations and ratios
- Risk Management: Comprehensive risk matrix
- Market Intelligence: Strategic analysis

**Prompt Personas** (Simple Analysis):
- Technical Review: Straightforward technical assessment
- Compliance Review: Regulatory compliance check

## 📖 Usage Examples

### Creating a Custom Persona
```python
from src.personas import persona_manager

persona = persona_manager.create_custom_persona(
    name="Custom Analyst",
    description="Specialized analysis for specific domain",
    prompt_template="Analyze this document for {specific_criteria}...",
    analysis_focus=["custom_analysis", "domain_specific"],
    created_by="user123"
)
```

### Executing a Workflow
```python
from src.workflow_engine import workflow_engine
from src.models import DocumentInput

document = DocumentInput(
    content="Your document content here...",
    filename="document.txt",
    file_type="text/plain"
)

result = workflow_engine.execute_workflow(
    workflow_id="workflow_id",
    document=document,
    user_id="user123"
)
```

### Chatting with Analysis
```python
from src.chat_system import chat_system
from src.models import ChatRequest

chat_request = ChatRequest(
    analysis_id="analysis_id",
    message="What are the key risks identified?",
    user_id="user123"
)

response = chat_system.send_message(chat_request)
```

## 🧪 Testing

### Sample Documents
The `examples/` directory contains sample documents for testing:
- `sample_contract.txt` - Service agreement for contract analysis
- `sample_financial_report.txt` - Financial report for financial analysis

### Running Tests
```bash
# Test the API
curl http://localhost:8000/health

# Test persona creation
curl -X POST http://localhost:8000/personas \
  -F "name=Test Persona" \
  -F "description=Test description" \
  -F "prompt_template=Analyze this document..." \
  -F "analysis_focus=[\"test\"]" \
  -F "created_by=test_user"
```

## 🔒 Security Considerations

- API keys are stored in environment variables
- No external web search or API calls (firewall-compliant)
- Input validation on all endpoints
- CORS configured for web interface

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
1. Check the API documentation at `http://localhost:8000/docs`
2. Review the example documents in the `examples/` directory
3. Open an issue on GitHub

## 🔮 Future Enhancements

- Database persistence for workflows and analyses
- User authentication and authorization
- Advanced document parsing (PDF, DOCX)
- Export functionality (PDF, Excel)
- Integration with external document management systems
- Advanced analytics and reporting
- Multi-language support
