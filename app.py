import streamlit as st
from supabase import create_client, Client
from datetime import datetime, timezone
from streamlit_js_eval import streamlit_js_eval
import uuid
import json
import time
import hmac
import hashlib
import base64
from textwrap import dedent

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
/* MENU ROXO ESCURO — elegante e com alto contraste */
section[data-testid="stSidebar"],
div[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #2A1242 0%, #211035 50%, #170A26 100%) !important;
    border-right: 1px solid rgba(242,214,117,0.35) !important;
}
section[data-testid="stSidebar"] > div,
div[data-testid="stSidebarContent"] {
    background: transparent !important;
}
/* Texto do menu sempre legível */
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] .stMarkdown {
    color: #FFFFFF !important;
}
/* Opções do menu em cartões lilás */
section[data-testid="stSidebar"] div[role="radiogroup"] label {
    background: rgba(104, 67, 157, 0.24) !important;
    border: 1px solid rgba(255,255,255,0.16) !important;
    border-radius: 14px !important;
    padding: 8px 10px !important;
    margin-bottom: 5px !important;
}
section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
    background: rgba(126, 83, 184, 0.38) !important;
}
/* Opção selecionada — destaque forte roxo + dourado */
section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked),
section[data-testid="stSidebar"] div[role="radiogroup"] label[data-baseweb="radio"]:has(input:checked) {
    background: linear-gradient(90deg, #5A2A8A 0%, #6B35A0 55%, #7A46B2 100%) !important;
    border: 2px solid #F6D86B !important;
    box-shadow:
        0 0 0 2px rgba(255,255,255,0.08) inset,
        0 0 16px rgba(246,216,107,0.22),
        0 5px 16px rgba(45, 20, 80, 0.30) !important;
    transform: translateX(3px);
}
section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) p,
section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) span,
section[data-testid="stSidebar"] div[role="radiogroup"] label[data-baseweb="radio"]:has(input:checked) p,
section[data-testid="stSidebar"] div[role="radiogroup"] label[data-baseweb="radio"]:has(input:checked) span {
    color: #FFFFFF !important;
    font-weight: 900 !important;
    text-shadow: 0 1px 2px rgba(0,0,0,0.18);
}
/* Bolinha do rádio: dourada quando selecionada */
section[data-testid="stSidebar"] input[type="radio"] {
    accent-color: #F6D86B !important;
}
section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) div:first-child {
    border-color: #F6D86B !important;
}
/* E-mail e qualquer link da barra lateral ficam claros */
section[data-testid="stSidebar"] a,
section[data-testid="stSidebar"] a:visited,
section[data-testid="stSidebar"] a:hover,
section[data-testid="stSidebar"] a:active {
    color: #FFFFFF !important;
    text-decoration-color: rgba(255,255,255,0.72) !important;
}
/* Caixa de usuário no rodapé do menu */
section[data-testid="stSidebar"] div[data-testid="stAlert"] {
    background: rgba(82, 49, 122, 0.34) !important;
    border: 1px solid rgba(242,214,117,0.34) !important;
}
section[data-testid="stSidebar"] div[data-testid="stAlert"] p,
section[data-testid="stSidebar"] div[data-testid="stAlert"] span,
section[data-testid="stSidebar"] div[data-testid="stAlert"] a {
    color: #FFFFFF !important;
}
div[data-testid="stButton"] button {
    width: 100%;
    border-radius: 14px;
    min-height: 46px;
    font-weight: 700;
    background: linear-gradient(90deg, #6d28d9, #8b5cf6);
    color: white;
    border: 1px solid #d6b45f;
}
div[data-testid="stButton"] button:hover {
    background: linear-gradient(90deg, #7c3aed, #9f7aea);
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

/* Botões compactos somente dentro dos cards do catálogo */
[class*="st-key-cardacoes_"] div[data-testid="stButton"] button {
    min-height: 38px !important;
    padding: 0.28rem 0.45rem !important;
    border-radius: 12px !important;
}
[class*="st-key-cardacoes_"] div[data-testid="stButton"] button p {
    font-size: 0.88rem !important;
    font-weight: 800 !important;
    white-space: nowrap !important;
}

/* Títulos compactos dos cards */
.titulo-card {
    width: 170px;
    font-size: 1.02rem;
    font-weight: 800;
    line-height: 1.22;
    color: #FFFFFF;
    margin: 0.18rem 0 0.08rem 0;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

/* Menos espaço entre título, categoria e botões dos cards */
.titulo-card + div {
    margin-top: 0.05rem !important;
}
[class*="st-key-cardacoes_"] {
    margin-top: -0.05rem !important;
    margin-bottom: 0.15rem !important;
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


def render_html(markup):
    """Exibe HTML sem o Streamlit transformar a indentação em bloco de código."""
    st.markdown(dedent(markup).strip(), unsafe_allow_html=True)


@st.cache_resource
def get_supabase() -> Client:
    return create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"]
    )


supabase = get_supabase()
BUCKET = "videos"

# -----------------------------
# LOGIN PERSISTENTE NO NAVEGADOR
# -----------------------------
# O token salvo no navegador contém apenas user_id, e-mail e validade.
# Ele é assinado no servidor para impedir alterações.
LOGIN_STORAGE_KEY = "mundo_luna_login_v1"

def _segredo_login():
    try:
        segredo = str(st.secrets.get("LOGIN_SESSION_SECRET", "")).strip()
        if not segredo:
            # Fallback para não derrubar o app enquanto o novo Secret ainda não foi criado.
            segredo = str(st.secrets.get("ADMIN_PASSWORD", "")).strip()
        return segredo
    except Exception:
        return ""

def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")

def _b64url_decode(texto: str) -> bytes:
    padding = "=" * (-len(texto) % 4)
    return base64.urlsafe_b64decode(texto + padding)

def criar_token_login(user_id: str, email: str, dias: int = 30) -> str | None:
    segredo = _segredo_login()
    if not segredo:
        return None

    payload = {
        "uid": str(user_id),
        "email": str(email).strip().lower(),
        "exp": int(time.time()) + (dias * 24 * 60 * 60),
    }
    payload_json = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    corpo = _b64url_encode(payload_json)
    assinatura = hmac.new(
        segredo.encode("utf-8"),
        corpo.encode("utf-8"),
        hashlib.sha256,
    ).digest()
    return f"{corpo}.{_b64url_encode(assinatura)}"

def validar_token_login(token: str):
    segredo = _segredo_login()
    if not segredo or not token or "." not in token:
        return None

    try:
        corpo, assinatura_recebida = token.split(".", 1)
        assinatura_esperada = hmac.new(
            segredo.encode("utf-8"),
            corpo.encode("utf-8"),
            hashlib.sha256,
        ).digest()
        assinatura_recebida_bytes = _b64url_decode(assinatura_recebida)

        if not hmac.compare_digest(assinatura_esperada, assinatura_recebida_bytes):
            return None

        payload = json.loads(_b64url_decode(corpo).decode("utf-8"))
        if int(payload.get("exp", 0)) < int(time.time()):
            return None
        if not payload.get("uid") or not payload.get("email"):
            return None
        return payload
    except Exception:
        return None

def agendar_salvar_login_navegador(token: str):
    if token:
        st.session_state["_login_token_para_salvar"] = token

def agendar_remover_login_navegador():
    st.session_state["_remover_login_browser"] = True

def executar_pendencias_browser():
    token = st.session_state.pop("_login_token_para_salvar", None)
    if token:
        js_token = json.dumps(token)
        streamlit_js_eval(
            js_expressions=f"localStorage.setItem('{LOGIN_STORAGE_KEY}', {js_token}); true",
            want_output=False,
            key=f"salvar_login_{hashlib.sha1(token.encode()).hexdigest()[:10]}",
        )

    if st.session_state.pop("_remover_login_browser", False):
        streamlit_js_eval(
            js_expressions=f"localStorage.removeItem('{LOGIN_STORAGE_KEY}'); true",
            want_output=False,
            key=f"remover_login_{int(time.time())}",
        )


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
        # Usa a chave administrativa quando disponível. Isso permite restaurar
        # o plano mesmo depois que o Streamlit reiniciar a sessão do navegador.
        admin = cliente_admin_assinaturas()
        if admin is not None:
            resp = (
                admin.table("assinaturas")
                .select("plano,status")
                .eq("user_id", st.session_state.usuario_id)
                .limit(1)
                .execute()
            )
        else:
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

        dados = resp.data or []
        if dados:
            item = dados[0]
            st.session_state.plano_atual = item.get("plano") or "Grátis"
            st.session_state.status_assinatura = item.get("status") or "inativo"
        else:
            st.session_state.plano_atual = "Grátis"
            st.session_state.status_assinatura = "inativo"
    except Exception:
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

        token_login = criar_token_login(st.session_state.usuario_id, st.session_state.usuario_logado)
        if token_login:
            agendar_salvar_login_navegador(token_login)

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
        token_login = criar_token_login(st.session_state.usuario_id, st.session_state.usuario_logado)
        if token_login:
            agendar_salvar_login_navegador(token_login)
        carregar_plano_usuario()
        return "logado"

    if resposta.user:
        return "confirmar_email"

    return "erro"


def sair_da_conta():
    agendar_remover_login_navegador()
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


def restaurar_login_do_navegador():
    if st.session_state.usuario_logado:
        return

    # Na primeira execução do componente, o valor pode vir como None.
    # Quando o navegador responder, o Streamlit executa o script novamente.
    token_salvo = streamlit_js_eval(
        js_expressions=f"localStorage.getItem('{LOGIN_STORAGE_KEY}') || '__SEM_LOGIN__'",
        want_output=True,
        key="ler_login_persistente",
    )

    if token_salvo is None:
        return

    if token_salvo == "__SEM_LOGIN__":
        return

    payload = validar_token_login(str(token_salvo))
    if not payload:
        # Token inválido ou expirado: limpa o navegador.
        streamlit_js_eval(
            js_expressions=f"localStorage.removeItem('{LOGIN_STORAGE_KEY}'); true",
            want_output=False,
            key="limpar_login_invalido",
        )
        return

    st.session_state.usuario_logado = payload["email"]
    st.session_state.usuario_id = payload["uid"]
    st.session_state.usuario_access_token = None
    st.session_state.usuario_refresh_token = None
    carregar_plano_usuario()


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


# -------------------------------------------------
# VÍDEOS GRÁTIS E PREMIUM SEM ALTERAR A TABELA SQL
# -------------------------------------------------
# Para não exigir uma nova coluna no Supabase, vídeos Premium são
# identificados pelo prefixo "Premium::" dentro do campo categoria.
# Exemplo: "Premium::Infantil". Vídeos antigos continuam gratuitos.
PREMIUM_PREFIX = "Premium::"
CARD_WIDTH = 190  # largura dos cards horizontais no celular


def video_premium(item):
    categoria = str(item.get("categoria") or "")
    return categoria.startswith(PREMIUM_PREFIX)


def categoria_base(item):
    categoria = str(item.get("categoria") or "")
    if categoria.startswith(PREMIUM_PREFIX):
        return categoria[len(PREMIUM_PREFIX):]
    return categoria


def categoria_para_salvar(categoria, acesso):
    if acesso == "Premium":
        return f"{PREMIUM_PREFIX}{categoria}"
    return categoria


def videos_gratis(lista):
    return [v for v in lista if not video_premium(v)]


def videos_premium(lista):
    return [v for v in lista if video_premium(v)]


def mostrar_card(item, contexto, em_minha_lista=False, compacto=False):
    if item.get("capa_url"):
        if compacto:
            st.image(item["capa_url"], width=280)
        else:
            st.image(item["capa_url"], use_container_width=True)

    if compacto:
        st.markdown(f"#### ✨ {item.get('nome', 'Sem título')}")
    else:
        st.markdown(f"### ✨ {item.get('nome', 'Sem título')}")
    categoria_visivel = categoria_base(item)
    if video_premium(item):
        st.caption(f"💎 Premium • 🌟 {categoria_visivel}")
    else:
        st.caption(f"🌟 {categoria_visivel}")

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


def mostrar_card_horizontal(item, contexto):
    """Card compacto para fileiras horizontais da Área Premium."""
    if item.get("capa_url"):
        st.image(item["capa_url"], width=170)

    nome = str(item.get("nome") or "Sem título")
    # Título compacto: menor e com no máximo 2 linhas.
    st.markdown(
        f"""<div class="titulo-card">✨ {nome}</div>""",
        unsafe_allow_html=True,
    )
    st.caption(f"💎 Premium • 🌟 {categoria_base(item)}")

    chave = f"aberto_{contexto}_{item['id']}"
    if chave not in st.session_state:
        st.session_state[chave] = False

    # Área compacta de ações: 150 px de largura.
    try:
        acoes = st.container(
            key=f"cardacoes_{contexto}_{item['id']}",
            width=142,
            border=False,
        )
    except TypeError:
        acoes = st.container(key=f"cardacoes_{contexto}_{item['id']}")

    with acoes:
        if not st.session_state[chave]:
            if st.button(
                "▶ Assistir",
                key=f"assistir_{contexto}_{item['id']}",
                use_container_width=True,
            ):
                registrar_assistido(item)
                st.session_state[chave] = True
                st.rerun()
        else:
            if st.button(
                "✖ Fechar",
                key=f"fechar_{contexto}_{item['id']}",
                use_container_width=True,
            ):
                st.session_state[chave] = False
                st.rerun()

        favorito = bool(item.get("favorito", False))
        texto = "💖 Na Lista" if favorito else "🤍 Minha Lista"
        if st.button(
            texto,
            key=f"fav_{contexto}_{item['id']}",
            use_container_width=True,
        ):
            alternar_favorito(item)

    if st.session_state.get(chave, False):
        st.video(item["video_url"])


def mostrar_fileira_premium(titulo, itens, contexto, limite=12):
    """Fileira horizontal com cards realmente pequenos (190 px)."""
    itens = list(itens)[:limite]
    if not itens:
        return

    st.markdown(f"### {titulo}")

    try:
        # Streamlit atual: cada card recebe largura fixa de 190 px.
        # A fileira não quebra e pode ser deslizada horizontalmente no celular.
        fileira = st.container(horizontal=True, wrap=False, gap="xsmall")
        for i, item in enumerate(itens):
            card = fileira.container(width=190, border=False)
            with card:
                mostrar_card_horizontal(item, f"{contexto}_{i}")
    except TypeError:
        # Compatibilidade com versões antigas do Streamlit.
        cols = st.columns(max(len(itens), 3), gap="xsmall", wrap=False)
        for i, (col, item) in enumerate(zip(cols, itens)):
            with col:
                mostrar_card_horizontal(item, f"{contexto}_{i}")


def mostrar_card_catalogo(item, contexto):
    """Card compacto para fileiras horizontais da tela inicial."""
    if item.get("capa_url"):
        st.image(item["capa_url"], width=170)

    nome = str(item.get("nome") or "Sem título")
    # Título compacto: menor e com no máximo 2 linhas.
    st.markdown(
        f"""<div class="titulo-card">✨ {nome}</div>""",
        unsafe_allow_html=True,
    )

    categoria_visivel = categoria_base(item)
    if video_premium(item):
        st.caption(f"💎 Premium • 🌟 {categoria_visivel}")
    else:
        st.caption(f"🌟 {categoria_visivel}")

    chave = f"aberto_{contexto}_{item['id']}"
    if chave not in st.session_state:
        st.session_state[chave] = False

    # Área compacta de ações: 150 px de largura.
    try:
        acoes = st.container(
            key=f"cardacoes_{contexto}_{item['id']}",
            width=142,
            border=False,
        )
    except TypeError:
        acoes = st.container(key=f"cardacoes_{contexto}_{item['id']}")

    with acoes:
        if not st.session_state[chave]:
            if st.button(
                "▶ Assistir",
                key=f"assistir_{contexto}_{item['id']}",
                use_container_width=True,
            ):
                registrar_assistido(item)
                st.session_state[chave] = True
                st.rerun()
        else:
            if st.button(
                "✖ Fechar",
                key=f"fechar_{contexto}_{item['id']}",
                use_container_width=True,
            ):
                st.session_state[chave] = False
                st.rerun()

        favorito = bool(item.get("favorito", False))
        texto = "💖 Na Lista" if favorito else "🤍 Minha Lista"
        if st.button(
            texto,
            key=f"fav_{contexto}_{item['id']}",
            use_container_width=True,
        ):
            alternar_favorito(item)

    if st.session_state.get(chave, False):
        st.video(item["video_url"])


def mostrar_fileira_catalogo(titulo, itens, contexto, limite=12):
    """Fileira horizontal da tela inicial com cards de 190 px."""
    itens = list(itens)[:limite]
    if not itens:
        return

    st.markdown(f"### {titulo}")

    try:
        fileira = st.container(horizontal=True, wrap=False, gap="xsmall")
        for i, item in enumerate(itens):
            card = fileira.container(width=190, border=False)
            with card:
                mostrar_card_catalogo(item, f"{contexto}_{i}")
    except TypeError:
        cols = st.columns(max(len(itens), 3), gap="xsmall", wrap=False)
        for i, (col, item) in enumerate(zip(cols, itens)):
            with col:
                mostrar_card_catalogo(item, f"{contexto}_{i}")


# Aplica gravação/remoção pendente do login no navegador e tenta restaurar a conta.
executar_pendencias_browser()
restaurar_login_do_navegador()

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
    videos_inicio = videos_gratis(videos)

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

    total = len(videos_inicio)
    infantil = len([v for v in videos_inicio if categoria_base(v) == "Infantil"])
    filmes = len([v for v in videos_inicio if categoria_base(v) == "Filmes"])
    series = len([v for v in videos_inicio if categoria_base(v) == "Séries"])

    render_html(f"""
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
    """)

    ultimo = ultimo_assistido(videos_inicio)
    if ultimo:
        st.subheader("▶ Continuar assistindo")
        try:
            continuar = st.container(width=240, border=False)
            with continuar:
                mostrar_card_catalogo(ultimo, "continuar_home")
        except TypeError:
            mostrar_card(ultimo, "continuar_home", compacto=True)
        st.markdown("---")

    if not videos_inicio:
        st.info("Ainda não há vídeos gratuitos. Abra 📤 Enviar vídeo para começar.")
    else:
        st.caption("Deslize as fileiras para o lado para ver mais vídeos. 💜")

        mostrar_fileira_catalogo(
            "✨ Novidades",
            videos_inicio,
            "home_novidades",
            limite=12,
        )

        infantil_home = [v for v in videos_inicio if categoria_base(v) == "Infantil"]
        filmes_home = [v for v in videos_inicio if categoria_base(v) == "Filmes"]
        series_home = [v for v in videos_inicio if categoria_base(v) == "Séries"]

        mostrar_fileira_catalogo(
            "🧸 Infantil",
            infantil_home,
            "home_infantil",
            limite=12,
        )
        mostrar_fileira_catalogo(
            "🎬 Filmes",
            filmes_home,
            "home_filmes",
            limite=12,
        )
        mostrar_fileira_catalogo(
            "📺 Séries",
            series_home,
            "home_series",
            limite=12,
        )

elif menu == "🔎 Buscar":
    st.subheader("🔎 Buscar vídeos")

    termo = st.text_input("Digite o nome do vídeo", placeholder="Ex.: Luna")
    categoria_busca = st.selectbox(
        "Filtrar por categoria",
        ["Todas", "Infantil", "Filmes", "Séries"]
    )

    filtrados = videos_gratis(videos)

    if termo.strip():
        termo_lower = termo.lower().strip()
        filtrados = [
            v for v in filtrados
            if termo_lower in v.get("nome", "").lower()
        ]

    if categoria_busca != "Todas":
        filtrados = [
            v for v in filtrados
            if categoria_base(v) == categoria_busca
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
    novidades = videos_gratis(videos)

    if not novidades:
        st.info("Ainda não há novidades.")
    else:
        cols = st.columns(2)
        for i, item in enumerate(novidades[:10]):
            with cols[i % 2]:
                mostrar_card(item, f"novidades_{i}")

elif menu == "❤️ Minha Lista":
    st.subheader("❤️ Minha Lista")

    favoritos = [
        v for v in videos_gratis(videos)
        if bool(v.get("favorito", False))
    ]

    if not favoritos:
        st.info("Sua lista ainda está vazia. Toque em 🤍 Minha Lista em qualquer vídeo.")
    else:
        cols = st.columns(2)
        for i, item in enumerate(favoritos):
            with cols[i % 2]:
                mostrar_card(item, f"favoritos_{i}", em_minha_lista=True)

elif menu == "🕒 Assistidos recentemente":
    st.subheader("🕒 Assistidos recentemente")

    recentes = listar_assistidos_recentes(videos_gratis(videos), limite=10)

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

        render_html("""
        <div class="plan-card">
            <div class="plan-title">🌙 Plano Grátis</div>
            <div class="plan-price">R$ 0</div>
            <p>• Conteúdos gratuitos</p>
            <p>• Minha Lista</p>
            <p>• Continuar assistindo</p>
        </div>
        """)

        render_html("""
        <div class="plan-card">
            <div class="plan-title">💎 Plano Premium</div>
            <div class="plan-price">R$ 30,00 por mês</div>
            <p>• Conteúdos exclusivos</p>
            <p>• Área Premium</p>
            <p>• Novidades para assinantes</p>
        </div>
        """)

        checkout_url = link_plano_pagamento()

        if checkout_url:
            render_html(
                f"""
                <a href="{checkout_url}" target="_blank" rel="noopener noreferrer"
                   style="
                       display:flex;
                       align-items:center;
                       justify-content:center;
                       width:100%;
                       min-height:62px;
                       box-sizing:border-box;
                       padding:0.75rem 1rem;
                       border-radius:16px;
                       border:2px solid #f2d675;
                       background:linear-gradient(90deg, #6d28d9, #8b5cf6);
                       color:#ffffff;
                       font-size:1.22rem;
                       font-weight:800;
                       text-decoration:none;
                       text-align:center;
                   ">
                    💳 Assinar Premium — R$ 30/mês
                </a>
                """
            )
            st.caption(
                "A Kiwify abrirá em outra aba. "
                "Depois do pagamento, volte para esta aba e toque em "
                "'Já paguei — atualizar meu plano'."
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
        render_html("""
        <div class="lock-card">
            <h3>🔒 Conteúdo Premium bloqueado</h3>
            <p>Essa área será liberada quando sua assinatura Premium for confirmada no sistema.</p>
        </div>
        """)

        st.button(
            "💎 Ver plano Premium",
            key="premium_ver_planos",
            on_click=mudar_menu,
            args=("💎 Planos",)
        )
    else:
        st.success("💎 Premium ativo!")
        exclusivos = videos_premium(videos)

        if not exclusivos:
            st.info("Ainda não há vídeos exclusivos. Envie um vídeo e marque o acesso como Premium.")
        else:
            st.caption("Deslize as fileiras para o lado para ver mais vídeos. 💜")

            # Novidades: mantém a ordem retornada pelo banco (mais recentes primeiro).
            mostrar_fileira_premium(
                "✨ Novidades",
                exclusivos,
                "premium_novidades",
                limite=12,
            )

            infantil_premium = [v for v in exclusivos if categoria_base(v) == "Infantil"]
            filmes_premium = [v for v in exclusivos if categoria_base(v) == "Filmes"]
            series_premium = [v for v in exclusivos if categoria_base(v) == "Séries"]

            mostrar_fileira_premium(
                "🧸 Infantil",
                infantil_premium,
                "premium_infantil",
                limite=12,
            )
            mostrar_fileira_premium(
                "🎬 Filmes",
                filmes_premium,
                "premium_filmes",
                limite=12,
            )
            mostrar_fileira_premium(
                "📺 Séries",
                series_premium,
                "premium_series",
                limite=12,
            )

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

        acesso = st.selectbox(
            "Quem pode assistir?",
            ["Grátis", "Premium"],
            help="Grátis aparece nas áreas normais. Premium aparece somente na Área Premium."
        )

        if acesso == "Premium":
            st.info("💎 Este vídeo ficará disponível somente para assinantes Premium ativos.")
        else:
            st.caption("🌙 Este vídeo ficará disponível nas áreas gratuitas do app.")

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
                            "categoria": categoria_para_salvar(categoria, acesso),
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

    itens = [
        v for v in videos_gratis(videos)
        if categoria_base(v) == categoria_atual
    ]

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
                acesso_item = "💎 Premium" if video_premium(item) else "🌙 Grátis"
                st.write(
                    f"**{item.get('nome', 'Sem título')}** — "
                    f"{categoria_base(item)} — {acesso_item}"
                )
                if st.button("Excluir", key=f"excluir_{item['id']}"):
                    excluir_video(item)
