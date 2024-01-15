import streamlit as st
from streamlit_chat import message
from dotenv import load_dotenv
import os
import json

from langchain.chat_models import ChatOpenAI
from langchain.schema import (
    SystemMessage,
    HumanMessage,
    AIMessage
)

# Function to check the user login (placeholder for real authentication)
def check_login(username, password, registered_users):
    # Placeholder for user validation (replace with real validation logic)
    for user in registered_users:
        if user['username'] == username and user['password'] == password:
            return True
    return False

# Function to register a new user
def register_user(username, password):
    # Placeholder for user registration (replace with real registration logic)
    # Store the user credentials in a dictionary
    user_credentials = {
        'username': username,
        'password': password
    }
    return user_credentials

# Function to serialize chat messages to JSON-serializable format
def serialize_chat_messages(chat_history):
    serialized_messages = []
    for message in chat_history:
        if isinstance(message, SystemMessage):
            serialized_messages.append({'type': 'system', 'content': str(message.content)})
        elif isinstance(message, HumanMessage):
            serialized_messages.append({'type': 'human', 'content': str(message.content)})
        elif isinstance(message, AIMessage):
            serialized_messages.append({'type': 'ai', 'content': str(message.content)})
    return serialized_messages

# Function to save chat history to a file
def save_chat_history(user_id, chat_history):
    chat_file = f"chat_history_{user_id}.json"
    serialized_chat = serialize_chat_messages(chat_history)
    with open(chat_file, 'w') as file:
        json.dump(serialized_chat, file)

# Function to save registered users to a file
def save_registered_users(registered_users):
    users_file = "registered_users.json"
    with open(users_file, 'w') as file:
        json.dump(registered_users, file)

# Function to fetch registered users from a file
def fetch_registered_users():
    users_file = "registered_users.json"
    if os.path.exists(users_file):
        with open(users_file, 'r') as file:
            return json.load(file)
    else:
        return []

def init():
    load_dotenv()
    if os.getenv("OPENAI_API_KEY") is None or os.getenv("OPENAI_API_KEY") == "":
        print("OPENAI_API_KEY is not set")
        exit(1)
    else:
        print("OPENAI_API_KEY is set")

    st.set_page_config(
        page_title="Your Helper",
        page_icon="🤖"
    )

SystemPrompt = "You are a translating bot. "
# Who is tasked with translating English to Marathi. You are not allowed to translate technical terms such as C++, Hash function, etc. this is done to ensure the meaning of the text is not lost."
def gptModel(input_user):
    chat = ChatOpenAI(model_name="gpt-4-1106-preview", temperature=0)
    messages = [
        SystemMessage(content=f"{SystemPrompt}"),
        HumanMessage(content=
                    f"""Translate the phrase "{input_user}" to Marathi. However leave the technical programming terms in English and translate generic English words to Marathi. Do not translate the"""),
    ]
    response = chat(messages)
    # Log input and output to a text file
    # with open('log.txt', 'a') as log_file:
    #     log_file.write(f"Input to the LLM Model:\n System Prompt:{SystemPrompt}\n User Input:{input_user}\n")
    #     log_file.write(f"Output of the LLM Model:\n{response.content}\n")
    #     log_file.write("------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------\n")

    return response.content

def main():
    init()

    # Fetch registered users
    registered_users = fetch_registered_users()

    # Login and Registration form
    if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
        registration_mode = st.sidebar.checkbox("Register a new user")
        if registration_mode:
            new_username = st.sidebar.text_input("New Username")
            new_password = st.sidebar.text_input("New Password", type="password")
            if st.sidebar.button("Register"):
                user_credentials = register_user(new_username, new_password)
                registered_users.append(user_credentials)
                save_registered_users(registered_users)  # Save the updated list
                st.session_state['registered_users'] = registered_users
                st.sidebar.success("Registration successful. You can now login.")
        else:
            username = st.sidebar.text_input("Username")
            password = st.sidebar.text_input("Password", type="password")
            if st.sidebar.button("Login"):
                if check_login(username, password, registered_users):
                    st.session_state['logged_in'] = True
                    st.session_state['user_id'] = username
                else:
                    st.sidebar.error("Incorrect username or password.")

    if 'logged_in' in st.session_state and st.session_state['logged_in']:
        user_id = st.session_state['user_id']
        key = f"messages_{user_id}"
        if key not in st.session_state:
            st.session_state[key] = [
                SystemMessage(content="You are a translating bot.")
            ]

        st.header(f"GPT Helper (User: {user_id})")

        with st.sidebar:
            user_input = st.text_input("Your message: ", key=f"user_input_{user_id}")

            if user_input:
                st.session_state[key].append(HumanMessage(content=user_input))
                with st.spinner("Thinking..."):
                    response = gptModel(user_input)  # Use the gptModel function
                st.session_state[key].append(
                    AIMessage(content=response))

                # Save chat history to a file
                chat_history = st.session_state.get(key, [])
                save_chat_history(user_id, chat_history)

        messages = st.session_state.get(key, [])
        for i, msg in enumerate(messages[1:]):
            if i % 2 == 0:
                message(msg.content, is_user=True, key=f"{i}_{user_id}_user")
            else:
                message(msg.content, is_user=False, key=f"{i}_{user_id}_ai")

if __name__ == '__main__':
    main()
