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

# Estilos personalizados: fondo blanco y texto negro, sin barras negras
st.markdown("""
    <style>
        html, body, .stApp {
            background-color: white !important;
            color: black !important;
        }
        .stMarkdown h1, .stMarkdown h2, .stMarkdown p, .markdown-text-container,
        .stChatMessage p, .stChatMessage ul, .stChatMessage ol, .stChatMessage li,
        .stChatMessage span, .stChatMessage div {
            color: black !important;
        }
        .block-container {
            padding-top: 1rem;
        }
        .stChatMessage, .stChatInputContainer, .stTextInput, .stTextArea {
            background-color: white !important;
            color: black !important;
        }
        input, textarea {
            color: black !important;
        }
    </style>
""", unsafe_allow_html=True)

# Logo superior
st.image("https://piasar-capacita.creation.camp/wp-content/uploads/sites/55/2021/12/Logo-1-MVCS.png", width=200)

# Título y subtítulo
st.title("Asistente Virtual sobre el TUPA")
st.markdown("Haz tus consultas sobre trámites administrativos y obtén respuestas claras y rápidas.")

# ---------------------------
# ESTADO INICIAL
# ---------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.ultima_pregunta = ""
    st.session_state.thread_id = None
    st.session_state.historial_preguntas = []  # Lista de las últimas preguntas reales

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
    # Si es contextual, buscamos la última pregunta válida en el historial
    if es_contextual and st.session_state.historial_preguntas and st.session_state.thread_id:
        referencia = st.session_state.historial_preguntas[-1]  # la más reciente
        prompt = f"Responde con más claridad sobre esto: {referencia}"
    else:
        prompt = user_input
        st.session_state.ultima_pregunta = user_input
        st.session_state.historial_preguntas.append(user_input)
        # Nueva pregunta → nuevo thread
        thread = openai.beta.threads.create()
        st.session_state.thread_id = thread.id

    st.session_state.messages.append(("usuario", user_input))

    # Enviar el mensaje al modelo
    openai.beta.threads.messages.create(
        thread_id=st.session_state.thread_id,
        role="user",
        content=prompt
    )

    # Ejecutar el asistente
    run = openai.beta.threads.runs.create(
        thread_id=st.session_state.thread_id,
        assistant_id=assistant_id
    )

    # Esperar respuesta
    with st.spinner("Pensando..."):
        while True:
            status = openai.beta.threads.runs.retrieve(
                thread_id=st.session_state.thread_id,
                run_id=run.id
            )
            if status.status == "completed":
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
