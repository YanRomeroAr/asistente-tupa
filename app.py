import streamlit as st
import openai
import time

# ---------------------------
# CONFIGURACIÓN SEGURA
# ---------------------------
# Estas claves se definen en: Streamlit Cloud > Manage app > Secrets
openai.api_key = st.secrets["openai_api_key"]
assistant_id = st.secrets["assistant_id"]

# ---------------------------
# CONFIGURACIÓN DE LA APP
# ---------------------------
st.set_page_config(page_title="Asistente TUPA", page_icon="🤖")
st.title("Asistente Virtual sobre el TUPA")
st.markdown("Haz tus consultas sobre trámites administrativos y obtén respuestas automáticas.")

# ---------------------------
# INICIALIZACIÓN DE SESIÓN
# ---------------------------
# Mantenemos la conversación viva entre preguntas y respuestas
if "thread_id" not in st.session_state:
    thread = openai.beta.threads.create()
    st.session_state.thread_id = thread.id
    st.session_state.messages = []

# ---------------------------
# ENTRADA DEL USUARIO
# ---------------------------
user_input = st.chat_input("Escribe tu consulta aquí...")

if user_input:
    # Guardamos lo que escribió el usuario en el thread del asistente
    openai.beta.threads.messages.create(
        thread_id=st.session_state.thread_id,
        role="user",
        content=user_input
    )
    st.session_state.messages.append(("usuario", user_input))

    # Ejecutamos al asistente para que genere una respuesta
    run = openai.beta.threads.runs.create(
        thread_id=st.session_state.thread_id,
        assistant_id=assistant_id
    )

    # Mostramos un spinner mientras esperamos la respuesta
    with st.spinner("Pensando..."):
        while True:
            status = openai.beta.threads.runs.retrieve(
                thread_id=st.session_state.thread_id,
                run_id=run.id
            )
            if status.status == "completed":
                break
            time.sleep(1)

        # Obtenemos la respuesta del asistente
        messages = openai.beta.threads.messages.list(
            thread_id=st.session_state.thread_id
        )
        for msg in reversed(messages.data):
            if msg.role == "assistant":
                respuesta = msg.content[0].text.value
                st.session_state.messages.append(("asistente", respuesta))
                break

# ---------------------------
# MOSTRAR EL CHAT
# ---------------------------
# Presentamos cada mensaje del usuario y del asistente en estilo chat
for rol, mensaje in st.session_state.messages:
    if rol == "usuario":
        with st.chat_message("Usuario"):
            st.markdown(mensaje)
    else:
        with st.chat_message("Asistente"):
            st.markdown(mensaje)
