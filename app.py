import streamlit as st
from supabase import create_client, Client
from datetime import datetime, timezone
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
        linear-gradient(180deg, #160825 0%, #24103f 46%, #0d0717 100%);
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
    background: #13081f;
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
    background: #2b123f;
    border: 1px solid #8b5cf6;
    border-radius: 16px;
}
.hero {
    padding: 18px;
    border: 1px solid rgba(242,214,117,0.30);
    border-radius: 22px;
    background: rgba(255,255,255,0.025);
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
    background: rgba(255,255,255,0.04);
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
.plan-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(242,214,117,0.28);
    border-radius: 20px;
    padding: 18px;
    margin: 10px 0 14px 0;
}
.plan-title {
    font-size: 1.45rem;
    font-weight: 800;
    margin-bottom: 6px;
}
.plan-price {
    color: #f2d675 !important;
    font-size: 1.15rem;
    font-weight: 700;
}
.lock-card {
    background: rgba(255,255,255,0.035);
    border: 1px dashed rgba(242,214,117,0.40);
    border-radius: 20px;
    padding: 22px;
    text-align: center;
}

/* LETRAS MAIORES PARA CELULAR */
h1 {
    font-size: 3rem !important;
    line-height: 1.1 !important;
}
h2 {
    font-size: 2.35rem !important;
    line-height: 1.15 !important;
}
h3 {
    font-size: 1.8rem !important;
    line-height: 1.2 !important;
}
p, .stMarkdown, .stCaption, label {
    font-size: 1.15rem !important;
}
div[data-testid="stButton"] button {
    min-height: 58px !important;
    padding: 0.75rem 1rem !important;
}
div[data-testid="stButton"] button p {
    font-size: 1.22rem !important;
    font-weight: 800 !important;
}
div[data-testid="stLinkButton"] a {
    min-height: 58px !important;
    font-size: 1.22rem !important;
    font-weight: 800 !important;
}
div[data-testid="stRadio"] label p {
    font-size: 1.22rem !important;
    font-weight: 700 !important;
}
div[data-testid="stTextInput"] label p,
div[data-testid="stSelectbox"] label p,
div[data-testid="stFileUploader"] label p {
    font-size: 1.18rem !important;
    font-weight: 700 !important;
}
div[data-testid="stTextInput"] input {
    font-size: 1.15rem !important;
    min-height: 54px !important;
}
.metric-number {
    font-size: 2.15rem !important;
}
.metric-label {
    font-size: 1.15rem !important;
}
.plan-title {
    font-size: 1.75rem !important;
}
.plan-price {
    font-size: 1.35rem !important;
}

@media (max-width: 700px) {
    h1 { font-size: 2.75rem !important; }
    h2 { font-size: 2.15rem !important; }
    h3 { font-size: 1.7rem !important; }
    div[data-testid="stRadio"] label p {
        font-size: 1.18rem !important;
    }
}

