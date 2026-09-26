import streamlit as st

st.set_page_config(
    page_title="Minha TV",
    page_icon="📺",
    layout="wide"
)

st.title("📺 Minha TV")
st.caption("Adicione e assista aos seus próprios vídeos.")

if "videos" not in st.session_state:
    st.session_state.videos = []

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

if menu == "🏠 Início":
    st.subheader("Bem-vindo ❤️")
    st.write(
        "Use o menu para enviar um vídeo da sua galeria "
        "e assistir dentro do aplicativo."
    )
    st.info("Toque em 📤 Enviar vídeo para começar.")

elif menu == "📤 Enviar vídeo":
    st.subheader("📤 Enviar vídeo da galeria")

    nome = st.text_input("Nome do vídeo")

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

        if st.button("💾 Adicionar vídeo"):
            st.session_state.videos.append(
                {
                    "nome": nome if nome else video.name,
                    "categoria": categoria,
                    "dados": video.getvalue(),
                    "tipo": video.type
                }
            )
            st.success("Vídeo adicionado com sucesso!")

else:
    categoria_atual = {
        "📡 TV ao vivo": "TV ao vivo",
        "🎬 Filmes": "Filmes",
        "📺 Séries": "Séries",
        "🧸 Infantil": "Infantil"
    }[menu]

    st.subheader(menu)

    itens = [
        item for item in st.session_state.videos
        if item["categoria"] == categoria_atual
    ]

    if not itens:
        st.info("Ainda não há vídeos nessa categoria.")
    else:
        escolhido = st.selectbox(
            "Escolha um vídeo",
            [item["nome"] for item in itens]
        )

        item = next(
            item for item in itens
            if item["nome"] == escolhido
        )

        st.video(item["dados"])
