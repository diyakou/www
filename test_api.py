import requests

API_URL = "http://localhost:8000"
NEW_FILE_NAME = "test_from_script.py"
FILE_CONTENT = "print('This file was created from a test script.')"

def test_create_file():
    """Tests creating a new file via the API."""
    response = requests.post(
        f"{API_URL}/files/{NEW_FILE_NAME}",
        json={"content": FILE_CONTENT}
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")

if __name__ == "__main__":
    test_create_file()
