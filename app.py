import streamlit as st

st.set_page_config(
    page_title="Minha TV",
    page_icon="📺",
    layout="wide"
)

st.title("📺 Minha TV")
st.caption("Use apenas vídeos, transmissões e playlists que você tem autorização para usar.")

if "items" not in st.session_state:
    st.session_state.items = []

menu = st.sidebar.radio(
    "Menu",
    [
        "🏠 Início",
        "📡 TV ao vivo",
        "🎬 Filmes",
        "📺 Séries",
        "🧸 Infantil",
        "➕ Adicionar"
    ]
)

if menu == "🏠 Início":
    st.subheader("Bem-vindo")
    st.write("Adicione seus próprios links autorizados e organize por categoria.")
    st.info("Abra **➕ Adicionar** no menu para começar.")

elif menu == "➕ Adicionar":
    st.subheader("➕ Adicionar conteúdo")

    nome = st.text_input("Nome")

    categoria = st.selectbox(
        "Categoria",
        [
            "TV ao vivo",
            "Filmes",
            "Séries",
            "Infantil"
        ]
    )

    url = st.text_input("Link do vídeo ou transmissão")

    if st.button("Adicionar"):
        if nome and url:
            st.session_state.items.append(
                {
                    "nome": nome,
                    "categoria": categoria,
                    "url": url
                }
            )

            st.success("Conteúdo adicionado.")

        else:
            st.warning("Preencha o nome e o link.")

else:
    categoria_atual = {
        "📡 TV ao vivo": "TV ao vivo",
        "🎬 Filmes": "Filmes",
        "📺 Séries": "Séries",
        "🧸 Infantil": "Infantil"
    }[menu]

    st.subheader(menu)

    itens = [
        item
        for item in st.session_state.items
        if item["categoria"] == categoria_atual
    ]

    if not itens:
        st.info("Ainda não há conteúdo nessa categoria.")

    else:
        escolhido = st.selectbox(
            "Escolha",
            [item["nome"] for item in itens]
        )

        item = next(
            item
            for item in itens
            if item["nome"] == escolhido
        )

        st.video(item["url"])
