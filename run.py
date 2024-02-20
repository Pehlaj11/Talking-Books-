import streamlit as st
import subprocess

def main():
    st.set_page_config(page_title="PDF Chatbot Display Page", page_icon=":Books")
    st.title("Welcome to PDF Chatbot")

    # Display options to the user
    user_choice = st.radio("Choose an option:", ["Temporary PDF", "Store PDF"])

    if user_choice == "Temporary PDF":
        st.markdown("### Redirecting to Temporary PDF Chat...")

        # Run main.py using subprocess
        try:
            subprocess.run(["streamlit", "run", "temporaryPDF.py"], check=True)
            st.success("Redirection to Temporary PDF Chat completed successfully!")
        except subprocess.CalledProcessError as e:
            st.error(f"Error during redirection: {e}")

    elif user_choice == "Store PDF":
        st.markdown("### Redirecting to Store PDF App...")

        # Run app.py using subprocess
        try:
            subprocess.run(["streamlit", "run", "StorePDF.py"], check=True)
            st.success("Redirection to Store PDF App completed successfully!")
        except subprocess.CalledProcessError as e:
            st.error(f"Error during redirection: {e}")

if __name__ == "__main__":
    main()
