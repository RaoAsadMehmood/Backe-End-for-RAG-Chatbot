#!/usr/bin/env python3
"""
Test script to verify the deployed RAG chatbot API endpoint
"""
import requests
import json

def get_api_url():
    """Get the API URL from user input or use a default"""
    print("Please enter your Railway deployment URL (e.g., https://your-app-name.up.railway.app)")
    print("If you don't know it, you can find it in your Railway dashboard")
    url = input("Enter your API URL: ").strip()

    if not url:
        print("Using default format - please update with your actual URL")
        url = "https://your-railway-app-name.up.railway.app"

    # Ensure URL has proper format
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url

    return url

def test_chatbot():
    API_BASE_URL = get_api_url()

    print(f"\nTesting API at: {API_BASE_URL}")
    print("Testing general questions that were causing issues...\n")

    # Test general questions that were causing issues
    test_messages = [
        "Who are you?",
        "How are you?",
        "What can you do?",
        "Tell me about yourself",
        "Hello",
        # Test a topic-specific question
        "What is Physical AI?",
        "Explain humanoid robotics"
    ]

    for message in test_messages:
        print(f"Sending message: '{message}'")

        try:
            response = requests.post(
                f"{API_BASE_URL}/chat",
                headers={"Content-Type": "application/json"},
                json={"message": message},
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                if result.get('error'):
                    print(f"  Error: {result['error']}")
                else:
                    print(f"  Response: {result['response']}")
            else:
                print(f"  HTTP Error: {response.status_code} - {response.text}")

        except requests.exceptions.RequestException as e:
            print(f"  Request Error: {str(e)}")
        except json.JSONDecodeError:
            print(f"  Response: {response.text[:200]}...")  # Show raw response if not JSON

        print("-" * 80)

if __name__ == "__main__":
    print("RAG Chatbot API Tester")
    print("=" * 50)
    test_chatbot()