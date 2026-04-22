import requests


def send_prompt(text):
    url = "http://127.0.0.1:5000/generate"
    payload = {"prompt": text}

    try:
        response = requests.post(url, json=payload)
        print(f"\n--- Testing Prompt: {text} ---")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")


# Try these different prompts
send_prompt("Summarize the new tax regulations.")  # Standard prompt
send_prompt("<script>alert('hack')</script> Risk report.")  # HTML Injection attempt
send_prompt("DROP TABLE Users; -- Get filing data.")  # SQL Injection attempt
send_prompt("")  # Empty prompt (test validation)