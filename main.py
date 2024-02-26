import streamlit as st
from streamlit_chat import message
from dotenv import load_dotenv
import os
import json
import streamlit.components.v1 as components  
from pymongo import MongoClient
from langchain.chat_models import ChatOpenAI
from langchain.schema import (
    SystemMessage,
    HumanMessage,
    AIMessage
)
from datetime import datetime

# Function to serialize chat messages to JSON-serializable format with timestamps
def serialize_chat_messages(chat_history):
    serialized_messages = []
    for message in chat_history:
        if isinstance(message, SystemMessage):
            serialized_messages.append({'type': 'system', 'content': str(message.content), 'timestamp': datetime.now()})
        elif isinstance(message, HumanMessage):
            serialized_messages.append({'type': 'human', 'content': str(message.content), 'timestamp': datetime.now()})
        elif isinstance(message, AIMessage):
            serialized_messages.append({'type': 'ai', 'content': str(message.content), 'timestamp': datetime.now()})
    return serialized_messages


MONGO_URL="mongodb+srv://avvalhalani:1234@db.aeoo5eo.mongodb.net/?retryWrites=true&w=majority&appName=DB"
client = MongoClient(MONGO_URL)
db = client.DB_Dis

# MongoDB collections
users_collection = db.users
chat_history_collection = db.chat_history
submissions_collection = db.submissions

# Function to check the user login (placeholder for real authentication)
def check_login(username, password):
    user = users_collection.find_one({'username': username, 'password': password})
    return user is not None

# Function to register a new user
def register_user(username, password):
    user_credentials = {
        'username': username,
        'password': password,
        'language': 'Marathi',
        'created_at': datetime.now()
    }
    users_collection.insert_one(user_credentials)
    return user_credentials


def handle_submit(question, text):
    # Collect data from text inputs
    input_data = {
        'username': st.session_state['user_id'],
        'question': question,
        'answer': text,
        'timestamp': datetime.now()
    }

    # Save submission data to MongoDB
    save_submission(st.session_state['user_id'], input_data)

    st.success("Data submitted successfully!")

# Function to save chat history to MongoDB
def save_chat_history(user_id, chat_history):
    serialized_chat = serialize_chat_messages(chat_history)
    chat_history_collection.update_one(
        {'user_id': user_id},
        {'$set': {'chat_history': serialized_chat}},
        upsert=True
    )

# Function to save submissions to MongoDB
def save_submission(user_id, submission_data):
    submissions_collection.insert_one({
        'user_id': user_id,
        'submissions': submission_data
    })


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

def update_language_preference(username, language):
    users_collection.update_one(
        {'username': username},
        {'$set': {'language': language}},
        upsert=True
    )


def gptModel(input_user, language, user_id):
    update_language_preference(user_id, language)
    if language == 'Marathi':
        chat = ChatOpenAI(model_name="gpt-4-1106-preview", temperature=0)
        messages = [
            SystemMessage(content=f"{SystemPrompt}"),
            HumanMessage(content=
                        f"""
                        You are mentoring a student who is trying to solve the following programming problem:\n\"{questionDescription}\"\n"
                        The student will ask questions related to the problem. DO NOT OUTPUT THE SOLUTION OF THE ENTIRE PROBLEM. You can provide hints and suggestions to their questions. If they have questions related to programming concepts, you can answer them by providing snippets of code.\n
                        Only provide answers if it is related to the question.\n
                        Provide the answer in Marathi\n
                        The student's question is: {input_user}
                        """),
        ]
    elif language == 'English':
        chat = ChatOpenAI(model_name="gpt-4-1106-preview", temperature=0)
        messages = [
            SystemMessage(content=f"{SystemPrompt}"),
            HumanMessage(content=
                        f"""
                        You are mentoring a student who is trying to solve the following programming problem:"{questionDescription}
                        The student will ask questions related to the problem. DO NOT OUTPUT THE SOLUTION OF THE ENTIRE PROBLEM. You can provide hints and suggestions to their questions. If they have questions related to programming concepts, you can answer them by providing snippets of code.\n
                        Only provide answers if it is related to the question.\n
                        Provide the answer in Marathi\n
                        The student's question is: {input_user}

                        """),
        ]
    response = chat(messages)
    return response.content

