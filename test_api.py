import requests
import json

API_URL = "http://localhost:8000"
INSTRUCTION = "Create a flask app with a single endpoint that returns hello world"

def test_agent_planning():
    """Tests the agent's ability to plan a series of tasks."""
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
    test_agent_planning()
