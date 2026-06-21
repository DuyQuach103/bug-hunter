# Bug Hunter - AI-Powered Code Debugger

Bug Hunter is a single-page web application that analyzes Python code using the Google Gemini API to identify syntax errors, logic errors, performance bottlenecks, security vulnerabilities, and highlights code strengths and actionable improvements.

## Features

- **GitHub Dark-Style UI**: A beautiful, dark-themed user interface optimized for code reading and inspection.
- **AI-Powered Code Analysis**: Direct integration with Gemini API using structured outputs.
- **Categorized Results**: Details about bugs, warnings, strengths, and recommendations.
- **Recommended Fixes with Syntax Highlighting**: View exactly what needs to be changed, styled nicely with Prism.js syntax highlighting.
- **Example Loader**: Pre-loads a buggy Python script to let you experience the analysis instantly.

## Tech Stack

- **Frontend**: HTML5, CSS3, Vanilla JavaScript, Prism.js (Syntax Highlighting), Lucide Icons
- **Backend**: Python, Flask, Flask-CORS, python-dotenv
- **AI Engine**: Google Gemini API via official SDK (`google-genai` / `google-generativeai` fallback)

---

## Setup & Installation

### 1. Clone/Navigate to the Project Directory
Navigate to the directory containing the application code:
```bash
cd bug-hunter
```

### 2. Install Dependencies
Create a virtual environment (optional but recommended) and install the python dependencies:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure Gemini API Key
Obtain a Google Gemini API Key from Google AI Studio. Set it in your environment:

On macOS/Linux:
```bash
export GEMINI_API_KEY="your-api-key-here"
```

On Windows (Command Prompt):
```cmd
set GEMINI_API_KEY=your-api-key-here
```

On Windows (PowerShell):
```powershell
$env:GEMINI_API_KEY="your-api-key-here"
```

Alternatively, create a `.env` file in the `bug-hunter` directory:
```env
GEMINI_API_KEY=your-api-key-here
```

---

## Running the Application

Start the Flask server:
```bash
python server.py
```

The application will start, and the web interface will be available at:
**[http://127.0.0.1:5000](http://127.0.0.1:5000)**

Open this URL in your browser, paste your Python code, and click **Find Bugs**.
