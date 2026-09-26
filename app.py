import streamlit as st

st.set_page_config(
    page_title="Mundo da Luna TV",
    page_icon="🌙",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background: linear-gradient(180deg, #111827 0%, #1f2937 100%);
    color: white;
}
.block-container {
    padding-top: 1.2rem;
}
h1, h2, h3, p, label {
    color: white !important;
}
div[data-testid="stSidebar"] {
    background: #0b1020;
}
.card {
    background: #182033;
    padding: 14px;
    border-radius: 16px;
    margin-bottom: 14px;
}
</style>
""", unsafe_allow_html=True)

st.title("🌙 Mundo da Luna TV")
st.caption("Seus vídeos organizados como um pequeno app de streaming.")

if "videos" not in st.session_state:
    st.session_state.videos = []

menu = st.sidebar.radio(
    "Menu",
    [
        "🏠 Início",
        "📤 Enviar vídeo",
        "🧸 Infantil",
        "🎬 Filmes",
        "📺 Séries"
    ]
)

if menu == "🏠 Início":
    st.subheader("✨ Bem-vindo")
    st.write("Escolha uma categoria no menu ou envie um novo vídeo.")

    if st.session_state.videos:
        st.subheader("🎞️ Seus vídeos")
        cols = st.columns(2)

        for i, item in enumerate(st.session_state.videos):
            with cols[i % 2]:
                if item.get("capa"):
                    st.image(item["capa"], use_container_width=True)
                st.markdown(f"### {item['nome']}")
                st.caption(item["categoria"])
    else:
        st.info("Ainda não há vídeos. Abra 📤 Enviar vídeo.")

elif menu == "📤 Enviar vídeo":
    st.subheader("📤 Enviar vídeo")

    nome = st.text_input("Nome do vídeo")

    categoria = st.selectbox(
        "Categoria",
        ["Infantil", "Filmes", "Séries"]
    )

    capa = st.file_uploader(
        "Escolha uma capa",
        type=["jpg", "jpeg", "png"],
        key="capa"
    )

    video = st.file_uploader(
        "Escolha um vídeo da galeria",
        type=["mp4", "mov", "m4v"],
        key="video"
    )

    if capa is not None:
        st.image(capa, caption="Prévia da capa", use_container_width=True)

    if video is not None:
        st.video(video)

    if st.button("💾 Adicionar vídeo"):
        if video is None:
            st.warning("Escolha um vídeo primeiro.")
        else:
            st.session_state.videos.append(
                {
                    "nome": nome if nome else video.name,
                    "categoria": categoria,
                    "dados": video.getvalue(),
                    "capa": capa.getvalue() if capa else None
                }
            )
            st.success("Vídeo adicionado com sucesso!")

else:
    categoria_atual = {
        "🧸 Infantil": "Infantil",
        "🎬 Filmes": "Filmes",
        "📺 Séries": "Séries"
    }[menu]

    st.subheader(menu)

    itens = [
        item for item in st.session_state.videos
        if item["categoria"] == categoria_atual
    ]

    if not itens:
        st.info("Ainda não há vídeos nessa categoria.")
    else:
        for item in itens:
            st.markdown("---")
            if item.get("capa"):
                st.image(item["capa"], use_container_width=True)

            st.markdown(f"### {item['nome']}")
            st.video(item["dados"])
