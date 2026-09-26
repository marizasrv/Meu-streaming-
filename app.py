import streamlit as st

st.set_page_config(
    page_title="Mundo da Luna TV",
    page_icon="🌙",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background: linear-gradient(180deg, #0f172a 0%, #111827 55%, #0b1020 100%);
    color: white;
}
.block-container {
    padding-top: 1rem;
    padding-bottom: 2rem;
}
h1, h2, h3, p, label, .stMarkdown {
    color: white !important;
}
div[data-testid="stSidebar"] {
    background: #0b1020;
}
div[data-testid="stButton"] button {
    width: 100%;
    border-radius: 12px;
    min-height: 44px;
    font-weight: 700;
}
.video-card {
    background: #182033;
    border-radius: 18px;
    padding: 14px;
    margin-bottom: 16px;
    border: 1px solid rgba(255,255,255,.08);
}
.small {
    color: #aab2c3 !important;
}
</style>
""", unsafe_allow_html=True)

st.title("🌙 Mundo da Luna TV")
st.caption("Seu pequeno app de streaming.")

if "videos" not in st.session_state:
    st.session_state.videos = []

if "assistindo" not in st.session_state:
    st.session_state.assistindo = None

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

def card_video(item, idx):
    with st.container():
        if item.get("capa"):
            st.image(item["capa"], use_container_width=True)

        st.markdown(f"### {item['nome']}")
        st.caption(item["categoria"])

        if st.button("▶ Assistir", key=f"assistir_{idx}"):
            st.session_state.assistindo = idx

        if st.session_state.assistindo == idx:
            st.video(item["dados"])
            if st.button("✖ Fechar vídeo", key=f"fechar_{idx}"):
                st.session_state.assistindo = None
                st.rerun()

if menu == "🏠 Início":
    st.subheader("✨ Destaques")

    if not st.session_state.videos:
        st.info("Ainda não há vídeos. Abra 📤 Enviar vídeo para começar.")
    else:
        cols = st.columns(2)
        for i, item in enumerate(st.session_state.videos):
            with cols[i % 2]:
                card_video(item, i)

elif menu == "📤 Enviar vídeo":
    st.subheader("📤 Enviar novo vídeo")

    nome = st.text_input(
        "Nome do vídeo",
        placeholder="Ex.: O Mundo Encantado de Luna"
    )

    categoria = st.selectbox(
        "Categoria",
        ["Infantil", "Filmes", "Séries"]
    )

    capa = st.file_uploader(
        "Escolha uma capa",
        type=["jpg", "jpeg", "png"],
        key="capa_upload"
    )

    video = st.file_uploader(
        "Escolha um vídeo da galeria",
        type=["mp4", "mov", "m4v"],
        key="video_upload"
    )

    if capa is not None:
        st.image(
            capa,
            caption="Prévia da capa",
            use_container_width=True
        )

    if video is not None:
        st.success("Vídeo carregado. Agora toque em Adicionar vídeo.")

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
            st.session_state.assistindo = None
            st.success("Vídeo adicionado com sucesso!")

else:
    categoria_atual = {
        "🧸 Infantil": "Infantil",
        "🎬 Filmes": "Filmes",
        "📺 Séries": "Séries"
    }[menu]

    st.subheader(menu)

    itens = [
        (i, item)
        for i, item in enumerate(st.session_state.videos)
        if item["categoria"] == categoria_atual
    ]

    if not itens:
        st.info("Ainda não há vídeos nessa categoria.")
    else:
        cols = st.columns(2)

        for pos, (idx, item) in enumerate(itens):
            with cols[pos % 2]:
                card_video(item, idx)