/* BOTÃO DE ASSINATURA KIWIFY - VISÍVEL NO CELULAR */
div[data-testid="stLinkButton"] a {
    background: linear-gradient(90deg, #6d28d9, #8b5cf6) !important;
    color: #ffffff !important;
    border: 2px solid #f2d675 !important;
    border-radius: 16px !important;
    min-height: 62px !important;
    font-size: 1.22rem !important;
    font-weight: 800 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    text-decoration: none !important;
}
div[data-testid="stLinkButton"] a p,
div[data-testid="stLinkButton"] a span {
    color: #ffffff !important;
    font-size: 1.22rem !important;
    font-weight: 800 !important;
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


def link_plano_pagamento():
    try:
        # Preferimos Kiwify. Mantemos o nome antigo apenas como fallback.
        url = str(st.secrets.get("KIWIFY_CHECKOUT_URL", "")).strip()
        if not url:
            url = str(st.secrets.get("MERCADO_PAGO_PLAN_URL", "")).strip()
        return url
    except Exception:
        return ""


# -----------------------------
# LOGIN / CADASTRO DE USUÁRIOS
# -----------------------------
if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = None

if "usuario_id" not in st.session_state:
    st.session_state.usuario_id = None

if "usuario_access_token" not in st.session_state:
    st.session_state.usuario_access_token = None

if "usuario_refresh_token" not in st.session_state:
    st.session_state.usuario_refresh_token = None

if "plano_atual" not in st.session_state:
    st.session_state.plano_atual = "Grátis"

if "status_assinatura" not in st.session_state:
    st.session_state.status_assinatura = "inativo"


def novo_cliente_auth():
    # Cliente separado para login, evitando misturar a sessão
    # de um usuário com outro.
    return create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"]
    )


def cliente_usuario_autenticado():
    if not st.session_state.usuario_access_token or not st.session_state.usuario_refresh_token:
        return None

    cliente = novo_cliente_auth()
    cliente.auth.set_session(
        st.session_state.usuario_access_token,
        st.session_state.usuario_refresh_token
    )
    return cliente


def carregar_plano_usuario():
    if not st.session_state.usuario_id:
        st.session_state.plano_atual = "Grátis"
        st.session_state.status_assinatura = "inativo"
        return

    try:
        cliente = cliente_usuario_autenticado()
        if cliente is None:
            return

        resp = (
            cliente.table("assinaturas")
            .select("plano,status")
            .eq("user_id", st.session_state.usuario_id)
            .limit(1)
            .execute()
        )

        dados = (resp.data or [])
        if dados:
            item = dados[0]
            st.session_state.plano_atual = item.get("plano") or "Grátis"
            st.session_state.status_assinatura = item.get("status") or "inativo"
        else:
            st.session_state.plano_atual = "Grátis"
            st.session_state.status_assinatura = "inativo"
    except Exception:
        # Mantém o app funcionando mesmo antes da tabela de assinaturas ser criada.
        st.session_state.plano_atual = "Grátis"
        st.session_state.status_assinatura = "inativo"


def cliente_admin_assinaturas():
    try:
        # Preferimos a nova Secret Key do Supabase (sb_secret_...).
        # Mantemos compatibilidade com a antiga service_role, caso necessário.
        chave = str(st.secrets.get("SUPABASE_SECRET_KEY", "")).strip()
        if not chave:
            chave = str(st.secrets.get("SUPABASE_SERVICE_ROLE_KEY", "")).strip()
    except Exception:
        chave = ""

    if not chave:
        return None

    return create_client(st.secrets["SUPABASE_URL"], chave)


def ativar_plano_admin(email, plano, status):
    admin = cliente_admin_assinaturas()
    if admin is None:
        raise RuntimeError(
            "Falta configurar SUPABASE_SECRET_KEY nos Secrets do Streamlit."
        )

    busca = (
        admin.table("assinaturas")
        .select("user_id,email")
        .ilike("email", email.strip())
        .limit(1)
        .execute()
    )

    itens = busca.data or []
    if not itens:
        raise RuntimeError("Não encontrei uma conta cadastrada com esse e-mail.")

    user_id = itens[0]["user_id"]

    admin.table("assinaturas").update({
        "plano": plano,
        "status": status
    }).eq("user_id", user_id).execute()


def fazer_login(email, senha):
    auth = novo_cliente_auth()
    resposta = auth.auth.sign_in_with_password({
        "email": email.strip(),
        "password": senha
    })

    if resposta.user:
        st.session_state.usuario_logado = resposta.user.email
        st.session_state.usuario_id = str(resposta.user.id)

        if resposta.session:
            st.session_state.usuario_access_token = resposta.session.access_token
            st.session_state.usuario_refresh_token = resposta.session.refresh_token

        carregar_plano_usuario()
        return True
    return False


def fazer_cadastro(email, senha):
    auth = novo_cliente_auth()
    resposta = auth.auth.sign_up({
        "email": email.strip(),
        "password": senha
    })

    # Se a confirmação por e-mail estiver desativada,
    # o Supabase pode criar a sessão imediatamente.
    if resposta.session and resposta.user:
        st.session_state.usuario_logado = resposta.user.email
        st.session_state.usuario_id = str(resposta.user.id)
        st.session_state.usuario_access_token = resposta.session.access_token
        st.session_state.usuario_refresh_token = resposta.session.refresh_token
        carregar_plano_usuario()
        return "logado"

    if resposta.user:
        return "confirmar_email"

    return "erro"


def sair_da_conta():
    st.session_state.usuario_logado = None
    st.session_state.usuario_id = None
    st.session_state.usuario_access_token = None
    st.session_state.usuario_refresh_token = None
    st.session_state.plano_atual = "Grátis"
    st.session_state.status_assinatura = "inativo"
    st.rerun()


def mudar_menu(destino):
    # Callback seguro: altera o menu antes de o radio ser reconstruído.
    st.session_state["menu_principal"] = destino


def abrir_minha_conta():
    mudar_menu("👤 Entrar / Minha conta")


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


def alternar_favorito(item):
    try:
        novo_valor = not bool(item.get("favorito", False))
        (
            supabase.table("videos")
            .update({"favorito": novo_valor})
            .eq("id", item["id"])
            .execute()
        )
        st.rerun()
    except Exception as e:
        st.error(f"Não consegui atualizar Minha Lista: {e}")


def registrar_assistido(item):
    try:
        agora = datetime.now(timezone.utc).isoformat()
        (
            supabase.table("videos")
            .update({"ultimo_assistido_at": agora})
            .eq("id", item["id"])
            .execute()
        )
    except Exception as e:
        st.warning(f"O vídeo abriu, mas não consegui salvar o histórico: {e}")


def ultimo_assistido(videos):
    assistidos = [v for v in videos if v.get("ultimo_assistido_at")]
    if not assistidos:
        return None
    return max(assistidos, key=lambda v: v.get("ultimo_assistido_at", ""))


def listar_assistidos_recentes(videos, limite=10):
    assistidos = [v for v in videos if v.get("ultimo_assistido_at")]
    assistidos.sort(
        key=lambda v: v.get("ultimo_assistido_at", ""),
        reverse=True
    )
    return assistidos[:limite]


def mostrar_card(item, contexto, em_minha_lista=False):
    if item.get("capa_url"):
        st.image(item["capa_url"], use_container_width=True)

    st.markdown(f"### ✨ {item.get('nome', 'Sem título')}")
    st.caption(f"🌟 {item.get('categoria', '')}")

    col1, col2 = st.columns([3, 2])

    with col1:
        chave = f"aberto_{contexto}_{item['id']}"
        if chave not in st.session_state:
            st.session_state[chave] = False

        if not st.session_state[chave]:
            if st.button("▶ Assistir", key=f"assistir_{contexto}_{item['id']}"):
                registrar_assistido(item)
                st.session_state[chave] = True
                st.rerun()
        else:
            if st.button("✖ Fechar vídeo", key=f"fechar_{contexto}_{item['id']}"):
                st.session_state[chave] = False
                st.rerun()

    with col2:
        favorito = bool(item.get("favorito", False))

        if em_minha_lista and favorito:
            texto = "🗑️ Remover"
        else:
            texto = "💖 Na Minha Lista" if favorito else "🤍 Minha Lista"

        if st.button(texto, key=f"fav_{contexto}_{item['id']}"):
            alternar_favorito(item)

    if st.session_state.get(f"aberto_{contexto}_{item['id']}", False):
        st.video(item["video_url"])


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
        "❤️ Minha Lista",
        "🕒 Assistidos recentemente",
        "👤 Entrar / Minha conta",
        "💎 Planos",
        "🔒 Premium",
        "📤 Enviar vídeo",
        "🧸 Infantil",
        "🎬 Filmes",
        "📺 Séries",
        "🗑️ Gerenciar"
    ],
    key="menu_principal"
)

