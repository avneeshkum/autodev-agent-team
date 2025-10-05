# AutoDev Agent Team: A Multi-Agent System for Autonomous Web Development

## Overview

AutoDev Agent Team is a sophisticated multi-agent system designed to automate the entire workflow of creating full-stack web applications. By leveraging a team of specialized AI agents, this project can take a high-level user request, plan the development process, write, test, and debug both backend and frontend code, and generate final documentation.

The system is built on a supervisor-worker architecture, where a Project Manager agent orchestrates a team of experts: a Planner, a Backend Developer, a Frontend Developer, and a QA Specialist. This structure ensures a logical, robust, and efficient development process that mimics a real-world software team.

## ✨ Features

* **🤖 Autonomous Workflow:** Takes a single prompt and generates a complete, functional web application.

* **👨‍💼 Specialized Agent Roles:** Each agent has a specific expertise (planning, backend, frontend, QA), ensuring high-quality output at each stage.

* **✅ Self-Verification & Debugging:** The Backend Agent uses a secure sandbox environment (`E2B Code Interpreter`) to test its own code, identify errors, and attempt fixes *before* saving the final file.

* **🧪 Automated Testing & Docs:** The QA Agent automatically generates `pytest` unit tests and a project `README.md` file based on the final application.

* **🔗 Seamless Integration:** The Frontend Agent uses a summary from the Backend Agent to ensure perfect API integration.

* **✋ Human-in-the-Loop (Optional):** The system can be configured to pause for human approval at critical steps, giving you ultimate control over the development process.

## 🏗️ System Architecture

The project operates on a sequential, managed workflow orchestrated by a Supervisor Agent.

1. **User Request:** The process begins with a user providing a high-level goal (e.g., "make a weather app").

2. **`Planner Agent`:** The Supervisor first delegates the task to the Planner, who breaks down the request into a concise technical plan with sections for the frontend and backend.

3. **`Backend Agent`:** The plan is then passed to the Backend Agent. This agent:

   * Writes the FastAPI server code.

   * Implements best practices like CORS and error handling.

   * **Crucially, it uses the `run_python_code` tool to test its code in a sandbox, identifies dependencies, and fixes bugs.**

   * Saves the final `backend.py` file.

   * Generates a summary of the API (endpoints, methods, etc.).

4. **`Frontend Agent`:** The backend summary is given to the Frontend Agent, who writes a single, self-contained `index.html` file with HTML, CSS, and vanilla JavaScript to interact with the backend.

5. **`QA Agent`:** Finally, the backend summary is passed to the QA Agent, who writes `pytest` unit tests and a `README.md` file for the project.

6. **Completion:** The Supervisor confirms that all tasks are complete.

## 🛠️ Technology Stack

* **Orchestration:** LangChain / LangGraph

* **Large Language Models (LLMs):** Groq, Google Gemini, Cohere

* **Code Execution Sandbox:** E2B Code Interpreter

* **Tools:** Tavily (for web search)

* **Backend:** Python, FastAPI

* **Frontend:** HTML, CSS, Vanilla JavaScript

* **Testing:** Pytest

## 🚀 Setup and Installation

### 1. Prerequisites

* Python 3.10+

* An account for each of the required services (Groq, Google AI, Cohere, E2B, Tavily)

### 2. Clone the Repository
git clone https://github.com/avneeshkum/autodev-agent-team.git
cd autodev-agent-team


### 3. Install Dependencies

It is recommended to use a virtual environment.

python -m venv venv
source venv/bin/activate  # On Windows, use venv\Scripts\activate
pip install -r requirements.txt


### 4. Configure Environment Variables

Create a file named `.env` in the root directory of the project and add your API keys:

TAVILY_API_KEY="your_tavily_api_key"
GROQ_API_KEY="your_groq_api_key"
GOOGLE_API_KEY="your_google_api_key"
E2B_API_KEY="your_e2b_api_key"
COHERE_API_KEY="your_cohere_api_key"


## 🏃 How to Run the System

To start the agentic workflow, run the main script from your terminal:

python super.py


The system will begin executing the task defined in the script. You will see real-time updates as each agent completes its work. All generated files will be placed in the `output/` directory.

### To Use the Generated Application:

1. **Start the Backend Server:**

cd output
python backend.py


(Or for auto-reloading during development: `uvicorn backend:app --reload`)

2. **Open the Frontend:**

* Navigate to the `output/` directory in your file explorer.

* Open the `index.html` file in your web browser.

## 📈 Future Improvements

* **Implement a Feedback Loop:** Enhance the Supervisor to send tasks back to the Backend Agent if the QA Agent's tests fail.

* **Empower the QA Agent:** Provide the QA Agent with the `run_python_code` tool so it can not only write tests but also execute them and report the results.

* **Stateful Memory:** Integrate a persistent checkpointer (like `SQLite` or `Redis`) to allow the workflow to be resumed across sessions.

