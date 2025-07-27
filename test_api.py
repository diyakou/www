import requests
import json

API_URL = "http://localhost:8000"
INSTRUCTION = "Create a file named README.md and write 'This is a test project.' into it."

def test_agent_execution():
    """Tests the agent's ability to plan and execute a series of tasks."""
    response = requests.post(
        f"{API_URL}/agent/execute",
        json={"instruction": INSTRUCTION}
    )
    print(f"Status Code: {response.status_code}")
    try:
        response_json = response.json()
        print("Response JSON:")
        print(json.dumps(response_json, indent=2))
    except json.JSONDecodeError:
        print("Response is not valid JSON:")
        print(response.text)

if __name__ == "__main__":
    test_agent_execution()
