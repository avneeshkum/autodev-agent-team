import os
import shutil
import streamlit as st
from langchain_core.messages import convert_to_messages
import time

# --- Page Configuration ---
st.set_page_config(
    page_title="AutoDev Agent Team UI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Sidebar for API Keys ---
st.sidebar.title("🔑 API Configuration")
st.sidebar.markdown("Enter your API keys below. These are required to run the agent system.")

# We collect all keys first before doing anything else
tavily_api_key = st.sidebar.text_input("Tavily API Key", type="password")
groq_api_key = st.sidebar.text_input("Groq API Key", type="password")
google_api_key = st.sidebar.text_input("Google API Key", type="password")
e2b_api_key = st.sidebar.text_input("E2B API Key", type="password")


st.sidebar.info("The application will only run after all API keys are provided.")
st.sidebar.markdown("---")
st.sidebar.markdown("Made with ❤️ for Agentic AI Systems.")


# --- Main UI ---
st.title("🤖 AutoDev Agent Team")
st.header("Build Full-Stack Web Applications with AI Agents", divider="rainbow")
st.markdown("Provide your application idea, and the AI team will handle the rest—from planning to coding and testing.")

# Initialize session state for log messages
if "log_messages" not in st.session_state:
    st.session_state.log_messages = []

# --- Helper function to render messages ---
def render_message(msg):
    if msg.type == "ai":
        st.markdown(f"**🤖 Agent Message:**\n> {msg.content.strip()}")
    elif msg.type == "tool":
        tool_name = msg.name.split('.')[-1]
        tool_content = str(msg.content)
        with st.expander(f"🛠️ Tool Call: `{tool_name}`", expanded=False):
            st.code(tool_content, language="text", line_numbers=True)

# --- Input and Control Area ---
prompt = st.text_area(
    "What would you like to build?",
    placeholder="e.g., Make a simple blog with a homepage and a posts page.",
    height=100
)

if st.button("🚀 Build Application", type="primary", use_container_width=True):
    # Validate that all inputs are provided
    if not all([tavily_api_key, groq_api_key, google_api_key, e2b_api_key,]):
        st.error("Please enter all the required API keys in the sidebar.")
    elif not prompt:
        st.warning("Please enter a prompt to build the application.")
    else:
        # Clean up previous run's output and logs
        if os.path.exists("output"):
            shutil.rmtree("output")
        st.session_state.log_messages = []

        # --- CRITICAL STEP ---
        # Set environment variables from the user's input.
        # This MUST be done before importing the agents file.
        os.environ["TAVILY_API_KEY"] = tavily_api_key
        os.environ["GROQ_API_KEY"] = groq_api_key
        os.environ["GOOGLE_API_KEY"] = google_api_key
        os.environ["E2B_API_KEY"] = e2b_api_key
        
        
        # --- CRITICAL STEP ---
        # Import the supervisor object now that the environment variables are set.
        from agents import supervisor

        user_input = {"messages": [{"role": "user", "content": prompt}]}
        
        st.header("📢 Agent Activity Log", divider="rainbow")
        log_container = st.empty()

        with st.spinner("Agents are working... This might take a few minutes."):
            # Use a unique config for each run to avoid state conflicts
            config = {"configurable": {"thread_id": f"streamlit-run-{time.time()}"}}
            
            for chunk in supervisor.stream(user_input, config=config):
                # The structure of chunks from the supervisor is a bit different
                if "supervisor" in chunk:
                    for message in chunk["supervisor"].get("messages", []):
                        st.session_state.log_messages.append(message)
                
                # Re-render the entire log on each update
                with log_container.container():
                    for log_msg in st.session_state.log_messages:
                        render_message(log_msg)
        
        st.success("✅ Workflow completed successfully!")

        st.header("🎉 Your Application is Ready!", divider="rainbow")
        
        output_files = {
            "📄 Frontend (index.html)": "output/index.html",
            "🐍 Backend (backend.py)": "output/backend.py",
            "🧪 Tests (test_app.py)": "output/test_app.py",
            "📖 README.md": "output/readme.md"
        }
        
        tabs = st.tabs(list(output_files.keys()))
        
        for tab, (label, filepath) in zip(tabs, output_files.items()):
            with tab:
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read()
                    
                    language = "python" if filepath.endswith(".py") else "html" if filepath.endswith(".html") else "markdown"
                    st.code(content, language=language, line_numbers=True)

                    mime_type = "text/plain"
                    if filepath.endswith(".html"): mime_type = "text/html"
                    elif filepath.endswith(".md"): mime_type = "text/markdown"
                    
                    st.download_button(
                        label=f"📥 Download {os.path.basename(filepath)}",
                        data=content,
                        file_name=os.path.basename(filepath),
                        mime=mime_type,
                        use_container_width=True
                    )
                except FileNotFoundError:
                    st.warning(f"File `{os.path.basename(filepath)}` was not generated by the agent.")

