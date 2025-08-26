import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime
import uuid

# Configuration
API_BASE_URL = "http://localhost:8000"

def main():
    st.set_page_config(
        page_title="Document Analysis Workflow",
        page_icon="📄",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("📄 Document Analysis Workflow System")
    st.markdown("Create custom workflows with selectable personas for comprehensive document analysis")
    
    # Sidebar navigation
    page = st.sidebar.selectbox(
        "Navigation",
        ["🏠 Dashboard", "👥 Personas", "⚙️ Workflows", "📊 Analysis", "💬 Chat", "📁 Upload"]
    )
    
    if page == "🏠 Dashboard":
        show_dashboard()
    elif page == "👥 Personas":
        show_personas()
    elif page == "⚙️ Workflows":
        show_workflows()
    elif page == "📊 Analysis":
        show_analysis()
    elif page == "💬 Chat":
        show_chat()
    elif page == "📁 Upload":
        show_upload()

def show_dashboard():
    """Dashboard page"""
    st.header("Dashboard")
    
    # Get system status
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            st.success("✅ API is running")
        else:
            st.error("❌ API is not responding")
    except:
        st.error("❌ Cannot connect to API")
    
    # Quick stats
    col1, col2, col3, col4 = st.columns(4)
    
    try:
        # Get personas count
        personas_response = requests.get(f"{API_BASE_URL}/personas")
        if personas_response.status_code == 200:
            personas = personas_response.json()
            col1.metric("Available Personas", len(personas))
        
        # Get workflows count
        workflows_response = requests.get(f"{API_BASE_URL}/workflows")
        if workflows_response.status_code == 200:
            workflows = workflows_response.json()
            col2.metric("Created Workflows", len(workflows))
        
        # Placeholder metrics
        col3.metric("Analyses Run", "0")
        col4.metric("Active Chats", "0")
        
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
    
    # Recent activity
    st.subheader("Recent Activity")
    st.info("No recent activity to display")

def show_personas():
    """Personas management page"""
    st.header("👥 Personas Management")
    
    tab1, tab2 = st.tabs(["Available Personas", "Create Custom Persona"])
    
    with tab1:
        st.subheader("Available Personas")
        
        try:
            response = requests.get(f"{API_BASE_URL}/personas")
            if response.status_code == 200:
                personas = response.json()
                
                for persona in personas:
                    with st.expander(f"{persona['name']} ({persona['persona_type']})"):
                        st.write(f"**Description:** {persona['description']}")
                        st.write(f"**Focus Areas:** {', '.join(persona['analysis_focus'])}")
                        st.write(f"**Type:** {persona['persona_type']}")
                        if persona.get('is_custom'):
                            st.write("**Custom Persona**")
                        
                        # Show prompt template in a code block
                        st.code(persona['prompt_template'], language="text")
            else:
                st.error("Failed to fetch personas")
        except Exception as e:
            st.error(f"Error: {str(e)}")
    
    with tab2:
        st.subheader("Create Custom Persona")
        
        with st.form("create_persona"):
            name = st.text_input("Persona Name")
            description = st.text_area("Description")
            prompt_template = st.text_area("Prompt Template", 
                                         placeholder="Enter the prompt template for this persona...")
            
            # Analysis focus areas
            focus_areas = st.multiselect(
                "Analysis Focus Areas",
                ["legal_terms", "risk_assessment", "compliance", "financial_ratios", 
                 "trends", "cash_flow", "technical_specs", "market_analysis", "governance"],
                default=[]
            )
            
            created_by = st.text_input("Created By", value="user")
            
            submitted = st.form_submit_button("Create Persona")
            
            if submitted:
                if name and description and prompt_template:
                    try:
                        data = {
                            "name": name,
                            "description": description,
                            "prompt_template": prompt_template,
                            "analysis_focus": json.dumps(focus_areas),
                            "created_by": created_by
                        }
                        
                        response = requests.post(f"{API_BASE_URL}/personas", data=data)
                        if response.status_code == 200:
                            st.success("Persona created successfully!")
                            st.rerun()
                        else:
                            st.error(f"Failed to create persona: {response.text}")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
                else:
                    st.error("Please fill in all required fields")

def show_workflows():
    """Workflows management page"""
    st.header("⚙️ Workflows Management")
    
    tab1, tab2 = st.tabs(["Existing Workflows", "Create New Workflow"])
    
    with tab1:
        st.subheader("Existing Workflows")
        
        try:
            response = requests.get(f"{API_BASE_URL}/workflows")
            if response.status_code == 200:
                workflows = response.json()
                
                if not workflows:
                    st.info("No workflows created yet. Create your first workflow!")
                else:
                    for workflow in workflows:
                        with st.expander(f"{workflow['name']} - {workflow['description']}"):
                            st.write(f"**Created by:** {workflow['created_by']}")
                            st.write(f"**Created:** {workflow['created_at']}")
                            st.write(f"**Personas:** {len(workflow['personas'])}")
                            
                            # Show personas in this workflow
                            for persona in workflow['personas']:
                                st.write(f"- {persona['name']} ({persona['persona_type']})")
            else:
                st.error("Failed to fetch workflows")
        except Exception as e:
            st.error(f"Error: {str(e)}")
    
    with tab2:
        st.subheader("Create New Workflow")
        
        # Get available personas
        try:
            personas_response = requests.get(f"{API_BASE_URL}/personas")
            if personas_response.status_code == 200:
                personas = personas_response.json()
                
                with st.form("create_workflow"):
                    name = st.text_input("Workflow Name")
                    description = st.text_area("Description")
                    
                    # Persona selection
                    st.write("Select Personas for this Workflow:")
                    selected_personas = []
                    
                    for persona in personas:
                        if st.checkbox(f"{persona['name']} - {persona['description']}", key=persona['id']):
                            selected_personas.append(persona['id'])
                    
                    created_by = st.text_input("Created By", value="user")
                    
                    submitted = st.form_submit_button("Create Workflow")
                    
                    if submitted:
                        if name and description and selected_personas:
                            try:
                                data = {
                                    "name": name,
                                    "description": description,
                                    "persona_ids": json.dumps(selected_personas),
                                    "created_by": created_by
                                }
                                
                                response = requests.post(f"{API_BASE_URL}/workflows", data=data)
                                if response.status_code == 200:
                                    st.success("Workflow created successfully!")
                                    st.rerun()
                                else:
                                    st.error(f"Failed to create workflow: {response.text}")
                            except Exception as e:
                                st.error(f"Error: {str(e)}")
                        else:
                            st.error("Please fill in all required fields and select at least one persona")
            else:
                st.error("Failed to fetch personas")
        except Exception as e:
            st.error(f"Error: {str(e)}")

def show_analysis():
    """Analysis execution page"""
    st.header("📊 Document Analysis")
    
    # Get available workflows
    try:
        workflows_response = requests.get(f"{API_BASE_URL}/workflows")
        if workflows_response.status_code == 200:
            workflows = workflows_response.json()
            
            if not workflows:
                st.warning("No workflows available. Please create a workflow first.")
                return
            
            # Workflow selection
            workflow_options = {f"{w['name']} - {w['description']}": w['id'] for w in workflows}
            selected_workflow_name = st.selectbox("Select Workflow", list(workflow_options.keys()))
            selected_workflow_id = workflow_options[selected_workflow_name]
            
            # Document input
            st.subheader("Document Input")
            
            input_method = st.radio("Input Method", ["Text Input", "File Upload"])
            
            document_content = ""
            filename = ""
            file_type = ""
            
            if input_method == "Text Input":
                document_content = st.text_area("Document Content", height=300)
                filename = st.text_input("Document Name", value="document.txt")
                file_type = "text/plain"
            else:
                uploaded_file = st.file_uploader("Upload Document", type=['txt', 'pdf', 'doc', 'docx'])
                if uploaded_file:
                    document_content = uploaded_file.read().decode('utf-8')
                    filename = uploaded_file.name
                    file_type = uploaded_file.type
            
            user_id = st.text_input("User ID", value="user")
            
            if st.button("Run Analysis", disabled=not document_content):
                if document_content:
                    with st.spinner("Running analysis..."):
                        try:
                            data = {
                                "workflow_id": selected_workflow_id,
                                "document_content": document_content,
                                "filename": filename,
                                "file_type": file_type,
                                "user_id": user_id
                            }
                            
                            response = requests.post(f"{API_BASE_URL}/analysis/execute", data=data)
                            if response.status_code == 200:
                                analysis_result = response.json()
                                st.success("Analysis completed successfully!")
                                
                                # Display results
                                st.subheader("Analysis Results")
                                
                                for persona_id, result in analysis_result['analysis_content'].items():
                                    with st.expander(f"{result['persona_name']} Analysis"):
                                        if isinstance(result['analysis'], dict):
                                            st.json(result['analysis'])
                                        else:
                                            st.write(result['analysis'])
                                
                                # Store analysis ID in session state for chat
                                st.session_state.current_analysis_id = analysis_result['id']
                                
                            else:
                                st.error(f"Analysis failed: {response.text}")
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
                else:
                    st.error("Please provide document content")
        else:
            st.error("Failed to fetch workflows")
    except Exception as e:
        st.error(f"Error: {str(e)}")

def show_chat():
    """Chat interface page"""
    st.header("💬 Chat with Analysis")
    
    # Get user analyses
    try:
        user_id = st.text_input("User ID", value="user")
        
        if user_id:
            response = requests.get(f"{API_BASE_URL}/analysis/user/{user_id}")
            if response.status_code == 200:
                analyses = response.json()
                
                if not analyses:
                    st.info("No analyses found for this user. Run an analysis first!")
                    return
                
                # Analysis selection
                analysis_options = {f"{a['document_name']} - {a['created_at']}": a['id'] for a in analyses}
                selected_analysis_name = st.selectbox("Select Analysis", list(analysis_options.keys()))
                selected_analysis_id = analysis_options[selected_analysis_name]
                
                # Chat interface
                st.subheader("Chat Interface")
                
                # Get chat history
                chat_response = requests.get(f"{API_BASE_URL}/chat/{selected_analysis_id}/history")
                if chat_response.status_code == 200:
                    chat_history = chat_response.json()
                    
                    # Display chat history
                    for message in chat_history:
                        if message['user_message']:
                            st.write(f"**You:** {message['user_message']}")
                        if message['assistant_response']:
                            st.write(f"**Assistant:** {message['assistant_response']}")
                            st.divider()
                
                # New message input
                new_message = st.text_input("Type your message...")
                
                col1, col2 = st.columns([1, 4])
                with col1:
                    if st.button("Send"):
                        if new_message:
                            try:
                                data = {
                                    "analysis_id": selected_analysis_id,
                                    "message": new_message,
                                    "user_id": user_id
                                }
                                
                                response = requests.post(f"{API_BASE_URL}/chat/send", data=data)
                                if response.status_code == 200:
                                    st.success("Message sent!")
                                    st.rerun()
                                else:
                                    st.error(f"Failed to send message: {response.text}")
                            except Exception as e:
                                st.error(f"Error: {str(e)}")
                
                with col2:
                    if st.button("Clear Chat"):
                        try:
                            response = requests.delete(f"{API_BASE_URL}/chat/{selected_analysis_id}/history")
                            if response.status_code == 200:
                                st.success("Chat cleared!")
                                st.rerun()
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
                
                # Analysis summary
                if st.button("Get Analysis Summary"):
                    try:
                        summary_response = requests.get(f"{API_BASE_URL}/chat/{selected_analysis_id}/summary")
                        if summary_response.status_code == 200:
                            summary = summary_response.json()
                            
                            st.subheader("Analysis Summary")
                            st.write(f"**Executive Summary:** {summary['summary']['executive_summary']}")
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write("**Key Insights:**")
                                for insight in summary['summary']['key_insights']:
                                    st.write(f"- {insight}")
                            
                            with col2:
                                st.write("**Recommendations:**")
                                for rec in summary['summary']['recommendations']:
                                    st.write(f"- {rec}")
                            
                            st.write(f"**Risk Level:** {summary['summary']['risk_level']}")
                        else:
                            st.error("Failed to get summary")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
            else:
                st.error("Failed to fetch analyses")
    except Exception as e:
        st.error(f"Error: {str(e)}")

def show_upload():
    """File upload page"""
    st.header("📁 File Upload")
    
    uploaded_file = st.file_uploader("Upload Document", type=['txt', 'pdf', 'doc', 'docx'])
    
    if uploaded_file:
        st.write(f"**File:** {uploaded_file.name}")
        st.write(f"**Type:** {uploaded_file.type}")
        st.write(f"**Size:** {uploaded_file.size} bytes")
        
        # Display file content
        try:
            content = uploaded_file.read().decode('utf-8')
            st.subheader("File Content Preview")
            st.text_area("Content", content, height=200, disabled=True)
            
            # Store in session state for use in analysis
            st.session_state.uploaded_content = content
            st.session_state.uploaded_filename = uploaded_file.name
            st.session_state.uploaded_file_type = uploaded_file.type
            
            st.success("File uploaded successfully! You can now use this content in the Analysis page.")
            
        except Exception as e:
            st.error(f"Error reading file: {str(e)}")

if __name__ == "__main__":
    main()