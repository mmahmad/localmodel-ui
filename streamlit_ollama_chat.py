# https://blog.streamlit.io/build-a-chatbot-with-custom-data-sources-powered-by-llamaindex/
import os
import streamlit as st
from llama_index.llms import Ollama
from llama_index.llms import ChatMessage

# OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'localhost')
OLLAMA_HOST = "localhost"
# print(f"Connecting to ollama server {OLLAMA_HOST}")

# connect to ollama service running locally
my_llm = Ollama(model="mistral", base_url="http://"+OLLAMA_HOST+":11434")

st.title("Local Bot")
st.subheader("All messages are local to the Streamlit app and not stored on the server.")

if "messages" not in st.session_state.keys(): # Initialize the chat message history
    st.session_state.messages = [
        ChatMessage(
            role="system", content="You are a helpful assistant."
        )
]

if prompt := st.chat_input("Ask me a question about Linus or Linux"): 
    st.session_state.messages.append(ChatMessage(role="user", content=prompt),)

# Display previous chat messages
for message in st.session_state.messages:
    if message.role == "system":
        continue
    with st.chat_message(message.role):
        st.write(message.content)

# Generate a new response if last message is not from assistant
if st.session_state.messages[-1].role != "assistant" and st.session_state.messages[-1].role != "system":
    with st.chat_message("assistant"):
        with st.spinner("Receiving response..."):
            streaming_response = my_llm.stream_chat(messages=st.session_state.messages)
            placeholder = st.empty()
            full_response = ''
            for r in streaming_response:
                full_response += r.delta
                placeholder.markdown(full_response)
            placeholder.markdown(full_response)
            message = ChatMessage(role="assistant", content=full_response)
            st.session_state.messages.append(message) # Add response to message history