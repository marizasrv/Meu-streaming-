import streamlit as st

st.set_page_config(
    page_title="Minha TV",
    page_icon="📺",
    layout="wide"
)

st.title("📺 Minha TV")
st.caption("Adicione e assista aos seus próprios vídeos.")

menu = st.sidebar.radio(
    "Menu",
    [
        "🏠 Início",
        "📤 Enviar vídeo",
        "📡 TV ao vivo",
        "🎬 Filmes",
        "📺 Séries",
        "🧸 Infantil"
    ]
)

if "videos" not in st.session_state:
    st.session_state.videos = []

# TELA INICIAL
if menu == "🏠 Início":

    st.subheader("Bem-vindo ❤️")

    st.write(
        "Use o menu para enviar um vídeo da sua galeria "
        "e assistir dentro do aplicativo."
    )

    st.info("Toque em 📤 Enviar vídeo para começar.")


# ENVIAR VÍDEO DA GALERIA
elif menu == "📤 Enviar vídeo":

    st.subheader("📤 Enviar vídeo da galeria")

    nome = st.text_input(
        "Nome do vídeo"
    )

    categoria = st.selectbox(
        "Escolha a categoria",
        [
            "TV ao vivo",
            "Filmes",
            "Séries",
            "Infantil"
        ]
    )

    video = st.file_uploader(
        "Escolha um vídeo da sua galeria",
        type=["mp4", "mov", "m4v", "avi"]
    )

    if video is not None:

        st.video(video)

        if st.button("💾 Ad
