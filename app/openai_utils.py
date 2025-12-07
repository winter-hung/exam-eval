import os
import requests
import base64
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load from the root directory where the application is run
root_dir = Path(__file__).resolve().parent.parent
dotenv_path = root_dir / '.env'

if dotenv_path.exists():
    load_dotenv(dotenv_path=dotenv_path)
else:
    # Fallback to app directory
    load_dotenv()

OPENAI_API_URL = os.getenv('OPENAI_API_URL')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Validate configuration
if not OPENAI_API_URL:
    print("Error: OPENAI_API_URL environment variable is not set.")

if not OPENAI_API_KEY:
    print("Error: OPENAI_API_KEY environment variable is not set.")
else:
    # Print API key info for debugging
    print(f"API Key format: {OPENAI_API_KEY[:5]}...{OPENAI_API_KEY[-4:]} (length: {len(OPENAI_API_KEY)})")

    # Check Line OpenAI proxy key format
    if not (OPENAI_API_KEY.startswith('ck-') or OPENAI_API_KEY.startswith('sk-')):
        print("Warning: API key format may be incorrect. Line OpenAI proxy keys typically start with 'ck-' or 'sk-'.")

def encode_image_to_base64(image_path):
    """
    Encodes an image file to base64 string.

    Args:
        image_path (str): Path to the image file.

    Returns:
        str: Base64 encoded string of the image.
    """
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def evaluate_exam(exam_content, file_path=None, file_type=None):
    """
    Sends exam content to OpenAI API for evaluation and returns the score.

    Args:
        exam_content (str): The content of the exam to evaluate. For text files.
        file_path (str, optional): Path to the file for image-based evaluation.
        file_type (str, optional): The type of file being processed.

    Returns:
        dict: The response containing the evaluation and score.
    """
    # Check if API key contains "Bearer" already - some services require this format
    api_key_for_header = OPENAI_API_KEY

    # Ensure the header doesn't include "Bearer" twice if it's already in the key
    if "Bearer" in OPENAI_API_KEY:
        headers = {
            'Authorization': api_key_for_header,
            'Content-Type': 'application/json'
        }
        print("Using API key with Bearer included")
    else:
        headers = {
            'Authorization': f'Bearer {api_key_for_header}',
            'Content-Type': 'application/json'
        }
        print("Using API key with Bearer prefix")

    # Determine if we're handling text or image
    if file_type in ['jpg', 'jpeg', 'png'] and file_path:
        # Image-based exam evaluation
        base64_image = encode_image_to_base64(file_path)

        # Try GPT-4o first (supports vision), with fallbacks if not available
        model = 'gpt-4o'

        payload = {
            'model': model,  # Current model with vision capabilities
            'messages': [
                {
                    'role': 'system',
                    'content': 'You are an exam grading assistant. Evaluate the following exam image and provide a score out of 100 along with feedback.'
                },
                {
                    'role': 'user',
                    'content': [
                        {
                            'type': 'text',
                            'text': 'Please evaluate this exam image and give a score:'
                        },
                        {
                            'type': 'image_url',
                            'image_url': {
                                'url': f"data:image/{file_type};base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            'temperature': 0.7,
            'max_tokens': 1000
        }
    else:
        # Text-based exam evaluation
        payload = {
            'model': 'gpt-4o', # Updated to current model for consistency
            'messages': [
                {
                    'role': 'system',
                    'content': 'You are an exam grading assistant. Evaluate the following exam submission and provide a score out of 100 along with feedback.'
                },
                {
                    'role': 'user',
                    'content': f'Please evaluate this exam and give a score: \n\n{exam_content}'
                }
            ],
            'temperature': 0.7
        }

    try:
        # Check if API credentials are properly configured
        if not OPENAI_API_URL or not OPENAI_API_KEY:
            return {
                'success': False,
                'error': '未設定 API 參數。請檢查 .env 檔案中的 OPENAI_API_URL 和 OPENAI_API_KEY。'
            }

        print(f"Making request to {OPENAI_API_URL}/chat/completions")
        print(f"Using API key: {OPENAI_API_KEY[:5]}...{OPENAI_API_KEY[-4:]} (partially hidden)")

        response = requests.post(f'{OPENAI_API_URL}/chat/completions',
                               headers=headers,
                               json=payload)

        if response.status_code == 401:
            return {
                'success': False,
                'error': '認證錯誤：API 金鑰無效或已過期。請檢查 API 金鑰是否正確設定。'
            }
        elif response.status_code == 403:
            return {
                'success': False,
                'error': '權限錯誤：您沒有訪問此 API 的權限。請確認您有權限使用此服務。'
            }
        elif response.status_code == 404:
            # Specific handling for model not found
            try:
                error_json = response.json()
                error_message = error_json.get('error', {}).get('message', '')

                # Check if it's a model-related error
                if 'model' in error_message.lower() and 'not found' in error_message.lower():
                    if 'gpt-4o' in payload['model']:
                        # Retry with a different model if gpt-4o failed
                        print("Model gpt-4o not found. Retrying with gpt-4...")
                        payload['model'] = 'gpt-4'
                        response = requests.post(f'{OPENAI_API_URL}/chat/completions',
                                           headers=headers,
                                           json=payload)
                        if response.status_code == 200:
                            return {
                                'success': True,
                                'result': response.json()['choices'][0]['message']['content']
                            }
                        elif response.status_code == 404:
                            # Try again with GPT-3.5 as a last resort
                            print("Model gpt-4 not found. Retrying with gpt-3.5-turbo...")
                            payload['model'] = 'gpt-3.5-turbo'
                            response = requests.post(f'{OPENAI_API_URL}/chat/completions',
                                               headers=headers,
                                               json=payload)
                            if response.status_code == 200:
                                return {
                                    'success': True,
                                    'result': response.json()['choices'][0]['message']['content'] + "\n\n(注意：評分是使用 GPT-3.5 模型完成的，結果可能不如使用更高級的模型準確。)"
                                }

                    return {
                        'success': False,
                        'error': f'模型不可用：您的 API 金鑰無法訪問所需的 AI 模型 ({payload["model"]})。請確認您的帳號有權限使用此模型。'
                    }
            except:
                pass

        elif response.status_code >= 400:
            error_detail = f"API 回應錯誤 (HTTP {response.status_code})"
            try:
                error_json = response.json()
                if 'error' in error_json:
                    error_detail += f": {error_json['error'].get('message', '')}"
            except:
                pass
            return {
                'success': False,
                'error': error_detail
            }

        response.raise_for_status()

        try:
            return {
                'success': True,
                'result': response.json()['choices'][0]['message']['content']
            }
        except (KeyError, IndexError, ValueError) as e:
            return {
                'success': False,
                'error': f'處理 API 回應時出錯: {str(e)}。API 回應格式可能已更改。'
            }

    except requests.exceptions.ConnectionError:
        return {
            'success': False,
            'error': '連線錯誤：無法連線到 API 伺服器。請檢查網路連線或 API 端點 URL。'
        }
    except requests.exceptions.Timeout:
        return {
            'success': False,
            'error': '請求超時：API 伺服器沒有及時回應。請稍後再試。'
        }
    except requests.exceptions.RequestException as e:
        return {
            'success': False,
            'error': f'API 請求錯誤：{str(e)}'
        }