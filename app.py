import streamlit as st
import openai
import time

# ---------------------------
# CONFIGURACIÓN SEGURA
# ---------------------------
openai.api_key = st.secrets["openai_api_key"]
assistant_id = st.secrets["assistant_id"]

# ---------------------------
# CONFIGURACIÓN DE LA APP
# ---------------------------
st.set_page_config(page_title="Asistente TUPA", page_icon="🤖", layout="centered")

# Estilos personalizados con compatibilidad para Chrome
st.markdown("""
    <style>
        html, body, .stApp {
            background-color: white !important;
            color: black !important;
        }
        .stMarkdown h1, .stMarkdown h2, .stMarkdown p,
        .stChatMessage p, .stChatMessage ul, .stChatMessage ol, .stChatMessage li,
        .stChatMessage span, .stChatMessage div {
            color: black !important;
        }
        input[type="text"] {
            background-color: white !important;
            color: black !important;
            border: 2px solid black !important;
            border-radius: 20px !important;
            padding: 10px !important;
        }
        input[type="text"]::placeholder {
            color: #888 !important;
        }
        .stChatInputContainer button {
            background-color: black !important;
            color: white !important;
            border: 2px solid black !important;
            border-radius: 20px !important;
        }
    </style>
""", unsafe_allow_html=True)

# Logo superior
st.image("https://piasar-capacita.creation.camp/wp-content/uploads/sites/55/2021/12/Logo-1-MVCS.png", width=300)

# Título y subtítulo
st.title("TUAI - Texto Único asistido por IA")
st.markdown("Haz tus consultas sobre trámites administrativos y obtén respuestas claras y rápidas.")

# ---------------------------
# ESTADO INICIAL
# ---------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.ultima_pregunta = ""
    st.session_state.thread_id = None
    st.session_state.historial_preguntas = []

# ---------------------------
# ENTRADA DEL USUARIO
# ---------------------------
user_input = st.chat_input("Escribe tu consulta aquí...")

# Palabras clave que indican aclaración o referencia al contexto anterior
frases_contextuales = [
    "no entendí", "explica", "dudas", "más claro", "más simple", "no me parece",
    "repite", "aclara", "sencillo", "para qué sirve", "cuál es el objetivo", 
    "qué finalidad tiene", "por qué se hace", "qué implica", "cuál es el propósito",
    "a qué se refiere", "qué significa esto", "no quedó claro", "detalla mejor",
    "en otras palabras", "hazlo más fácil", "explícame mejor", "no me queda claro"
]
es_contextual = user_input and any(p in user_input.lower() for p in frases_contextuales)

if user_input:
    if es_contextual and st.session_state.historial_preguntas and st.session_state.thread_id:
        referencia = st.session_state.historial_preguntas[-1]
        prompt = f"Responde con más claridad sobre esto: {referencia}"
    else:
        prompt = user_input
        st.session_state.ultima_pregunta = user_input
        st.session_state.historial_preguntas.append(user_input)
        thread = openai.beta.threads.create()
        st.session_state.thread_id = thread.id

    st.session_state.messages.append(("usuario", user_input))

    openai.beta.threads.messages.create(
        thread_id=st.session_state.thread_id,
        role="user",
        content=prompt
    )

    run = openai.beta.threads.runs.create(
        thread_id=st.session_state.thread_id,
        assistant_id=assistant_id
    )

    with st.spinner("Generando respuesta..."):
        while True:
            status_info = openai.beta.threads.runs.retrieve(
                thread_id=st.session_state.thread_id,
                run_id=run.id
            )
            if status_info.status == "completed":
                break
            elif status_info.status == "failed":
                st.error("Hubo un error al procesar la respuesta")
                break
            time.sleep(1)

        messages = openai.beta.threads.messages.list(
            thread_id=st.session_state.thread_id
        )

        for msg in reversed(messages.data):
            if msg.role == "assistant":
                respuesta = msg.content[0].text.value
                st.session_state.messages.append(("asistente", respuesta))
                break

# ---------------------------
# MOSTRAR EL HISTORIAL DEL CHAT
# ---------------------------
for rol, mensaje in st.session_state.messages:
    with st.chat_message("Usuario" if rol == "usuario" else "Asistente"):
        st.markdown(mensaje)
