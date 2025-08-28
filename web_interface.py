from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import json
import os
from advanced_workflow import AdvancedWorkflowEngine, PersonaConfig

app = FastAPI(title="Persona Workflow System")

# Mount static files and templates
templates = Jinja2Templates(directory="templates")

# Initialize workflow engine
engine = AdvancedWorkflowEngine()

# Available personas
AVAILABLE_PERSONAS = [
    "Risk Assessment",
    "Claims Analysis", 
    "Compliance Review",
    "Financial Analysis",
    "Operational Excellence",
    "Summary Only"
]

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "personas": AVAILABLE_PERSONAS
    })

@app.post("/execute-workflow")
async def execute_workflow(
    input_text: str = Form(...),
    selected_personas: str = Form(...)
):
    """Execute workflow with selected personas"""
    try:
        # Parse selected personas
        persona_sequence = json.loads(selected_personas)
        
        # Execute workflow
        results = engine.execute_workflow(input_text, persona_sequence)
        
        # Convert results to serializable format
        serializable_results = {}
        for persona_name, output in results.items():
            serializable_results[persona_name] = {
                'analysis': output.analysis,
                'confidence': output.confidence,
                'key_findings': output.key_findings,
                'recommendations': output.recommendations
            }
        
        return {
            "success": True,
            "results": serializable_results,
            "summary": engine.get_workflow_summary(results)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.post("/chat")
async def chat_with_results(
    message: str = Form(...),
    workflow_results: str = Form(...)
):
    """Chat with workflow results"""
    try:
        # Parse workflow results
        results_data = json.loads(workflow_results)
        
        # Convert back to PersonaOutput objects
        from advanced_workflow import PersonaOutput
        results = {}
        for persona_name, data in results_data.items():
            results[persona_name] = PersonaOutput(**data)
        
        # Get chat response
        response = engine.chat_with_output(message, results)
        
        return {
            "success": True,
            "response": response
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

# Create templates directory and HTML file
os.makedirs("templates", exist_ok=True)

html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Persona Workflow System</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 30px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
            color: #555;
        }
        textarea, select {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 14px;
        }
        textarea {
            height: 120px;
            resize: vertical;
        }
        .persona-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 10px;
            margin-top: 10px;
        }
        .persona-checkbox {
            display: flex;
            align-items: center;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            background: #f9f9f9;
        }
        .persona-checkbox input {
            margin-right: 10px;
        }
        button {
            background: #007bff;
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            margin-right: 10px;
        }
        button:hover {
            background: #0056b3;
        }
        button:disabled {
            background: #ccc;
            cursor: not-allowed;
        }
        .results {
            margin-top: 30px;
        }
        .persona-result {
            background: #f8f9fa;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 5px;
            border-left: 4px solid #007bff;
        }
        .persona-result h3 {
            margin-top: 0;
            color: #007bff;
        }
        .confidence {
            color: #28a745;
            font-weight: bold;
        }
        .chat-section {
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
        }
        .chat-messages {
            height: 300px;
            overflow-y: auto;
            border: 1px solid #ddd;
            padding: 15px;
            background: #f9f9f9;
            border-radius: 5px;
            margin-bottom: 15px;
        }
        .message {
            margin-bottom: 10px;
            padding: 10px;
            border-radius: 5px;
        }
        .user-message {
            background: #007bff;
            color: white;
            margin-left: 20%;
        }
        .ai-message {
            background: #e9ecef;
            color: #333;
            margin-right: 20%;
        }
        .loading {
            text-align: center;
            color: #666;
            font-style: italic;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 Persona Workflow System</h1>
        
        <form id="workflowForm">
            <div class="form-group">
                <label for="inputText">Input Text:</label>
                <textarea id="inputText" name="inputText" placeholder="Enter your text here..." required></textarea>
            </div>
            
            <div class="form-group">
                <label>Select Personas (in order):</label>
                <div class="persona-grid">
                    {% for persona in personas %}
                    <div class="persona-checkbox">
                        <input type="checkbox" id="{{ persona }}" value="{{ persona }}" name="personas">
                        <label for="{{ persona }}">{{ persona }}</label>
                    </div>
                    {% endfor %}
                </div>
            </div>
            
            <button type="submit" id="executeBtn">Execute Workflow</button>
        </form>
    </div>
    
    <div class="container results" id="results" style="display: none;">
        <h2>Workflow Results</h2>
        <div id="resultsContent"></div>
        
        <div class="chat-section">
            <h3>💬 Chat with Results</h3>
            <div class="chat-messages" id="chatMessages"></div>
            <div class="form-group">
                <input type="text" id="chatInput" placeholder="Ask a question about the results..." style="width: 70%;">
                <button onclick="sendChatMessage()" id="chatBtn">Send</button>
            </div>
        </div>
    </div>

    <script>
        let workflowResults = null;
        
        document.getElementById('workflowForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const inputText = document.getElementById('inputText').value;
            const selectedPersonas = Array.from(document.querySelectorAll('input[name="personas"]:checked'))
                .map(cb => cb.value);
            
            if (selectedPersonas.length === 0) {
                alert('Please select at least one persona');
                return;
            }
            
            // Show loading
            document.getElementById('executeBtn').disabled = true;
            document.getElementById('executeBtn').textContent = 'Processing...';
            
            try {
                const formData = new FormData();
                formData.append('input_text', inputText);
                formData.append('selected_personas', JSON.stringify(selectedPersonas));
                
                const response = await fetch('/execute-workflow', {
                    method: 'POST',
                    body: formData
                });
                
                const result = await response.json();
                
                if (result.success) {
                    workflowResults = result.results;
                    displayResults(result);
                    document.getElementById('results').style.display = 'block';
                } else {
                    alert('Error: ' + result.error);
                }
            } catch (error) {
                alert('Error: ' + error.message);
            } finally {
                document.getElementById('executeBtn').disabled = false;
                document.getElementById('executeBtn').textContent = 'Execute Workflow';
            }
        });
        
        function displayResults(result) {
            const resultsContent = document.getElementById('resultsContent');
            let html = '';
            
            for (const [persona, output] of Object.entries(result.results)) {
                html += `
                    <div class="persona-result">
                        <h3>${persona}</h3>
                        <p class="confidence">Confidence: ${(output.confidence * 100).toFixed(1)}%</p>
                        <h4>Analysis:</h4>
                        <p>${output.analysis}</p>
                        <h4>Key Findings:</h4>
                        <ul>
                            ${output.key_findings.map(finding => `<li>${finding}</li>`).join('')}
                        </ul>
                        ${output.recommendations.length > 0 ? `
                            <h4>Recommendations:</h4>
                            <ul>
                                ${output.recommendations.map(rec => `<li>${rec}</li>`).join('')}
                            </ul>
                        ` : ''}
                    </div>
                `;
            }
            
            resultsContent.innerHTML = html;
        }
        
        async function sendChatMessage() {
            const message = document.getElementById('chatInput').value.trim();
            if (!message || !workflowResults) return;
            
            // Add user message to chat
            addMessage(message, 'user');
            document.getElementById('chatInput').value = '';
            
            // Disable chat button
            document.getElementById('chatBtn').disabled = true;
            document.getElementById('chatBtn').textContent = 'Sending...';
            
            try {
                const formData = new FormData();
                formData.append('message', message);
                formData.append('workflow_results', JSON.stringify(workflowResults));
                
                const response = await fetch('/chat', {
                    method: 'POST',
                    body: formData
                });
                
                const result = await response.json();
                
                if (result.success) {
                    addMessage(result.response, 'ai');
                } else {
                    addMessage('Error: ' + result.error, 'ai');
                }
            } catch (error) {
                addMessage('Error: ' + error.message, 'ai');
            } finally {
                document.getElementById('chatBtn').disabled = false;
                document.getElementById('chatBtn').textContent = 'Send';
            }
        }
        
        function addMessage(text, sender) {
            const chatMessages = document.getElementById('chatMessages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${sender}-message`;
            messageDiv.textContent = text;
            chatMessages.appendChild(messageDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
        
        // Allow Enter key to send chat message
        document.getElementById('chatInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                sendChatMessage();
            }
        });
    </script>
</body>
</html>
"""

with open("templates/index.html", "w") as f:
    f.write(html_template)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)