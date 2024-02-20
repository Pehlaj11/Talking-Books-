import streamlit as st
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import faiss
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
import os
from htmlTemplates import css, bot_template, user_template
from dotenv import load_dotenv

def get_pdf_text(pdf, encoding='utf-8'):
    text = ""
    pdf_reader = PdfReader(pdf)
    for page in pdf_reader.pages:
        text += page.extract_text().encode('latin1', 'replace').decode(encoding, 'replace')
    return text

def get_text_chunks(text):
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    return chunks

def get_vectorstore(text_chunks):
    embeddings = OpenAIEmbeddings()
    vectorstore = faiss.FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    return vectorstore

def get_conversation_chain(vectorstore):
    llm = ChatOpenAI()
    memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True)
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        memory=memory
    )
    return conversation_chain

def handle_userinput(user_question):
    response = st.session_state.conversation({'question': user_question})
    st.session_state.chat_history = response['chat_history']

    for i, message in enumerate(st.session_state.chat_history):
        if i % 2 == 0:
            st.write(user_template.replace("{{MSG}}", message.content), unsafe_allow_html=True)
        else:
            st.write(bot_template.replace("{{MSG}}", message.content), unsafe_allow_html=True)

def main():
    load_dotenv()
    st.set_page_config(page_title="Chat with Multiple PDFs", page_icon=":Books")
    st.write(css, unsafe_allow_html=True)

    st.sidebar.markdown("---")
    st.sidebar.subheader("About")
    st.sidebar.info("This app allows you to chat with multiple PDFs.")
    st.sidebar.info("Select an option and start chatting!")

    st.header("Welcome to PDF Chatbot")

    # Display options to the user
    user_choice = st.radio("Choose an option:", ["Chat with PDF", "Store PDF permanently"])

    if user_choice == "Chat with PDF":
        st.header("Chat with PDF")
        st.warning("Select a permanently stored PDF to start chatting.")

        # Display available PDFs and allow the user to select one for chatting
        available_pdfs = [pdf for pdf in os.listdir("stored_chunks") if os.path.isdir(os.path.join("stored_chunks", pdf))]
        if available_pdfs:
            st.subheader("Available PDFs")
            selected_pdf = st.selectbox("Select a PDF to chat with:", available_pdfs)
            st.success(f"Chunks of {selected_pdf} are available!")

            # Chat with the selected PDF
            user_question = st.text_input("Ask a question about the stored PDF:")
            if user_question:
                stored_chunks_folder = os.path.join("stored_chunks", selected_pdf)
                vectorstore = get_vectorstore(
                    [open(os.path.join(stored_chunks_folder, file), encoding="utf-8").read() for file in sorted(os.listdir(stored_chunks_folder))]
                )
                st.session_state.conversation = get_conversation_chain(vectorstore)
                response = st.session_state.conversation({'question': user_question})
                st.session_state.chat_history = response['chat_history']

                for i, message in enumerate(st.session_state.chat_history):
                    if i % 2 == 0:
                        st.write(f"User: {message.content}")
                    else:
                        st.write(f"Bot: {message.content}")

    elif user_choice == "Store PDF permanently":
        st.header("Store PDF permanently")

        # Option to upload new PDFs for permanent storage
        uploaded_pdfs = st.file_uploader("Upload new PDFs for permanent storage:", type=["pdf"], accept_multiple_files=True)
        if uploaded_pdfs is not None:
            for uploaded_pdf in uploaded_pdfs:
                with st.spinner(f"Storing {uploaded_pdf.name} permanently"):
                    raw_text = get_pdf_text(uploaded_pdf, encoding='utf-8')
                    text_chunks = get_text_chunks(raw_text)

                    # Create a folder for each PDF
                    stored_chunks_folder = os.path.join("stored_chunks", uploaded_pdf.name.replace(".pdf", ""))
                    os.makedirs(stored_chunks_folder, exist_ok=True)

                    # Store chunks locally for permanent storage
                    for i, chunk in enumerate(text_chunks):
                        chunk_filename = os.path.join(stored_chunks_folder, f"chunk_{i + 1}.txt")
                        with open(chunk_filename, "w", encoding="utf-8") as file:
                            file.write(chunk)

                    st.success(f"{uploaded_pdf.name} stored permanently!")

if __name__ == "__main__":
    main()
