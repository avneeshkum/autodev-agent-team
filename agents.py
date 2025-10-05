import os
from langchain_core.messages import convert_to_messages
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langchain_tavily import TavilySearch
from langgraph.prebuilt import create_react_agent
from langgraph_supervisor import create_supervisor
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_cohere import ChatCohere
from langsmith import traceable
from dotenv import load_dotenv
import time
import traceback
from e2b_code_interpreter import Sandbox

load_dotenv()

# --- Environment Keys ---
tavily_api_key = os.getenv("TAVILY_API_KEY")
groq_api_key = os.getenv("GROQ_API_KEY")
google_api_key = os.getenv("GOOGLE_API_KEY")
e2b_api_key = os.getenv("E2B_API_KEY")
cohere_api_key = os.getenv("COHERE_API_KEY")

# --- Tools (Now decorated with @tool) ---
web_search = TavilySearch(api_key=tavily_api_key, max_results=3)




@tool
def manage_file(filepath: str, mode: str, content: str = None) -> str:
    """
    Manages file operations: read, write, or append.

    Args:
        filepath: The full path to the file.
        mode: The operation to perform. Must be one of 'read', 'write', or 'append'.
        content: The text content to write or append. Required for 'write' and 'append' modes.

    Returns:
        The content of the file if mode is 'read', otherwise a status message.
    """
    if mode not in ['read', 'write', 'append']:
        return "Error: Invalid mode. Use 'read', 'write', or 'append'."

    try:
        if mode == 'read':
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        
        # --- For write and append modes ---
        
        # Content is required for these modes, so we check it here.
        if content is None:
            return f"Error: Content is required for '{mode}' mode."
        
        # Ensure the directory exists.
        directory = os.path.dirname(filepath)
        if directory:
            os.makedirs(directory, exist_ok=True)

        # Use 'w' for write (overwrite) and 'a' for append.
        file_mode = 'w' if mode == 'write' else 'a'
        
        with open(filepath, file_mode, encoding='utf-8') as f:
            f.write(content)
        
        return f"Successfully performed '{mode}' on file: {filepath}"

    except FileNotFoundError:
        # This error is only relevant for 'read' mode. 
        # For 'write'/'append', the file is created automatically.
        return f"Error: The file '{filepath}' was not found for reading."
    except Exception as e:
        return f"An unexpected error occurred: {e}"
@tool   
def run_python_code(code: str, dependencies: list[str] = None) -> dict:
    """
    Executes Python code or shell commands in a secure E2B sandbox. It can install
    dependencies before execution. This tool is smart enough to handle multi-line Python code
    by automatically saving it to a file and running it.
    """
    start_time = time.time()
    try:
        is_python_script = "\n" in code and ("import " in code or "def " in code or "print(" in code)
        
        with Sandbox.create(api_key=e2b_api_key) as sbx:
            if dependencies:
                pip_command = f"pip install --quiet {' '.join(dependencies)}"
                install_proc = sbx.commands.run(pip_command, timeout=300)
                if install_proc.exit_code != 0:
                    return {
                        "stdout": install_proc.stdout, "stderr": install_proc.stderr,
                        "error": f"Dependency installation failed.",
                    }
            
            if is_python_script:
                sbx.files.write("/home/user/script.py", code)
                execution_command = "python /home/user/script.py"
            else:
                execution_command = code

            execution = sbx.commands.run(execution_command, timeout=120)

            return {
                "stdout": execution.stdout,
                "stderr": execution.stderr,
                "exit_code": execution.exit_code,
                "duration_s": round(time.time() - start_time, 3),
            }

    except Exception:
        return {
            "stdout": "", "stderr": "", "error": traceback.format_exc(),
            "duration_s": round(time.time() - start_time, 3),
        }
    
# --- Models ---
@traceable
def create_groq_supervisor_model():
    return ChatGroq(model="openai/gpt-oss-20b", api_key=groq_api_key )# Powerful model for reasoning

@traceable
def create_groq_coding_model():
    return ChatGroq(model="llama-3.3-70b-versatile", api_key=groq_api_key) # Powerful model for coding

@traceable
def create_google_coding2_model():
    return ChatGoogleGenerativeAI(model="gemini-2.5-flash",api_key=google_api_key) # Powerful model for coding

@traceable
def create_groq_coding3_model():
    return ChatGroq(model="moonshotai/kimi-k2-instruct-0905", api_key=groq_api_key) # Powerful model for coding


@traceable
def create_cohere_coding4_model():
    return ChatCohere(api_key=cohere_api_key,
    model="command-a-03-2025", # Using the stable and powerful model
    max_retries=3,
    temperature=0.7,max_token=4000) 


sup_model = create_groq_supervisor_model()
coding_model = create_groq_coding_model()
coding_model2 = create_google_coding2_model()
coding_model3 = create_groq_coding3_model()
coding_model4 = create_cohere_coding4_model() 

#--Agents---
# --- Planner Agent ---

planner_agent = create_react_agent(
    model=coding_model4,
    tools=[],         
    prompt=(
        """You are a Planner Agent who will take a task from the user and create a proper plan. This plan should be concise. You have two agents with you: a Frontend Agent and a Backend Agent. You have to create the plan according to both of their roles so that the agents do not get confused or make mistakes.

Your Backend Agent writes code in Python using FastAPI, Django, or Flask and creates a single, self-contained backend file. Your Frontend Agent writes code in HTML and vanilla JS and creates a single, self-contained frontend file.

You must create a concise plan in which you will make two sections: a frontend section and a backend section.pass plan to supervisor but do not call any tool  respond with the exact message: "plan passed successfully to supervisor." 

"""
    ),
    name="planner_agent",
)