def main():
    init()
    # Fetch registered users

    # Login and Registration form
    if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
        registration_mode = st.sidebar.checkbox("Register a new user")
        if registration_mode:
            new_username = st.sidebar.text_input("New Username")
            new_password = st.sidebar.text_input("New Password", type="password")
            if st.sidebar.button("Register"):
                user_credentials = register_user(new_username, new_password)
                # registered_users.append(user_credentials)
                # save_registered_users(registered_users)  # Save the updated list
                # st.session_state['registered_users'] = registered_users
                st.sidebar.success("Registration successful. You can now login.")
            
        else:
            username = st.sidebar.text_input("Username")
            password = st.sidebar.text_input("Password", type="password")
            if st.sidebar.button("Login"):
                if check_login(username, password):
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
        st.sidebar.title("Navigation")
        page = st.sidebar.radio("Go to", ["Question 1", "Question 2", "Question 3"])

        language = st.sidebar.selectbox("Select Language", ['Marathi', 'English'])

        if page == "Question 1":
            st.subheader("Question 1")
            st.image("./image 1.png", caption="Image 1")
            components.html(
                """
                <!DOCTYPE html>
                <html>
                    <head>
                        <title>Hello, World!</title>
                        <style>
                            body {
                                display: flex;
                                justify-content: flex-start;
                            }
                            iframe {
                                margin: 0;
                            }
                        </style>
                    </head>
                    <body>
                        <iframe width="700px" height="500px" src="https://www.programiz.com/c-programming/online-compiler/"></iframe>
                    </body>
                </html>
                """,
                height=500,
                width=700,
            )
        
            fetch_latest_submission = submissions_collection.find_one({'user_id': user_id, 'submissions.question': 'Question 1'}, sort=[('submissions.timestamp', -1)])
            if fetch_latest_submission:
                st.text_area("Your previous answer:", value=fetch_latest_submission['submissions']['answer'], height=100, key="text_area_Question 1")
            else:
                st.text_area("Enter your text here:", key="text_area_Question 1", height=100)

        elif page == "Question 2":
            st.subheader("Question 2")
            st.image("./image 2.png", caption="Image 2")
            components.html(
                """
                <!DOCTYPE html>
                <html>
                    <head>
                        <title>Hello, World!</title>
                        <style>
                            body {
                                display: flex;
                                justify-content: flex-start;
                            }
                            iframe {
                                margin: 0;
                            }
                        </style>
                    </head>
                    <body>
                        <iframe width="700px" height="500px" src="https://www.programiz.com/c-programming/online-compiler/"></iframe>
                    </body>
                </html>
                """,
                height=500,
                width=700,
            )
            fetch_latest_submission = submissions_collection.find_one({'user_id': user_id, 'submissions.question': 'Question 2'}, sort=[('submissions.timestamp', -1)])
            if fetch_latest_submission:
                st.text_area("Your previous answer:", value=fetch_latest_submission['submissions']['answer'], height=100, key="text_area_Question 2")
            else:
                st.text_area("Enter your text here:", key="text_area_Question 2", height=100)

        elif page == "Question 3":
            st.subheader("Question 3")
            st.image("./image 3.png", caption="Image 3")
            components.html(
                """
                <!DOCTYPE html>
                <html>
                    <head>
                        <title>Hello, World!</title>
                        <style>
                            body {
                                display: flex;
                                justify-content: flex-start;
                            }
                            iframe {
                                margin: 0;
                            }
                        </style>
                    </head>
                    <body>
                        <iframe width="700px" height="500px" src="https://www.programiz.com/c-programming/online-compiler/"></iframe>
                    </body>
                </html>
                """,
                height=500,
                width=700,
            )
            fetch_latest_submission = submissions_collection.find_one({'user_id': user_id, 'submissions.question': 'Question 3'}, sort=[('submissions.timestamp', -1)])
            if fetch_latest_submission:
                st.text_area("Your previous answer:", value=fetch_latest_submission['submissions']['answer'], height=100, key="text_area_Question 3")
            else:
                st.text_area("Enter your text here:", key="text_area_Question 3", height=100)
        if st.button("Submit"):
            handle_submit(page, st.session_state[f"text_area_{page}"])
        
        def clear_input():
            if user_input:  # Check if there is user input
                    st.session_state[key].append(HumanMessage(content=user_input))
                    with st.spinner("Thinking..."):
                        response = gptModel(user_input, language, user_id)
                    st.session_state[key].append(
                        AIMessage(content=response))

                    # Save chat history to a file
                    chat_history = st.session_state.get(key, [])
                    save_chat_history(user_id, chat_history)

                    # Clear the input box after sending the message
                    st.session_state[f"user_input_{user_id}"] = ""


        with st.sidebar:
            user_input = st.text_input("Your message: ", key=f"user_input_{user_id}")

            if st.sidebar.button("Send", on_click=clear_input):
                pass

            messages = st.session_state.get(key, [])
            for i, msg in enumerate(messages[1:]):
                if i % 2 == 0:
                    message(msg.content, is_user=True, key=f"{i}_{user_id}_user")
                else:
                    message(msg.content, is_user=False, key=f"{i}_{user_id}_ai")

if __name__ == '__main__':
    main()