if st.session_state.usuario_logado:
    st.sidebar.success(f"👤 {st.session_state.usuario_logado}")
else:
    st.sidebar.caption("👤 Visitante — faça login para sua conta")

videos = listar_videos()

if menu == "🏠 Início":
    if st.session_state.usuario_logado:
        st.button(
            "👤 Minha conta",
            key="atalho_minha_conta",
            on_click=abrir_minha_conta
        )
    else:
        st.button(
            "👤 Entrar / Criar conta",
            key="atalho_login_home",
            on_click=abrir_minha_conta
        )

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

    ultimo = ultimo_assistido(videos)
    if ultimo:
        st.subheader("▶ Continuar assistindo")
        mostrar_card(ultimo, "continuar")
        st.markdown("---")

    st.subheader("✨ Destaques")

    if not videos:
        st.info("Ainda não há vídeos. Abra 📤 Enviar vídeo para começar.")
    else:
        mostrar_card(videos[0], "destaque")

        if len(videos) > 1:
            st.markdown("---")
            st.subheader("🎞️ Últimos adicionados")
            cols = st.columns(2)
            for i, item in enumerate(videos[1:5]):
                with cols[i % 2]:
                    mostrar_card(item, f"ultimos_{i}")

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
                mostrar_card(item, f"busca_{i}")

