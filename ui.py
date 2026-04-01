import streamlit as st
from datetime import datetime
import requests
import os 


if "infra_ready" not in st.session_state:
    with st.spinner("🔧 Initializing Qdrant & Docker..."):
        from setup import bootstrap
        bootstrap()
    st.session_state["infra_ready"] = True

os.environ["TOKENIZERS_PARALLELISM"] = "false"

API_URL = "http://localhost:8000/api/v1/chat/query"
DELETE_URL = "http://localhost:8000/api/v1/delete/memory"



# --------------------------------------------------------
# Streamlit App Configuration
# --------------------------------------------------------
st.set_page_config(
    page_title="🧠 Cognitive Digital Twin Chat",
    page_icon="🧠",
    layout="wide",
)

# --------------------------------------------------------
# Initialize DigitalTwin once
# --------------------------------------------------------
# if "twin" not in st.session_state:
#     st.session_state.messages = []  # store chat history

if "messages" not in st.session_state:
    st.session_state.messages = []


# --------------------------------------------------------
# Header
# --------------------------------------------------------
st.markdown(
    """
    <h2 style="text-align:center;">🧠 Cognitive Digital Twin Interface</h2>
    <p style="text-align:center; color:gray;">
    Your AI Twin that remembers, reasons, and responds intelligently.
    </p>
    <hr>
    """,
    unsafe_allow_html=True
)

# --------------------------------------------------------
# Chat Container
# --------------------------------------------------------
chat_container = st.container()

with chat_container:
    # Display previous chat messages
    for msg in st.session_state.messages:
        role = msg["role"]
        if role == "user":
            with st.chat_message("user"):
                st.markdown(f"🧍‍♂️ **You:** {msg['content']}")
        else:
            response = msg["response"]
            with st.chat_message("assistant"):
                st.markdown(f"🤖 **AssistantBot:** {response['response']}")

                # Expandable section for details
                with st.expander("🔍 View Full Execution Details"):
                    st.markdown("### 🧠 Cognitive Processing Details")
                    st.markdown(
                        f"""
                        <div style='font-size:13px; color:gray;'>
                        ⏱️ <b>Time:</b> {response.get('timestamp_id', 'N/A')}  
                        ✅ <b>Status:</b> {response.get('status', 'N/A')}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    # Label predictions
                    st.markdown("#### 🔎 Label Predictions")
                    st.markdown(
                        f"""
                        - 🧭 **Operation Type (Attention Head):** `{response.get('operation', 'unknown')}`  
                        - 🧠 **Memory Type:** `{response.get('memory_type', 'unknown')}`  
                        - 💬 **Answer Type:** `{response.get('answer', 'unknown')}`
                        """,
                        unsafe_allow_html=True
                    )
                    
                    emotions = response.get('emotions')
                    if emotions and isinstance(emotions, dict) and len(emotions) > 0:
                        st.markdown("#### 💫 Emotional State (Sorted by Intensity)")

                        cols = st.columns(3)
                        for idx, (emotion, value) in enumerate(emotions.items()):
                            with cols[idx % 3]:
                                st.metric(label=emotion, value=f"{value*100:.1f}%")
                                st.progress(value)
                    else:
                            st.info("No emotion data available yet.")
                        
                    # Optional backend details
                    if "raw_output" in response:
                        st.markdown("#### 🧮 Raw Model Output")
                        st.code(response["raw_output"], language="json")

                    if "logs" in response:
                        st.markdown("#### 📜 Logs / Debug Info")
                        st.text(response["logs"])

                st.markdown("---")

# --------------------------------------------------------
# User Input Section
# --------------------------------------------------------
query = st.chat_input("Type your query (e.g., 'Remember my meeting at 2 PM')")

if query:
    # Display user message
    st.chat_message("user").markdown(f"🧍‍♂️ **You:** {query}")
    st.session_state.messages.append({"role": "user", "content": query})

    # Process query with DigitalTwin
    with st.spinner("Thinking..."):
        
        res = requests.post(
            API_URL,
            json={"query": query, "agent": "AssistantBot"},
            timeout=500
        )

    if res.status_code != 200:
        st.error("Backend error")
        st.stop()

    response = res.json()
    emotions = response.get("emotions", {})
    
    # Display assistant message
    with st.chat_message("assistant"):
        st.markdown(f"🤖 **AssistantBot:** {response['response']}")

        # Expandable section for details
        with st.expander("🔍 View Full Execution Details"):
            st.markdown("### 🧠 Cognitive Processing Details")
            st.markdown(
                f"""
                <div style='font-size:13px; color:gray;'>
                ⏱️ <b>Time:</b> {response.get('timestamp_id', 'N/A')}  
                ✅ <b>Status:</b> {response.get('status', 'N/A')}
                </div>
                """,
                unsafe_allow_html=True
            )

            # Label predictions
            st.markdown("#### 🔎 Label Predictions")
            st.markdown(
                f"""
                - 🧭 **Operation Type (Attention Head):** `{response.get('operation', 'unknown')}`  
                - 🧠 **Memory Type:** `{response.get('memory_type', 'unknown')}`  
                - 💬 **Answer Type:** `{response.get('answer', 'unknown')}`
                """,
                unsafe_allow_html=True
            )
            
            
            if emotions and isinstance(emotions, dict) and len(emotions) > 0:
                st.markdown("#### 💫 Emotional State (Sorted by Intensity)")

                cols = st.columns(3)
                for idx, (emotion, value) in enumerate(emotions.items()):
                    percent = value * 100
                    with cols[idx % 3]:
                            st.metric(label=emotion, value=f"{value*100:.1f}%")
                            st.progress(value)
            else:
                st.info("No emotion data available yet.")
                
            # Optional backend details
            if "raw_output" in response:
                st.markdown("#### 🧮 Raw Model Output")
                st.code(response["raw_output"], language="json")

            if "logs" in response:
                st.markdown("#### 📜 Logs / Debug Info")
                st.text(response["logs"])

        st.markdown("---")

    # Save assistant response
    st.session_state.messages.append({"role": "assistant", "response": response})

# --------------------------------------------------------
# Sidebar Controls
# --------------------------------------------------------
with st.sidebar:
    st.markdown("## ⚙️ Controls")
    if st.button("🧹 Clear Chat History"):
        try:
            res = requests.delete(DELETE_URL, timeout=60)
            data = res.json()

            if res.status_code == 200:
                
                st.session_state.messages = []
                st.success(data["message"])
            else:
                st.error(data)

        except Exception as e:
            st.error(f"API Error: {e}")

    st.markdown("---")
    st.markdown("### 📋 Info")
    st.info("""
    **Operation Types:**
    - `memory_in`: Storing new information  
    - `memory_out`: Retrieving stored memory  
    - `cur`: Direct reasoning (no memory access)

    **Memory Types:**
    - `STM`: Short-Term Memory  
    - `LTM`: Long-Term Memory  
    - `none`: No memory involved

    **Answer Types:**
    - `single`: One focused answer  
    - `multiple`: Combined/multi-part answer  
    - `none`: No clear answer type
    """)

# --------------------------------------------------------
# Footer
# --------------------------------------------------------
st.markdown(
    """
    <hr>
    <div style='text-align:center; color:gray; font-size:13px;'>
        🧠 Built with ❤️ using Streamlit + Ollama + Custom Memory Systems
    </div>
    """,
    unsafe_allow_html=True
)
