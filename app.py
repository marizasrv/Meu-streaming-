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
    background:
        radial-gradient(circle at top right, rgba(255,215,0,0.12), transparent 26%),
        radial-gradient(circle at bottom left, rgba(198,132,255,0.16), transparent 30%),
        linear-gradient(180deg, #2b124c 0%, #3d1a6e 46%, #1f0f33 100%);
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
    background: #241038;
}
div[data-testid="stButton"] button {
    width: 100%;
    border-radius: 14px;
    min-height: 46px;
    font-weight: 700;
    background: linear-gradient(90deg, #7c3aed, #9f7aea);
    color: white;
    border: 1px solid #d6b45f;
}
div[data-testid="stButton"] button:hover {
    background: linear-gradient(90deg, #8b5cf6, #b794f4);
    border-color: #f2d675;
}
div[data-testid="stAlert"] {
    border-radius: 16px;
}
[data-testid="stFileUploaderDropzone"] {
    background: #4b216f;
    border: 1px solid #8b5cf6;
    border-radius: 16px;
}
.hero {
    padding: 18px;
    border: 1px solid rgba(242,214,117,0.30);
    border-radius: 22px;
    background: rgba(255,255,255,0.04);
    margin-bottom: 18px;
}
.gold-line {
    height: 2px;
    background: linear-gradient(90deg, transparent, #f2d675, transparent);
    margin: 8px 0 18px 0;
}
.magic {
    color: #f2d675 !important;
    font-size: 1.05rem;
}
.metric-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 10px;
    margin: 14px 0 20px 0;
}
.metric-card {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(242,214,117,0.22);
    border-radius: 16px;
    padding: 12px 10px;
    text-align: center;
}
.metric-number {
    font-size: 1.8rem;
    font-weight: 800;
    line-height: 1.1;
}
.metric-label {
    color: #f2d675;
    font-size: 0.95rem;
    margin-top: 4px;
}
video {
    border-radius: 16px !important;
}
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_supabase() -> Client:
    return create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"]
    )

supabase = get_supabase()
BUCKET = "videos"

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

    supabase.storage.from_(BUCKET).upload(
        nome_unico,
        arquivo.getvalue(),
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

if "ultimo_assistido_id" not in st.session_state:
    st.session_state.ultimo_assistido_id = None

def mostrar_card(item):
    if item.get("capa_url"):
        st.image(item["capa_url"], use_container_width=True)

    st.markdown(f"### ✨ {item.get('nome', 'Sem título')}")
    st.caption(f"🌟 {item.get('categoria', '')}")

    chave = f"aberto_{item['id']}"
    if chave not in st.session_state:
        st.session_state[chave] = False

    if not st.session_state[chave]:
        if st.button("▶ Assistir", key=f"assistir_{item['id']}"):
            st.session_state[chave] = True
            st.session_state.ultimo_assistido_id = item["id"]
            st.rerun()
    else:
        st.video(item["video_url"])
        if st.button("✖ Fechar vídeo", key=f"fechar_{item['id']}"):
            st.session_state[chave] = False
            st.rerun()

st.markdown("""
<div class="hero">
<h1>🌙 Mundo da Luna TV ✨</h1>
<p class="magic">⭐ Histórias mágicas, aventuras e sonhos em um só lugar ⭐</p>
</div>
<div class="gold-line"></div>
""", unsafe_allow_html=True)

menu = st.sidebar.radio(
    "Menu",
    [
        "🏠 Início",
        "🔎 Buscar",
        "🆕 Novidades",
        "📤 Enviar vídeo",
        "🧸 Infantil",
        "🎬 Filmes",
        "📺 Séries",
        "🗑️ Gerenciar"
    ]
)

videos = listar_videos()

if menu == "🏠 Início":
    total = len(videos)
    infantil = len([v for v in videos if v.get("categoria") == "Infantil"])
    filmes = len([v for v in videos if v.get("categoria") == "Filmes"])
    series = len([v for v in videos if v.get("categoria") == "Séries"])

    st.markdown(f"""
    <div class="metric-grid">
        <div class="metric-card">
            <div class="metric-number">{total}</div>
            <div class="metric-label">🎞️ Total</div>
        </div>
        <div class="metric-card">
            <div class="metric-number">{infantil}</div>
            <div class="metric-label">🧸 Infantil</div>
        </div>
        <div class="metric-card">
            <div class="metric-number">{filmes}</div>
            <div class="metric-label">🎬 Filmes</div>
        </div>
        <div class="metric-card">
            <div class="metric-number">{series}</div>
            <div class="metric-label">📺 Séries</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.ultimo_assistido_id is not None:
        ultimo = next(
            (v for v in videos if v["id"] == st.session_state.ultimo_assistido_id),
            None
        )
        if ultimo:
            st.subheader("▶ Continuar assistindo")
            mostrar_card(ultimo)
            st.markdown("---")

    st.subheader("✨ Destaques")

    if not videos:
        st.info("Ainda não há vídeos. Abra 📤 Enviar vídeo para começar.")
    else:
        mostrar_card(videos[0])

        if len(videos) > 1:
            st.markdown("---")
            st.subheader("🎞️ Últimos adicionados")
            cols = st.columns(2)
            for i, item in enumerate(videos[1:5]):
                with cols[i % 2]:
                    mostrar_card(item)

elif menu == "🔎 Buscar":
    st.subheader("🔎 Buscar vídeos")

    termo = st.text_input("Digite o nome do vídeo", placeholder="Ex.: Luna")
    categoria_busca = st.selectbox(
        "Filtrar por categoria",
        ["Todas", "Infantil", "Filmes", "Séries"]
    )

    filtrados = videos

    if termo.strip():
        termo_lower = termo.lower().strip()
        filtrados = [
            v for v in filtrados
            if termo_lower in v.get("nome", "").lower()
        ]

    if categoria_busca != "Todas":
        filtrados = [
            v for v in filtrados
            if v.get("categoria") == categoria_busca
        ]

    if not filtrados:
        st.info("Nenhum vídeo encontrado.")
    else:
        cols = st.columns(2)
        for i, item in enumerate(filtrados):
            with cols[i % 2]:
                mostrar_card(item)

elif menu == "🆕 Novidades":
    st.subheader("🆕 Novidades")

    if not videos:
        st.info("Ainda não há novidades.")
    else:
        cols = st.columns(2)
        for i, item in enumerate(videos[:10]):
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
            st.image(capa, caption="✨ Prévia da capa", use_container_width=True)

        if video is not None:
            st.write(f"⭐ Vídeo selecionado: **{video.size / (1024 * 1024):.1f} MB**")

        if st.button("💾 Salvar permanentemente"):
            if video is None:
                st.warning("Escolha um vídeo primeiro.")
            else:
                with st.spinner("✨ Enviando e salvando..."):
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

    senha = st.text_input(
        "Senha de administrador",
        type="password",
        key="senha_gerenciar"
    )

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
