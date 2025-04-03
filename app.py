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
st.set_page_config(page_title="Asistente TUPA", page_icon="🤖")
st.title("Asistente Virtual sobre el TUPA")
st.markdown("Haz tus consultas sobre trámites administrativos y obtén respuestas claras y rápidas.")

# ---------------------------
# ESTADO INICIAL
# ---------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.ultima_pregunta = ""
    st.session_state.thread_id = None

# ---------------------------
# ENTRADA DEL USUARIO
# ---------------------------
user_input = st.chat_input("Escribe tu consulta aquí...")

# Palabras clave que indican aclaración o seguimiento implícito
frases_contextuales = [
    "no entendí", "explica", "dudas", "más claro", "más simple", "no me parece",
    "repite", "aclara", "sencillo", "para qué sirve", "cuál es el objetivo", 
    "qué finalidad tiene", "por qué se hace", "qué implica", "cuál es el propósito",
    "a qué se refiere", "qué significa esto", "no quedó claro", "detalla mejor",
    "en otras palabras", "hazlo más fácil"
]
es_contextual = user_input and any(p in user_input.lower() for p in frases_contextuales)

if user_input:
    # Si es contextual y hay una pregunta anterior, se reformula
    if es_contextual and st.session_state.ultima_pregunta and st.session_state.thread_id:
        prompt = f"Responde con más claridad sobre esto: {st.session_state.ultima_pregunta}"
    else:
        prompt = user_input
        st.session_state.ultima_pregunta = user_input
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
