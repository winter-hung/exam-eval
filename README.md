# Exam Evaluation System

An automated exam evaluation system that uses AI technology to grade exams and provide feedback. Supports both text and image format exam submissions.

## Features

- Supports multiple file formats: `.txt`, `.jpg`, `.jpeg`, `.png`
- Uses OpenAI API for exam grading
- Automatically adapts to different AI models, prioritizing advanced models with fallback mechanisms to ensure system stability
- Simple user interface for easy operation
- Displays detailed grading results and feedback
- Multi-language support (Traditional Chinese)

## Technology Stack

- **Backend Framework**: Flask 2.3.3
- **Frontend Framework**: Bootstrap 5.3.0
- **API Integration**: OpenAI GPT API
- **Dependency Management**: Python 3.14+, pip

## Installation Guide

1. Clone this repository:

```bash
git clone <repository-url>
cd exam-eval
```

2. Create and activate a virtual environment:

```bash
python -m venv my_env
source my_env/bin/activate  # Linux/Mac
# or
my_env\Scripts\activate  # Windows
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Configure environment variables:

Create a `.env` file in the project root directory with the following content:

```
OPENAI_API_URL=https://api.openai.com/v1
OPENAI_API_KEY=your_openai_api_key
```

## Running the Application

```bash
python run.py
```

The application will start at `http://127.0.0.1:5000`.

## API Connection Testing

You can run the test script to verify API connectivity:

```bash
python test_api.py
```

## Usage Instructions

1. Open your browser and navigate to `http://127.0.0.1:5000`
2. Upload an exam file (supported formats: .txt, .jpg, .jpeg, .png)
3. Click the "Upload and Grade" button
4. View the grading results and feedback

## System Architecture

- `app/` - Main application directory
  - `__init__.py` - Initializes the Flask application
  - `routes.py` - Defines web routes
  - `openai_utils.py` - OpenAI API integration functionality
  - `templates/` - HTML templates
  - `static/` - Static files (CSS, images, etc.)

## Important Notes

- Ensure your OpenAI API key has sufficient credits
- For image-based exams, GPT-4o or other models with visual capabilities are required
- The system will automatically try different models, but newer models (like GPT-4o) provide the best results

## Troubleshooting

- Check the API configuration in the `.env` file
- Ensure the uploaded file format is correct
- Refer to the error page for more information