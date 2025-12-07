import os
import requests
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
root_dir = Path(__file__).resolve().parent
dotenv_path = root_dir / '.env'

if dotenv_path.exists():
    load_dotenv(dotenv_path=dotenv_path)
else:
    load_dotenv()

OPENAI_API_URL = os.getenv('OPENAI_API_URL')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

def test_api_connection():
    print("\n===== API Connection Test =====")
    print(f"API URL: {OPENAI_API_URL}")
    print(f"API Key: {OPENAI_API_KEY[:5]}...{OPENAI_API_KEY[-4:]} (partially hidden)")

    headers = {
        'Authorization': f'Bearer {OPENAI_API_KEY}',
        'Content-Type': 'application/json'
    }

    payload = {
        'model': 'gpt-4o',  # Updated to use the same model as the main application
        'messages': [
            {
                'role': 'system',
                'content': 'You are a test assistant.'
            },
            {
                'role': 'user',
                'content': 'Say "API connection successful"'
            }
        ],
        'temperature': 0.7
    }

    try:
        print("\nSending test request to API...")
        models_to_try = ['gpt-4o', 'gpt-4', 'gpt-3.5-turbo']
        model_index = 0

        while model_index < len(models_to_try):
            current_model = models_to_try[model_index]
            payload['model'] = current_model
            print(f"\nTrying model: {current_model}")

            response = requests.post(f'{OPENAI_API_URL}/chat/completions',
                                   headers=headers,
                                   json=payload)

            print(f"Response status code: {response.status_code}")

            if response.status_code == 200:
                print(f"✅ API connection successful with model {current_model}!")
                print("\nAPI Response:")
                try:
                    json_response = response.json()
                    content = json_response['choices'][0]['message']['content']
                    print(f"Message: {content}")
                    break  # Exit the loop on success
                except Exception as e:
                    print(f"Could not parse response: {e}")
                    print(f"Raw response: {response.text[:500]}")
                    break
            elif response.status_code == 404:
                # Model not found, try the next one
                error_message = "Unknown error"
                try:
                    error_json = response.json()
                    error_message = error_json.get('error', {}).get('message', 'Unknown error')
                except:
                    pass

                if 'model' in error_message.lower():
                    print(f"❌ Model {current_model} not available. Trying next model...")
                    model_index += 1
                    continue
                else:
                    # Not a model error, stop trying
                    print(f"❌ API request failed with status code: {response.status_code}")
                    print(f"Response: {response.text[:500]}")
                    break
            elif response.status_code == 401:
                print("❌ Authentication error: Invalid API key or expired key")
                print(f"Response: {response.text[:500]}")
                break
            else:
                print(f"❌ API request failed with status code: {response.status_code}")
                print(f"Response: {response.text[:500]}")
                break

        # Check if all models failed
        if model_index >= len(models_to_try):
            print("❌ All models failed. The API key may not have access to any of the supported models.")

    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_api_connection()