# ---Frontend_Agent ---
frontend_agent = create_react_agent(
    model=coding_model3,
    tools=[manage_file, web_search],
    prompt=(
        """You are an expert frontend developer. Your task is to write a single, self-contained HTML file.

Follow these critical instructions exactly:

1. Use only the backend summary provided to you to connect the frontend with the backend via fetch() calls.  
2. Write the complete HTML code in one file, including inline CSS and vanilla JavaScript.  
3. Use the manage_file tool to save the file. The filepath argument MUST be exactly 'output/index.html'.  
4. After saving, respond with the exact message: "Frontend code saved successfully."  
5. Do not include any explanations, reasoning, or extra commentary in your output."""

    ),
    name="frontend_agent",
    
)

# --- Backend Agent ---


backend_agent = create_react_agent(
    model=sup_model,
    tools=[manage_file, web_search,run_python_code],
    prompt=(
        """ou are an expert, production-focused backend developer. Your task is to write a single, self-contained, and robust FastAPI file.

Follow these critical instructions precisely:

1.  **CORS Configuration:** You MUST import `CORSMiddleware` from `fastapi.middleware.cors` and configure it to allow all origins by setting `allow_origins=["*"]`.

2.  **Error Handling:** If the code involves making external network requests (e.g., using the `requests` library), you MUST wrap the network call in a `try...except` block to handle potential connection errors gracefully.

3.  **Code Verification and Debugging:** Before saving the file, you are required to verify its correctness.
    a. First, identify all necessary Python library dependencies (e.g., `fastapi`, `uvicorn`, `requests`).
    b. Next, use the `run_python_code` tool to install these dependencies and execute your full script.
    c. If the tool reports an error, you must debug the code and retry the execution. You may attempt to fix the code a maximum of two times. If it still fails, proceed to the next step and save the file as-is.

4.  **Save the File:** Use the `manage_file` tool to save the final code. The `filepath` argument MUST be exactly `'output/backend.py'`.

5.  **Confirmation:** After saving the file, you MUST respond with the exact message: "Backend code saved successfully."

6.  **Provide Summary:** Following the confirmation message, provide a concise summary of the backend, including: all API endpoints, their HTTP methods, the server URL, expected inputs, and successful outputs."""

    ),
    name="backend_agent",
)

#_-- QA Agent ---
qa_agent = create_react_agent(
    model=coding_model3,
    tools=[manage_file],
    prompt=(
  """You are a specialized QA Test Writer. Your sole purpose is to write pytest unit tests.

Follow these instructions exactly:
1.  You will be given a summary of a backend API.
2.  Based on that summary, write thorough unit tests using the pytest framework.
3.  Use the `manage_file` tool to save the complete test code to 'output/test_app.py'.
4.  After saving the file, respond with the exact message: `Pytest tests generated successfully`.
5.  Make a readme.md file of the project using manage_file tool and save it to output/readme.md file
6.  Do not include any explanations, reasoning, or extra commentary in your output."""

    ),
    name="qa_agent",
)


# --- Supervisor ---
supervisor = create_supervisor(
    model=coding_model2,
    agents=[planner_agent, backend_agent, frontend_agent, qa_agent],
    prompt=(
"""
You are a Project Manager Supervisor. Your job is to manage a step-by-step workflow.

1.  First, pass the user request to `planner_agent`.
2.  After the planner agent is finished,you get the plan delegate to backend task to `backend_agent`.
3.  After the backend  is saved, you give the backend summary to `frontend_agent`.
4.  After the frontend is done, delegate to `qa_agent` to write tests and a README.
5.  Do not do any work yourself, only delegate the task to agents. Respond with the final confirmation once all tasks are complete."""

    ),
    sanitize_names=True,
    add_handoff_back_messages=True,
    output_mode="full_history",
).compile()

# --- Printing and Execution Logic ---
def pretty_print_message(message, indent=False):
    pretty_message = message.pretty_repr(html=True)
    if not indent:
        print(pretty_message)
        return
    indented = "\n".join("\t" + c for c in pretty_message.split("\n"))
    print(indented)

def pretty_print_messages(update, last_message=False):
    is_subgraph = False
    if isinstance(update, tuple):
        ns, update = update
        if len(ns) == 0:
            return
        graph_id = ns[-1].split(":")[0]
        print(f"--- Update from Agent: {graph_id} ---")
        print("\n")
        is_subgraph = True
    for node_name, node_update in update.items():
        if "messages" not in node_update:
            continue
        messages = convert_to_messages(node_update["messages"])
        if last_message:
            messages = messages[-1:]
        if not messages:
            continue
        print(f"Update from node {node_name}:")
        print("\n")
        for m in messages:
            pretty_print_message(m, indent=is_subgraph)
        print("\n")

# --- Run the Stream ---
if __name__ == "__main__":
    for chunk in supervisor.stream(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "Create a FastAPI application that provides the current time in India...",
                }
            ]
        },
    ):
        pretty_print_messages(chunk, last_message=True)

    final_message_history = chunk["supervisor"]["messages"]
