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

question_description = {
    "Question 1": """
    Calculating Virus Spread
    People who study epidemiology use models to analyze the spread of disease. In this problem, we use a simple model.
    When a person has a disease, they infect exactly R other people but only on the very next day. No person is infected more than once. 
    We want to determine when a total of more than P people have had the disease.
    
    Input Specification
    There are three lines of input. Each line contains one positive integer. 
    The first line contains the value of P. 
    The second line contains N, the number of people who have the disease on Day 0. 
    The third line contains the value of R. Assume that P ≤ 10^7 and N ≤ P and R ≤ 10.
    
    Output Specification
    Output the number of the first day on which the total number of people who have had the disease is greater than P.
    """,
    "Question 2": """
    Eating Gems
    When I eat my Gems (a type of chocolate) I always eat the red ones last. I separate them into their color groups and 
    I start by eating the orange ones, then blue, green, yellow, pink, violet, brown and finally red. The red ones  are the best, 
    so I eat them slowly one at a time. The other colors I eat quickly by the handful (my hand can hold a maximum of 7 Gems). 
    I always finish all the Gems of one color before I move on to the next, so sometimes the last handful of a color isn't a full one.
    But wait, there's more! I have turned my Gem-eating into a science. I know it always takes me exactly  
    13 seconds to eat a handful of non-red Gems and I adjust my chewing rate so that I always take 13 seconds even if my hand is not 
    completely full. When I eat the red Gems I like to take my time, so it takes me exactly  16  seconds to eat each one. 
    I have a big box of Gems. After  I've finished sorting the colors, how long will it take me to eat them?
    The input will contain N lines ( 50 ≤ N ≤ 200 ), where each line holds the color of a single Gems in lower case. 
    Then the last line will read `end of box` meaning there are no more Gems in the box for that test case. Your program should output a 
    single line indicating how long (in seconds) it will take me to eat the entire box according to the rules given above. 
    """,
    "Question 3": """
    It is a well-researched fact that men in a restroom generally prefer to maximize  their distance from already occupied stalls, 
    by occupying the middle of the longest sequence of unoccupied places. For example, consider the situation where all ten stalls are 
    empty. - _ _ _ _ _ _ _ _ _ _. The first visitor will occupy a middle position: _ _ _ _ X _ _ _ _ _. The next visitor will be in the 
    middle of the empty area at the right.    _ _ _ _ X _ _ X _ _. Given an array of bool values, where true indicates an occupied stall, 
    find the position for the next visitor. Your computation should be placed in a function ``next_visitor(bool occupied[], int stalls)"""
}
print(question_description['Question 1'])
# Function to serialize chat messages to JSON-serializable format with timestamps
def serialize_chat_messages(chat_history, language):
    serialized_messages = []
    for message in chat_history:
        if isinstance(message, SystemMessage):
            serialized_messages.append({'type': 'system', 'content': str(message.content), 'timestamp': datetime.now(), 'language': language})
        elif isinstance(message, HumanMessage):
            serialized_messages.append({'type': 'human', 'content': str(message.content), 'timestamp': datetime.now(), 'language': language})
        elif isinstance(message, AIMessage):
            serialized_messages.append({'type': 'ai', 'content': str(message.content), 'timestamp': datetime.now(), 'language': language})
    return serialized_messages


MONGO_URL="mongodb+srv://aahalani:1234@cluster0.2qrozjw.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
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
def save_chat_history(user_id, chat_history, language):
    serialized_chat = serialize_chat_messages(chat_history, language)
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


def gptModel(input_user, language, user_id, question):
    update_language_preference(user_id, language)
    print(f"Language: {language}")
    print(f"Question: {question}")
    if language == 'Marathi':
        chat = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
        messages = [
            SystemMessage(content=f"{SystemPrompt}"),
            HumanMessage(content=
                        f"""
                        You are mentoring a student who is trying to solve the following programming problem:\n\"{question_description[question]}\"\n"
                        The student will ask questions related to the problem. DO NOT OUTPUT THE SOLUTION OF THE ENTIRE PROBLEM. You can provide hints and suggestions to their questions. If they have questions related to programming concepts, you can answer them by providing snippets of code.\n
                        Only provide answers if it is related to the question.\n
                        Provide the answer in Marathi\n
                        The student's question is: {input_user}
                        """),
        ]
    elif language == 'English':
        chat = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
        messages = [
            SystemMessage(content=f"{SystemPrompt}"),
            HumanMessage(content=
                        f"""
                        You are mentoring a student who is trying to solve the following programming problem:"{question_description[question]}
                        The student has to write code in C. The student will ask questions related to the problem. DO NOT OUTPUT THE SOLUTION OF THE ENTIRE PROBLEM. You can provide hints and suggestions to their questions. If they have questions related to programming concepts, you can answer them by providing snippets of code.\n
                        Only provide answers if it is related to the question.\n
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
                st.sidebar.success("Registration successful. You can now login.")
            
        else:
            username = st.sidebar.text_input("Username")
            password = st.sidebar.text_input("Password", type="password")
            if st.sidebar.button("Login"):
                if check_login(username, password):
                    st.session_state['logged_in'] = True
                    st.session_state['user_id'] = username
                    st.experimental_rerun()  # Refresh the page
                else:
                    st.sidebar.error("Incorrect username or password.")

    if 'logged_in' in st.session_state and st.session_state['logged_in']:
        user_id = st.session_state['user_id']
        key = f"messages_{user_id}"
        if key not in st.session_state:
            st.session_state[key] = [
                SystemMessage(content="You are a translating bot.")
            ]
        

        st.header(f"Chatbot (User: {user_id})")
        st.sidebar.title("Navigation")
        page = st.sidebar.radio("Go to", ["Question 1", "Question 2", "Question 3"])

        language = st.sidebar.selectbox("Output Language for the Chatbot", ['Marathi', 'English'])

        if page == "Question 1":
            st.subheader("Question 1")
            st.image("./q1_1.png")
            st.image("./q1_2.png")
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
                st.text_area("Copy Paste your code here and click submit to save it:", key="text_area_Question 1", height=100)

        elif page == "Question 2":
            st.subheader("Question 2")
            st.image("./q2_1.png")
            st.image("./q2_2.png")
            st.image("./q2_3.png")
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
                st.text_area("Copy Paste your code here and click submit to save it:", key="text_area_Question 2", height=100)

        elif page == "Question 3":
            st.subheader("Question 3")
            st.image("./q3.png")
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
                st.text_area("Copy Paste your code here and click submit to save it:", key="text_area_Question 3", height=100)
        if st.button("Submit"):
            handle_submit(page, st.session_state[f"text_area_{page}"])
        
        def clear_input():
            if user_input:  # Check if there is user input
                    st.session_state[key].append(HumanMessage(content=user_input))
                    with st.spinner("Thinking..."):
                        response = gptModel(user_input, language, user_id, page)
                    st.session_state[key].append(
                        AIMessage(content=response))

                    # Save chat history to a file
                    chat_history = st.session_state.get(key, [])
                    save_chat_history(user_id, chat_history, language)

                    # Clear the input box after sending the message
                    st.session_state[f"user_input_{user_id}"] = ""

        def clear_chat():
            st.session_state[key] = []  # Clear chat history

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
            
            if st.sidebar.button("Clear Chat", on_click=clear_chat):
                pass

if __name__ == '__main__':
    main()
