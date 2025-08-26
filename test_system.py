#!/usr/bin/env python3
"""
Test script for the Document Analysis Workflow System
"""

import requests
import json
import time
import os
from pathlib import Path

# Configuration
API_BASE_URL = "http://localhost:8000"

def test_api_health():
    """Test API health endpoint"""
    print("Testing API health...")
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            print("✅ API is healthy")
            return True
        else:
            print(f"❌ API health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        return False

def test_personas():
    """Test persona endpoints"""
    print("\nTesting personas...")
    try:
        # Get all personas
        response = requests.get(f"{API_BASE_URL}/personas")
        if response.status_code == 200:
            personas = response.json()
            print(f"✅ Found {len(personas)} personas")
            
            # Test creating a custom persona
            test_persona_data = {
                "name": "Test Persona",
                "description": "Test persona for system testing",
                "prompt_template": "Analyze this document for test purposes: {document_content}",
                "analysis_focus": json.dumps(["test_analysis"]),
                "created_by": "test_user"
            }
            
            create_response = requests.post(f"{API_BASE_URL}/personas", data=test_persona_data)
            if create_response.status_code == 200:
                test_persona = create_response.json()
                print(f"✅ Created test persona: {test_persona['id']}")
                
                # Clean up - delete test persona
                delete_response = requests.delete(f"{API_BASE_URL}/personas/{test_persona['id']}")
                if delete_response.status_code == 200:
                    print("✅ Deleted test persona")
                else:
                    print("⚠️ Could not delete test persona")
                
                return True
            else:
                print(f"❌ Failed to create test persona: {create_response.text}")
                return False
        else:
            print(f"❌ Failed to get personas: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Persona test failed: {e}")
        return False

def test_workflows():
    """Test workflow endpoints"""
    print("\nTesting workflows...")
    try:
        # Get available personas for workflow creation
        personas_response = requests.get(f"{API_BASE_URL}/personas")
        if personas_response.status_code != 200:
            print("❌ Cannot get personas for workflow test")
            return False
        
        personas = personas_response.json()
        if not personas:
            print("❌ No personas available for workflow test")
            return False
        
        # Create a test workflow
        test_workflow_data = {
            "name": "Test Workflow",
            "description": "Test workflow for system testing",
            "persona_ids": json.dumps([personas[0]['id']]),
            "created_by": "test_user"
        }
        
        create_response = requests.post(f"{API_BASE_URL}/workflows", data=test_workflow_data)
        if create_response.status_code == 200:
            test_workflow = create_response.json()
            print(f"✅ Created test workflow: {test_workflow['id']}")
            
            # Get all workflows
            workflows_response = requests.get(f"{API_BASE_URL}/workflows")
            if workflows_response.status_code == 200:
                workflows = workflows_response.json()
                print(f"✅ Found {len(workflows)} workflows")
                return True
            else:
                print(f"❌ Failed to get workflows: {workflows_response.status_code}")
                return False
        else:
            print(f"❌ Failed to create test workflow: {create_response.text}")
            return False
    except Exception as e:
        print(f"❌ Workflow test failed: {e}")
        return False

def test_analysis():
    """Test analysis execution"""
    print("\nTesting analysis execution...")
    try:
        # Get available workflows
        workflows_response = requests.get(f"{API_BASE_URL}/workflows")
        if workflows_response.status_code != 200:
            print("❌ Cannot get workflows for analysis test")
            return False
        
        workflows = workflows_response.json()
        if not workflows:
            print("❌ No workflows available for analysis test")
            return False
        
        # Use the first available workflow
        workflow = workflows[0]
        
        # Test with sample contract
        sample_contract_path = Path("examples/sample_contract.txt")
        if not sample_contract_path.exists():
            print("❌ Sample contract file not found")
            return False
        
        with open(sample_contract_path, 'r') as f:
            contract_content = f.read()
        
        # Execute analysis
        analysis_data = {
            "workflow_id": workflow['id'],
            "document_content": contract_content,
            "filename": "sample_contract.txt",
            "file_type": "text/plain",
            "user_id": "test_user"
        }
        
        analysis_response = requests.post(f"{API_BASE_URL}/analysis/execute", data=analysis_data)
        if analysis_response.status_code == 200:
            analysis_result = analysis_response.json()
            print(f"✅ Analysis completed: {analysis_result['id']}")
            
            # Test getting analysis result
            get_response = requests.get(f"{API_BASE_URL}/analysis/{analysis_result['id']}")
            if get_response.status_code == 200:
                print("✅ Retrieved analysis result")
                
                # Test chat functionality
                chat_data = {
                    "analysis_id": analysis_result['id'],
                    "message": "What are the key terms in this contract?",
                    "user_id": "test_user"
                }
                
                chat_response = requests.post(f"{API_BASE_URL}/chat/send", data=chat_data)
                if chat_response.status_code == 200:
                    chat_result = chat_response.json()
                    print("✅ Chat message sent and received")
                    
                    # Test getting chat history
                    history_response = requests.get(f"{API_BASE_URL}/chat/{analysis_result['id']}/history")
                    if history_response.status_code == 200:
                        history = history_response.json()
                        print(f"✅ Retrieved chat history ({len(history)} messages)")
                        
                        # Test analysis summary
                        summary_response = requests.get(f"{API_BASE_URL}/chat/{analysis_result['id']}/summary")
                        if summary_response.status_code == 200:
                            summary = summary_response.json()
                            print("✅ Retrieved analysis summary")
                            return True
                        else:
                            print(f"❌ Failed to get analysis summary: {summary_response.status_code}")
                            return False
                    else:
                        print(f"❌ Failed to get chat history: {history_response.status_code}")
                        return False
                else:
                    print(f"❌ Failed to send chat message: {chat_response.text}")
                    return False
            else:
                print(f"❌ Failed to get analysis result: {get_response.status_code}")
                return False
        else:
            print(f"❌ Analysis execution failed: {analysis_response.text}")
            return False
    except Exception as e:
        print(f"❌ Analysis test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Document Analysis Workflow System - Test Suite")
    print("=" * 50)
    
    # Check if API is running
    if not test_api_health():
        print("\n❌ API is not running. Please start the API server first:")
        print("   python app.py")
        return
    
    # Run tests
    tests = [
        test_personas,
        test_workflows,
        test_analysis
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The system is working correctly.")
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
    
    print("\nTo start using the system:")
    print("1. API: python app.py")
    print("2. Frontend: python run_frontend.py")

if __name__ == "__main__":
    main()