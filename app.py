import streamlit as st
import sqlite3
from mirbit import MirbotAI


ai = MirbotAI()

st.set_page_config(page_title="Mirbot AI Chat", layout="wide")


conn = sqlite3.connect('chat_history.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS chats (chat_name TEXT, role TEXT, content TEXT)''')
conn.commit()


def save_message(chat_name, role, content):
    c.execute("INSERT INTO chats (chat_name, role, content) VALUES (?, ?, ?)", (chat_name, role, content))
    conn.commit()

def get_chat_messages(chat_name):
    c.execute("SELECT role, content FROM chats WHERE chat_name=?", (chat_name,))
    return c.fetchall()

def get_all_chat_names():
    c.execute("SELECT DISTINCT chat_name FROM chats")
    return [row[0] for row in c.fetchall()]


st.sidebar.title("💬 MirbotAI Chat")

chat_names = get_all_chat_names()
chat_names.insert(0, "New Chat")
selected_chat = st.sidebar.selectbox("Select Chat", chat_names)

if "current_chat" not in st.session_state:
    st.session_state.current_chat = "New Chat"

if st.sidebar.button("➕ New Chat"):
    new_chat_name = f"Chat {len(chat_names)}"
    st.session_state.current_chat = new_chat_name

if selected_chat != "New Chat":
    st.session_state.current_chat = selected_chat

chat_title = st.session_state.current_chat
st.title(f"🧠 {chat_title}")

if chat_title != "New Chat":
    messages = get_chat_messages(chat_title)
else:
    messages = []


chat_placeholder = st.container()
with chat_placeholder:
    for role, content in messages:
        if role == "user":
            st.markdown(f"""
            <div style='background-color:#DCF8C6; padding:10px; border-radius:12px; margin-bottom:5px; text-align:right;'>
            <strong>🧑‍💻 You:</strong><br>{content}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style='background-color:#F1F0F0; padding:10px; border-radius:12px; margin-bottom:5px; text-align:left;'>
            <strong>🤖 MirbotAI:</strong><br>{content}
            </div>
            """, unsafe_allow_html=True)


if chat_title != "New Chat":
    user_input = st.chat_input("💬 Type your message")

    if user_input and user_input.strip() != "":
        save_message(chat_title, "user", user_input)

        ai_response = ai.respond(user_input)

        save_message(chat_title, "ai", ai_response)

        # Refresh messages locally
        messages = get_chat_messages(chat_title)

        with chat_placeholder:
            for role, content in messages:
                if role == "user":
                    st.markdown(f"""
                    <div style='background-color:#DCF8C6; padding:10px; border-radius:12px; margin-bottom:5px; text-align:right;'>
                    <strong>🧑‍💻 You:</strong><br>{content}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style='background-color:#F1F0F0; padding:10px; border-radius:12px; margin-bottom:5px; text-align:left;'>
                    <strong>🤖 MirbotAI:</strong><br>{content}
                    </div>
                    """, unsafe_allow_html=True)


custom_css = """
<style>
textarea {
    border-radius: 10px;
    padding: 8px;
}
button[kind="primary"] {
    background-color: #4CAF50;
    color: white;
    border-radius: 8px;
}
.sidebar .css-1d391kg {
    background-color: #f0f2f6;
}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

