# https://blog.streamlit.io/build-a-chatbot-with-custom-data-sources-powered-by-llamaindex/
import os
import streamlit as st
from llama_index import VectorStoreIndex, ServiceContext, Document
from llama_index import SimpleDirectoryReader
from llama_index.llms import Ollama

# OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'localhost')
OLLAMA_HOST = "localhost"
print(f"Connecting to ollama server {OLLAMA_HOST}")
# connect to ollama service running on OpenShift
my_llm = Ollama(model="mistral", base_url="http://"+OLLAMA_HOST+":11434")

system_prompt = \
    "You are Linuxbot, an expert on Linux and Linus Torvalds and your job is to answer questions about these two topics." \
    "Assume that all questions are related to Linus Torvalds or Linux." \
    "Keep your answers to a few sentences and based on context – do not hallucinate facts." \
    "Always try to cite your source document."

st.title("Linuxbot 🐧🤖")
st.subheader("Everything you want to know about Linux or Linus")

if "messages" not in st.session_state.keys(): # Initialize the chat message history
    st.session_state.messages = [
        {"role": "assistant", "content": "Ask me a question about Linus or Linux"}
    ]

@st.cache_resource(show_spinner=False)
def load_data(_llm):
    with st.spinner(text="Loading and indexing the document data – might take 1-2 minutes."):
        reader = SimpleDirectoryReader(input_dir="./docs", recursive=True)
        docs = reader.load_data()
        service_context = ServiceContext.from_defaults(llm=_llm, embed_model="local")
        index = VectorStoreIndex.from_documents(docs, service_context=service_context)
        return index

index = load_data(my_llm)

chat_engine = index.as_chat_engine(
    chat_mode="context", verbose=True, system_prompt=system_prompt
)

if prompt := st.chat_input("Ask me a question about Linus or Linux"): 
    st.session_state.messages.append({"role": "user", "content": prompt})
# Display previous chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Generate a new response if last message is not from assistant
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Querying..."):
            streaming_response = chat_engine.stream_chat(prompt)
            placeholder = st.empty()
            full_response = ''
            for token in streaming_response.response_gen:
                full_response += token
                placeholder.markdown(full_response)
            placeholder.markdown(full_response)
            message = {"role": "assistant", "content": full_response}
            st.session_state.messages.append(message) # Add response to message history