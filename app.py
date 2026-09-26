import streamlit as st
from supabase import create_client, Client
import uuid

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
.block-container {padding-top: 1rem; padding-bottom: 2rem;}
h1, h2, h3, p, label, .stMarkdown {color: white !important;}
div[data-testid="stSidebar"] {background: #0b1020;}
div[data-testid="stButton"] button {
    width: 100%;
    border-radius: 12px;
    min-height: 44px;
    font-weight: 700;
}
</style>
""", unsafe_allow_html=True)

# ---------- Conexão com Supabase ----------
@st.cache_resource
def get_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = get_supabase()

BUCKET = "videos"

# ---------- Funções ----------
def listar_videos():
    try:
        resp = (
            supabase.table("videos")
            .select("*")
            .order("created_at", desc=True)
            .execute()
        )
        return resp.data or []
    except Exception as e:
        st.error(f"Erro ao carregar os vídeos: {e}")
        return []

def upload_arquivo(arquivo, pasta):
    ext = arquivo.name.rsplit(".", 1)[-1].lower()
    nome_unico = f"{pasta}/{uuid.uuid4().hex}.{ext}"
    dados = arquivo.getvalue()

    supabase.storage.from_(BUCKET).upload(
        nome_unico,
        dados,
        {"content-type": arquivo.type or "application/octet-stream"}
    )

    url = supabase.storage.from_(BUCKET).get_public_url(nome_unico)
    return nome_unico, url

def excluir_video(item):
    try:
        caminhos = []
        if item.get("video_path"):
            caminhos.append(item["video_path"])
        if item.get("capa_path"):
            caminhos.append(item["capa_path"])

        if caminhos:
            supabase.storage.from_(BUCKET).remove(caminhos)

        supabase.table("videos").delete().eq("id", item["id"]).execute()
        st.success("Vídeo excluído.")
        st.rerun()
    except Exception as e:
        st.error(f"Não consegui excluir: {e}")

def mostrar_card(item):
    if item.get("capa_url"):
        st.image(item["capa_url"], use_container_width=True)

    st.markdown(f"### {item.get('nome', 'Sem título')}")
    st.caption(item.get("categoria", ""))

    chave = f"aberto_{item['id']}"
    if chave not in st.session_state:
        st.session_state[chave] = False

    if not st.session_state[chave]:
        if st.button("▶ Assistir", key=f"assistir_{item['id']}"):
            st.session_state[chave] = True
            st.rerun()
    else:
        st.video(item["video_url"])
        if st.button("✖ Fechar vídeo", key=f"fechar_{item['id']}"):
            st.session_state[chave] = False
            st.rerun()

# ---------- Interface ----------
st.title("🌙 Mundo da Luna TV")
st.caption("Seus vídeos ficam salvos mesmo depois de fechar ou atualizar o app.")

menu = st.sidebar.radio(
    "Menu",
    [
        "🏠 Início",
        "📤 Enviar vídeo",
        "🧸 Infantil",
        "🎬 Filmes",
        "📺 Séries",
        "🗑️ Gerenciar"
    ]
)

videos = listar_videos()

if menu == "🏠 Início":
    st.subheader("✨ Destaques")

    if not videos:
        st.info("Ainda não há vídeos. Abra 📤 Enviar vídeo para começar.")
    else:
        cols = st.columns(2)
        for i, item in enumerate(videos):
            with cols[i % 2]:
                mostrar_card(item)

elif menu == "📤 Enviar vídeo":
    st.subheader("📤 Enviar novo vídeo")

    senha = st.text_input("Senha de administrador", type="password")

    if senha != st.secrets["ADMIN_PASSWORD"]:
        st.info("Digite a senha de administrador para liberar o envio.")
    else:
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
            st.image(capa, caption="Prévia da capa", use_container_width=True)

        if video is not None:
            tamanho_mb = video.size / (1024 * 1024)
            st.write(f"Vídeo selecionado: **{tamanho_mb:.1f} MB**")

        if st.button("💾 Salvar permanentemente"):
            if video is None:
                st.warning("Escolha um vídeo primeiro.")
            else:
                with st.spinner("Enviando e salvando..."):
                    try:
                        video_path, video_url = upload_arquivo(video, "videos")

                        capa_path = None
                        capa_url = None
                        if capa is not None:
                            capa_path, capa_url = upload_arquivo(capa, "capas")

                        supabase.table("videos").insert({
                            "nome": nome.strip() if nome.strip() else video.name,
                            "categoria": categoria,
                            "video_url": video_url,
                            "video_path": video_path,
                            "capa_url": capa_url,
                            "capa_path": capa_path
                        }).execute()

                        st.success("✅ Vídeo salvo permanentemente!")
                        st.balloons()
                    except Exception as e:
                        st.error(f"Não consegui salvar o vídeo: {e}")

elif menu in ["🧸 Infantil", "🎬 Filmes", "📺 Séries"]:
    categoria_atual = {
        "🧸 Infantil": "Infantil",
        "🎬 Filmes": "Filmes",
        "📺 Séries": "Séries"
    }[menu]

    st.subheader(menu)
    itens = [v for v in videos if v.get("categoria") == categoria_atual]

    if not itens:
        st.info("Ainda não há vídeos nessa categoria.")
    else:
        cols = st.columns(2)
        for i, item in enumerate(itens):
            with cols[i % 2]:
                mostrar_card(item)

elif menu == "🗑️ Gerenciar":
    st.subheader("🗑️ Gerenciar vídeos")

    senha = st.text_input("Senha de administrador", type="password", key="senha_gerenciar")

    if senha != st.secrets["ADMIN_PASSWORD"]:
        st.info("Digite a senha de administrador.")
    elif not videos:
        st.info("Não há vídeos cadastrados.")
    else:
        for item in videos:
            st.markdown("---")
            st.write(f"**{item.get('nome', 'Sem título')}** — {item.get('categoria', '')}")
            if st.button("Excluir", key=f"excluir_{item['id']}"):
                excluir_video(item)
