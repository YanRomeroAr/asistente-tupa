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
# GESTIÓN DE CONTEXTO CON THREAD PERSISTENTE
# ---------------------------
if "thread_id" not in st.session_state:
    thread = openai.beta.threads.create()
    st.session_state.thread_id = thread.id
    st.session_state.messages = []
    st.session_state.ultima_pregunta = ""

# ---------------------------
# ENTRADA DEL USUARIO
# ---------------------------
user_input = st.chat_input("Escribe tu consulta aquí...")

# Detectar si la entrada es una aclaración (tipo "no entendí") con coincidencia parcial
palabras_clave = ["no entendí", "explica", "dudas", "más claro", "más simple", "no me parece", "repite", "aclara", "sencillo"]
es_aclaracion = user_input and any(palabra in user_input.lower() for palabra in palabras_clave)

if user_input:
    if es_aclaracion and st.session_state.ultima_pregunta:
        prompt = f"Explica de forma más simple lo siguiente: {st.session_state.ultima_pregunta}"
    else:
        prompt = user_input
        st.session_state.ultima_pregunta = user_input

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