elif menu == "🆕 Novidades":
    st.subheader("🆕 Novidades")

    if not videos:
        st.info("Ainda não há novidades.")
    else:
        cols = st.columns(2)
        for i, item in enumerate(videos[:10]):
            with cols[i % 2]:
                mostrar_card(item, f"novidades_{i}")

elif menu == "❤️ Minha Lista":
    st.subheader("❤️ Minha Lista")

    favoritos = [v for v in videos if bool(v.get("favorito", False))]

    if not favoritos:
        st.info("Sua lista ainda está vazia. Toque em 🤍 Minha Lista em qualquer vídeo.")
    else:
        cols = st.columns(2)
        for i, item in enumerate(favoritos):
            with cols[i % 2]:
                mostrar_card(item, f"favoritos_{i}", em_minha_lista=True)

elif menu == "🕒 Assistidos recentemente":
    st.subheader("🕒 Assistidos recentemente")

    recentes = listar_assistidos_recentes(videos, limite=10)

    if not recentes:
        st.info("Você ainda não assistiu a nenhum vídeo.")
    else:
        st.caption("Os vídeos assistidos mais recentemente aparecem primeiro.")
        cols = st.columns(2)
        for i, item in enumerate(recentes):
            with cols[i % 2]:
                mostrar_card(item, f"recentes_{i}")

