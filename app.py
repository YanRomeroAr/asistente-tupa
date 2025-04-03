import streamlit as st
import openai
import time

# ---------------------------
# CONFIGURACIÓN SEGURA
# ---------------------------
# Estas claves deben estar configuradas en Streamlit Cloud > Manage app > Secrets
# Ejemplo en Secrets:
# openai_api_key = "sk-..."
# assistant_id = "asst-..."
openai.api_key = st.secrets["openai_api_key"]
assistant_id = st.secrets["assistant_id"]

# ---------------------------
# CONFIGURACIÓN DE LA PÁGINA
# ---------------------------
st.set_page_config(page_title="Asistente TUPA", page_icon="🤖")
st.title("Asistente Virtual sobre el TUPA")
st.markdown("Haz tus consultas sobre trámites administrativos y obtén respuestas claras y rápidas.")

# ---------------------------
# HISTORIAL DE MENSAJES
# ---------------------------
# Guardamos los mensajes para mostrar el historial en la interfaz
if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------------------------
# ENTRADA DEL USUARIO
# ---------------------------
# Caja de entrada tipo chat
user_input = st.chat_input("Escribe tu consulta aquí...")

if user_input:
    # Guardamos el mensaje del usuario
    st.session_state.messages.append(("usuario", user_input))

    # CREAMOS UN NUEVO THREAD por cada consulta (evita respuestas repetidas)
    thread = openai.beta.threads.create()

    # Enviamos el mensaje del usuario al modelo
    openai.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=user_input
    )

    # Ejecutamos al asistente con el thread creado
    run = openai.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant_id
    )

    # Esperamos la respuesta del asistente
    with st.spinner("Pensando..."):
        while True:
            status = openai.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )
            if status.status == "completed":
                break
            time.sleep(1)

        # Obtenemos la respuesta del asistente
        messages = openai.beta.threads.messages.list(
            thread_id=thread.id
        )
        for msg in reversed(messages.data):
            if msg.role == "assistant":
                respuesta = msg.content[0].text.value
                st.session_state.messages.append(("asistente", respuesta))
                break

# ---------------------------
# MOSTRAR EL CHAT COMPLETO
# ---------------------------
# Mostramos todos los mensajes del historial tipo conversación
for rol, mensaje in st.session_state.messages:
    if rol == "usuario":
        with st.chat_message("Usuario"):
            st.markdown(mensaje)
    else:
        with st.chat_message("Asistente"):
            st.markdown(mensaje)