elif menu == "👤 Entrar / Minha conta":
    st.subheader("👤 Minha conta")

    if st.session_state.usuario_logado:
        carregar_plano_usuario()

        st.success("✅ Você está conectado!")
        st.write(f"**E-mail:** {st.session_state.usuario_logado}")
        st.write(f"**Plano atual:** {st.session_state.plano_atual}")
        st.write(f"**Status:** {st.session_state.status_assinatura}")

        if st.button("🔄 Atualizar meu plano", key="atualizar_plano_conta"):
            carregar_plano_usuario()
            st.rerun()

        st.button(
            "💎 Ver planos",
            key="ver_planos_conta",
            on_click=mudar_menu,
            args=("💎 Planos",)
        )

        if st.button("🚪 Sair da conta"):
            sair_da_conta()

    else:
        aba_login, aba_cadastro = st.tabs(["🔑 Entrar", "✨ Criar conta"])

        with aba_login:
            st.write("Entre com seu e-mail e senha.")
            email_login = st.text_input(
                "E-mail",
                key="email_login",
                placeholder="seuemail@exemplo.com"
            )
            senha_login = st.text_input(
                "Senha",
                type="password",
                key="senha_login"
            )

            if st.button("🔑 Entrar na Mundo da Luna TV", key="botao_login"):
                if not email_login.strip() or not senha_login:
                    st.warning("Digite o e-mail e a senha.")
                else:
                    try:
                        if fazer_login(email_login, senha_login):
                            st.success("✅ Login realizado!")
                            st.rerun()
                        else:
                            st.error("Não consegui entrar. Confira o e-mail e a senha.")
                    except Exception as e:
                        mensagem = str(e)
                        if "Invalid login credentials" in mensagem:
                            st.error("E-mail ou senha incorretos.")
                        elif "Email not confirmed" in mensagem:
                            st.warning("Confirme seu e-mail antes de entrar.")
                        else:
                            st.error(f"Não consegui entrar: {mensagem}")

        with aba_cadastro:
            st.write("Crie uma conta gratuita para testar.")
            email_cadastro = st.text_input(
                "Seu e-mail",
                key="email_cadastro",
                placeholder="seuemail@exemplo.com"
            )
            senha_cadastro = st.text_input(
                "Crie uma senha",
                type="password",
                key="senha_cadastro"
            )
            senha_confirmacao = st.text_input(
                "Repita a senha",
                type="password",
                key="senha_confirmacao"
            )

            if st.button("✨ Criar minha conta", key="botao_cadastro"):
                if not email_cadastro.strip():
                    st.warning("Digite seu e-mail.")
                elif len(senha_cadastro) < 6:
                    st.warning("A senha precisa ter pelo menos 6 caracteres.")
                elif senha_cadastro != senha_confirmacao:
                    st.warning("As duas senhas estão diferentes.")
                else:
                    try:
                        resultado = fazer_cadastro(email_cadastro, senha_cadastro)

                        if resultado == "logado":
                            st.success("✅ Conta criada! Você já está conectado.")
                            st.rerun()
                        elif resultado == "confirmar_email":
                            st.success("✅ Conta criada!")
                            st.info(
                                "📧 Se o Supabase pedir confirmação, abra seu e-mail "
                                "e toque no link de confirmação. Depois volte aqui para entrar."
                            )
                        else:
                            st.error("Não consegui criar a conta.")
                    except Exception as e:
                        mensagem = str(e)
                        if "already registered" in mensagem.lower():
                            st.info("Esse e-mail já tem uma conta. Use a aba Entrar.")
                        else:
                            st.error(f"Não consegui criar a conta: {mensagem}")

elif menu == "💎 Planos":
    st.subheader("💎 Planos da Mundo da Luna TV")

    if not st.session_state.usuario_logado:
        st.info("Entre ou crie uma conta para contratar um plano.")
        st.button(
            "👤 Entrar / Criar conta",
            key="planos_ir_login",
            on_click=mudar_menu,
            args=("👤 Entrar / Minha conta",)
        )
    else:
        carregar_plano_usuario()

        st.info(
            f"Seu plano atual é **{st.session_state.plano_atual}** "
            f"({st.session_state.status_assinatura})."
        )

        if st.button("🔄 Já paguei — atualizar meu plano", key="planos_atualizar"):
            carregar_plano_usuario()
            st.rerun()

        st.markdown("""
        <div class="plan-card">
            <div class="plan-title">🌙 Plano Grátis</div>
            <div class="plan-price">R$ 0</div>
            <p>• Conteúdos gratuitos</p>
            <p>• Minha Lista</p>
            <p>• Continuar assistindo</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="plan-card">
            <div class="plan-title">💎 Plano Premium</div>
            <div class="plan-price">R$ 30,00 por mês</div>
            <p>• Conteúdos exclusivos</p>
            <p>• Área Premium</p>
            <p>• Novidades para assinantes</p>
        </div>
        """, unsafe_allow_html=True)

        checkout_url = link_plano_pagamento()

        if checkout_url:
            st.markdown(
                f"""
                <a href="{checkout_url}" target="_blank" rel="noopener noreferrer"
                   style="
                       display:block;
                       width:100%;
                       text-align:center;
                       padding:16px 20px;
                       background:linear-gradient(90deg,#6d28d9,#8b5cf6);
                       color:white;
                       border:2px solid #f2d675;
                       border-radius:16px;
                       text-decoration:none;
                       font-size:1.22rem;
                       font-weight:800;
                       box-sizing:border-box;
                   ">
                   💳 Assinar Premium — R$ 30/mês
                </a>
                """,
                unsafe_allow_html=True
            )
            st.caption(
                "A Kiwify abrirá em outra aba. Depois do pagamento, volte para esta aba "
                "e toque em 'Já paguei — atualizar meu plano'."
            )
        else:
            st.info(
                "💳 O botão de pagamento já está preparado. "
                "Falta apenas adicionar o link do checkout da sua assinatura na Kiwify."
            )
            st.caption(
                "Nenhuma cobrança será feita enquanto o link da Kiwify não estiver configurado."
            )

elif menu == "🔒 Premium":
    st.subheader("🔒 Área Premium")

    if st.session_state.usuario_logado:
        carregar_plano_usuario()

    if not st.session_state.usuario_logado:
        st.warning("Entre na sua conta para acessar a área Premium.")
        st.button(
            "👤 Entrar / Criar conta",
            key="premium_ir_login",
            on_click=mudar_menu,
            args=("👤 Entrar / Minha conta",)
        )
    elif not (
        st.session_state.plano_atual == "Premium"
        and st.session_state.status_assinatura == "ativo"
    ):
        st.markdown("""
        <div class="lock-card">
            <h3>🔒 Conteúdo Premium bloqueado</h3>
            <p>Essa área será liberada quando sua assinatura Premium for confirmada no sistema.</p>
        </div>
        """, unsafe_allow_html=True)

        st.button(
            "💎 Ver plano Premium",
            key="premium_ver_planos",
            on_click=mudar_menu,
            args=("💎 Planos",)
        )
    else:
        st.success("💎 Premium ativo!")
        st.write("Aqui aparecerão os vídeos exclusivos para assinantes.")

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
                            "capa_path": capa_path,
                            "favorito": False
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
                mostrar_card(item, f"categoria_{categoria_atual}_{i}")

elif menu == "🗑️ Gerenciar":
    st.subheader("🗑️ Gerenciar")

    senha = st.text_input(
        "Senha de administrador",
        type="password",
        key="senha_gerenciar"
    )

    if senha != st.secrets["ADMIN_PASSWORD"]:
        st.info("Digite a senha de administrador.")
    else:
        st.subheader("💳 Gerenciar assinaturas")
        st.caption(
            "Depois de conferir o pagamento na Kiwify, "
            "você pode liberar ou retirar o Premium por aqui."
        )

        email_assinante = st.text_input(
            "E-mail do assinante",
            key="admin_email_assinante",
            placeholder="cliente@exemplo.com"
        )

        plano_admin = st.selectbox(
            "Plano",
            ["Grátis", "Premium"],
            key="admin_plano_assinante"
        )

        status_admin = st.selectbox(
            "Status",
            ["ativo", "inativo"],
            key="admin_status_assinante"
        )

        if st.button("💾 Salvar assinatura", key="admin_salvar_assinatura"):
            if not email_assinante.strip():
                st.warning("Digite o e-mail do assinante.")
            else:
                try:
                    ativar_plano_admin(
                        email_assinante,
                        plano_admin,
                        status_admin
                    )
                    st.success("✅ Assinatura atualizada!")
                except Exception as e:
                    st.error(f"Não consegui atualizar a assinatura: {e}")

        st.markdown("---")
        st.subheader("🎞️ Gerenciar vídeos")

        if not videos:
            st.info("Não há vídeos cadastrados.")
        else:
            for item in videos:
                st.markdown("---")
                st.write(
                    f"**{item.get('nome', 'Sem título')}** — "
                    f"{item.get('categoria', '')}"
                )
                if st.button("Excluir", key=f"excluir_{item['id']}"):
                    excluir_video(item)
