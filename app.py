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
from io import BytesIO

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
    grid-template-columns: repeat(4, minmax(82px, 1fr));
    gap: 7px;
    margin: 8px 0 12px 0;
    overflow-x: auto;
    padding-bottom: 2px;
}
.metric-card {
    background: rgba(255,255,255,0.035);
    border: 1px solid rgba(242,214,117,0.22);
    border-radius: 13px;
    padding: 8px 6px;
    text-align: center;
    min-width: 82px;
}
.metric-number {
    font-size: 1.35rem;
    font-weight: 800;
    line-height: 1.05;
}
.metric-label {
    color: #f2d675;
    font-size: 0.76rem;
    margin-top: 2px;
    white-space: nowrap;
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

/* Botão compacto da conta na tela inicial */
[class*="st-key-atalho_conta_home"] div[data-testid="stButton"] button {
    min-height: 40px !important;
    padding: 0.28rem 0.75rem !important;
    border-radius: 13px !important;
}
[class*="st-key-atalho_conta_home"] div[data-testid="stButton"] button p {
    font-size: 0.96rem !important;
    font-weight: 800 !important;
    white-space: nowrap !important;
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


/* Cabeçalho principal super compacto no celular */
@media (max-width: 640px) {
    .hero {
        padding: 10px 12px 10px 12px !important;
        border-radius: 16px !important;
        margin-bottom: 4px !important;
        min-height: 0 !important;
    }
    .hero .hero-title {
        font-size: 1.45rem !important;
        line-height: 1.0 !important;
        margin: 0 0 5px 0 !important;
        display: block !important;
    }
    .hero .hero-subtitle {
        font-size: 0.78rem !important;
        line-height: 1.18 !important;
        margin: 0 !important;
        display: block !important;
    }
    .hero .magic {
        margin: 0 !important;
        line-height: 1.18 !important;
    }
    .gold-line {
        margin: 4px 0 10px 0 !important;
    }
}


/* Títulos compactos das seções */
.secao-titulo-compacto {
    color: #FFFFFF;
    font-size: 1.65rem;
    font-weight: 800;
    line-height: 1.08;
    margin: 0.30rem 0 0.55rem 0;
}
@media (max-width: 640px) {
    .secao-titulo-compacto {
        font-size: 1.22rem !important;
        line-height: 1.06 !important;
        margin: 0.18rem 0 0.38rem 0 !important;
    }
}


/* Menu lateral compacto no celular */
@media (max-width: 640px) {
    section[data-testid="stSidebar"] div[role="radiogroup"] {
        gap: 0 !important;
    }
    section[data-testid="stSidebar"] div[role="radiogroup"] label {
        border-radius: 11px !important;
        padding: 5px 8px !important;
        margin-bottom: 3px !important;
        min-height: 42px !important;
    }
    section[data-testid="stSidebar"] div[role="radiogroup"] label p,
    section[data-testid="stSidebar"] div[role="radiogroup"] label span {
        font-size: 0.90rem !important;
        line-height: 1.08 !important;
    }
    section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked),
    section[data-testid="stSidebar"] div[role="radiogroup"] label[data-baseweb="radio"]:has(input:checked) {
        border-width: 2px !important;
        transform: translateX(1px) !important;
    }
    section[data-testid="stSidebar"] div[role="radiogroup"] input[type="radio"] {
        transform: scale(0.88);
    }
    section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {
        font-size: 1.05rem !important;
        margin-bottom: 0.25rem !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stAlert"] {
        padding: 0.45rem 0.6rem !important;
    }
}


/* Selo NOVO compacto e mais próximo da capa/título */
.selo-novo {
    display: inline-block;
    width: fit-content;
    background: rgba(255, 193, 7, 0.18);
    border: 1px solid rgba(255, 214, 80, 0.58);
    color: #FFD54F;
    font-size: 0.78rem;
    font-weight: 800;
    line-height: 1;
    padding: 0.26rem 0.48rem;
    border-radius: 8px;
    margin: -0.10rem 0 0.05rem 0;
}
@media (max-width: 640px) {
    .selo-novo {
        font-size: 0.74rem;
        padding: 0.22rem 0.42rem;
        margin-top: -0.18rem;
        margin-bottom: 0.02rem;
    }
    .titulo-card {
        margin-top: 0.08rem !important;
    }
}


/* Menos espaço entre o fim de um card e o título da próxima seção */
@media (max-width: 640px) {
    .secao-titulo-compacto {
        margin-top: 0.08rem !important;
    }
    [class*="st-key-cardacoes_"] {
        margin-bottom: 0 !important;
    }
}


/* Selo compacto do plano na Home e na sidebar */
.status-plano {
    display: inline-block;
    width: fit-content;
    border-radius: 999px;
    padding: 0.28rem 0.58rem;
    font-size: 0.78rem !important;
    font-weight: 800;
    line-height: 1;
    margin: 0.20rem 0 0.35rem 0;
    letter-spacing: 0.01em;
}
.status-plano.premium {
    background: rgba(139, 92, 246, 0.18);
    border: 1px solid rgba(196, 181, 253, 0.55);
    color: #E9D5FF !important;
}
.status-plano.gratis {
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.18);
    color: #F3F4F6 !important;
}
section[data-testid="stSidebar"] .status-plano {
    font-size: 0.72rem !important;
    padding: 0.24rem 0.50rem;
    margin-top: 0.15rem;
    margin-bottom: 0.20rem;
}


/* Botão voltar compacto */
@media (max-width: 640px) {
    [class*="st-key-botao_voltar_inicio"] button,
    button[kind="secondary"]:has(p:contains("← Voltar")) {
        min-height: 34px !important;
        padding: 0.20rem 0.50rem !important;
        border-radius: 10px !important;
        font-size: 0.82rem !important;
    }
}


/* Botão Voltar bem compacto nas páginas internas */
[class*="st-key-botao_voltar_inicio"] button {
    min-height: 34px !important;
    height: 34px !important;
    padding: 0.12rem 0.48rem !important;
    border-radius: 10px !important;
}
[class*="st-key-botao_voltar_inicio"] button p {
    font-size: 0.80rem !important;
    font-weight: 800 !important;
    white-space: nowrap !important;
}
@media (max-width: 640px) {
    [class*="st-key-botao_voltar_inicio"] {
        width: 92px !important;
        max-width: 92px !important;
        margin-bottom: 0.20rem !important;
    }
}


/* Aproxima Minha conta do selo Premium na tela inicial */
@media (max-width: 640px) {
    [class*="st-key-atalho_conta_home"] {
        margin-bottom: -0.10rem !important;
    }
    .status-plano {
        margin-top: 0.05rem !important;
        margin-bottom: 0.22rem !important;
    }
}


/* Reduz o espaço entre os botões do card e a próxima seção */
@media (max-width: 640px) {
    [class*="st-key-cardacoes_"] {
        margin-bottom: -0.18rem !important;
    }

    .secao-titulo-compacto {
        margin-top: 0.04rem !important;
    }
}


/* Aproxima a legenda "Deslize..." da seção Novidades no celular */
@media (max-width: 640px) {
    div[data-testid="stCaptionContainer"] {
        margin-top: -0.10rem !important;
        margin-bottom: -0.18rem !important;
    }

    div[data-testid="stCaptionContainer"] p {
        font-size: 0.78rem !important;
        line-height: 1.15 !important;
    }

    .secao-titulo-compacto {
        margin-top: 0.02rem !important;
    }
}


/* Reduz o grande espaço vazio antes da legenda "Deslize..." */
@media (max-width: 640px) {
    div[data-testid="stCaptionContainer"] {
        margin-top: -1.15rem !important;
    }

    hr {
        margin-top: 0.35rem !important;
        margin-bottom: 0.35rem !important;
    }
}


/* CORREÇÃO: captions normais voltam ao espaçamento correto */
@media (max-width: 640px) {
    div[data-testid="stCaptionContainer"] {
        margin-top: 0.12rem !important;
        margin-bottom: 0.18rem !important;
    }

    div[data-testid="stCaptionContainer"] p {
        font-size: 0.88rem !important;
        line-height: 1.22 !important;
    }

    /* Somente a dica de deslizar fica compacta */
    .dica-deslize {
        color: rgba(255,255,255,0.62);
        font-size: 0.78rem;
        line-height: 1.15;
        margin-top: 0.15rem;
        margin-bottom: 0.12rem;
    }
}


/* Categoria do card: separada do título para nunca sobrepor o texto */
.categoria-card {
    display: block;
    clear: both;
    color: rgba(255,255,255,0.62) !important;
    font-size: 0.82rem !important;
    line-height: 1.25 !important;
    margin-top: 0.18rem !important;
    margin-bottom: 0.22rem !important;
    min-height: 1.05rem;
}

.titulo-card {
    margin-bottom: 0.12rem !important;
}

@media (max-width: 640px) {
    .categoria-card {
        font-size: 0.78rem !important;
        margin-top: 0.16rem !important;
        margin-bottom: 0.18rem !important;
    }

    .titulo-card {
        margin-bottom: 0.10rem !important;
    }
}


/* Cards de estatísticas mais compactos no celular */
@media (max-width: 640px) {
    [class*="st-key-estat_"] {
        min-height: 108px !important;
        padding: 0.45rem 0.35rem !important;
        border-radius: 18px !important;
    }

    [class*="st-key-estat_"] h3,
    [class*="st-key-estat_"] div[data-testid="stMetricValue"] {
        font-size: 1.85rem !important;
        line-height: 1 !important;
        margin-bottom: 0.10rem !important;
    }

    [class*="st-key-estat_"] p,
    [class*="st-key-estat_"] div[data-testid="stMetricLabel"] {
        font-size: 0.76rem !important;
        line-height: 1.08 !important;
    }
}


/* CORREÇÃO: estes cards são HTML próprio (.metric-card), não widgets Streamlit */
@media (max-width: 640px) {
    .metric-grid {
        grid-template-columns: repeat(4, minmax(70px, 1fr)) !important;
        gap: 5px !important;
        margin-top: 5px !important;
        margin-bottom: 9px !important;
    }

    .metric-card {
        min-width: 70px !important;
        padding: 6px 3px !important;
        border-radius: 12px !important;
    }

    .metric-number {
        font-size: 1.45rem !important;
        line-height: 1 !important;
    }

    .metric-label {
        font-size: 0.70rem !important;
        line-height: 1.05 !important;
        margin-top: 3px !important;
    }
}


/* Botão da área Criar vídeo com IA */
@media (max-width: 640px) {
    [class*="st-key-gerar_video_ia"] button {
        min-height: 48px !important;
        border-radius: 14px !important;
        font-weight: 800 !important;
    }
}


/* Jogos e atividades */
@media (max-width: 640px) {
    [class*="st-key-conferir_"] button {
        min-height: 44px !important;
        border-radius: 14px !important;
        font-weight: 800 !important;
    }
}


/* Área Premium */
.premium-hero {
    padding: 16px;
    border-radius: 20px;
    border: 1px solid rgba(242,214,117,0.40);
    background:
        radial-gradient(circle at top right, rgba(242,214,117,0.13), transparent 35%),
        linear-gradient(135deg, rgba(91,33,182,0.34), rgba(49,17,78,0.58));
    margin: 0.20rem 0 0.75rem 0;
}

.premium-hero-title {
    color: #FFFFFF !important;
    font-size: 1.45rem;
    font-weight: 900;
    line-height: 1.15;
    margin-bottom: 0.28rem;
}

.premium-hero-text {
    color: rgba(255,255,255,0.78) !important;
    font-size: 0.95rem;
    line-height: 1.35;
}

.premium-stats {
    display: grid;
    grid-template-columns: repeat(4, minmax(72px, 1fr));
    gap: 7px;
    margin: 0.55rem 0 0.85rem 0;
}

.premium-stat {
    border-radius: 14px;
    border: 1px solid rgba(242,214,117,0.28);
    background: rgba(255,255,255,0.045);
    padding: 9px 5px;
    text-align: center;
}

.premium-stat-num {
    color: #FFFFFF !important;
    font-size: 1.45rem;
    font-weight: 900;
    line-height: 1;
}

.premium-stat-label {
    color: #F2D675 !important;
    font-size: 0.74rem;
    line-height: 1.12;
    margin-top: 4px;
}

@media (max-width: 640px) {
    .premium-hero {
        padding: 12px !important;
        border-radius: 17px !important;
        margin-bottom: 0.55rem !important;
    }

    .premium-hero-title {
        font-size: 1.18rem !important;
    }

    .premium-hero-text {
        font-size: 0.82rem !important;
    }

    .premium-stats {
        gap: 5px !important;
        margin-top: 0.40rem !important;
        margin-bottom: 0.65rem !important;
    }

    .premium-stat {
        padding: 7px 3px !important;
        border-radius: 12px !important;
    }

    .premium-stat-num {
        font-size: 1.28rem !important;
    }

    .premium-stat-label {
        font-size: 0.66rem !important;
    }
}


/* Jogo da memória — cartas maiores e desenhos mais visíveis */
[class*="st-key-memoria_carta_"] button {
    min-height: 104px !important;
    font-size: 3rem !important;
    border-radius: 18px !important;
    border: 2px solid #8b5cf6 !important;
    font-weight: 800 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    padding: 0.25rem !important;
}
[class*="st-key-memoria_carta_"] button p,
[class*="st-key-memoria_carta_"] button span,
[class*="st-key-memoria_carta_"] button [data-testid="stMarkdownContainer"] p {
    font-size: 3rem !important;
    line-height: 1 !important;
    margin: 0 !important;
}
[class*="st-key-memoria_novo_jogo"] button,
[class*="st-key-memoria_continuar"] button {
    min-height: 46px !important;
    border-radius: 14px !important;
    font-weight: 800 !important;
}


/* Atualização completa: vídeo IA, jogos e atividades */
[class*="st-key-gerar_video_ia"] button,
[class*="st-key-conferir_atividade_"] button,
[class*="st-key-baixar_atividade_"] button {
    min-height: 52px !important;
    border-radius: 16px !important;
    font-weight: 800 !important;
}


/* Crédito, download e jogo no celular */
div[data-testid="stDownloadButton"] button {
    width: 100% !important;
    min-height: 54px !important;
    border-radius: 16px !important;
    border: 2px solid #f2d675 !important;
    background: linear-gradient(90deg, #6d28d9, #8b5cf6) !important;
    color: #ffffff !important;
    font-weight: 800 !important;
}
div[data-testid="stDownloadButton"] button p,
div[data-testid="stDownloadButton"] button span {
    color: #ffffff !important;
    font-size: 1.05rem !important;
    font-weight: 800 !important;
}
[class*="st-key-memoria_carta_"] {
    min-width: 0 !important;
    width: 100% !important;
    max-width: 100% !important;
}

/* Jogo da memória responsivo no celular */
@media (max-width: 640px) {
    [class*="st-key-memoria_carta_"] {
        min-width: 0 !important;
        width: 100% !important;
        max-width: 100% !important;
        overflow: hidden !important;
    }

    [class*="st-key-memoria_carta_"] button {
        width: 100% !important;
        min-width: 0 !important;
        min-height: 92px !important;
        padding: 0.20rem 0.10rem !important;
        font-size: 2.65rem !important;
        border-radius: 16px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }

    [class*="st-key-memoria_carta_"] button p,
    [class*="st-key-memoria_carta_"] button span,
    [class*="st-key-memoria_carta_"] button [data-testid="stMarkdownContainer"] p {
        font-size: 2.65rem !important;
        line-height: 1 !important;
        margin: 0 !important;
    }

    [class*="st-key-memoria_carta_"] + div[data-testid="stCaptionContainer"] {
        text-align: center !important;
    }
}



/* =========================================================
   MODO NOTEBOOK / SMART TV — telas grandes
   Mantém o celular como está e amplia a interface em telas maiores.
   ========================================================= */
@media (min-width: 1100px) {
    .block-container {
        max-width: 1500px !important;
        padding-left: 2.2rem !important;
        padding-right: 2.2rem !important;
        padding-top: 1.2rem !important;
    }

    .hero {
        padding: 22px 28px !important;
        border-radius: 24px !important;
    }

    .hero .hero-title {
        font-size: 2.45rem !important;
        line-height: 1.08 !important;
    }

    .hero .hero-subtitle,
    .hero .magic {
        font-size: 1.2rem !important;
    }

    .secao-titulo-compacto {
        font-size: 2rem !important;
        margin-top: 0.7rem !important;
        margin-bottom: 0.7rem !important;
    }

    .titulo-card {
        width: 230px !important;
        font-size: 1.18rem !important;
        line-height: 1.24 !important;
        -webkit-line-clamp: 2 !important;
    }

    .categoria-card {
        font-size: 0.94rem !important;
    }

    [class*="st-key-cardacoes_"] div[data-testid="stButton"] button {
        min-height: 46px !important;
        padding: 0.45rem 0.7rem !important;
        border-radius: 13px !important;
    }

    [class*="st-key-cardacoes_"] div[data-testid="stButton"] button p {
        font-size: 0.98rem !important;
    }

    div[data-testid="stButton"] button,
    div[data-testid="stLinkButton"] a {
        min-height: 54px !important;
    }

    video {
        width: 100% !important;
        max-height: 72vh !important;
        background: #000 !important;
        border-radius: 18px !important;
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] label {
        min-height: 46px !important;
        padding: 8px 10px !important;
    }
}

/* TVs e monitores grandes: leitura confortável à distância */
@media (min-width: 1600px) {
    .block-container {
        max-width: 1800px !important;
        padding-left: 3rem !important;
        padding-right: 3rem !important;
    }

    .hero .hero-title {
        font-size: 3rem !important;
    }

    .hero .hero-subtitle,
    .hero .magic {
        font-size: 1.35rem !important;
    }

    .secao-titulo-compacto {
        font-size: 2.35rem !important;
    }

    .titulo-card {
        width: 270px !important;
        font-size: 1.3rem !important;
    }

    .categoria-card {
        font-size: 1.02rem !important;
    }

    [class*="st-key-cardacoes_"] div[data-testid="stButton"] button {
        min-height: 52px !important;
    }

    [class*="st-key-cardacoes_"] div[data-testid="stButton"] button p {
        font-size: 1.08rem !important;
    }
}

/* MODO TV — leitura à distância e foco no catálogo */
.tv-dica {
    font-size: 1.05rem;
    color: rgba(255,255,255,0.78);
    margin: 0.25rem 0 1rem 0;
}
@media (min-width: 1100px) {
    [class*="st-key-tv_assistir_"] button,
    [class*="st-key-tv_fechar_"] button,
    [class*="st-key-tv_fav_"] button {
        min-height: 62px !important;
        font-size: 1.15rem !important;
    }
}
@media (min-width: 1600px) {
    .tv-dica {
        font-size: 1.28rem !important;
    }
    [class*="st-key-tv_assistir_"] button,
    [class*="st-key-tv_fechar_"] button,
    [class*="st-key-tv_fav_"] button {
        min-height: 74px !important;
    }
    [class*="st-key-tv_assistir_"] button p,
    [class*="st-key-tv_fechar_"] button p,
    [class*="st-key-tv_fav_"] button p {
        font-size: 1.35rem !important;
    }
}


/* =========================================================
   ATUALIZAÇÃO RESPONSIVA V3 — CELULAR / NOTEBOOK / TV
   ========================================================= */

/* Capas uniformes nos cards do catálogo e do Modo TV */
[class*="st-key-catalogcard_"] [data-testid="stImage"] img,
[class*="st-key-premiumcard_"] [data-testid="stImage"] img,
[class*="st-key-tvcard_"] [data-testid="stImage"] img {
    width: 100% !important;
    aspect-ratio: 16 / 9 !important;
    object-fit: cover !important;
    border-radius: 16px !important;
}

/* Cards usam toda a largura disponível de cada coluna */
[class*="st-key-catalogcard_"],
[class*="st-key-premiumcard_"],
[class*="st-key-tvcard_"] {
    width: 100% !important;
}

/* Títulos do catálogo: duas linhas em telas maiores */
.titulo-card {
    width: 100% !important;
    max-width: 100% !important;
}

/* Player sempre ocupa toda a largura do card/coluna */
[data-testid="stVideo"] video,
video {
    width: 100% !important;
    max-width: 100% !important;
}

/* Notebook e desktop: 3 cards por linha no catálogo normal */
@media (min-width: 641px) and (max-width: 1399px) {
    [class*="st-key-catalogcard_"] .titulo-card,
    [class*="st-key-premiumcard_"] .titulo-card {
        font-size: 1.05rem !important;
    }
}

/* TV/telas grandes: botões e títulos confortáveis */
@media (min-width: 1400px) {
    [class*="st-key-tvcard_"] h3 {
        font-size: 1.35rem !important;
        line-height: 1.15 !important;
    }
    [class*="st-key-tvcard_"] div[data-testid="stButton"] button {
        min-height: 58px !important;
        font-size: 1.05rem !important;
    }
}

/* CELULAR: uma coluna, título completo e botões largos */
@media (max-width: 640px) {
    .titulo-card {
        width: 100% !important;
        max-width: 100% !important;
        font-size: 1.08rem !important;
        line-height: 1.22 !important;
        display: block !important;
        overflow: visible !important;
        -webkit-line-clamp: unset !important;
        -webkit-box-orient: initial !important;
        white-space: normal !important;
        overflow-wrap: anywhere !important;
    }

    [class*="st-key-cardacoes_"] {
        width: 100% !important;
        max-width: 100% !important;
    }

    [class*="st-key-cardacoes_"] div[data-testid="stButton"] button {
        width: 100% !important;
        min-height: 46px !important;
        padding: 0.45rem 0.7rem !important;
    }

    [class*="st-key-cardacoes_"] div[data-testid="stButton"] button p {
        font-size: 0.98rem !important;
        white-space: normal !important;
    }

    /* Voltar pequeno de verdade no celular */
    [class*="st-key-botao_voltar_inicio"] {
        width: 108px !important;
        max-width: 108px !important;
    }
    [class*="st-key-botao_voltar_inicio"] div[data-testid="stButton"] button {
        min-height: 36px !important;
        height: 36px !important;
        padding: 0.10rem 0.45rem !important;
        border-radius: 10px !important;
    }
    [class*="st-key-botao_voltar_inicio"] div[data-testid="stButton"] button p {
        font-size: 0.82rem !important;
        line-height: 1 !important;
    }

    [class*="st-key-catalogcard_"] [data-testid="stImage"] img,
    [class*="st-key-premiumcard_"] [data-testid="stImage"] img,
    [class*="st-key-tvcard_"] [data-testid="stImage"] img {
        aspect-ratio: 16 / 9 !important;
        object-fit: cover !important;
    }
}


/* =========================================================
   ATUALIZAÇÃO V4 — CELULAR MAIS COMPACTO
   Mantém notebook/TV grandes e reduz rolagem no celular.
   ========================================================= */
@media (max-width: 640px) {
    /* Menos margens laterais e verticais no conteúdo principal */
    .block-container {
        padding-left: 0.75rem !important;
        padding-right: 0.75rem !important;
        padding-bottom: 1.2rem !important;
    }

    /* Cards do catálogo e Modo TV mais compactos */
    [class*="st-key-catalogcard_"],
    [class*="st-key-premiumcard_"],
    [class*="st-key-tvcard_"] {
        margin-bottom: 0.55rem !important;
        padding-bottom: 0 !important;
    }

    /* Capas continuam largas, porém um pouco mais baixas no celular */
    [class*="st-key-catalogcard_"] [data-testid="stImage"] img,
    [class*="st-key-premiumcard_"] [data-testid="stImage"] img,
    [class*="st-key-tvcard_"] [data-testid="stImage"] img {
        width: 100% !important;
        aspect-ratio: 16 / 8.3 !important;
        max-height: 190px !important;
        object-fit: cover !important;
        border-radius: 13px !important;
    }

    /* Títulos completos sem ficarem enormes */
    .titulo-card,
    [class*="st-key-tvcard_"] h3 {
        font-size: 1.12rem !important;
        line-height: 1.18 !important;
        margin-top: 0.22rem !important;
        margin-bottom: 0.10rem !important;
        white-space: normal !important;
        overflow-wrap: anywhere !important;
    }

    [class*="st-key-tvcard_"] div[data-testid="stCaptionContainer"] {
        margin-top: 0.02rem !important;
        margin-bottom: 0.18rem !important;
    }

    [class*="st-key-tvcard_"] div[data-testid="stCaptionContainer"] p,
    .categoria-card {
        font-size: 0.82rem !important;
        line-height: 1.15 !important;
    }

    /* Botões do catálogo: menores e confortáveis ao toque */
    [class*="st-key-cardacoes_"] div[data-testid="stButton"] button,
    [class*="st-key-tv_assistir_"] button,
    [class*="st-key-tv_fechar_"] button,
    [class*="st-key-tv_fav_"] button {
        min-height: 46px !important;
        height: 46px !important;
        padding: 0.28rem 0.55rem !important;
        border-radius: 13px !important;
        margin: 0 !important;
    }

    [class*="st-key-cardacoes_"] div[data-testid="stButton"] button p,
    [class*="st-key-tv_assistir_"] button p,
    [class*="st-key-tv_fechar_"] button p,
    [class*="st-key-tv_fav_"] button p {
        font-size: 0.95rem !important;
        line-height: 1 !important;
        font-weight: 800 !important;
        white-space: normal !important;
    }

    /* Menos espaço entre os dois botões de cada card */
    [class*="st-key-cardacoes_"] div[data-testid="stButton"],
    [class*="st-key-tvcard_"] div[data-testid="stButton"] {
        margin-top: 0.12rem !important;
        margin-bottom: 0.12rem !important;
    }

    /* Seções mais próximas umas das outras */
    .secao-titulo-compacto {
        margin-top: 0.30rem !important;
        margin-bottom: 0.35rem !important;
        font-size: 1.28rem !important;
    }

    /* Separadores do Modo TV não criam grandes vazios */
    hr {
        margin-top: 0.45rem !important;
        margin-bottom: 0.45rem !important;
    }

    .tv-dica {
        font-size: 0.82rem !important;
        line-height: 1.2 !important;
        margin: 0.18rem 0 0.55rem 0 !important;
    }

    /* Player: largo, mas sem ocupar a tela inteira verticalmente */
    [data-testid="stVideo"] video,
    video {
        width: 100% !important;
        max-height: 58vh !important;
        border-radius: 13px !important;
        background: #000 !important;
    }

    /* Botão Voltar menor */
    [class*="st-key-botao_voltar_inicio"] {
        width: 92px !important;
        max-width: 92px !important;
    }
    [class*="st-key-botao_voltar_inicio"] div[data-testid="stButton"] button {
        min-height: 34px !important;
        height: 34px !important;
        padding: 0.08rem 0.36rem !important;
    }
    [class*="st-key-botao_voltar_inicio"] div[data-testid="stButton"] button p {
        font-size: 0.78rem !important;
    }
}


/* =========================================================
   POLIMENTO FINAL V7 — CELULAR, JOGOS, PLAYER E ACESSIBILIDADE
   ========================================================= */

/* Foco visível para teclado/controle remoto de TV */
div[data-testid="stButton"] button:focus-visible,
div[data-testid="stLinkButton"] a:focus-visible,
section[data-testid="stSidebar"] label:focus-within {
    outline: 3px solid #F6D86B !important;
    outline-offset: 3px !important;
}

/* Player consistente em celular, notebook e TV */
[data-testid="stVideo"],
[data-testid="stVideo"] video {
    width: 100% !important;
    max-width: 100% !important;
}
[data-testid="stVideo"] video {
    aspect-ratio: 16 / 9 !important;
    object-fit: contain !important;
    background: #000 !important;
}

/* Legendas do jogo da memória centralizadas e próximas das cartas */
[class*="st-key-memoria_carta_"] + div[data-testid="stCaptionContainer"],
[class*="st-key-memoria_carta_"] ~ div[data-testid="stCaptionContainer"] {
    text-align: center !important;
    margin-top: 0.10rem !important;
    margin-bottom: 0.30rem !important;
}
[class*="st-key-memoria_carta_"] + div[data-testid="stCaptionContainer"] p,
[class*="st-key-memoria_carta_"] ~ div[data-testid="stCaptionContainer"] p {
    font-size: 0.82rem !important;
    line-height: 1.1 !important;
}

/* Botões auxiliares do jogo da memória mais compactos */
[class*="st-key-memoria_continuar"] button,
[class*="st-key-memoria_novo_jogo"] button {
    min-height: 44px !important;
    padding: 0.35rem 0.70rem !important;
    border-radius: 13px !important;
}
[class*="st-key-memoria_continuar"] button p,
[class*="st-key-memoria_novo_jogo"] button p {
    font-size: 0.95rem !important;
}

/* Mobile: reduz rolagem sem perder legibilidade */
@media (max-width: 640px) {
    .block-container {
        padding-top: 0.65rem !important;
    }

    [class*="st-key-catalogcard_"],
    [class*="st-key-premiumcard_"],
    [class*="st-key-tvcard_"] {
        margin-bottom: 0.35rem !important;
    }

    [class*="st-key-cardacoes_"] button,
    [class*="st-key-tv_assistir_"] button,
    [class*="st-key-tv_fechar_"] button,
    [class*="st-key-tv_fav_"] button {
        min-height: 44px !important;
        padding: 0.34rem 0.58rem !important;
    }

    [class*="st-key-cardacoes_"] button p,
    [class*="st-key-tv_assistir_"] button p,
    [class*="st-key-tv_fechar_"] button p,
    [class*="st-key-tv_fav_"] button p {
        font-size: 0.94rem !important;
        line-height: 1.05 !important;
    }

    [class*="st-key-memoria_carta_"] button {
        min-height: 96px !important;
    }

    [class*="st-key-memoria_carta_"] button p,
    [class*="st-key-memoria_carta_"] button span,
    [class*="st-key-memoria_carta_"] button [data-testid="stMarkdownContainer"] p {
        font-size: 2.8rem !important;
    }

    [data-testid="stVideo"] video {
        max-height: 55vh !important;
        border-radius: 13px !important;
    }
}

/* Notebook: aproveita largura sem deixar os elementos gigantes */
@media (min-width: 641px) and (max-width: 1399px) {
    .block-container {
        max-width: 1250px !important;
    }
}

/* Smart TV / monitor grande: foco em leitura à distância */
@media (min-width: 1400px) {
    [class*="st-key-tv_assistir_"] button,
    [class*="st-key-tv_fechar_"] button,
    [class*="st-key-tv_fav_"] button {
        min-height: 62px !important;
    }
}


/* V8 — PROGRESSO DOS JOGOS */
@media (max-width: 640px) {
    div[data-testid="stProgress"] {
        margin-top: 0.20rem !important;
        margin-bottom: 0.35rem !important;
    }
    div[data-testid="stProgress"] p {
        font-size: 0.82rem !important;
        line-height: 1.1 !important;
    }
}

.fase-desbloqueada {
    display: inline-block;
    margin: 0.35rem 0 0.55rem 0;
    padding: 0.42rem 0.72rem;
    border-radius: 999px;
    background: rgba(246,216,107,0.13);
    border: 1px solid rgba(246,216,107,0.55);
    color: #F6D86B;
    font-weight: 800;
    font-size: 0.95rem;
}


/* V9 — aproxima o texto das cartas no jogo da memória */
@media (max-width: 640px) {
    [class*="st-key-memoria_carta_"] {
        margin-bottom: 0 !important;
    }

    [class*="st-key-memoria_carta_"] + div[data-testid="stCaptionContainer"],
    [class*="st-key-memoria_carta_"] ~ div[data-testid="stCaptionContainer"] {
        margin-top: -0.15rem !important;
        margin-bottom: 0.10rem !important;
        padding-top: 0 !important;
        padding-bottom: 0 !important;
        text-align: center !important;
    }

    [class*="st-key-memoria_carta_"] + div[data-testid="stCaptionContainer"] p,
    [class*="st-key-memoria_carta_"] ~ div[data-testid="stCaptionContainer"] p {
        font-size: 0.76rem !important;
        line-height: 1 !important;
        margin: 0 !important;
    }
}


/* V10 — melhora contraste dos campos de resposta nas atividades */
div[data-testid="stTextInput"] input,
div[data-testid="stTextArea"] textarea {
    color: #1f2937 !important;
    background: #ffffff !important;
    caret-color: #1f2937 !important;
    -webkit-text-fill-color: #1f2937 !important;
}

div[data-testid="stTextInput"] input::placeholder,
div[data-testid="stTextArea"] textarea::placeholder {
    color: #7c8798 !important;
    opacity: 1 !important;
    -webkit-text-fill-color: #7c8798 !important;
}

div[data-testid="stTextInput"] input:focus,
div[data-testid="stTextArea"] textarea:focus {
    color: #111827 !important;
    background: #ffffff !important;
    -webkit-text-fill-color: #111827 !important;
}


/* V11 — Modo TV compacto no notebook/computador */
@media (min-width: 641px) and (max-width: 1399px) {
    [class*="st-key-tvcard_"] [data-testid="stImage"] img {
        max-height: 125px !important;
        aspect-ratio: 16 / 9 !important;
        object-fit: cover !important;
        border-radius: 12px !important;
    }

    [class*="st-key-tvcard_"] h3 {
        font-size: 1rem !important;
        line-height: 1.12 !important;
        margin-top: 0.20rem !important;
        margin-bottom: 0.08rem !important;
    }

    [class*="st-key-tvcard_"] div[data-testid="stCaptionContainer"] p {
        font-size: 0.78rem !important;
        line-height: 1.1 !important;
    }

    [class*="st-key-tv_assistir_"] button,
    [class*="st-key-tv_fechar_"] button,
    [class*="st-key-tv_fav_"] button {
        min-height: 40px !important;
        height: 40px !important;
        padding: 0.20rem 0.45rem !important;
        border-radius: 11px !important;
    }

    [class*="st-key-tv_assistir_"] button p,
    [class*="st-key-tv_fechar_"] button p,
    [class*="st-key-tv_fav_"] button p {
        font-size: 0.86rem !important;
        line-height: 1 !important;
    }

    [class*="st-key-tvcard_"] div[data-testid="stButton"] {
        margin-top: 0.08rem !important;
        margin-bottom: 0.08rem !important;
    }

    [class*="st-key-tvcard_"] [data-testid="stVideo"] video {
        max-height: 155px !important;
        object-fit: contain !important;
    }

    .tv-dica {
        font-size: 0.84rem !important;
        margin-bottom: 0.55rem !important;
    }

    hr {
        margin-top: 0.45rem !important;
        margin-bottom: 0.45rem !important;
    }
}


/* V12 — catálogo ainda mais compacto no notebook */
@media (min-width: 641px) and (max-width: 1399px) {
    [class*="st-key-catalogcard_"] [data-testid="stImage"] img,
    [class*="st-key-premiumcard_"] [data-testid="stImage"] img {
        max-height: 118px !important;
        aspect-ratio: 16 / 9 !important;
        object-fit: cover !important;
        border-radius: 11px !important;
    }

    [class*="st-key-catalogcard_"] .titulo-card,
    [class*="st-key-premiumcard_"] .titulo-card {
        font-size: 0.92rem !important;
        line-height: 1.08 !important;
        margin-top: 0.16rem !important;
        margin-bottom: 0.05rem !important;
    }

    [class*="st-key-cardacoes_"] div[data-testid="stButton"] button {
        min-height: 38px !important;
        height: 38px !important;
        padding: 0.16rem 0.38rem !important;
        border-radius: 10px !important;
    }

    [class*="st-key-cardacoes_"] div[data-testid="stButton"] button p {
        font-size: 0.82rem !important;
        line-height: 1 !important;
    }

    .categoria-card {
        font-size: 0.74rem !important;
        line-height: 1.05 !important;
        margin-bottom: 0.10rem !important;
    }
}


/* V13 — Jogos mais compactos no notebook */
@media (min-width: 641px) and (max-width: 1399px) {
    [class*="st-key-memoria_carta_"] button {
        min-height: 74px !important;
        height: 74px !important;
        font-size: 2.15rem !important;
        border-radius: 14px !important;
        padding: 0.15rem !important;
    }

    [class*="st-key-memoria_carta_"] button p,
    [class*="st-key-memoria_carta_"] button span,
    [class*="st-key-memoria_carta_"] button [data-testid="stMarkdownContainer"] p {
        font-size: 2.15rem !important;
        line-height: 1 !important;
    }

    [class*="st-key-memoria_carta_"] + div[data-testid="stCaptionContainer"],
    [class*="st-key-memoria_carta_"] ~ div[data-testid="stCaptionContainer"] {
        margin-top: -0.05rem !important;
        margin-bottom: 0.05rem !important;
    }

    [class*="st-key-memoria_carta_"] + div[data-testid="stCaptionContainer"] p,
    [class*="st-key-memoria_carta_"] ~ div[data-testid="stCaptionContainer"] p {
        font-size: 0.70rem !important;
        line-height: 1 !important;
    }

    [class*="st-key-memoria_novo_jogo"] button,
    [class*="st-key-memoria_continuar"] button {
        min-height: 38px !important;
        height: 38px !important;
        border-radius: 11px !important;
        padding: 0.16rem 0.45rem !important;
    }

    [class*="st-key-memoria_novo_jogo"] button p,
    [class*="st-key-memoria_continuar"] button p {
        font-size: 0.84rem !important;
        line-height: 1 !important;
    }

    div[data-testid="stProgress"] {
        margin-top: 0.20rem !important;
        margin-bottom: 0.35rem !important;
    }
}


/* V14 — Gerenciar mais compacto no notebook */
.admin-video-card {
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 12px;
    padding: 10px 12px;
    background: rgba(255,255,255,0.03);
    margin-bottom: 7px;
}
.admin-video-title {
    font-weight: 800;
    font-size: 0.95rem;
    line-height: 1.15;
    margin-bottom: 4px;
}
.admin-video-meta {
    opacity: 0.78;
    font-size: 0.78rem;
    line-height: 1.1;
}

@media (min-width: 641px) and (max-width: 1399px) {
    [class*="st-key-admin_"] input,
    [class*="st-key-admin_"] select {
        min-height: 38px !important;
    }

    [class*="st-key-admin_salvar_assinatura"] button,
    [class*="st-key-admin_adicionar_creditos"] button {
        min-height: 38px !important;
        height: 38px !important;
        padding: 0.15rem 0.65rem !important;
        border-radius: 10px !important;
    }

    [class*="st-key-excluir_"] button {
        min-height: 36px !important;
        height: 36px !important;
        padding: 0.12rem 0.45rem !important;
        border-radius: 9px !important;
        font-size: 0.82rem !important;
    }

    .admin-video-card {
        padding: 8px 10px !important;
        border-radius: 10px !important;
    }

    .admin-video-title {
        font-size: 0.88rem !important;
    }

    .admin-video-meta {
        font-size: 0.72rem !important;
    }
}


/* V15 — texto visível nos botões de upload */
div[data-testid="stFileUploader"] button,
div[data-testid="stFileUploaderDropzone"] button {
    background: #ffffff !important;
    color: #2b123f !important;
    border: 1px solid #c7b6df !important;
    font-weight: 800 !important;
}

div[data-testid="stFileUploader"] button p,
div[data-testid="stFileUploader"] button span,
div[data-testid="stFileUploaderDropzone"] button p,
div[data-testid="stFileUploaderDropzone"] button span {
    color: #2b123f !important;
    font-weight: 800 !important;
    opacity: 1 !important;
}

div[data-testid="stFileUploaderDropzone"] small,
div[data-testid="stFileUploaderDropzone"] p,
div[data-testid="stFileUploaderDropzone"] span {
    color: #cfc4dd !important;
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
# CRÉDITOS PARA VÍDEO COM IA
# -----------------------------
def links_pacotes_creditos():
    """Links opcionais dos checkouts de créditos na Kiwify."""
    try:
        return {
            5: str(st.secrets.get("KIWIFY_CREDITOS_5_URL", "")).strip(),
            15: str(st.secrets.get("KIWIFY_CREDITOS_15_URL", "")).strip(),
            30: str(st.secrets.get("KIWIFY_CREDITOS_30_URL", "")).strip(),
        }
    except Exception:
        return {5: "", 15: "", 30: ""}


def obter_carteira_creditos():
    """
    Cria a carteira na primeira vez e entrega 1 crédito grátis.
    Retorna None se a tabela ainda não estiver criada.
    """
    if not st.session_state.get("usuario_id"):
        return None

    admin = cliente_admin_assinaturas()
    if admin is None:
        return None

    try:
        resp = (
            admin.table("video_creditos")
            .select("user_id,email,saldo,creditos_gratis_recebidos")
            .eq("user_id", st.session_state.usuario_id)
            .limit(1)
            .execute()
        )
        dados = resp.data or []

        if dados:
            return dados[0]

        nova = {
            "user_id": st.session_state.usuario_id,
            "email": st.session_state.usuario_logado or "",
            "saldo": 1,
            "creditos_gratis_recebidos": True,
        }
        criado = admin.table("video_creditos").insert(nova).execute()
        itens = criado.data or []
        return itens[0] if itens else nova
    except Exception:
        return None


def saldo_creditos_video():
    carteira = obter_carteira_creditos()
    if not carteira:
        return None
    try:
        return max(0, int(carteira.get("saldo", 0)))
    except Exception:
        return 0


def consumir_credito_video():
    """
    Desconta 1 crédito somente depois de uma geração bem-sucedida.
    """
    if not st.session_state.get("usuario_id"):
        return False

    admin = cliente_admin_assinaturas()
    if admin is None:
        return False

    carteira = obter_carteira_creditos()
    if not carteira:
        return False

    saldo = int(carteira.get("saldo", 0) or 0)
    if saldo <= 0:
        return False

    admin.table("video_creditos").update({
        "saldo": saldo - 1,
        "updated_at": datetime.now(timezone.utc).isoformat()
    }).eq("user_id", st.session_state.usuario_id).execute()

    return True


def adicionar_creditos_admin(email, quantidade):
    """
    Permite ao administrador adicionar créditos manualmente depois de
    conferir uma compra na Kiwify. Mais tarde o webhook pode automatizar isso.
    """
    admin = cliente_admin_assinaturas()
    if admin is None:
        raise RuntimeError("Falta SUPABASE_SECRET_KEY nos Secrets.")

    busca = (
        admin.table("video_creditos")
        .select("user_id,email,saldo")
        .ilike("email", email.strip())
        .limit(1)
        .execute()
    )
    itens = busca.data or []

    if not itens:
        # Busca o user_id na tabela de assinaturas, que o app já usa.
        conta = (
            admin.table("assinaturas")
            .select("user_id,email")
            .ilike("email", email.strip())
            .limit(1)
            .execute()
        )
        contas = conta.data or []
        if not contas:
            raise RuntimeError("Não encontrei uma conta cadastrada com esse e-mail.")

        item = contas[0]
        admin.table("video_creditos").insert({
            "user_id": item["user_id"],
            "email": item.get("email") or email.strip(),
            "saldo": int(quantidade),
            "creditos_gratis_recebidos": True,
        }).execute()
        return

    item = itens[0]
    novo_saldo = int(item.get("saldo", 0) or 0) + int(quantidade)

    admin.table("video_creditos").update({
        "saldo": novo_saldo,
        "updated_at": datetime.now(timezone.utc).isoformat()
    }).eq("user_id", item["user_id"]).execute()




# -----------------------------
# PDF DAS ATIVIDADES ESCOLARES
# -----------------------------
def criar_pdf_atividade(idade, materia, atividade_texto):
    """
    Gera uma folha A4 pronta para imprimir.
    Usa somente elementos vetoriais e fontes padrão do PDF,
    para funcionar bem no celular e na impressão.
    """
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.pdfbase.pdfmetrics import stringWidth

    buffer = BytesIO()
    largura, altura = A4
    margem = 42

    pdf = canvas.Canvas(buffer, pagesize=A4)
    pdf.setTitle(f"Mundo da Luna TV - {materia}")

    roxo = colors.HexColor("#5B2C83")
    roxo_claro = colors.HexColor("#EFE6F7")
    dourado = colors.HexColor("#D4A72C")
    cinza = colors.HexColor("#555555")
    preto = colors.HexColor("#222222")

    # Cabeçalho
    pdf.setFillColor(roxo)
    pdf.roundRect(
        margem,
        altura - 118,
        largura - (margem * 2),
        72,
        16,
        fill=1,
        stroke=0,
    )

    pdf.setFillColor(colors.white)
    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawString(margem + 18, altura - 78, "MUNDO DA LUNA TV")

    pdf.setFont("Helvetica", 10)
    pdf.drawString(
        margem + 18,
        altura - 96,
        "Folha de atividade para imprimir",
    )

    # Lua simples no cabeçalho
    pdf.setFillColor(dourado)
    pdf.circle(largura - margem - 32, altura - 82, 16, fill=1, stroke=0)
    pdf.setFillColor(roxo)
    pdf.circle(largura - margem - 24, altura - 77, 15, fill=1, stroke=0)

    # Identificação
    y = altura - 150
    pdf.setFillColor(preto)
    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(margem, y, "Nome:")
    pdf.line(margem + 38, y - 2, largura - 170, y - 2)
    pdf.drawString(largura - 150, y, "Data:")
    pdf.line(largura - 116, y - 2, largura - margem, y - 2)

    # Título da atividade
    y -= 42
    pdf.setFillColor(roxo)
    pdf.setFont("Helvetica-Bold", 16)
    titulo = f"{materia} - {idade}".replace("–", "-")
    pdf.drawString(margem, y, titulo)

    y -= 22
    pdf.setStrokeColor(dourado)
    pdf.setLineWidth(2)
    pdf.line(margem, y, largura - margem, y)
    y -= 28

    # Função de quebra de texto
    def desenhar_paragrafo(texto_linha, x, y_atual, largura_max, tamanho=12, espacamento=18):
        pdf.setFillColor(preto)
        pdf.setFont("Helvetica", tamanho)

        palavras = str(texto_linha).replace("–", "-").split()
        linha = ""
        linhas = []

        for palavra in palavras:
            teste = f"{linha} {palavra}".strip()
            if stringWidth(teste, "Helvetica", tamanho) <= largura_max:
                linha = teste
            else:
                if linha:
                    linhas.append(linha)
                linha = palavra

        if linha:
            linhas.append(linha)

        for item in linhas:
            pdf.drawString(x, y_atual, item)
            y_atual -= espacamento

        return y_atual

    # Texto/instruções
    linhas_atividade = [
        linha.strip()
        for linha in str(atividade_texto).splitlines()
        if linha.strip()
    ]

    # O primeiro texto costuma repetir o título.
    if linhas_atividade and materia.upper() in linhas_atividade[0].upper():
        linhas_atividade = linhas_atividade[1:]

    pdf.setFillColor(roxo_claro)
    pdf.roundRect(
        margem,
        y - 115,
        largura - (margem * 2),
        125,
        12,
        fill=1,
        stroke=0,
    )

    texto_y = y - 22
    for linha in linhas_atividade[:6]:
        texto_y = desenhar_paragrafo(
            linha,
            margem + 16,
            texto_y,
            largura - (margem * 2) - 32,
            tamanho=12,
            espacamento=18,
        )
        texto_y -= 3

    y -= 145

    # Área específica por matéria
    pdf.setStrokeColor(roxo)
    pdf.setFillColor(preto)
    pdf.setLineWidth(1.3)

    if materia == "Cores e formas":
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(margem, y, "Pinte o círculo de roxo e o quadrado de amarelo.")
        y -= 60
        pdf.circle(margem + 95, y, 44, fill=0, stroke=1)
        pdf.rect(margem + 235, y - 44, 88, 88, fill=0, stroke=1)
        y -= 80

    elif materia == "Atividade para colorir":
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(margem, y, "Use o espaço abaixo para desenhar e colorir.")
        y -= 24
        pdf.roundRect(
            margem,
            110,
            largura - (margem * 2),
            y - 110,
            12,
            fill=0,
            stroke=1,
        )
        # Pequenas estrelas-guia
        pdf.setFont("Helvetica-Bold", 18)
        for x in [margem + 30, margem + 75, largura - margem - 80, largura - margem - 35]:
            pdf.drawString(x, y - 38, "*")

    elif materia == "Animais":
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(margem, y, "Circule a resposta correta:")
        y -= 40
        opcoes = ["COELHO", "GATO", "CACHORRO"]
        for i, opcao in enumerate(opcoes):
            x = margem + (i * 155)
            pdf.roundRect(x, y - 28, 135, 48, 8, fill=0, stroke=1)
            pdf.setFont("Helvetica-Bold", 11)
            pdf.drawCentredString(x + 67.5, y - 10, opcao)
        y -= 90

    elif materia == "Matemática":
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(margem, y, "Faça a conta no espaço abaixo:")
        y -= 26
        pdf.roundRect(
            margem,
            y - 150,
            largura - (margem * 2),
            150,
            10,
            fill=0,
            stroke=1,
        )
        pdf.setFont("Helvetica", 12)
        pdf.drawString(margem + 16, y - 30, "Resposta: ______________________________")
        y -= 175

    elif materia == "Leitura":
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(margem, y, "Resposta:")
        y -= 25
        for _ in range(5):
            pdf.line(margem, y, largura - margem, y)
            y -= 34

    elif materia == "Alfabetização":
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(margem, y, "Escreva sua resposta:")
        y -= 30
        for _ in range(4):
            pdf.line(margem, y, largura - margem, y)
            y -= 38

    # Botão clicável para voltar ao site.
    # st.context.url traz a URL atual do app sem parâmetros.
    try:
        url_app = st.context.url
    except Exception:
        url_app = None

    if url_app:
        botao_x = margem
        botao_y = 64
        botao_w = largura - (margem * 2)
        botao_h = 30

        pdf.setFillColor(roxo)
        pdf.roundRect(
            botao_x,
            botao_y,
            botao_w,
            botao_h,
            10,
            fill=1,
            stroke=0,
        )

        pdf.setFillColor(colors.white)
        pdf.setFont("Helvetica-Bold", 10.5)
        pdf.drawCentredString(
            largura / 2,
            botao_y + 10,
            "< VOLTAR AO MUNDO DA LUNA TV",
        )

        pdf.linkURL(
            url_app,
            (
                botao_x,
                botao_y,
                botao_x + botao_w,
                botao_y + botao_h,
            ),
            relative=0,
            thickness=0,
        )

    # Rodapé
    pdf.setFillColor(cinza)
    pdf.setFont("Helvetica", 8.5)
    pdf.drawCentredString(
        largura / 2,
        42,
        "Mundo da Luna TV - atividade educativa para uso pessoal",
    )

    pdf.save()
    buffer.seek(0)
    return buffer.getvalue()


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


def voltar_inicio():
    # Não altera diretamente o valor do st.radio depois que ele já foi criado.
    # Apenas agenda o destino e deixa a alteração acontecer no próximo rerun,
    # antes de o widget ser instanciado.
    st.session_state["_menu_destino"] = "🏠 Início"
    st.rerun()


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
            st.image(item["capa_url"], width="stretch")

    if compacto:
        st.markdown(f"#### ✨ {item.get('nome', 'Sem título')}")
    else:
        st.markdown(f"### ✨ {item.get('nome', 'Sem título')}")
    categoria_visivel = categoria_base(item)
    if video_premium(item):
        st.markdown(
            f'<div class="categoria-card">💎 Premium • 🌟 {categoria_visivel}</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div class="categoria-card">🌟 {categoria_visivel}</div>',
            unsafe_allow_html=True,
        )

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
        reproduzir_video_url(item.get("video_url"))



def reproduzir_video_url(url):
    """Reproduz MP4/HLS e troca apenas o antigo link de teste que ficou instável."""
    url = str(url or "").strip()
    if not url:
        st.warning("Este vídeo está sem link.")
        return

    # O primeiro teste do app usava o FileSamples. Se esse link antigo
    # ainda estiver salvo, usa um MP4 público estável do Google apenas
    # para manter o teste do player funcionando.
    if "filesamples.com/samples/video/mp4/sample_640x360.mp4" in url.lower():
        url = "https://storage.googleapis.com/cloud-samples-data/video/animals.mp4"

    formato = (
        "application/vnd.apple.mpegurl"
        if ".m3u8" in url.lower()
        else "video/mp4"
    )

    try:
        st.video(
            url,
            format=formato,
            width="stretch",
        )
    except Exception as e:
        st.warning("Não consegui abrir este vídeo dentro do player.")
        st.link_button(
            "🌐 Abrir vídeo direto",
            url,
            width="stretch",
        )
        with st.expander("Detalhe técnico"):
            st.code(str(e))


def mostrar_card_horizontal(item, contexto, novo=False):
    """Card compacto para fileiras horizontais da Área Premium."""
    if item.get("capa_url"):
        st.image(item["capa_url"], width="stretch")
    if novo:
        st.markdown(
            '<div class="selo-novo">✨ NOVO</div>',
            unsafe_allow_html=True,
        )

    nome = str(item.get("nome") or "Sem título")
    # Título compacto: menor e com no máximo 2 linhas.
    st.markdown(
        f"""<div class="titulo-card">✨ {nome}</div>""",
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="categoria-card">💎 Premium • 🌟 {categoria_base(item)}</div>',
        unsafe_allow_html=True,
    )

    chave = f"aberto_{contexto}_{item['id']}"
    if chave not in st.session_state:
        st.session_state[chave] = False

    # Área compacta de ações: 150 px de largura.
    try:
        acoes = st.container(
            key=f"cardacoes_{contexto}_{item['id']}",
            width="stretch",
            border=False,
        )
    except TypeError:
        acoes = st.container(key=f"cardacoes_{contexto}_{item['id']}")

    with acoes:
        if not st.session_state[chave]:
            if st.button(
                "▶ Assistir",
                key=f"assistir_{contexto}_{item['id']}",
                width="stretch",
            ):
                registrar_assistido(item)
                st.session_state[chave] = True
                st.rerun()
        else:
            if st.button(
                "✖ Fechar",
                key=f"fechar_{contexto}_{item['id']}",
                width="stretch",
            ):
                st.session_state[chave] = False
                st.rerun()

        favorito = bool(item.get("favorito", False))
        texto = "💖 Na Lista" if favorito else "🤍 Minha Lista"
        if st.button(
            texto,
            key=f"fav_{contexto}_{item['id']}",
            width="stretch",
        ):
            alternar_favorito(item)

    if st.session_state.get(chave, False):
        reproduzir_video_url(item.get("video_url"))


def mostrar_fileira_premium(titulo, itens, contexto, limite=12, marcar_novo=False):
    """Fileira horizontal com cards realmente pequenos (190 px)."""
    itens = list(itens)[:limite]
    if not itens:
        return

    st.markdown(
        f'<div class="secao-titulo-compacto">{titulo}</div>',
        unsafe_allow_html=True,
    )

    # 3 cards por linha em notebook/desktop. Com wrap=True, o Streamlit
    # empilha automaticamente as colunas em telas de até 640 px.
    for inicio in range(0, len(itens), 3):
        grupo = itens[inicio:inicio + 3]
        try:
            cols = st.columns(3, gap="medium", wrap=True)
        except TypeError:
            cols = st.columns(3, gap="medium")

        for i, item in enumerate(grupo):
            with cols[i]:
                with st.container(key=f"premiumcard_{contexto}_{inicio+i}"):
                    mostrar_card_horizontal(item, f"{contexto}_{inicio+i}", novo=marcar_novo)


def mostrar_card_catalogo(item, contexto, novo=False):
    """Card compacto para fileiras horizontais da tela inicial."""
    if item.get("capa_url"):
        st.image(item["capa_url"], width="stretch")
    if novo:
        st.markdown(
            '<div class="selo-novo">✨ NOVO</div>',
            unsafe_allow_html=True,
        )

    nome = str(item.get("nome") or "Sem título")
    # Título compacto: menor e com no máximo 2 linhas.
    st.markdown(
        f"""<div class="titulo-card">✨ {nome}</div>""",
        unsafe_allow_html=True,
    )

    categoria_visivel = categoria_base(item)
    if video_premium(item):
        st.markdown(
            f'<div class="categoria-card">💎 Premium • 🌟 {categoria_visivel}</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div class="categoria-card">🌟 {categoria_visivel}</div>',
            unsafe_allow_html=True,
        )

    chave = f"aberto_{contexto}_{item['id']}"
    if chave not in st.session_state:
        st.session_state[chave] = False

    # Área compacta de ações: 150 px de largura.
    try:
        acoes = st.container(
            key=f"cardacoes_{contexto}_{item['id']}",
            width="stretch",
            border=False,
        )
    except TypeError:
        acoes = st.container(key=f"cardacoes_{contexto}_{item['id']}")

    with acoes:
        if not st.session_state[chave]:
            if st.button(
                "▶ Assistir",
                key=f"assistir_{contexto}_{item['id']}",
                width="stretch",
            ):
                registrar_assistido(item)
                st.session_state[chave] = True
                st.rerun()
        else:
            if st.button(
                "✖ Fechar",
                key=f"fechar_{contexto}_{item['id']}",
                width="stretch",
            ):
                st.session_state[chave] = False
                st.rerun()

        favorito = bool(item.get("favorito", False))
        texto = "💖 Na Lista" if favorito else "🤍 Minha Lista"
        if st.button(
            texto,
            key=f"fav_{contexto}_{item['id']}",
            width="stretch",
        ):
            alternar_favorito(item)

    if st.session_state.get(chave, False):
        reproduzir_video_url(item.get("video_url"))


def mostrar_fileira_catalogo(titulo, itens, contexto, limite=12, marcar_novo=False):
    """Fileira horizontal da tela inicial com cards de 190 px."""
    itens = list(itens)[:limite]
    if not itens:
        return

    st.markdown(
        f'<div class="secao-titulo-compacto">{titulo}</div>',
        unsafe_allow_html=True,
    )

    # 4 cards por linha em notebook/desktop para deixar o catálogo
    # mais compacto. No celular, wrap=True reorganiza os cards.
    for inicio in range(0, len(itens), 4):
        grupo = itens[inicio:inicio + 4]
        try:
            cols = st.columns(4, gap="small", wrap=True)
        except TypeError:
            cols = st.columns(4, gap="small")

        for i, item in enumerate(grupo):
            with cols[i]:
                with st.container(key=f"catalogcard_{contexto}_{inicio+i}"):
                    mostrar_card_catalogo(item, f"{contexto}_{inicio+i}", novo=marcar_novo)


# Aplica gravação/remoção pendente do login no navegador e tenta restaurar a conta.
executar_pendencias_browser()
restaurar_login_do_navegador()

st.markdown("""
<div class="hero">
<h1 class="hero-title">🌙 Mundo da Luna TV ✨</h1>
<p class="magic"><span class="hero-subtitle">⭐ Histórias mágicas, aventuras e sonhos em um só lugar ⭐</span></p>
</div>
<div class="gold-line"></div>
""", unsafe_allow_html=True)

def mostrar_card_tv(item, contexto):
    """Card grande e simples para uso em notebook e Smart TV."""
    if item.get("capa_url"):
        st.image(item["capa_url"], width="stretch")

    nome_tv = str(item.get("nome") or "Sem título")
    st.markdown(f"### ✨ {nome_tv}")

    categoria_tv = categoria_base(item)
    if video_premium(item):
        st.caption(f"💎 Premium • {categoria_tv}")
    else:
        st.caption(f"🌙 Grátis • {categoria_tv}")

    chave_tv = f"tv_aberto_{contexto}_{item['id']}"
    if chave_tv not in st.session_state:
        st.session_state[chave_tv] = False

    if not st.session_state[chave_tv]:
        if st.button(
            "▶ Assistir agora",
            key=f"tv_assistir_{contexto}_{item['id']}",
            width="stretch",
        ):
            registrar_assistido(item)
            st.session_state[chave_tv] = True
            st.rerun()
    else:
        if st.button(
            "✖ Fechar vídeo",
            key=f"tv_fechar_{contexto}_{item['id']}",
            width="stretch",
        ):
            st.session_state[chave_tv] = False
            st.rerun()

    favorito_tv = bool(item.get("favorito", False))
    texto_tv = "💖 Na Minha Lista" if favorito_tv else "🤍 Minha Lista"
    if st.button(
        texto_tv,
        key=f"tv_fav_{contexto}_{item['id']}",
        width="stretch",
    ):
        alternar_favorito(item)

    if st.session_state.get(chave_tv, False):
        reproduzir_video_url(item.get("video_url"))


# Aplica navegação pendente ANTES de criar o st.radio.
if "_menu_destino" in st.session_state:
    st.session_state["menu_principal"] = st.session_state.pop("_menu_destino")

menu = st.sidebar.radio(
    "Menu",
    [
        "🏠 Início",
        "📺 Modo TV",
        "🔎 Buscar",
        "🆕 Novidades",
        "❤️ Minha Lista",
        "🕒 Recentes",
        "👤 Entrar / Minha conta",
        "💎 Planos",
        "🔒 Premium",
        "📤 Enviar vídeo",
        "🧸 Infantil",
        "🎬 Filmes",
        "📺 Séries",
        "🎬 Criar vídeo com IA",
        "🎮 Jogos",
        "📚 Atividades escolares",
        "🗑️ Gerenciar"
    ],
    key="menu_principal",
    width="content"
)

if st.session_state.usuario_logado:
    st.sidebar.success(f"👤 {st.session_state.usuario_logado}")

    if st.session_state.plano_atual == "Premium":
        st.sidebar.markdown(
            '<div class="status-plano premium">💎 Premium ativo</div>',
            unsafe_allow_html=True,
        )
    else:
        st.sidebar.markdown(
            '<div class="status-plano gratis">🌙 Plano grátis</div>',
            unsafe_allow_html=True,
        )

    saldo_sidebar = saldo_creditos_video()
    if saldo_sidebar is not None:
        st.sidebar.caption(f"🎬 Créditos de vídeo: {saldo_sidebar}")
else:
    st.sidebar.caption("👤 Visitante — faça login para sua conta")

videos = listar_videos()


if menu != "🏠 Início":
    try:
        voltar_box = st.container(width=105, border=False)
    except TypeError:
        voltar_box = st.container()

    with voltar_box:
        if st.button(
            "← Voltar",
            key="botao_voltar_inicio",
            width="stretch",
        ):
            voltar_inicio()

if menu == "🏠 Início":
    videos_inicio = videos_gratis(videos)

    try:
        conta_box = st.container(
            key="atalho_conta_home",
            width=210,
            border=False,
        )
    except TypeError:
        conta_box = st.container(key="atalho_conta_home")

    with conta_box:
        if st.session_state.usuario_logado:
            st.button(
                "👤 Minha conta",
                key="atalho_minha_conta",
                on_click=abrir_minha_conta,
                width="stretch",
            )

            if st.session_state.plano_atual == "Premium":
                st.markdown(
                    '<div class="status-plano premium">💎 Premium ativo</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    '<div class="status-plano gratis">🌙 Plano grátis</div>',
                    unsafe_allow_html=True,
                )
        else:
            st.button(
                "👤 Entrar / Criar conta",
                key="atalho_login_home",
                on_click=abrir_minha_conta,
                width="stretch",
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
        st.markdown(
            '<div class="secao-titulo-compacto">▶ Continuar assistindo</div>',
            unsafe_allow_html=True,
        )
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
        st.markdown(
            '<div class="dica-deslize">Deslize para o lado para ver mais vídeos. 💜</div>',
            unsafe_allow_html=True,
        )

        mostrar_fileira_catalogo(
            "✨ Novidades",
            videos_inicio,
            "home_novidades",
            limite=12,
            marcar_novo=True,
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

elif menu == "📺 Modo TV":
    st.markdown("## 📺 Modo TV")
    st.caption(
        "Tela simplificada com capas e botões maiores para notebook, computador e Smart TV."
    )

    # Usuário Premium ativo vê todo o catálogo. Os demais veem apenas conteúdo grátis.
    premium_tv = (
        st.session_state.usuario_logado
        and st.session_state.plano_atual == "Premium"
        and st.session_state.status_assinatura == "ativo"
    )

    catalogo_tv = list(videos) if premium_tv else videos_gratis(videos)

    filtro_tv = st.selectbox(
        "🎞️ Escolha uma categoria",
        ["Todos", "Infantil", "Filmes", "Séries"],
        key="filtro_modo_tv",
    )

    if filtro_tv != "Todos":
        catalogo_tv = [
            item for item in catalogo_tv
            if categoria_base(item) == filtro_tv
        ]

    if not catalogo_tv:
        st.info("Ainda não há vídeos nesta categoria.")
    else:
        st.markdown(
            "<div class='tv-dica'>Use o navegador da TV em tela cheia para uma experiência melhor.</div>",
            unsafe_allow_html=True,
        )

        # Quatro cards por linha em telas grandes. Em telas estreitas,
        # wrap=True empilha automaticamente para facilitar o uso no celular.
        for inicio in range(0, len(catalogo_tv), 4):
            grupo = catalogo_tv[inicio:inicio + 4]
            try:
                colunas_tv = st.columns(4, gap="large", wrap=True)
            except TypeError:
                colunas_tv = st.columns(4, gap="large")

            for indice, item in enumerate(grupo):
                with colunas_tv[indice]:
                    with st.container(key=f"tvcard_{inicio}_{indice}"):
                        mostrar_card_tv(item, f"modo_tv_{inicio}_{indice}")

            st.markdown("---")

elif menu == "🔎 Buscar":
    st.subheader("🔎 Buscar vídeos")
    st.caption(
        "Encontre seus vídeos pelo nome, categoria e tipo de acesso."
    )

    # Mantém o plano atualizado para decidir se a busca pode mostrar Premium.
    if st.session_state.usuario_logado:
        carregar_plano_usuario()

    premium_ativo_busca = (
        st.session_state.usuario_logado
        and st.session_state.plano_atual == "Premium"
        and st.session_state.status_assinatura == "ativo"
    )

    termo = st.text_input(
        "🔎 Digite o nome do vídeo",
        placeholder="Ex.: Luna",
        key="busca_termo",
    )

    categoria_busca = st.selectbox(
        "🎞️ Categoria",
        ["Todas", "Infantil", "Filmes", "Séries"],
        key="busca_categoria",
    )

    if premium_ativo_busca:
        acesso_busca = st.selectbox(
            "💎 Tipo de acesso",
            ["Todos", "Grátis", "Premium"],
            key="busca_acesso",
        )
        st.caption(
            "💎 Seu Premium está ativo: os conteúdos exclusivos também aparecem na busca."
        )
        disponiveis_busca = list(videos)
    else:
        acesso_busca = "Grátis"
        disponiveis_busca = videos_gratis(videos)
        st.caption(
            "🌙 A busca mostra os conteúdos gratuitos. "
            "Assinantes Premium também encontram os exclusivos aqui."
        )

    filtrados = list(disponiveis_busca)

    if termo.strip():
        termo_lower = termo.lower().strip()
        filtrados = [
            v for v in filtrados
            if termo_lower in str(v.get("nome") or "").lower()
        ]

    if categoria_busca != "Todas":
        filtrados = [
            v for v in filtrados
            if categoria_base(v) == categoria_busca
        ]

    if premium_ativo_busca and acesso_busca != "Todos":
        if acesso_busca == "Premium":
            filtrados = [
                v for v in filtrados
                if video_premium(v)
            ]
        else:
            filtrados = [
                v for v in filtrados
                if not video_premium(v)
            ]

    st.markdown("---")

    if not filtrados:
        st.info(
            "Nenhum vídeo encontrado com esses filtros. "
            "Tente outro nome ou categoria."
        )
    else:
        quantidade_resultados = len(filtrados)

        st.markdown(
            f"### ✨ {quantidade_resultados} "
            f"{'resultado' if quantidade_resultados == 1 else 'resultados'}"
        )

        st.markdown(
            '<div class="dica-deslize">'
            'Deslize para o lado para ver os resultados. 💜'
            '</div>',
            unsafe_allow_html=True,
        )

        mostrar_fileira_catalogo(
            "🔎 Resultados",
            filtrados,
            "busca_resultados",
            limite=30,
        )

elif menu == "🆕 Novidades":
    st.subheader("🆕 Novidades")
    novidades = videos_gratis(videos)

    if not novidades:
        st.info("Ainda não há novidades.")
    else:
        mostrar_fileira_catalogo(
            "✨ Últimos conteúdos",
            novidades,
            "novidades",
            limite=12,
            marcar_novo=True,
        )

elif menu == "❤️ Minha Lista":
    st.subheader("❤️ Minha Lista")

    favoritos = [
        v for v in videos_gratis(videos)
        if bool(v.get("favorito", False))
    ]

    if not favoritos:
        st.info("Sua lista ainda está vazia. Toque em 🤍 Minha Lista em qualquer vídeo.")
    else:
        mostrar_fileira_catalogo(
            "💖 Salvos para assistir",
            favoritos,
            "favoritos",
            limite=30,
        )

elif menu == "🕒 Recentes":
    st.subheader("🕒 Assistidos recentemente")

    recentes = listar_assistidos_recentes(videos_gratis(videos), limite=12)

    if not recentes:
        st.info("Você ainda não assistiu a nenhum vídeo.")
    else:
        st.caption("Os vídeos assistidos mais recentemente aparecem primeiro.")
        mostrar_fileira_catalogo(
            "🕒 Continue de onde parou",
            recentes,
            "recentes",
            limite=12,
        )

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
        st.warning(
            "Entre na sua conta para acessar a Área Premium."
        )

        st.button(
            "👤 Entrar / Criar conta",
            key="premium_ir_login",
            on_click=mudar_menu,
            args=("👤 Entrar / Minha conta",),
            width="stretch",
        )

    elif not (
        st.session_state.plano_atual == "Premium"
        and st.session_state.status_assinatura == "ativo"
    ):
        render_html("""
        <div class="lock-card">
            <h3>🔒 Conteúdo Premium bloqueado</h3>
            <p>
                Essa área é exclusiva para assinantes Premium ativos.
                Assine para assistir aos conteúdos exclusivos.
            </p>
        </div>
        """)

        st.button(
            "💎 Ver plano Premium",
            key="premium_ver_planos",
            on_click=mudar_menu,
            args=("💎 Planos",),
            width="stretch",
        )

    else:
        exclusivos = videos_premium(videos)

        render_html("""
        <div class="premium-hero">
            <div class="premium-hero-title">
                💎 Bem-vindo à Área Premium
            </div>
            <div class="premium-hero-text">
                Conteúdos exclusivos do Mundo da Luna TV,
                organizados para você encontrar tudo com facilidade.
            </div>
        </div>
        """)

        if not exclusivos:
            st.info(
                "Ainda não há vídeos exclusivos. "
                "Envie um vídeo e marque o acesso como Premium."
            )

        else:
            infantil_premium = [
                v for v in exclusivos
                if categoria_base(v) == "Infantil"
            ]

            filmes_premium = [
                v for v in exclusivos
                if categoria_base(v) == "Filmes"
            ]

            series_premium = [
                v for v in exclusivos
                if categoria_base(v) == "Séries"
            ]

            total_premium = len(exclusivos)

            # Resumo Premium compacto para celular.
            # Duas linhas dentro de um único cartão, sem colunas que se empilham.
            with st.container(border=True):
                st.markdown(
                    f"**💎 {total_premium} Exclusivos**  •  "
                    f"**🧸 {len(infantil_premium)} Infantil**"
                )
                st.markdown(
                    f"**🎬 {len(filmes_premium)} Filmes**  •  "
                    f"**📺 {len(series_premium)} Séries**"
                )

            # Organização inteligente da Área Premium:
            # com poucos vídeos, cada conteúdo aparece apenas uma vez.
            modo_poucos_videos = total_premium <= 4

            def chave_video_premium(item):
                return str(
                    item.get("id")
                    or item.get("video_url")
                    or item.get("nome")
                    or ""
                )

            ultimo_premium = ultimo_assistido(exclusivos)

            favoritos_premium = [
                v for v in exclusivos
                if bool(v.get("favorito", False))
            ]

            if modo_poucos_videos:
                st.caption(
                    "✨ Como há poucos conteúdos, cada vídeo aparece "
                    "apenas uma vez para a tela ficar mais organizada."
                )

                ids_mostrados = set()

                # 1) Prioriza o conteúdo que a pessoa já começou a assistir.
                if ultimo_premium:
                    mostrar_fileira_premium(
                        "▶ Continuar assistindo",
                        [ultimo_premium],
                        "premium_continuar",
                        limite=1,
                    )
                    ids_mostrados.add(
                        chave_video_premium(ultimo_premium)
                    )

                # 2) Depois mostra favoritos que ainda não apareceram.
                favoritos_sem_repetir = [
                    v for v in favoritos_premium
                    if chave_video_premium(v) not in ids_mostrados
                ]

                if favoritos_sem_repetir:
                    mostrar_fileira_premium(
                        "❤️ Minha Lista Premium",
                        favoritos_sem_repetir,
                        "premium_favoritos",
                        limite=12,
                    )

                    ids_mostrados.update(
                        chave_video_premium(v)
                        for v in favoritos_sem_repetir
                    )

                # 3) O restante aparece somente na própria categoria.
                restantes = [
                    v for v in exclusivos
                    if chave_video_premium(v) not in ids_mostrados
                ]

                grupos_compactos = [
                    (
                        "🧸 Infantil",
                        [
                            v for v in restantes
                            if categoria_base(v) == "Infantil"
                        ],
                        "premium_infantil",
                    ),
                    (
                        "🎬 Filmes",
                        [
                            v for v in restantes
                            if categoria_base(v) == "Filmes"
                        ],
                        "premium_filmes",
                    ),
                    (
                        "📺 Séries",
                        [
                            v for v in restantes
                            if categoria_base(v) == "Séries"
                        ],
                        "premium_series",
                    ),
                ]

                for titulo_grupo, itens_grupo, chave_grupo in grupos_compactos:
                    if itens_grupo:
                        mostrar_fileira_premium(
                            titulo_grupo,
                            itens_grupo,
                            chave_grupo,
                            limite=12,
                        )

            else:
                # Com mais conteúdos, usa a organização completa.
                st.markdown(
                    '<div class="dica-deslize">'
                    'Deslize para o lado para ver mais vídeos. 💜'
                    '</div>',
                    unsafe_allow_html=True,
                )

                if ultimo_premium:
                    mostrar_fileira_premium(
                        "▶ Continuar assistindo",
                        [ultimo_premium],
                        "premium_continuar",
                        limite=1,
                    )

                if favoritos_premium:
                    mostrar_fileira_premium(
                        "❤️ Minha Lista Premium",
                        favoritos_premium,
                        "premium_favoritos",
                        limite=12,
                    )

                mostrar_fileira_premium(
                    "✨ Novidades",
                    exclusivos,
                    "premium_novidades",
                    limite=12,
                    marcar_novo=True,
                )

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

        modo_video = st.radio(
            "Como deseja adicionar o vídeo?",
            [
                "📁 Arquivo até 500 MB",
                "🌐 Vídeo grande por link / streaming",
            ],
            help=(
                "Para filmes grandes, use um link direto de vídeo MP4 "
                "ou um link HLS terminado em .m3u8."
            ),
        )

        video = None
        video_url_grande = ""

        if modo_video == "📁 Arquivo até 500 MB":
            video = st.file_uploader(
                "Escolha um vídeo da galeria",
                type=["mp4", "mov", "m4v"],
                key="video_upload",
                max_upload_size=500,
                help="Você pode enviar vídeos de até 500 MB por esta opção."
            )

            if video is not None:
                st.write(
                    f"⭐ Vídeo selecionado: **{video.size / (1024 * 1024):.1f} MB**"
                )

        else:
            st.info(
                "🎞️ Para filmes grandes, cole o endereço direto do vídeo. "
                "Pode ser um MP4 hospedado para streaming ou um link HLS (.m3u8). "
                "O arquivo não passa pelo servidor do app, então pode ter vários GB."
            )

            video_url_grande = st.text_input(
                "Link do vídeo grande",
                placeholder="https://.../filme.mp4 ou https://.../playlist.m3u8",
                key="video_url_grande",
            )

        if capa is not None:
            st.image(capa, caption="✨ Prévia da capa", use_container_width=True)

        if st.button("💾 Salvar permanentemente"):
            usando_arquivo = modo_video == "📁 Arquivo até 500 MB"

            if usando_arquivo and video is None:
                st.warning("Escolha um vídeo primeiro.")

            elif (not usando_arquivo) and (
                not video_url_grande.strip().lower().startswith(("http://", "https://"))
            ):
                st.warning("Cole um link válido começando com http:// ou https://.")

            else:
                with st.spinner("✨ Enviando e salvando..."):
                    try:
                        if usando_arquivo:
                            video_path, video_url = upload_arquivo(video, "videos")
                            nome_padrao = video.name
                        else:
                            video_url = video_url_grande.strip()
                            video_path = video_url
                            nome_padrao = "Vídeo grande"

                        capa_path = None
                        capa_url = None

                        if capa is not None:
                            capa_path, capa_url = upload_arquivo(capa, "capas")

                        supabase.table("videos").insert({
                            "nome": nome.strip() if nome.strip() else nome_padrao,
                            "categoria": categoria_para_salvar(categoria, acesso),
                            "video_url": video_url,
                            "video_path": video_path,
                            "capa_url": capa_url,
                            "capa_path": capa_path,
                            "favorito": False
                        }).execute()

                        st.success("✅ Vídeo salvo permanentemente!")
                        if not usando_arquivo:
                            st.success(
                                "🎬 Modo de vídeo grande ativado: "
                                "o app reproduzirá o conteúdo direto do serviço de streaming."
                            )
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
        mostrar_fileira_catalogo(
            menu,
            itens,
            f"categoria_{categoria_atual.lower()}",
            limite=30,
        )


elif menu == "🎬 Criar vídeo com IA":
    st.markdown("## 🎬 Criar vídeo com IA")

    st.caption("Transforme uma imagem em vídeo e escolha como cada elemento deve se mover.")

    st.markdown("### 💎 Créditos de vídeo")

    if not st.session_state.usuario_logado:
        st.info(
            "🎁 Crie uma conta ou entre para receber **1 crédito grátis** "
            "e poder guardar seu saldo."
        )
        st.button(
            "👤 Entrar / Criar conta",
            key="video_ir_login",
            on_click=mudar_menu,
            args=("👤 Entrar / Minha conta",),
            width="stretch",
        )
        saldo_video = 0
    else:
        saldo_video = saldo_creditos_video()

        if saldo_video is None:
            st.warning(
                "A área de créditos está pronta, mas falta criar a tabela "
                "`video_creditos` no Supabase. Use o arquivo SQL que acompanha esta atualização."
            )
            saldo_video = 0
        else:
            st.success(f"💎 Seus créditos de vídeo: **{saldo_video}**")
            if saldo_video == 1:
                st.caption("🎁 Este pode ser o seu crédito grátis de boas-vindas.")

        if st.button(
            "🔄 Atualizar meus créditos",
            key="atualizar_meus_creditos_video",
            width="stretch",
        ):
            st.rerun()

    try:
        fal_configurado = bool(
            str(st.secrets.get("FAL_API_KEY", "")).strip()
        )
    except Exception:
        fal_configurado = False

    if fal_configurado:
        st.caption("🟢 fal.ai configurado • Wan 2.2 Turbo econômico • prioridade ativa")
    else:
        st.caption("🟣 Provedor alternativo fal.ai: ainda não configurado")

    pacotes = links_pacotes_creditos()
    links_configurados = any(pacotes.values())

    with st.expander("💳 Comprar mais créditos"):
        st.write("Escolha um pacote. O pagamento pode abrir na Kiwify em outra aba.")

        precos_exemplo = {5: "5 créditos", 15: "15 créditos", 30: "30 créditos"}

        for qtd in (5, 15, 30):
            url = pacotes.get(qtd, "")
            if url:
                render_html(
                    f"""
                    <a href="{url}" target="_blank" rel="noopener noreferrer"
                       style="
                           display:flex;
                           align-items:center;
                           justify-content:center;
                           width:100%;
                           min-height:54px;
                           box-sizing:border-box;
                           margin:8px 0;
                           padding:0.65rem 1rem;
                           border-radius:15px;
                           border:2px solid #f2d675;
                           background:linear-gradient(90deg,#6d28d9,#8b5cf6);
                           color:#fff;
                           font-size:1.05rem;
                           font-weight:800;
                           text-decoration:none;
                           text-align:center;
                       ">
                        💎 Comprar {precos_exemplo[qtd]}
                    </a>
                    """
                )
            else:
                st.button(
                    f"💎 Comprar {precos_exemplo[qtd]}",
                    key=f"pacote_creditos_{qtd}_sem_link",
                    disabled=True,
                    width="stretch",
                )

        if not links_configurados:
            st.caption(
                "Para liberar os botões de compra, adicione nos Secrets: "
                "KIWIFY_CREDITOS_5_URL, KIWIFY_CREDITOS_15_URL e KIWIFY_CREDITOS_30_URL."
            )
        else:
            st.caption(
                "Depois do pagamento, os créditos precisam ser adicionados pelo webhook "
                "ou pelo painel Gerenciar. Nesta versão deixei o painel administrativo pronto."
            )


    imagem_video = st.file_uploader(
        "🖼️ Envie a imagem",
        type=["png", "jpg", "jpeg", "webp"],
        key="upload_imagem_video_ia",
    )

    if imagem_video is not None:
        st.image(imagem_video, use_container_width=True)

    modo_video = st.radio(
        "⚙️ Modo de criação",
        ["Simples", "Avançado"],
        horizontal=True,
        key="modo_video_ia",
    )

    prompt_video = st.text_area(
        "✨ O que deve acontecer na cena?",
        placeholder=(
            "Exemplo: Luna caminha devagar pela floresta, pisca naturalmente, "
            "o cabelo se move suavemente e o coelhinho mexe as orelhas."
        ),
        height=115,
        key="prompt_video_ia",
    )

    col1, col2 = st.columns(2)
    with col1:
        duracao_video = st.selectbox(
            "⏱️ Duração desejada",
            [5, 6, 8, 10],
            format_func=lambda x: f"{x} segundos",
            key="duracao_video_ia",
        )
    with col2:
        camera_video = st.selectbox(
            "🎥 Câmera",
            [
                "Parada",
                "Zoom suave",
                "Aproximar lentamente",
                "Afastar lentamente",
                "Movimento leve",
                "Panorâmica suave",
                "Acompanhar personagem",
            ],
            key="camera_video_ia",
        )

    intensidade = "Leve"
    expressao = "Natural"
    olhos = "Piscar naturalmente"
    cabelo = "Movimento suave"
    secundario = "Movimento leve"
    ambiente = "Sem efeito extra"
    formato = "YouTube 16:9"
    qualidade = "Equilibrada"

    if modo_video == "Avançado":
        st.markdown("### 🎭 Atuação e movimentos")

        c1, c2 = st.columns(2)
        with c1:
            intensidade = st.selectbox(
                "💫 Intensidade",
                ["Muito leve", "Leve", "Média", "Forte"],
                index=1,
                key="intensidade_video_ia",
            )
            expressao = st.selectbox(
                "🙂 Expressão",
                ["Natural", "Feliz", "Sorrindo", "Surpresa", "Curiosa", "Séria"],
                key="expressao_video_ia",
            )
            olhos = st.selectbox(
                "👀 Olhos",
                [
                    "Piscar naturalmente",
                    "Olhar para frente",
                    "Olhar para o lado suavemente",
                    "Acompanhar algo com os olhos",
                ],
                key="olhos_video_ia",
            )
        with c2:
            cabelo = st.selectbox(
                "💇 Cabelo/roupa",
                [
                    "Quase parado",
                    "Movimento suave",
                    "Brisa leve",
                    "Vento moderado",
                ],
                index=1,
                key="cabelo_video_ia",
            )
            secundario = st.selectbox(
                "🐰 Personagem secundário",
                [
                    "Quase parado",
                    "Movimento leve",
                    "Piscar e mexer a cabeça",
                    "Mexer orelhas/patas suavemente",
                ],
                index=1,
                key="secundario_video_ia",
            )
            ambiente = st.selectbox(
                "🌬️ Ambiente",
                [
                    "Sem efeito extra",
                    "Folhas mexendo suavemente",
                    "Partículas mágicas discretas",
                    "Luzes mágicas suaves",
                    "Brisa suave",
                ],
                key="ambiente_video_ia",
            )

        c3, c4 = st.columns(2)
        with c3:
            formato = st.selectbox(
                "📐 Formato desejado",
                ["YouTube 16:9", "TikTok/Reels 9:16", "Quadrado 1:1"],
                key="formato_video_ia",
            )
        with c4:
            qualidade = st.selectbox(
                "🎞️ Qualidade",
                ["Rápida", "Equilibrada", "Melhor qualidade"],
                index=1,
                key="qualidade_video_ia",
            )

    preservar = st.checkbox(
        "🧒 Preservar rosto, roupa e aparência da personagem",
        value=True,
        key="preservar_video_ia",
    )

    partes_prompt = []
    if prompt_video.strip():
        partes_prompt.append(prompt_video.strip())

    if modo_video == "Avançado":
        partes_prompt.append(f"Intensidade do movimento: {intensidade}.")
        partes_prompt.append(f"Expressão facial: {expressao}.")
        partes_prompt.append(f"Olhos: {olhos}.")
        partes_prompt.append(f"Cabelo e roupa: {cabelo}.")
        partes_prompt.append(f"Personagem secundário: {secundario}.")
        partes_prompt.append(f"Ambiente: {ambiente}.")
        partes_prompt.append(f"Formato visual desejado: {formato}.")

    partes_prompt.append(f"Câmera: {camera_video}.")
    partes_prompt.append(f"Duração desejada: cerca de {duracao_video} segundos.")

    if preservar:
        partes_prompt.append(
            "Preservar rigorosamente o mesmo rosto, cabelo, roupa, cores, "
            "idade aparente, proporções e identidade visual dos personagens da imagem de referência."
        )

    partes_prompt.append(
        "Movimentos naturais e cinematográficos, sem deformações, sem trocar personagens, "
        "sem alterar o cenário principal e sem movimentos bruscos."
    )

    prompt_final = "\n".join(partes_prompt)

    with st.expander("📝 Ver comando completo"):
        st.code(prompt_final, language="text")

    st.caption(
        "ℹ️ A geração real depende do acesso/créditos do provedor de IA. "
        "Se a conta não tiver saldo ou o modelo estiver indisponível, o app mostrará o motivo."
    )

    if qualidade == "Rápida":
        st.caption(
            "💰 Modo econômico: fal.ai Wan 2.2 Turbo em 480p."
        )

    confirmar_custo = st.checkbox(
        "💳 Confirmo que quero gerar o vídeo e usar saldo do provedor de IA",
        value=False,
        key="confirmar_custo_video_ia",
    )

    if st.button(
        "✨ Gerar vídeo com IA",
        key="gerar_video_ia",
        width="stretch",
        disabled=not confirmar_custo,
    ):
        if not st.session_state.usuario_logado:
            st.warning("Entre ou crie uma conta para gerar vídeo com IA.")
        elif saldo_creditos_video() is None:
            st.warning("Configure primeiro a tabela de créditos no Supabase.")
        elif saldo_creditos_video() <= 0:
            st.warning("💎 Você está sem créditos. Abra 'Comprar mais créditos' para escolher um pacote.")
        elif imagem_video is None:
            st.warning("Envie uma imagem primeiro.")
        elif not prompt_video.strip():
            st.warning("Escreva o movimento que você quer no vídeo.")
        else:
            try:
                from huggingface_hub import InferenceClient

                hf_token = str(st.secrets.get("HF_TOKEN", "")).strip()
                fal_api_key = str(st.secrets.get("FAL_API_KEY", "")).strip()

                hf_provider = str(
                    st.secrets.get("HF_VIDEO_PROVIDER", "auto")
                ).strip() or "auto"

                hf_model = str(
                    st.secrets.get(
                        "HF_VIDEO_MODEL",
                        "Wan-AI/Wan2.2-I2V-A14B"
                    )
                ).strip() or "Wan-AI/Wan2.2-I2V-A14B"

                fal_model = str(
                    st.secrets.get(
                        "FAL_VIDEO_MODEL",
                        "Wan-AI/Wan2.2-I2V-A14B"
                    )
                ).strip() or "Wan-AI/Wan2.2-I2V-A14B"

                if not hf_token and not fal_api_key:
                    st.error(
                        "Falta configurar um provedor de vídeo. "
                        "Adicione HF_TOKEN ou FAL_API_KEY nos Secrets."
                    )
                else:
                    passos = {
                        "Rápida": 20,
                        "Equilibrada": 30,
                        "Melhor qualidade": 40,
                    }.get(qualidade, 30)

                    negativo = (
                        "personagem diferente, rosto alterado, "
                        "roupa diferente, mudança de idade, "
                        "mãos deformadas, olhos deformados, "
                        "membros extras, baixa qualidade, "
                        "movimento brusco, câmera tremendo, "
                        "texto, legenda, marca d'água, "
                        "cenário completamente diferente"
                    )

                    imagem_bytes = imagem_video.getvalue()
                    provedor_usado = None

                    def gerar_video_provedor(cliente, modelo):
                        """
                        Tenta primeiro com os controles de qualidade.
                        Se o provedor não aceitar algum parâmetro,
                        repete em modo compatível.
                        """
                        try:
                            return cliente.image_to_video(
                                imagem_bytes,
                                model=modelo,
                                prompt=prompt_final,
                                negative_prompt=negativo,
                                num_inference_steps=passos,
                            )
                        except Exception as erro_param:
                            mensagem_param = str(erro_param).lower()
                            parametro_incompativel = any(
                                palavra in mensagem_param
                                for palavra in [
                                    "unsupported",
                                    "unexpected",
                                    "parameter",
                                    "num_inference_steps",
                                    "negative_prompt",
                                ]
                            )

                            if not parametro_incompativel:
                                raise

                            st.info(
                                "🔄 Ajustando os parâmetros para "
                                "o provedor de vídeo..."
                            )

                            return cliente.image_to_video(
                                imagem_bytes,
                                model=modelo,
                                prompt=prompt_final,
                            )

                    def gerar_video_fal_direto():
                        """
                        Chama o fal.ai diretamente, sem usar o roteamento do
                        Hugging Face. A imagem é enviada como Data URI/Base64
                        para evitar erro 403 ao acessar links temporários.
                        """
                        import os
                        import urllib.request
                        import fal_client

                        os.environ["FAL_KEY"] = fal_api_key

                        mime_imagem = (
                            getattr(imagem_video, "type", None)
                            or "image/png"
                        )

                        imagem_b64 = base64.b64encode(
                            imagem_bytes
                        ).decode("utf-8")

                        imagem_data_uri = (
                            f"data:{mime_imagem};base64,{imagem_b64}"
                        )

                        endpoint_fal = str(
                            st.secrets.get(
                                "FAL_VIDEO_ENDPOINT",
                                "fal-ai/wan/v2.2-a14b/image-to-video/turbo",
                            )
                        ).strip() or "fal-ai/wan/v2.2-a14b/image-to-video/turbo"

                        resolucao_fal = {
                            "Rápida": "480p",
                            "Equilibrada": "580p",
                            "Melhor qualidade": "720p",
                        }.get(qualidade, "580p")

                        aspecto_fal = {
                            "YouTube 16:9": "16:9",
                            "TikTok/Reels 9:16": "9:16",
                            "Quadrado 1:1": "1:1",
                        }.get(formato, "16:9")

                        # O endpoint trabalha a 16 fps para cobrança por
                        # segundo; 81 quadros ≈ 5 s e 161 ≈ 10 s.
                        num_frames_fal = min(
                            161,
                            max(
                                17,
                                int(duracao_video * 16) + 1,
                            ),
                        )

                        argumentos_fal = {
                            "image_url": imagem_data_uri,
                            "prompt": prompt_final,
                            "negative_prompt": negativo,
                            "num_frames": num_frames_fal,
                            "frames_per_second": 16,
                            "resolution": resolucao_fal,
                            "aspect_ratio": aspecto_fal,
                        }

                        resultado_fal = fal_client.subscribe(
                            endpoint_fal,
                            arguments=argumentos_fal,
                            with_logs=False,
                        )

                        if not isinstance(resultado_fal, dict):
                            raise RuntimeError(
                                "O fal.ai retornou uma resposta inesperada."
                            )

                        video_info = resultado_fal.get("video") or {}
                        video_url = (
                            video_info.get("url")
                            if isinstance(video_info, dict)
                            else None
                        )

                        if not video_url:
                            raise RuntimeError(
                                "O fal.ai concluiu a tarefa, mas não retornou "
                                "a URL do vídeo."
                            )

                        with urllib.request.urlopen(
                            video_url,
                            timeout=600,
                        ) as resposta_video:
                            return resposta_video.read()

                    with st.spinner(
                        "🎬 Criando o vídeo com IA... "
                        "isso pode levar alguns minutos."
                    ):
                        video_bytes = None
                        erro_hf = None

                        # Se o fal.ai estiver configurado, usa o Turbo econômico
                        # diretamente. Isso evita perder tempo tentando HF sem saldo.
                        if fal_api_key:
                            st.info(
                                "🎬 Usando fal.ai Wan 2.2 Turbo econômico."
                            )

                            video_bytes = gerar_video_fal_direto()
                            provedor_usado = "fal.ai direto • Wan 2.2 Turbo"

                        # Se fal.ai não estiver configurado, tenta Hugging Face.
                        elif hf_token:
                            try:
                                cliente_hf = InferenceClient(
                                    provider=hf_provider,
                                    token=hf_token,
                                    timeout=600,
                                )

                                video_bytes = gerar_video_provedor(
                                    cliente_hf,
                                    hf_model,
                                )
                                provedor_usado = "Hugging Face"

                            except Exception as erro_primario:
                                erro_hf = erro_primario
                                raise
                        if not video_bytes:
                            raise RuntimeError(
                                "O provedor não retornou o vídeo."
                            )

                        st.session_state[
                            "video_ia_gerado"
                        ] = video_bytes

                        st.session_state[
                            "video_ia_nome"
                        ] = "mundo_da_luna_video_ia.mp4"

                    # Só usa o crédito do Mundo da Luna
                    # depois que o vídeo realmente foi criado.
                    if consumir_credito_video():
                        st.success(
                            "✅ Vídeo criado! "
                            "Foi usado 1 crédito."
                        )
                    else:
                        st.success("✅ Vídeo criado!")

                    if provedor_usado:
                        st.caption(
                            f"🎬 Provedor usado: {provedor_usado}"
                        )

                    st.caption(
                        f"💎 Saldo atual: "
                        f"{saldo_creditos_video() or 0} crédito(s)"
                    )

            except ImportError as e:
                pacote = str(e)
                st.error(
                    "Falta uma biblioteca necessária para gerar o vídeo. "
                    "Atualize o requirements.txt conforme o arquivo desta atualização."
                )
                with st.expander("🔧 Ver detalhe técnico"):
                    st.code(pacote)

            except Exception as e:
                erro = str(e)
                erro_lower = erro.lower()

                st.error(
                    "Não consegui gerar o vídeo agora. "
                    "Nenhum crédito foi descontado."
                )

                sem_creditos = (
                    "402" in erro
                    or "payment required" in erro_lower
                    or "depleted" in erro_lower
                    or "monthly included credits" in erro_lower
                    or "billing" in erro_lower
                    or "quota" in erro_lower
                    or "payment" in erro_lower
                )

                if sem_creditos:
                    st.warning(
                        "💳 Os créditos do provedor de IA acabaram."
                    )

                    try:
                        tem_fal = bool(
                            str(
                                st.secrets.get(
                                    "FAL_API_KEY",
                                    ""
                                )
                            ).strip()
                        )
                    except Exception:
                        tem_fal = False

                    if not tem_fal:
                        st.info(
                            "🔄 O app já está preparado para tentar "
                            "fal.ai automaticamente. Para habilitar essa "
                            "alternativa, adicione FAL_API_KEY nos Secrets. "
                            "O fal.ai pode exigir saldo próprio."
                        )

                elif "cannot access content at" in erro_lower:
                    st.warning(
                        "🖼️ O provedor não conseguiu acessar a imagem enviada."
                    )
                elif (
                    "401" in erro
                    or "403" in erro
                    or "unauthorized" in erro_lower
                    or "forbidden" in erro_lower
                ):
                    st.warning(
                        "🔑 O provedor recusou a autorização. "
                        "Confira a chave e as permissões da conta."
                    )

                elif (
                    "provider" in erro_lower
                    or "model" in erro_lower
                    or "unavailable" in erro_lower
                ):
                    st.warning(
                        "🤖 O modelo ou provedor "
                        "está indisponível agora."
                    )

                elif (
                    "timeout" in erro_lower
                    or "timed out" in erro_lower
                ):
                    st.warning(
                        "⏳ A geração demorou demais. "
                        "Tente novamente."
                    )

                with st.expander(
                    "🔧 Ver detalhe técnico"
                ):
                    st.code(erro)

    if st.session_state.get("video_ia_gerado"):
        st.markdown("### 🎥 Seu vídeo")
        st.video(st.session_state["video_ia_gerado"])
        st.download_button(
            "⬇️ Baixar vídeo",
            data=st.session_state["video_ia_gerado"],
            file_name=st.session_state.get(
                "video_ia_nome",
                "mundo_da_luna_video_ia.mp4",
            ),
            mime="video/mp4",
            width="stretch",
            key="baixar_video_ia",
        )


elif menu == "🎮 Jogos":
    st.markdown("## 🎮 Jogos do Mundo da Luna")
    st.caption(
        "Escolha a idade e depois o jogo. "
        "Cada atividade muda de dificuldade conforme a faixa etária."
    )

    faixa = st.selectbox(
        "👧 Escolha a faixa etária",
        ["4–5 anos", "6–7 anos", "8–9 anos", "10–12 anos", "13–15 anos"],
        key="faixa_jogos",
    )

    jogo_escolhido = st.radio(
        "✨ Escolha um jogo",
        [
            "🧠 Memória",
            "🔤 Palavras",
            "🔢 Números",
            "🌟 Desafio mágico",
        ],
        key="jogo_escolhido",
    )

    st.markdown("---")

    # =========================================================
    # JOGO DA MEMÓRIA
    # =========================================================
    if jogo_escolhido == "🧠 Memória":
        st.markdown("### 🧠 Jogo da memória")
        st.caption(
            "Encontre os pares iguais. Cada fase fica um pouco mais difícil."
        )

        # Reinicia o progresso quando a faixa etária mudar.
        if st.session_state.get("memoria_faixa") != faixa:
            st.session_state["memoria_faixa"] = faixa
            st.session_state["memoria_fase"] = 0
            for chave in [
                "memoria_cartas",
                "memoria_selecionadas",
                "memoria_pares",
                "memoria_tentativas",
                "memoria_erro_pendente",
            ]:
                st.session_state.pop(chave, None)

        fases_memoria = {
            "4–5 anos": [3, 4, 5],
            "6–7 anos": [4, 5, 6],
            "8–9 anos": [5, 6, 7],
            "10–12 anos": [6, 8, 10],
            "13–15 anos": [8, 10, 12],
        }

        fase_memoria = st.session_state.get("memoria_fase", 0)
        niveis_memoria = fases_memoria[faixa]

        if fase_memoria >= len(niveis_memoria):
            st.progress(1.0, text="Todas as fases concluídas!", width="stretch")
            st.success("🏆 Parabéns! Você terminou todas as fases do Jogo da Memória!")
            st.balloons()

            if st.button(
                "🔄 Jogar todas as fases novamente",
                key=f"memoria_reiniciar_total_{faixa}",
                width="stretch",
            ):
                st.session_state["memoria_fase"] = 0
                for chave in [
                    "memoria_cartas",
                    "memoria_selecionadas",
                    "memoria_pares",
                    "memoria_tentativas",
                    "memoria_erro_pendente",
                ]:
                    st.session_state.pop(chave, None)
                st.rerun()
        else:
            quantidade_pares = niveis_memoria[fase_memoria]
            dificuldade_memoria = ["🌱 Fácil", "⭐ Intermediária", "🔥 Desafio"][fase_memoria]
            st.markdown(
                f"#### Fase {fase_memoria + 1} de {len(niveis_memoria)} · {dificuldade_memoria}"
            )

            personagens_memoria = [
                ("👧", "Luna"),
                ("🐰", "Coelhinho"),
                ("🏰", "Castelo"),
                ("⭐", "Estrela"),
                ("📖", "Livro mágico"),
                ("🌙", "Lua"),
                ("🔑", "Chave"),
                ("🪄", "Varinha"),
                ("🧭", "Bússola"),
                ("💎", "Cristal"),
                ("🦋", "Borboleta"),
                ("🌸", "Flor"),
            ][:quantidade_pares]

            if "memoria_cartas" not in st.session_state:
                import random

                cartas = []
                for emoji, nome in personagens_memoria:
                    cartas.append({"emoji": emoji, "nome": nome})
                    cartas.append({"emoji": emoji, "nome": nome})

                random.shuffle(cartas)

                st.session_state["memoria_cartas"] = cartas
                st.session_state["memoria_selecionadas"] = []
                st.session_state["memoria_pares"] = []
                st.session_state["memoria_tentativas"] = 0
                st.session_state["memoria_erro_pendente"] = False

            cartas = st.session_state["memoria_cartas"]
            selecionadas = st.session_state["memoria_selecionadas"]
            pares = st.session_state["memoria_pares"]
            erro_pendente = st.session_state["memoria_erro_pendente"]

            st.markdown(
                f"**🏆 {len(pares) // 2}/{quantidade_pares} pares**  ·  "
                f"🎯 {st.session_state['memoria_tentativas']} tentativas"
            )

            progresso_memoria = int(
                ((len(pares) // 2) / quantidade_pares) * 100
            )
            st.progress(
                progresso_memoria,
                text=f"Progresso: {len(pares) // 2} de {quantidade_pares} pares",
                width="stretch",
            )

            # Duas cartas por linha para manter boa leitura no celular.
            colunas_memoria = 2

            for linha in range(0, len(cartas), colunas_memoria):
                cols = st.columns(
                    colunas_memoria,
                    gap="small",
                    wrap=False,
                )

                for posicao, indice in enumerate(
                    range(
                        linha,
                        min(
                            linha + colunas_memoria,
                            len(cartas),
                        ),
                    )
                ):
                    carta = cartas[indice]
                    esta_aberta = (
                        indice in selecionadas
                        or indice in pares
                    )
                    texto_carta = (
                        carta["emoji"]
                        if esta_aberta
                        else "❓"
                    )

                    with cols[posicao]:
                        clicou = st.button(
                            texto_carta,
                            key=f"memoria_carta_{fase_memoria}_{indice}",
                            width="stretch",
                            disabled=(
                                indice in pares
                                or indice in selecionadas
                                or erro_pendente
                            ),
                        )

                        if esta_aberta:
                            st.caption(
                                carta["nome"],
                                text_alignment="center",
                                width="stretch",
                            )
                        else:
                            st.caption(
                                "Carta",
                                text_alignment="center",
                                width="stretch",
                            )

                        if (
                            clicou
                            and indice not in selecionadas
                            and indice not in pares
                        ):
                            selecionadas.append(indice)

                            if len(selecionadas) == 2:
                                st.session_state[
                                    "memoria_tentativas"
                                ] += 1

                                primeira, segunda = selecionadas

                                if (
                                    cartas[primeira]["nome"]
                                    == cartas[segunda]["nome"]
                                ):
                                    pares.extend(
                                        [primeira, segunda]
                                    )

                                    st.session_state[
                                        "memoria_selecionadas"
                                    ] = []

                                    st.session_state[
                                        "memoria_pares"
                                    ] = pares

                                    st.session_state[
                                        "memoria_erro_pendente"
                                    ] = False

                                    st.rerun()

                                else:
                                    st.session_state[
                                        "memoria_selecionadas"
                                    ] = selecionadas

                                    st.session_state[
                                        "memoria_erro_pendente"
                                    ] = True

                                    st.rerun()

                            else:
                                st.session_state[
                                    "memoria_selecionadas"
                                ] = selecionadas

                                st.rerun()

            if len(st.session_state["memoria_selecionadas"]) == 1:
                st.markdown(
                    ":small[👆 Agora escolha uma segunda carta.]"
                )

            if st.session_state[
                "memoria_erro_pendente"
            ]:
                st.markdown(
                    ":small[💜 Cartas diferentes. Elas vão virar novamente.]"
                )
                time.sleep(1.2)
                st.session_state[
                    "memoria_selecionadas"
                ] = []
                st.session_state[
                    "memoria_erro_pendente"
                ] = False
                st.rerun()

            terminou_fase_memoria = (
                len(st.session_state["memoria_pares"]) == len(cartas)
            )

            if terminou_fase_memoria:
                st.success(
                    f"🎉 Parabéns! Você concluiu a Fase {fase_memoria + 1} "
                    f"com {quantidade_pares} pares!"
                )
                st.balloons()

                if fase_memoria + 1 < len(niveis_memoria):
                    st.markdown(
                        f"<div class='fase-desbloqueada'>🔓 Fase {fase_memoria + 2} desbloqueada!</div>",
                        unsafe_allow_html=True,
                    )

                    if st.button(
                        "➡️ Ir para a próxima fase",
                        key=f"memoria_proxima_fase_{faixa}_{fase_memoria}",
                        width="stretch",
                    ):
                        st.session_state["memoria_fase"] = fase_memoria + 1
                        for chave in [
                            "memoria_cartas",
                            "memoria_selecionadas",
                            "memoria_pares",
                            "memoria_tentativas",
                            "memoria_erro_pendente",
                        ]:
                            st.session_state.pop(chave, None)
                        st.rerun()
                else:
                    if st.button(
                        "🏆 Concluir Jogo da Memória",
                        key=f"memoria_concluir_{faixa}",
                        width="stretch",
                    ):
                        st.session_state["memoria_fase"] = len(niveis_memoria)
                        for chave in [
                            "memoria_cartas",
                            "memoria_selecionadas",
                            "memoria_pares",
                            "memoria_tentativas",
                            "memoria_erro_pendente",
                        ]:
                            st.session_state.pop(chave, None)
                        st.rerun()

            if not terminou_fase_memoria:
                if st.button(
                    "🎲 Embaralhar esta fase",
                    key=f"memoria_novo_jogo_{faixa}_{fase_memoria}",
                    width="stretch",
                ):
                    for chave in [
                        "memoria_cartas",
                        "memoria_selecionadas",
                        "memoria_pares",
                        "memoria_tentativas",
                        "memoria_erro_pendente",
                    ]:
                        st.session_state.pop(
                            chave,
                            None,
                        )
                    st.rerun()

    # =========================================================
    # PALAVRAS
    # =========================================================
    elif jogo_escolhido == "🔤 Palavras":
        st.markdown("### 🔤 Brincando com palavras")

        banco_palavras = {
            "4–5 anos": [
                {
                    "pergunta": "Complete a palavra: **L _ N A**",
                    "rotulo": "Qual letra está faltando?",
                    "opcoes": ["A", "U", "O"],
                    "correta": "U",
                    "mensagem": "🎉 Muito bem! A palavra é LUNA.",
                },
                {
                    "pergunta": "Complete a palavra: **B _ L A**",
                    "rotulo": "Qual letra está faltando?",
                    "opcoes": ["O", "A", "E"],
                    "correta": "O",
                    "mensagem": "🎉 Isso! A palavra é BOLA.",
                },
                {
                    "pergunta": "Complete a palavra: **G _ T O**",
                    "rotulo": "Qual letra está faltando?",
                    "opcoes": ["A", "E", "I"],
                    "correta": "A",
                    "mensagem": "🎉 Certo! A palavra é GATO.",
                },
            ],
            "6–7 anos": [
                {
                    "pergunta": "Complete a palavra: **C _ E L H O**",
                    "rotulo": "Qual letra está faltando?",
                    "opcoes": ["A", "O", "U"],
                    "correta": "O",
                    "mensagem": "🎉 Muito bem! A palavra é COELHO.",
                },
                {
                    "pergunta": "Complete a palavra: **F L _ R E S T A**",
                    "rotulo": "Qual letra está faltando?",
                    "opcoes": ["O", "A", "E"],
                    "correta": "O",
                    "mensagem": "🎉 Certo! A palavra é FLORESTA.",
                },
                {
                    "pergunta": "Complete a palavra: **C A S T _ L O**",
                    "rotulo": "Qual letra está faltando?",
                    "opcoes": ["E", "A", "I"],
                    "correta": "E",
                    "mensagem": "🎉 Isso! A palavra é CASTELO.",
                },
            ],
            "8–9 anos": [
                {
                    "pergunta": "Complete a frase: **Luna abriu o ____ mágico.**",
                    "rotulo": "Escolha a palavra correta:",
                    "opcoes": ["livro", "sapato", "bolo"],
                    "correta": "livro",
                    "mensagem": "🎉 Certo! Luna abriu o livro mágico.",
                },
                {
                    "pergunta": "Complete a frase: **O coelhinho entrou na ____.**",
                    "rotulo": "Escolha a palavra correta:",
                    "opcoes": ["floresta", "garagem", "cozinha"],
                    "correta": "floresta",
                    "mensagem": "🎉 Muito bem! O coelhinho entrou na floresta.",
                },
                {
                    "pergunta": "Complete a frase: **A princesa mora no ____.**",
                    "rotulo": "Escolha a palavra correta:",
                    "opcoes": ["castelo", "barco", "mercado"],
                    "correta": "castelo",
                    "mensagem": "🎉 Isso! A princesa mora no castelo.",
                },
            ],
            "10–12 anos": [
                {
                    "pergunta": "Qual palavra completa melhor a frase? **Luna ficou ____ ao perceber que o caminho havia mudado.**",
                    "rotulo": "Escolha:",
                    "opcoes": ["intrigada", "adormecida", "invisível"],
                    "correta": "intrigada",
                    "mensagem": "✨ Isso! 'Intrigada' combina com alguém curioso diante de um mistério.",
                },
                {
                    "pergunta": "Qual palavra completa melhor? **O castelo parecia ____ durante a tempestade.**",
                    "rotulo": "Escolha:",
                    "opcoes": ["sombrio", "redondo", "doce"],
                    "correta": "sombrio",
                    "mensagem": "✨ Certo! 'Sombrio' combina com a cena.",
                },
                {
                    "pergunta": "Complete: **Luna seguiu as pistas com muita ____.**",
                    "rotulo": "Escolha:",
                    "opcoes": ["atenção", "fome", "pressa"],
                    "correta": "atenção",
                    "mensagem": "✨ Muito bem! 'Atenção' completa a frase.",
                },
            ],
            "13–15 anos": [
                {
                    "pergunta": "Qual alternativa apresenta um **sinônimo** de 'misterioso'?",
                    "rotulo": "Escolha:",
                    "opcoes": ["enigmático", "barulhento", "veloz"],
                    "correta": "enigmático",
                    "mensagem": "✨ Certo! 'Enigmático' é um sinônimo de 'misterioso'.",
                },
                {
                    "pergunta": "Qual palavra é sinônimo de **corajoso**?",
                    "rotulo": "Escolha:",
                    "opcoes": ["valente", "distraído", "quieto"],
                    "correta": "valente",
                    "mensagem": "✨ Isso! 'Valente' é sinônimo de 'corajoso'.",
                },
                {
                    "pergunta": "Qual palavra é o contrário de **escuro**?",
                    "rotulo": "Escolha:",
                    "opcoes": ["claro", "forte", "lento"],
                    "correta": "claro",
                    "mensagem": "✨ Muito bem! 'Claro' é o contrário de 'escuro'.",
                },
            ],
        }

        chave_faixa_palavras = "palavras_faixa"
        chave_etapa_palavras = "palavras_etapa"

        if st.session_state.get(chave_faixa_palavras) != faixa:
            st.session_state[chave_faixa_palavras] = faixa
            st.session_state[chave_etapa_palavras] = 0

        perguntas_palavras = banco_palavras[faixa]
        etapa_palavras = st.session_state.get(chave_etapa_palavras, 0)

        if etapa_palavras >= len(perguntas_palavras):
            st.progress(1.0, text="Progresso: 3 de 3 concluídas", width="stretch")
            st.success("🏆 Parabéns! Você terminou todas as palavras desta fase!")
            st.balloons()

            if st.button(
                "🔄 Jogar palavras novamente",
                key=f"reiniciar_palavras_{faixa}",
                width="stretch",
            ):
                st.session_state[chave_etapa_palavras] = 0
                st.rerun()

        else:
            pergunta_atual = perguntas_palavras[etapa_palavras]

            st.progress(
                etapa_palavras / len(perguntas_palavras),
                text=f"Progresso: {etapa_palavras} de {len(perguntas_palavras)} concluídas",
                width="stretch",
            )
            st.caption(
                f"Pergunta {etapa_palavras + 1} de {len(perguntas_palavras)}"
            )
            st.write(pergunta_atual["pergunta"])

            with st.form(
                key=f"form_palavra_{faixa}_{etapa_palavras}",
                clear_on_submit=False,
                enter_to_submit=True,
            ):
                resposta_palavra = st.radio(
                    pergunta_atual["rotulo"],
                    pergunta_atual["opcoes"],
                    key=f"jogo_palavra_{faixa}_{etapa_palavras}",
                )
                confirmar_palavra = st.form_submit_button(
                    "✅ Conferir palavra",
                    width="stretch",
                )

            st.caption("⌨️ No notebook, você também pode pressionar Enter para confirmar.")

            if confirmar_palavra:
                if resposta_palavra == pergunta_atual["correta"]:
                    st.success(pergunta_atual["mensagem"])
                    st.balloons()
                    time.sleep(1.1)
                    st.session_state[chave_etapa_palavras] = etapa_palavras + 1
                    st.rerun()
                else:
                    st.warning("💜 Quase! Tente outra opção.")

    # =========================================================
    # NÚMEROS
    # =========================================================
    elif jogo_escolhido == "🔢 Números":
        st.markdown("### 🔢 Brincando com números")

        fases_numeros = {
            "4–5 anos": [
                [
                    ("Conte as estrelas: ⭐ ⭐ ⭐ ⭐", 4, 10),
                    ("Quantos coelhinhos há? 🐰 🐰 🐰", 3, 10),
                    ("Quantas luas aparecem? 🌙 🌙 🌙 🌙 🌙", 5, 10),
                ],
                [
                    ("🍎 Luna tem **2 maçãs** e ganha mais **3**. Quantas tem?", 5, 10),
                    ("⭐ Há **6 estrelas** e 2 apagam. Quantas ficam?", 4, 10),
                    ("🐰 Quantos coelhos há em dois grupos de 2? 🐰🐰 + 🐰🐰", 4, 10),
                ],
                [
                    ("🌙 Conte: 🌙 🌙 🌙 🌙 🌙 🌙", 6, 10),
                    ("🎈 Luna tinha **7 balões** e soltou 3. Quantos sobraram?", 4, 10),
                    ("⭐ Quantas estrelas faltam para chegar a 10 se já temos 8?", 2, 10),
                ],
            ],
            "6–7 anos": [
                [
                    ("🐰 O coelhinho encontrou **3 cenouras** e depois mais **2**. Quantas cenouras ele tem?", 5, 20),
                    ("⭐ Luna tinha **5 estrelas** e ganhou mais **4**. Quantas estrelas tem agora?", 9, 20),
                    ("📖 Havia **10 livros** e 3 foram guardados. Quantos ficaram?", 7, 20),
                ],
                [
                    ("🏰 Há **8 janelas** em uma torre e **5** em outra. Quantas ao todo?", 13, 20),
                    ("🔑 Luna tinha **14 chaves** e perdeu 6. Quantas sobraram?", 8, 20),
                    ("🐰 4 coelhos têm 2 cenouras cada. Quantas cenouras ao todo?", 8, 20),
                ],
                [
                    ("⭐ 12 estrelas foram divididas em 3 grupos iguais. Quantas em cada grupo?", 4, 20),
                    ("🌙 9 luas + 7 estrelas = quantos símbolos?", 16, 20),
                    ("📚 18 livros menos 9 livros = ?", 9, 20),
                ],
            ],
            "8–9 anos": [
                [
                    ("🏰 No castelo havia **12 estrelas**. **5 apagaram**. Quantas ficaram acesas?", 7, 30),
                    ("🐰 O coelhinho encontrou **8 cenouras** de manhã e **6** à tarde. Quantas encontrou ao todo?", 14, 30),
                    ("🔑 Luna tinha **15 chaves** e usou **7**. Quantas sobraram?", 8, 30),
                ],
                [
                    ("⭐ 4 caixas têm 5 estrelas cada. Quantas estrelas ao todo?", 20, 30),
                    ("📖 24 livros foram divididos igualmente em 6 prateleiras. Quantos por prateleira?", 4, 30),
                    ("🏰 Um castelo tem 18 janelas e ganhou mais 9. Quantas agora?", 27, 30),
                ],
                [
                    ("🐰 30 cenouras foram divididas entre 5 coelhos. Quantas para cada um?", 6, 30),
                    ("🌟 Qual é o dobro de 13?", 26, 30),
                    ("🔮 21 cristais menos 8 = ?", 13, 30),
                ],
            ],
            "10–12 anos": [
                [
                    ("🔮 Luna encontrou **6 cristais**. Cada cristal vale **4 pontos**. Quantos pontos ela conseguiu?", 24, 100),
                    ("🌟 Cada caixa tem **8 estrelas**. Quantas estrelas há em **5 caixas**?", 40, 100),
                    ("🏰 Um castelo tem **36 janelas** divididas igualmente em **4 torres**. Quantas janelas por torre?", 9, 100),
                ],
                [
                    ("🧩 7 portais usam 6 símbolos cada. Quantos símbolos ao todo?", 42, 100),
                    ("⭐ 72 estrelas foram divididas em 8 grupos. Quantas por grupo?", 9, 100),
                    ("🔑 45 chaves menos 17 = ?", 28, 100),
                ],
                [
                    ("🔮 9 cristais valem 7 pontos cada. Quantos pontos?", 63, 100),
                    ("🏰 84 janelas divididas entre 7 torres = ?", 12, 100),
                    ("🌟 Qual é o triplo de 24?", 72, 100),
                ],
            ],
            "13–15 anos": [
                [
                    ("🧩 Um portal exige **3 chaves**, e cada chave tem **7 símbolos**. Se Luna encontrou 2 portais completos, quantos símbolos há ao todo?", 42, 200),
                    ("🔮 Um cristal vale **12 pontos**. Quantos pontos valem **7 cristais**?", 84, 200),
                    ("🧠 Se 96 estrelas forem divididas igualmente entre 8 torres, quantas estrelas ficam em cada torre?", 12, 200),
                ],
                [
                    ("⭐ 15 caixas têm 8 estrelas cada. Quantas estrelas ao todo?", 120, 200),
                    ("🔑 144 chaves divididas igualmente entre 12 salas = ?", 12, 200),
                    ("🔮 175 pontos menos 68 pontos = ?", 107, 200),
                ],
                [
                    ("🧠 Qual é 25% de 200?", 50, 200),
                    ("🏰 18 torres têm 9 janelas cada. Quantas janelas?", 162, 200),
                    ("🌟 192 estrelas divididas em 16 grupos = ?", 12, 200),
                ],
            ],
        }

        if st.session_state.get("numeros_faixa") != faixa:
            st.session_state["numeros_faixa"] = faixa
            st.session_state["numeros_fase"] = 0
            st.session_state["numeros_etapa"] = 0

        fases_num = fases_numeros[faixa]
        fase_num = st.session_state.get("numeros_fase", 0)
        etapa_numeros = st.session_state.get("numeros_etapa", 0)

        if fase_num >= len(fases_num):
            st.progress(1.0, text="Todas as fases concluídas!", width="stretch")
            st.success("🏆 Parabéns! Você terminou todas as fases de números!")
            if not st.session_state.get("numeros_festa_final", False):
                st.balloons()
                st.snow()
                st.session_state["numeros_festa_final"] = True

            if st.button(
                "🔄 Jogar Números desde o início",
                key=f"reiniciar_numeros_total_{faixa}",
                width="stretch",
            ):
                st.session_state["numeros_fase"] = 0
                st.session_state["numeros_etapa"] = 0
                st.session_state["numeros_festa_final"] = False
                st.rerun()
        else:
            perguntas_numeros = fases_num[fase_num]
            dificuldade_num = ["🌱 Fácil", "⭐ Intermediária", "🔥 Desafio"][min(fase_num, 2)]
            st.markdown(f"#### Fase {fase_num + 1} de {len(fases_num)} · {dificuldade_num}")

            if etapa_numeros >= len(perguntas_numeros):
                st.progress(1.0, text=f"Fase {fase_num + 1} concluída!", width="stretch")
                st.success(f"🎉 Você concluiu a Fase {fase_num + 1}!")
                st.balloons()

                proxima_num = fase_num + 2
                if fase_num + 1 < len(fases_num):
                    st.markdown(
                        f"<div class='fase-desbloqueada'>🔓 Fase {proxima_num} desbloqueada!</div>",
                        unsafe_allow_html=True,
                    )

                if st.button(
                    "➡️ Ir para a próxima fase",
                    key=f"proxima_fase_numeros_{faixa}_{fase_num}",
                    width="stretch",
                ):
                    if fase_num + 1 < len(fases_num):
                        st.toast(
                            f"Fase {proxima_num} desbloqueada!",
                            icon="🔓",
                            duration="short",
                        )
                    st.session_state["numeros_fase"] = fase_num + 1
                    st.session_state["numeros_etapa"] = 0
                    st.rerun()
            else:
                pergunta_numero, resposta_correta_num, maximo_num = perguntas_numeros[etapa_numeros]

                st.progress(
                    etapa_numeros / len(perguntas_numeros),
                    text=f"Fase {fase_num + 1}: {etapa_numeros} de {len(perguntas_numeros)} concluídas",
                    width="stretch",
                )
                st.caption(
                    f"Pergunta {etapa_numeros + 1} de {len(perguntas_numeros)}"
                )
                st.write(pergunta_numero)

                with st.form(
                    key=f"form_numero_{faixa}_{fase_num}_{etapa_numeros}",
                    clear_on_submit=False,
                    enter_to_submit=True,
                ):
                    resposta_numero = st.number_input(
                        "Digite sua resposta:",
                        min_value=0,
                        max_value=maximo_num,
                        step=1,
                        key=f"jogo_numero_{faixa}_{fase_num}_{etapa_numeros}",
                    )
                    confirmar_numero = st.form_submit_button(
                        "⭐ Conferir resposta",
                        width="stretch",
                    )

                st.caption("⌨️ Digite a resposta e pressione Enter para confirmar.")

                if confirmar_numero:
                    if int(resposta_numero) == resposta_correta_num:
                        st.success("🎉 Acertou! Muito bem!")
                        st.balloons()
                        time.sleep(1.0)
                        st.session_state["numeros_etapa"] = etapa_numeros + 1
                        st.rerun()
                    else:
                        st.warning("💜 Quase! Pense mais um pouco.")

    # =========================================================
    # DESAFIO MÁGICO
    # =========================================================
    else:
        st.markdown("### 🌟 Desafio mágico")

        fases_desafios = {
            "4–5 anos": [
                [
                    ("🟣 Qual é a cor deste círculo?", ["Roxo", "Amarelo", "Verde"], "Roxo", "✨ Isso! O círculo é roxo."),
                    ("🔺 Qual é esta forma?", ["Triângulo", "Círculo", "Quadrado"], "Triângulo", "✨ Muito bem! É um triângulo."),
                    ("⭐ Qual símbolo é uma estrela?", ["⭐", "🌙", "🐰"], "⭐", "✨ Certo! Esta é a estrela."),
                ],
                [
                    ("🐰 Qual destes é um animal?", ["🐰", "🏰", "⭐"], "🐰", "✨ Isso! O coelho é um animal."),
                    ("🌙 O que aparece no céu à noite?", ["Lua", "Cenoura", "Sapato"], "Lua", "✨ Muito bem! A lua aparece no céu."),
                    ("🟨 Qual forma tem quatro lados iguais?", ["Quadrado", "Círculo", "Triângulo"], "Quadrado", "✨ Certo! É o quadrado."),
                ],
                [
                    ("🎨 Qual destas cores é azul?", ["Azul", "Rosa", "Verde"], "Azul", "✨ Isso! Azul é a resposta."),
                    ("☀️ O que brilha de dia?", ["Sol", "Lua", "Chave"], "Sol", "✨ Muito bem! O sol brilha de dia."),
                    ("🐰 O coelho tem quantas orelhas?", ["1", "2", "4"], "2", "✨ Certo! O coelho tem duas orelhas."),
                ],
            ],
            "6–7 anos": [
                [
                    ("🔺 Qual é o nome desta forma?", ["Triângulo", "Quadrado", "Círculo"], "Triângulo", "✨ Certo! Essa forma é um triângulo."),
                    ("🌙 Qual símbolo representa a lua?", ["🌙 Lua", "⭐ Estrela", "🐰 Coelho"], "🌙 Lua", "✨ Muito bem! Essa é a lua."),
                    ("🎨 Qual dessas cores é uma cor primária?", ["Azul", "Roxo", "Rosa"], "Azul", "✨ Certo! Azul é uma cor primária."),
                ],
                [
                    ("🔍 Qual palavra começa com a mesma letra de LUNA?", ["Livro", "Coelho", "Estrela"], "Livro", "✨ Isso! Luna e Livro começam com L."),
                    ("⭐ Qual número vem depois de 9?", ["10", "11", "8"], "10", "✨ Muito bem! Depois de 9 vem 10."),
                    ("🐰 Qual é o plural de coelho?", ["Coelhos", "Coelhas", "Coelhinho"], "Coelhos", "✨ Certo! O plural é coelhos."),
                ],
                [
                    ("🌟 Complete: 2, 4, 6, __", ["7", "8", "10"], "8", "✨ Isso! A sequência cresce de 2 em 2."),
                    ("🏰 Onde normalmente mora uma princesa em contos?", ["Castelo", "Ônibus", "Mercado"], "Castelo", "✨ Muito bem! Castelo."),
                    ("🔑 Para que serve uma chave?", ["Abrir uma fechadura", "Comer", "Dormir"], "Abrir uma fechadura", "✨ Certo! A chave abre fechaduras."),
                ],
            ],
            "8–9 anos": [
                [
                    ("Complete a sequência mágica: **⭐ 🌙 ⭐ 🌙 ❓**", ["⭐ Estrela", "🌙 Lua", "🐰 Coelho"], "⭐ Estrela", "✨ Muito bem! A sequência alterna estrela e lua."),
                    ("Qual número vem depois? **2, 4, 6, 8, __**", ["9", "10", "12"], "10", "✨ Certo! A sequência aumenta de 2 em 2."),
                    ("Qual item não combina com os outros?", ["Castelo", "Palácio", "Cenoura"], "Cenoura", "✨ Isso! Cenoura é diferente dos outros dois."),
                ],
                [
                    ("🧠 Qual número completa: 5, 10, 15, __?", ["18", "20", "25"], "20", "✨ Certo! A sequência aumenta de 5 em 5."),
                    ("🔍 Qual palavra é sinônimo de feliz?", ["Alegre", "Escuro", "Lento"], "Alegre", "✨ Muito bem! Alegre é sinônimo de feliz."),
                    ("🌙 Qual é o contrário de claro?", ["Escuro", "Grande", "Rápido"], "Escuro", "✨ Isso! Escuro é o contrário de claro."),
                ],
                [
                    ("⭐ Qual número é o dobro de 7?", ["12", "14", "16"], "14", "✨ Certo! O dobro de 7 é 14."),
                    ("🧩 Se hoje é segunda-feira, que dia vem depois?", ["Terça-feira", "Domingo", "Sábado"], "Terça-feira", "✨ Muito bem! Depois de segunda vem terça."),
                    ("🔑 Qual objeto é usado para abrir uma porta?", ["Chave", "Livro", "Estrela"], "Chave", "✨ Certo! É a chave."),
                ],
            ],
            "10–12 anos": [
                [
                    ("🧠 Qual número completa a sequência? **2, 4, 8, 16, __**", ["20", "24", "32"], "32", "✨ Certo! Cada número é o dobro do anterior."),
                    ("🧩 Se uma chave abre 2 portas, quantas portas 4 chaves podem abrir?", ["6", "8", "10"], "8", "✨ Muito bem! 4 × 2 = 8."),
                    ("🔮 Qual número falta? **5, 10, 15, __, 25**", ["18", "20", "22"], "20", "✨ Certo! A sequência aumenta de 5 em 5."),
                ],
                [
                    ("🧠 Qual número completa: 3, 6, 12, 24, __?", ["36", "48", "54"], "48", "✨ Certo! Cada número dobra."),
                    ("🔍 Qual palavra significa quase o mesmo que 'rápido'?", ["Veloz", "Pesado", "Escuro"], "Veloz", "✨ Muito bem! Veloz é sinônimo de rápido."),
                    ("🧩 Se 5 caixas têm 4 objetos cada, quantos objetos existem?", ["9", "20", "25"], "20", "✨ Certo! 5 × 4 = 20."),
                ],
                [
                    ("🔮 Qual é metade de 50?", ["20", "25", "30"], "25", "✨ Isso! Metade de 50 é 25."),
                    ("🌟 Qual número vem depois: 10, 20, 30, __?", ["35", "40", "50"], "40", "✨ Muito bem! A sequência soma 10."),
                    ("🧠 Se A é maior que B e B é maior que C, quem é o maior?", ["A", "B", "C"], "A", "✨ Certo! A é o maior."),
                ],
            ],
            "13–15 anos": [
                [
                    ("🧩 Se todos os portais azuis são mágicos e este portal é azul, qual conclusão é logicamente correta?", ["Este portal é mágico", "Todo portal mágico é azul", "Nenhum portal azul é mágico"], "Este portal é mágico", "✨ Exato! Essa conclusão segue diretamente das informações dadas."),
                    ("🧠 Qual número completa a sequência? **3, 6, 12, 24, __**", ["36", "48", "60"], "48", "✨ Certo! Cada número dobra."),
                    ("🔍 Se A é maior que B e B é maior que C, qual afirmação é verdadeira?", ["A é maior que C", "C é maior que A", "A é igual a C"], "A é maior que C", "✨ Exato! A relação é transitiva."),
                ],
                [
                    ("🧠 Qual é 20% de 150?", ["20", "30", "40"], "30", "✨ Certo! 20% de 150 é 30."),
                    ("🔍 Qual palavra é antônimo de 'expandir'?", ["Contrair", "Aumentar", "Alongar"], "Contrair", "✨ Muito bem! Contrair é o antônimo."),
                    ("🧩 Se x + 8 = 20, qual é x?", ["10", "12", "14"], "12", "✨ Certo! x = 12."),
                ],
                [
                    ("🌟 Qual número completa: 1, 4, 9, 16, __?", ["20", "25", "36"], "25", "✨ Isso! São quadrados perfeitos."),
                    ("🧠 Se 3x = 27, qual é x?", ["6", "9", "12"], "9", "✨ Certo! x = 9."),
                    ("🔍 Qual é o resultado lógico: se P implica Q e P é verdadeiro?", ["Q é verdadeiro", "Q é falso", "Nada pode ser dito"], "Q é verdadeiro", "✨ Exato! Pela implicação, Q é verdadeiro."),
                ],
            ],
        }

        if st.session_state.get("desafio_faixa") != faixa:
            st.session_state["desafio_faixa"] = faixa
            st.session_state["desafio_fase"] = 0
            st.session_state["desafio_etapa"] = 0

        fases_des = fases_desafios[faixa]
        fase_desafio = st.session_state.get("desafio_fase", 0)
        etapa_desafio = st.session_state.get("desafio_etapa", 0)

        if fase_desafio >= len(fases_des):
            st.progress(1.0, text="Todas as fases concluídas!", width="stretch")
            st.success("🏆 Parabéns! Você venceu todas as fases do Desafio Mágico!")
            if not st.session_state.get("desafio_festa_final", False):
                st.balloons()
                st.snow()
                st.session_state["desafio_festa_final"] = True

            if st.button(
                "🔄 Jogar Desafio Mágico desde o início",
                key=f"reiniciar_desafio_total_{faixa}",
                width="stretch",
            ):
                st.session_state["desafio_fase"] = 0
                st.session_state["desafio_etapa"] = 0
                st.session_state["desafio_festa_final"] = False
                st.rerun()
        else:
            desafios = fases_des[fase_desafio]
            dificuldade_des = ["🌱 Fácil", "⭐ Intermediária", "🔥 Desafio"][min(fase_desafio, 2)]
            st.markdown(f"#### Fase {fase_desafio + 1} de {len(fases_des)} · {dificuldade_des}")

            if etapa_desafio >= len(desafios):
                st.progress(1.0, text=f"Fase {fase_desafio + 1} concluída!", width="stretch")
                st.success(f"🎉 Você concluiu a Fase {fase_desafio + 1}!")
                st.balloons()

                proxima_des = fase_desafio + 2
                if fase_desafio + 1 < len(fases_des):
                    st.markdown(
                        f"<div class='fase-desbloqueada'>🔓 Fase {proxima_des} desbloqueada!</div>",
                        unsafe_allow_html=True,
                    )

                if st.button(
                    "➡️ Ir para a próxima fase",
                    key=f"proxima_fase_desafio_{faixa}_{fase_desafio}",
                    width="stretch",
                ):
                    if fase_desafio + 1 < len(fases_des):
                        st.toast(
                            f"Fase {proxima_des} desbloqueada!",
                            icon="🔓",
                            duration="short",
                        )
                    st.session_state["desafio_fase"] = fase_desafio + 1
                    st.session_state["desafio_etapa"] = 0
                    st.rerun()
            else:
                pergunta_desafio, opcoes_desafio, correta_desafio, sucesso_desafio = desafios[etapa_desafio]

                st.progress(
                    etapa_desafio / len(desafios),
                    text=f"Fase {fase_desafio + 1}: {etapa_desafio} de {len(desafios)} concluídos",
                    width="stretch",
                )
                st.caption(
                    f"Desafio {etapa_desafio + 1} de {len(desafios)}"
                )
                st.write(pergunta_desafio)

                with st.form(
                    key=f"form_desafio_{faixa}_{fase_desafio}_{etapa_desafio}",
                    clear_on_submit=False,
                    enter_to_submit=True,
                ):
                    resposta_desafio = st.radio(
                        "Escolha:",
                        opcoes_desafio,
                        key=f"desafio_{faixa}_{fase_desafio}_{etapa_desafio}",
                    )
                    confirmar_desafio = st.form_submit_button(
                        "🌟 Conferir desafio",
                        width="stretch",
                    )

                st.caption("⌨️ No notebook, você também pode pressionar Enter para confirmar.")

                if confirmar_desafio:
                    if resposta_desafio == correta_desafio:
                        st.success(sucesso_desafio)
                        st.balloons()
                        time.sleep(1.0)
                        st.session_state["desafio_etapa"] = etapa_desafio + 1
                        st.rerun()
                    else:
                        st.warning("💜 Quase! Observe mais uma vez.")

    st.markdown("---")
    st.caption(
        "🌙 Os jogos são educativos e não usam créditos de IA."
    )

elif menu == "📚 Atividades escolares":
    st.markdown("## 📚 Atividades escolares")
    st.caption("Atividades educativas por idade, com correção na hora e avanço para novas fases.")

    idade = st.selectbox(
        "🎒 Faixa etária",
        ["4–5 anos", "6–7 anos", "8–9 anos"],
        key="idade_atividades",
    )

    materia = st.selectbox(
        "📘 Matéria",
        [
            "Alfabetização",
            "Leitura",
            "Matemática",
            "Cores e formas",
            "Animais",
            "Atividade para colorir",
        ],
        key="materia_atividades",
    )

    chave_contexto = f"{idade}|{materia}"
    if st.session_state.get("atividade_contexto") != chave_contexto:
        st.session_state["atividade_contexto"] = chave_contexto
        st.session_state["atividade_fase"] = 0
        st.session_state["atividade_etapa"] = 0

    fase_atividade = st.session_state.get("atividade_fase", 0)
    etapa_atividade = st.session_state.get("atividade_etapa", 0)

    bancos_atividades = {
        ("4–5 anos", "Alfabetização"): [
            ("Complete a palavra: **L _ N A**", "texto", "Digite a letra que falta:", "U",
             "ALFABETIZAÇÃO 4–5 ANOS\nComplete: L _ N A\nCircule as vogais da palavra LUNA."),
            ("Complete a palavra: **B _ L A**", "texto", "Digite a letra que falta:", "O",
             "ALFABETIZAÇÃO 4–5 ANOS\nComplete: B _ L A\nEscreva a palavra BOLA."),
            ("Complete a palavra: **G _ T O**", "texto", "Digite a letra que falta:", "A",
             "ALFABETIZAÇÃO 4–5 ANOS\nComplete: G _ T O\nCircule a vogal da palavra GATO."),
        ],
        ("6–7 anos", "Alfabetização"): [
            ("Complete a palavra: **C _ E L H O**", "texto", "Digite a letra que falta:", "O",
             "ALFABETIZAÇÃO 6–7 ANOS\nComplete: C _ E L H O\nSepare COELHO em sílabas."),
            ("Complete a palavra: **F L _ R E S T A**", "texto", "Digite a letra que falta:", "O",
             "ALFABETIZAÇÃO 6–7 ANOS\nComplete: F L _ R E S T A\nEscreva FLORESTA."),
            ("Complete a palavra: **C A S T _ L O**", "texto", "Digite a letra que falta:", "E",
             "ALFABETIZAÇÃO 6–7 ANOS\nComplete: C A S T _ L O\nEscreva CASTELO."),
        ],
        ("8–9 anos", "Alfabetização"): [
            ("Escreva uma frase usando **Luna**, **livro** e **floresta**.", "frase", "Sua frase:", 5,
             "ALFABETIZAÇÃO 8–9 ANOS\nEscreva uma frase usando: Luna, livro e floresta."),
            ("Escreva uma frase usando **coelhinho**, **castelo** e **estrela**.", "frase", "Sua frase:", 5,
             "ALFABETIZAÇÃO 8–9 ANOS\nEscreva uma frase usando: coelhinho, castelo e estrela."),
            ("Escreva uma frase usando **princesa**, **magia** e **aventura**.", "frase", "Sua frase:", 5,
             "ALFABETIZAÇÃO 8–9 ANOS\nEscreva uma frase usando: princesa, magia e aventura."),
        ],
        ("4–5 anos", "Leitura"): [
            ("Luna viu um coelhinho branco perto da árvore.", "leitura", "O que Luna viu?", "coelh",
             "LEITURA 4–5 ANOS\nLuna viu um coelhinho branco perto da árvore.\nPergunta: O que Luna viu?"),
            ("A princesa usava uma coroa dourada.", "leitura", "O que a princesa usava?", "coroa",
             "LEITURA 4–5 ANOS\nA princesa usava uma coroa dourada.\nPergunta: O que ela usava?"),
            ("No céu brilhava uma estrela.", "leitura", "O que brilhava no céu?", "estrela",
             "LEITURA 4–5 ANOS\nNo céu brilhava uma estrela.\nPergunta: O que brilhava no céu?"),
        ],
        ("6–7 anos", "Leitura"): [
            ("Luna abriu seu livro mágico e encontrou um mapa.", "leitura", "O que Luna encontrou?", "mapa",
             "LEITURA 6–7 ANOS\nLuna abriu seu livro mágico e encontrou um mapa.\nPergunta: O que ela encontrou?"),
            ("O coelhinho correu até o castelo para chamar a princesa.", "leitura", "Para onde o coelhinho correu?", "castelo",
             "LEITURA 6–7 ANOS\nO coelhinho correu até o castelo.\nPergunta: Para onde ele correu?"),
            ("Uma chave dourada estava escondida sob uma pedra.", "leitura", "O que estava sob a pedra?", "chave",
             "LEITURA 6–7 ANOS\nUma chave dourada estava escondida sob uma pedra.\nPergunta: O que estava escondido?"),
        ],
        ("8–9 anos", "Leitura"): [
            ("Luna abriu seu livro mágico. Uma luz roxa apareceu e ela e o coelhinho chegaram a uma floresta encantada.", "leitura", "Onde Luna e o coelhinho chegaram?", "floresta",
             "LEITURA 8–9 ANOS\nLuna abriu seu livro mágico e chegou a uma floresta encantada.\nPergunta: Onde ela chegou?"),
            ("A princesa entregou a Luna uma chave que abria a torre mais alta do castelo.", "leitura", "O que a princesa entregou a Luna?", "chave",
             "LEITURA 8–9 ANOS\nA princesa entregou a Luna uma chave.\nPergunta: O que ela entregou?"),
            ("O coelhinho percebeu pegadas brilhantes seguindo em direção ao jardim.", "leitura", "Para onde as pegadas iam?", "jardim",
             "LEITURA 8–9 ANOS\nHavia pegadas brilhantes indo ao jardim.\nPergunta: Para onde elas iam?"),
        ],
        ("4–5 anos", "Matemática"): [
            ("⭐ ⭐ + ⭐ = ?", "numero", "Sua resposta:", 3, "MATEMÁTICA 4–5 ANOS\n2 estrelas + 1 estrela = ?"),
            ("🐰 🐰 + 🐰 🐰 = ?", "numero", "Sua resposta:", 4, "MATEMÁTICA 4–5 ANOS\n2 coelhos + 2 coelhos = ?"),
            ("🌙 🌙 🌙 - 🌙 = ?", "numero", "Sua resposta:", 2, "MATEMÁTICA 4–5 ANOS\n3 luas - 1 lua = ?"),
        ],
        ("6–7 anos", "Matemática"): [
            ("Luna encontrou **4 cenouras** e ganhou mais **3**. Quantas tem?", "numero", "Sua resposta:", 7, "MATEMÁTICA 6–7 ANOS\n4 + 3 = ?"),
            ("Havia **10 estrelas** e 4 apagaram. Quantas ficaram?", "numero", "Sua resposta:", 6, "MATEMÁTICA 6–7 ANOS\n10 - 4 = ?"),
            ("3 coelhinhos têm 2 cenouras cada. Quantas cenouras ao todo?", "numero", "Sua resposta:", 6, "MATEMÁTICA 6–7 ANOS\n3 x 2 = ?"),
        ],
        ("8–9 anos", "Matemática"): [
            ("No castelo havia **12 estrelas**. **5 apagaram**. Quantas ficaram?", "numero", "Sua resposta:", 7, "MATEMÁTICA 8–9 ANOS\n12 - 5 = ?"),
            ("4 caixas têm 6 cristais cada. Quantos cristais ao todo?", "numero", "Sua resposta:", 24, "MATEMÁTICA 8–9 ANOS\n4 x 6 = ?"),
            ("27 chaves foram divididas em 3 grupos iguais. Quantas por grupo?", "numero", "Sua resposta:", 9, "MATEMÁTICA 8–9 ANOS\n27 dividido por 3 = ?"),
        ],
        ("4–5 anos", "Cores e formas"): [
            ("🟣 Qual é a cor deste círculo?", "opcao", "Escolha:", (["Roxo", "Amarelo", "Verde"], "Roxo"), "CORES E FORMAS 4–5 ANOS\nPinte um círculo de roxo."),
            ("🔺 Qual é esta forma?", "opcao", "Escolha:", (["Triângulo", "Círculo", "Quadrado"], "Triângulo"), "CORES E FORMAS 4–5 ANOS\nDesenhe um triângulo."),
            ("🟨 Qual forma tem quatro lados iguais?", "opcao", "Escolha:", (["Quadrado", "Círculo", "Triângulo"], "Quadrado"), "CORES E FORMAS 4–5 ANOS\nDesenhe um quadrado amarelo."),
        ],
        ("6–7 anos", "Cores e formas"): [
            ("Qual destas é uma cor primária?", "opcao", "Escolha:", (["Azul", "Roxo", "Rosa"], "Azul"), "CORES E FORMAS 6–7 ANOS\nPinte uma forma de azul."),
            ("Qual forma não tem lados?", "opcao", "Escolha:", (["Círculo", "Quadrado", "Triângulo"], "Círculo"), "CORES E FORMAS 6–7 ANOS\nDesenhe um círculo."),
            ("Qual forma tem 3 lados?", "opcao", "Escolha:", (["Triângulo", "Quadrado", "Círculo"], "Triângulo"), "CORES E FORMAS 6–7 ANOS\nDesenhe um triângulo."),
        ],
        ("8–9 anos", "Cores e formas"): [
            ("Qual forma tem 4 lados e lados opostos iguais?", "opcao", "Escolha:", (["Retângulo", "Círculo", "Triângulo"], "Retângulo"), "CORES E FORMAS 8–9 ANOS\nDesenhe um retângulo."),
            ("Misturar azul e amarelo forma qual cor?", "opcao", "Escolha:", (["Verde", "Roxo", "Laranja"], "Verde"), "CORES E FORMAS 8–9 ANOS\nMisture azul e amarelo."),
            ("Qual destas formas tem 5 lados?", "opcao", "Escolha:", (["Pentágono", "Triângulo", "Quadrado"], "Pentágono"), "CORES E FORMAS 8–9 ANOS\nDesenhe um pentágono."),
        ],
        ("4–5 anos", "Animais"): [
            ("🐰 Qual animal acompanha Luna?", "opcao", "Escolha:", (["Coelho", "Gato", "Cachorro"], "Coelho"), "ANIMAIS 4–5 ANOS\nCircule o COELHO."),
            ("🐱 Qual destes animais mia?", "opcao", "Escolha:", (["Gato", "Coelho", "Peixe"], "Gato"), "ANIMAIS 4–5 ANOS\nCircule o GATO."),
            ("🐶 Qual destes animais late?", "opcao", "Escolha:", (["Cachorro", "Peixe", "Pássaro"], "Cachorro"), "ANIMAIS 4–5 ANOS\nCircule o CACHORRO."),
        ],
        ("6–7 anos", "Animais"): [
            ("Qual animal vive na água?", "opcao", "Escolha:", (["Peixe", "Coelho", "Gato"], "Peixe"), "ANIMAIS 6–7 ANOS\nEscreva PEIXE."),
            ("Qual animal tem penas?", "opcao", "Escolha:", (["Pássaro", "Cachorro", "Coelho"], "Pássaro"), "ANIMAIS 6–7 ANOS\nEscreva PÁSSARO."),
            ("Qual animal costuma viver em uma toca?", "opcao", "Escolha:", (["Coelho", "Peixe", "Galinha"], "Coelho"), "ANIMAIS 6–7 ANOS\nEscreva COELHO."),
        ],
        ("8–9 anos", "Animais"): [
            ("Qual destes é um mamífero?", "opcao", "Escolha:", (["Coelho", "Galinha", "Peixe"], "Coelho"), "ANIMAIS 8–9 ANOS\nExplique por que o coelho é mamífero."),
            ("Qual destes animais põe ovos?", "opcao", "Escolha:", (["Galinha", "Cachorro", "Gato"], "Galinha"), "ANIMAIS 8–9 ANOS\nEscreva uma frase sobre a galinha."),
            ("Qual destes animais respira por brânquias?", "opcao", "Escolha:", (["Peixe", "Coelho", "Pássaro"], "Peixe"), "ANIMAIS 8–9 ANOS\nEscreva uma frase sobre o peixe."),
        ],
        ("4–5 anos", "Atividade para colorir"): [
            ("🎨 Desenhe Luna, o coelhinho e um castelo. Acrescente 5 estrelas.", "criativa", "", None, "ATIVIDADE PARA COLORIR 4–5 ANOS\nDesenhe Luna, o coelhinho e um castelo.\nAcrescente 5 estrelas."),
            ("🎨 Desenhe uma lua grande e pinte o céu.", "criativa", "", None, "ATIVIDADE PARA COLORIR 4–5 ANOS\nDesenhe uma lua grande e pinte o céu."),
            ("🎨 Desenhe o coelhinho em um jardim com flores.", "criativa", "", None, "ATIVIDADE PARA COLORIR 4–5 ANOS\nDesenhe o coelhinho em um jardim com flores."),
        ],
        ("6–7 anos", "Atividade para colorir"): [
            ("🎨 Desenhe Luna segurando seu livro mágico.", "criativa", "", None, "ATIVIDADE PARA COLORIR 6–7 ANOS\nDesenhe Luna segurando seu livro mágico."),
            ("🎨 Desenhe o castelo com 4 torres.", "criativa", "", None, "ATIVIDADE PARA COLORIR 6–7 ANOS\nDesenhe um castelo com 4 torres."),
            ("🎨 Desenhe uma floresta com 6 estrelas mágicas.", "criativa", "", None, "ATIVIDADE PARA COLORIR 6–7 ANOS\nDesenhe uma floresta com 6 estrelas mágicas."),
        ],
        ("8–9 anos", "Atividade para colorir"): [
            ("🎨 Crie uma cena de Luna entrando no castelo.", "criativa", "", None, "ATIVIDADE PARA COLORIR 8–9 ANOS\nCrie uma cena de Luna entrando no castelo."),
            ("🎨 Desenhe um mapa da floresta encantada.", "criativa", "", None, "ATIVIDADE PARA COLORIR 8–9 ANOS\nDesenhe um mapa da floresta encantada."),
            ("🎨 Desenhe uma nova sala mágica do castelo.", "criativa", "", None, "ATIVIDADE PARA COLORIR 8–9 ANOS\nDesenhe uma nova sala mágica do castelo."),
        ],
    }

    def criar_fase_extra(idade_atual, materia_atual, fase):
        # Fases 2 e 3 sempre trazem exercícios novos.
        if materia_atual == "Alfabetização":
            if idade_atual == "4–5 anos":
                palavras = {
                    2: [("S _ L", "O", "SOL"), ("P _ T O", "A", "PATO"), ("M _ S A", "E", "MESA")],
                    3: [("L _ A", "U", "LUA"), ("C _ S A", "A", "CASA"), ("F L _ R", "O", "FLOR")],
                }[fase]
                return [
                    (f"Complete a palavra: **{lacuna}**", "texto", "Digite a letra que falta:", letra,
                     f"ALFABETIZAÇÃO {idade_atual}\nComplete: {lacuna}\nEscreva {palavra}.")
                    for lacuna, letra, palavra in palavras
                ]
            elif idade_atual == "6–7 anos":
                palavras = {
                    2: [("E S T R _ L A", "E", "ESTRELA"), ("P R I N C _ S A", "E", "PRINCESA"), ("J A R D _ M", "I", "JARDIM")],
                    3: [("M _ G I A", "A", "MAGIA"), ("C R I S T _ L", "A", "CRISTAL"), ("A V E N T U R _", "A", "AVENTURA")],
                }[fase]
                return [
                    (f"Complete a palavra: **{lacuna}**", "texto", "Digite a letra que falta:", letra,
                     f"ALFABETIZAÇÃO {idade_atual}\nComplete: {lacuna}\nEscreva {palavra}.")
                    for lacuna, letra, palavra in palavras
                ]
            else:
                grupos = {
                    2: [("mapa", "chave", "torre"), ("jardim", "coelhinho", "lua"), ("castelo", "porta", "mistério")],
                    3: [("aventura", "amizade", "coragem"), ("floresta", "segredo", "estrela"), ("princesa", "livro", "portal")],
                }[fase]
                return [
                    (f"Escreva uma frase usando **{a}**, **{b}** e **{d}**.", "frase", "Sua frase:", 6 if fase == 2 else 7,
                     f"ALFABETIZAÇÃO {idade_atual}\nEscreva uma frase usando: {a}, {b} e {d}.")
                    for a, b, d in grupos
                ]

        if materia_atual == "Leitura":
            banco = {
                ("4–5 anos", 2): [
                    ("Luna encontrou uma flor roxa.", "O que Luna encontrou?", "flor"),
                    ("O coelhinho dormiu perto da árvore.", "Quem dormiu?", "coelh"),
                    ("A estrela estava no céu.", "Onde estava a estrela?", "céu"),
                ],
                ("4–5 anos", 3): [
                    ("Luna abriu uma porta azul.", "Qual era a cor da porta?", "azul"),
                    ("A princesa segurava um livro.", "O que a princesa segurava?", "livro"),
                    ("O coelho comeu uma cenoura.", "O que o coelho comeu?", "cenoura"),
                ],
                ("6–7 anos", 2): [
                    ("Luna seguiu pegadas brilhantes até o jardim.", "Até onde Luna seguiu as pegadas?", "jardim"),
                    ("A princesa abriu a janela para ver a lua.", "O que a princesa abriu?", "janela"),
                    ("O coelhinho encontrou uma chave atrás do livro.", "O que ele encontrou?", "chave"),
                ],
                ("6–7 anos", 3): [
                    ("Luna encontrou um cristal perto da torre.", "Onde estava o cristal?", "torre"),
                    ("Uma ponte ligava a floresta ao castelo.", "O que a ponte ligava ao castelo?", "floresta"),
                    ("A princesa entregou um mapa ao coelhinho.", "O que a princesa entregou?", "mapa"),
                ],
                ("8–9 anos", 2): [
                    ("Luna ouviu um sino vindo da torre e decidiu investigar.", "De onde vinha o sino?", "torre"),
                    ("O mapa indicava uma passagem escondida atrás da biblioteca.", "Onde ficava a passagem?", "biblioteca"),
                    ("O coelhinho encontrou um cristal azul no jardim.", "Qual era a cor do cristal?", "azul"),
                ],
                ("8–9 anos", 3): [
                    ("As estrelas formavam uma seta apontando para a ponte.", "O que as estrelas formavam?", "seta"),
                    ("A chave dourada abria apenas uma porta secreta.", "Que tipo de porta a chave abria?", "secreta"),
                    ("Luna e o coelhinho atravessaram a ponte antes da chuva.", "O que eles atravessaram?", "ponte"),
                ],
            }
            return [
                (texto, "leitura", pergunta, resposta,
                 f"LEITURA {idade_atual}\n{texto}\nPergunta: {pergunta}")
                for texto, pergunta, resposta in banco[(idade_atual, fase)]
            ]

        if materia_atual == "Matemática":
            banco = {
                ("4–5 anos", 2): [("🍎 🍎 + 🍎 = ?", 3), ("⭐ ⭐ ⭐ + ⭐ = ?", 4), ("🐰 🐰 🐰 - 🐰 = ?", 2)],
                ("4–5 anos", 3): [("🌙 🌙 + 🌙 🌙 = ?", 4), ("⭐ ⭐ ⭐ ⭐ ⭐ - ⭐ ⭐ = ?", 3), ("🐰 + 🐰 + 🐰 = ?", 3)],
                ("6–7 anos", 2): [("8 + 5 = ?", 13), ("15 - 6 = ?", 9), ("4 grupos de 3 estrelas = ?", 12)],
                ("6–7 anos", 3): [("18 dividido por 3 = ?", 6), ("9 + 8 = ?", 17), ("20 - 7 = ?", 13)],
                ("8–9 anos", 2): [("6 × 7 = ?", 42), ("48 dividido por 6 = ?", 8), ("35 + 27 = ?", 62)],
                ("8–9 anos", 3): [("72 dividido por 8 = ?", 9), ("9 × 6 = ?", 54), ("100 - 38 = ?", 62)],
            }
            return [
                (pergunta, "numero", "Sua resposta:", resposta,
                 f"MATEMÁTICA {idade_atual}\n{pergunta}")
                for pergunta, resposta in banco[(idade_atual, fase)]
            ]

        if materia_atual == "Cores e formas":
            banco = {
                2: [
                    ("Qual forma não tem lados?", ["Círculo", "Quadrado", "Triângulo"], "Círculo"),
                    ("Misturar azul e amarelo forma qual cor?", ["Verde", "Roxo", "Laranja"], "Verde"),
                    ("Qual forma tem 5 lados?", ["Pentágono", "Triângulo", "Quadrado"], "Pentágono"),
                ],
                3: [
                    ("Qual forma tem 6 lados?", ["Hexágono", "Pentágono", "Quadrado"], "Hexágono"),
                    ("Misturar vermelho e azul forma qual cor?", ["Roxo", "Verde", "Laranja"], "Roxo"),
                    ("Qual forma tem 8 lados?", ["Octógono", "Hexágono", "Triângulo"], "Octógono"),
                ],
            }
            return [
                (pergunta, "opcao", "Escolha:", (opcoes, correta),
                 f"CORES E FORMAS {idade_atual}\n{pergunta}")
                for pergunta, opcoes, correta in banco[fase]
            ]

        if materia_atual == "Animais":
            banco = {
                2: [
                    ("Qual animal vive na água?", ["Peixe", "Coelho", "Gato"], "Peixe"),
                    ("Qual animal tem penas?", ["Pássaro", "Cachorro", "Coelho"], "Pássaro"),
                    ("Qual animal põe ovos?", ["Galinha", "Cachorro", "Gato"], "Galinha"),
                ],
                3: [
                    ("Qual animal tem casco?", ["Tartaruga", "Gato", "Coelho"], "Tartaruga"),
                    ("Qual animal respira por brânquias?", ["Peixe", "Cachorro", "Pássaro"], "Peixe"),
                    ("Qual animal passa por metamorfose?", ["Borboleta", "Gato", "Coelho"], "Borboleta"),
                ],
            }
            return [
                (pergunta, "opcao", "Escolha:", (opcoes, correta),
                 f"ANIMAIS {idade_atual}\n{pergunta}")
                for pergunta, opcoes, correta in banco[fase]
            ]

        # Atividade para colorir
        temas = {
            2: [
                "Desenhe uma ponte entre a floresta e o castelo.",
                "Desenhe Luna seguindo pegadas mágicas.",
                "Desenhe a princesa na janela da torre.",
            ],
            3: [
                "Desenhe um mapa com três caminhos.",
                "Desenhe um jardim secreto do castelo.",
                "Desenhe Luna e o coelhinho sob um céu estrelado.",
            ],
        }
        return [
            (f"🎨 {tema}", "criativa", "", None,
             f"ATIVIDADE PARA COLORIR {idade_atual}\n{tema}")
            for tema in temas[fase]
        ]

    def criar_fase_avancada(idade_atual, materia_atual, fase):
        """Cria as fases 4 e 5 com atividades novas e um pouco mais difíceis."""
        if materia_atual == "Alfabetização":
            if idade_atual == "4–5 anos":
                banco = {
                    4: [("R _ T O", "A", "RATO"), ("B _ C A", "O", "BOCA"), ("D _ D O", "E", "DEDO")],
                    5: [("S _ P O", "A", "SAPO"), ("M _ L A", "A", "MALA"), ("V _ L A", "E", "VELA")],
                }
                return [
                    (f"Complete a palavra: **{lacuna}**", "texto", "Digite a letra que falta:", letra,
                     f"ALFABETIZAÇÃO {idade_atual}\nComplete: {lacuna}\nEscreva {palavra}.")
                    for lacuna, letra, palavra in banco[fase]
                ]
            elif idade_atual == "6–7 anos":
                banco = {
                    4: [("B O R B O L _ T A", "E", "BORBOLETA"), ("C A M I N H _", "O", "CAMINHO"), ("J A N _ L A", "E", "JANELA")],
                    5: [("E N C A N T A D _", "O", "ENCANTADO"), ("A M I Z A D _", "E", "AMIZADE"), ("M I S T É R I _", "O", "MISTÉRIO")],
                }
                return [
                    (f"Complete a palavra: **{lacuna}**", "texto", "Digite a letra que falta:", letra,
                     f"ALFABETIZAÇÃO {idade_atual}\nComplete: {lacuna}\nEscreva {palavra}.")
                    for lacuna, letra, palavra in banco[fase]
                ]
            else:
                grupos = {
                    4: [("portal", "segredo", "coragem"), ("torre", "mistério", "mapa"), ("floresta", "amizade", "aventura")],
                    5: [("cristal", "escolha", "caminho"), ("princesa", "desafio", "coragem"), ("livro", "portal", "descoberta")],
                }
                return [
                    (f"Escreva uma frase usando **{a}**, **{b}** e **{d}**.", "frase", "Sua frase:", 8 if fase == 4 else 9,
                     f"ALFABETIZAÇÃO {idade_atual}\nEscreva uma frase usando: {a}, {b} e {d}.")
                    for a, b, d in grupos[fase]
                ]

        if materia_atual == "Leitura":
            bancos = {
                ("4–5 anos", 4): [
                    ("Luna achou uma estrela perto da porta.", "O que Luna achou?", "estrela"),
                    ("O coelhinho pulou sobre uma pedra.", "Sobre o que ele pulou?", "pedra"),
                    ("A princesa abriu uma caixa roxa.", "Qual era a cor da caixa?", "roxa"),
                ],
                ("4–5 anos", 5): [
                    ("Luna levou o livro até o castelo.", "O que Luna levou?", "livro"),
                    ("O coelhinho viu uma borboleta amarela.", "O que ele viu?", "borboleta"),
                    ("A lua apareceu atrás da torre.", "Onde a lua apareceu?", "torre"),
                ],
                ("6–7 anos", 4): [
                    ("Luna encontrou uma mensagem escondida dentro do livro.", "Onde estava a mensagem?", "livro"),
                    ("O coelhinho ouviu um sino perto da ponte.", "O que ele ouviu?", "sino"),
                    ("A princesa guardou a chave em uma caixa dourada.", "Onde ela guardou a chave?", "caixa"),
                ],
                ("6–7 anos", 5): [
                    ("Luna atravessou a ponte para chegar à torre.", "Para onde Luna queria chegar?", "torre"),
                    ("O mapa mostrava um caminho secreto pela floresta.", "O que o mapa mostrava?", "caminho"),
                    ("O coelhinho encontrou uma flor azul perto do lago.", "Qual era a cor da flor?", "azul"),
                ],
                ("8–9 anos", 4): [
                    ("Luna percebeu que as pegadas desapareciam perto de uma porta antiga.", "Onde as pegadas desapareciam?", "porta"),
                    ("A princesa explicou que o mapa só funcionava à luz da lua.", "Quando o mapa funcionava?", "lua"),
                    ("O coelhinho encontrou um símbolo gravado na pedra.", "Onde estava o símbolo?", "pedra"),
                ],
                ("8–9 anos", 5): [
                    ("Ao abrir o livro, Luna descobriu uma mensagem escrita com tinta dourada.", "Como era a tinta?", "dourada"),
                    ("A torre mais alta tinha uma janela iluminada durante a noite.", "O que estava iluminado?", "janela"),
                    ("A ponte secreta só aparecia quando três estrelas brilhavam juntas.", "Quando a ponte aparecia?", "estrelas"),
                ],
            }
            return [
                (texto, "leitura", pergunta, resposta,
                 f"LEITURA {idade_atual}\n{texto}\nPergunta: {pergunta}")
                for texto, pergunta, resposta in bancos[(idade_atual, fase)]
            ]

        if materia_atual == "Matemática":
            bancos = {
                ("4–5 anos", 4): [("⭐⭐⭐ + ⭐⭐ = ?", 5), ("🐰🐰🐰🐰 - 🐰 = ?", 3), ("🌙🌙 + 🌙 = ?", 3)],
                ("4–5 anos", 5): [("🍎🍎🍎 + 🍎🍎🍎 = ?", 6), ("⭐⭐⭐⭐⭐ - ⭐⭐ = ?", 3), ("🐰🐰 + 🐰🐰🐰 = ?", 5)],
                ("6–7 anos", 4): [("14 + 7 = ?", 21), ("25 - 9 = ?", 16), ("5 grupos de 4 estrelas = ?", 20)],
                ("6–7 anos", 5): [("24 dividido por 4 = ?", 6), ("17 + 18 = ?", 35), ("30 - 12 = ?", 18)],
                ("8–9 anos", 4): [("7 × 8 = ?", 56), ("81 dividido por 9 = ?", 9), ("46 + 37 = ?", 83)],
                ("8–9 anos", 5): [("96 dividido por 8 = ?", 12), ("12 × 7 = ?", 84), ("150 - 67 = ?", 83)],
            }
            return [
                (pergunta, "numero", "Sua resposta:", resposta,
                 f"MATEMÁTICA {idade_atual}\n{pergunta}")
                for pergunta, resposta in bancos[(idade_atual, fase)]
            ]

        if materia_atual == "Cores e formas":
            bancos = {
                4: [
                    ("Qual forma tem 7 lados?", ["Heptágono", "Pentágono", "Quadrado"], "Heptágono"),
                    ("Misturar vermelho e amarelo forma qual cor?", ["Laranja", "Roxo", "Verde"], "Laranja"),
                    ("Qual destas figuras tem 4 lados iguais?", ["Quadrado", "Retângulo", "Triângulo"], "Quadrado"),
                ],
                5: [
                    ("Qual forma tem 10 lados?", ["Decágono", "Octógono", "Hexágono"], "Decágono"),
                    ("Qual é uma cor secundária?", ["Roxo", "Azul", "Amarelo"], "Roxo"),
                    ("Qual forma tem todos os lados curvos?", ["Círculo", "Quadrado", "Triângulo"], "Círculo"),
                ],
            }
            return [
                (pergunta, "opcao", "Escolha:", (opcoes, correta),
                 f"CORES E FORMAS {idade_atual}\n{pergunta}")
                for pergunta, opcoes, correta in bancos[fase]
            ]

        if materia_atual == "Animais":
            bancos = {
                4: [
                    ("Qual destes animais é um inseto?", ["Borboleta", "Coelho", "Peixe"], "Borboleta"),
                    ("Qual animal é conhecido por ter tromba?", ["Elefante", "Gato", "Galinha"], "Elefante"),
                    ("Qual destes vive em uma colmeia?", ["Abelha", "Cachorro", "Peixe"], "Abelha"),
                ],
                5: [
                    ("Qual destes animais é um réptil?", ["Cobra", "Coelho", "Pássaro"], "Cobra"),
                    ("Qual animal muda de cor para se camuflar?", ["Camaleão", "Vaca", "Galinha"], "Camaleão"),
                    ("Qual destes é um animal marinho?", ["Golfinho", "Coelho", "Gato"], "Golfinho"),
                ],
            }
            return [
                (pergunta, "opcao", "Escolha:", (opcoes, correta),
                 f"ANIMAIS {idade_atual}\n{pergunta}")
                for pergunta, opcoes, correta in bancos[fase]
            ]

        temas = {
            4: [
                "Desenhe um castelo visto à noite com estrelas no céu.",
                "Crie um jardim mágico com flores e borboletas.",
                "Desenhe Luna e o coelhinho encontrando uma chave dourada.",
            ],
            5: [
                "Crie uma nova aventura de Luna em uma floresta encantada.",
                "Desenhe um portal mágico e o mundo que existe do outro lado.",
                "Crie uma capa para uma nova história do Mundo da Luna.",
            ],
        }
        return [
            (f"🎨 {tema}", "criativa", "", None,
             f"ATIVIDADE PARA COLORIR {idade_atual}\n{tema}")
            for tema in temas[fase]
        ]

    fase1 = bancos_atividades[(idade, materia)]
    fase2 = criar_fase_extra(idade, materia, 2)
    fase3 = criar_fase_extra(idade, materia, 3)
    fase4 = criar_fase_avancada(idade, materia, 4)
    fase5 = criar_fase_avancada(idade, materia, 5)
    fases_atividades = [fase1, fase2, fase3, fase4, fase5]

    if fase_atividade >= len(fases_atividades):
        st.progress(1.0, text="Todas as fases concluídas!", width="stretch")
        st.success("🏆 Parabéns! Você terminou todas as fases desta matéria!")
        st.balloons()

        if st.button(
            "🔄 Fazer todas as fases novamente",
            key=f"reiniciar_atividades_total_{idade}_{materia}",
            width="stretch",
        ):
            st.session_state["atividade_fase"] = 0
            st.session_state["atividade_etapa"] = 0
            st.rerun()
    else:
        atividades = fases_atividades[fase_atividade]
        dificuldade = [
            "🌱 Fácil",
            "⭐ Intermediária",
            "🔥 Desafio",
            "💎 Avançada",
            "👑 Mestre",
        ][fase_atividade]
        st.markdown(
            f"### 📚 Fase {fase_atividade + 1} de {len(fases_atividades)} · {dificuldade}"
        )

        if etapa_atividade >= len(atividades):
            st.progress(
                1.0,
                text=f"Fase {fase_atividade + 1} concluída!",
                width="stretch",
            )
            st.success(f"🎉 Você concluiu a Fase {fase_atividade + 1}!")
            st.balloons()

            if fase_atividade + 1 < len(fases_atividades):
                st.markdown(
                    f"<div class='fase-desbloqueada'>🔓 Fase {fase_atividade + 2} desbloqueada!</div>",
                    unsafe_allow_html=True,
                )

            if st.button(
                "➡️ Ir para a próxima fase",
                key=f"proxima_fase_atividade_{idade}_{materia}_{fase_atividade}",
                width="stretch",
            ):
                st.session_state["atividade_fase"] = fase_atividade + 1
                st.session_state["atividade_etapa"] = 0
                st.rerun()
        else:
            enunciado, tipo, rotulo, esperado, atividade_baixar = atividades[etapa_atividade]

            st.markdown("### ✏️ Atividade do dia")
            st.progress(
                etapa_atividade / len(atividades),
                text=f"Fase {fase_atividade + 1} · Atividade {etapa_atividade + 1} de {len(atividades)}",
                width="stretch",
            )
            st.write(enunciado)

            resposta_correta = None

            if tipo == "texto":
                resposta = st.text_input(
                    rotulo,
                    key=f"resp_atividade_{idade}_{materia}_{fase_atividade}_{etapa_atividade}",
                ).strip().upper()
                resposta_correta = resposta == str(esperado).upper()

            elif tipo == "frase":
                resposta = st.text_area(
                    rotulo,
                    key=f"resp_atividade_{idade}_{materia}_{fase_atividade}_{etapa_atividade}",
                )
                resposta_correta = len(resposta.strip().split()) >= int(esperado)

            elif tipo == "leitura":
                st.info(enunciado)
                st.write(f"**Pergunta:** {rotulo}")
                resposta = st.text_input(
                    "Resposta:",
                    key=f"resp_atividade_{idade}_{materia}_{fase_atividade}_{etapa_atividade}",
                )
                resposta_correta = str(esperado).lower() in resposta.lower()

            elif tipo == "numero":
                resposta = st.number_input(
                    rotulo,
                    min_value=0,
                    max_value=500,
                    step=1,
                    key=f"resp_atividade_{idade}_{materia}_{fase_atividade}_{etapa_atividade}",
                )
                resposta_correta = int(resposta) == int(esperado)

            elif tipo == "opcao":
                opcoes, correta = esperado
                resposta = st.radio(
                    rotulo,
                    opcoes,
                    key=f"resp_atividade_{idade}_{materia}_{fase_atividade}_{etapa_atividade}",
                )
                resposta_correta = resposta == correta

            if tipo != "criativa":
                if st.button(
                    "✅ Conferir atividade",
                    key=f"conferir_atividade_{idade}_{materia}_{fase_atividade}_{etapa_atividade}",
                    width="stretch",
                ):
                    if resposta_correta:
                        st.success("🎉 Muito bem! Resposta correta!")
                        st.balloons()
                        time.sleep(1.0)
                        st.session_state["atividade_etapa"] = etapa_atividade + 1
                        st.rerun()
                    else:
                        st.warning("💜 Quase! Tente novamente.")
            else:
                if st.button(
                    "✅ Terminei esta atividade",
                    key=f"terminar_atividade_{idade}_{materia}_{fase_atividade}_{etapa_atividade}",
                    width="stretch",
                ):
                    st.success("🎨 Muito bem! Vamos para a próxima atividade.")
                    st.balloons()
                    time.sleep(0.8)
                    st.session_state["atividade_etapa"] = etapa_atividade + 1
                    st.rerun()

            nome_arquivo_base = (
                f"atividade_{materia.lower().replace(' ', '_')}_"
                f"{idade.replace('–','-')}_fase{fase_atividade + 1}_"
                f"{etapa_atividade + 1}"
            )

            try:
                pdf_atividade = criar_pdf_atividade(
                    idade,
                    materia,
                    atividade_baixar,
                )

                st.caption("💜 PDF colorido com cabeçalho, espaço para responder e botão para voltar ao site.")
                st.download_button(
                    label="Baixar folha em PDF",
                    icon="📄",
                    data=pdf_atividade,
                    file_name=f"{nome_arquivo_base}_folha_colorida.pdf",
                    mime="application/pdf",
                    width="stretch",
                    key=f"baixar_pdf_atividade_{idade}_{materia}_{fase_atividade}_{etapa_atividade}",
                )
            except Exception as e:
                st.warning(
                    "Não consegui preparar o PDF agora. "
                    "O arquivo de texto continua disponível abaixo."
                )
                with st.expander("Ver detalhe do PDF"):
                    st.code(str(e))

            with st.expander("Opcional: baixar somente o texto da atividade"):
                st.download_button(
                    label="Baixar atividade em texto",
                    icon="⬇️",
                    data=atividade_baixar.encode("utf-8"),
                    file_name=f"{nome_arquivo_base}.txt",
                    mime="text/plain",
                    width="stretch",
                    key=f"baixar_txt_atividade_{idade}_{materia}_{fase_atividade}_{etapa_atividade}",
                )

            st.caption(
                "PDF em folha A4, pronto para imprimir ou salvar no celular."
            )


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
        st.markdown("### 💳 Assinaturas")
        st.caption(
            "Depois de conferir o pagamento na Kiwify, "
            "libere ou retire o Premium por aqui."
        )

        col_email, col_plano, col_status = st.columns([2.2, 1, 1], gap="small")

        with col_email:
            email_assinante = st.text_input(
                "E-mail do assinante",
                key="admin_email_assinante",
                placeholder="cliente@exemplo.com"
            )

        with col_plano:
            plano_admin = st.selectbox(
                "Plano",
                ["Grátis", "Premium"],
                key="admin_plano_assinante"
            )

        with col_status:
            status_admin = st.selectbox(
                "Status",
                ["ativo", "inativo"],
                key="admin_status_assinante"
            )

        if st.button(
            "💾 Salvar assinatura",
            key="admin_salvar_assinatura",
            width="content",
        ):
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
        st.markdown("### 💎 Créditos de vídeo")
        st.caption(
            "Adicione créditos depois de conferir uma compra na Kiwify."
        )

        col_email_cred, col_qtd_cred = st.columns([2.8, 1], gap="small")

        with col_email_cred:
            email_creditos = st.text_input(
                "E-mail do cliente para créditos",
                key="admin_email_creditos",
                placeholder="cliente@exemplo.com",
            )

        with col_qtd_cred:
            qtd_creditos = st.selectbox(
                "Quantidade",
                [1, 5, 15, 30],
                index=1,
                key="admin_qtd_creditos",
            )

        if st.button(
            "💎 Adicionar créditos",
            key="admin_adicionar_creditos",
            width="content",
        ):
            if not email_creditos.strip():
                st.warning("Digite o e-mail do cliente.")
            else:
                try:
                    adicionar_creditos_admin(email_creditos, qtd_creditos)
                    st.success(f"✅ {qtd_creditos} crédito(s) adicionados!")
                except Exception as e:
                    st.error(f"Não consegui adicionar os créditos: {e}")

        st.markdown("---")
        st.markdown("### 🎞️ Gerenciar vídeos")

        if not videos:
            st.info("Não há vídeos cadastrados.")
        else:
            for inicio in range(0, len(videos), 3):
                grupo = videos[inicio:inicio + 3]
                cols_videos = st.columns(3, gap="small")

                for deslocamento, item in enumerate(grupo):
                    with cols_videos[deslocamento]:
                        acesso_item = "💎 Premium" if video_premium(item) else "🌙 Grátis"
                        st.markdown(
                            f"""
                            <div class="admin-video-card">
                                <div class="admin-video-title">{item.get('nome', 'Sem título')}</div>
                                <div class="admin-video-meta">{categoria_base(item)} · {acesso_item}</div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                        if st.button(
                            "🗑️ Excluir",
                            key=f"excluir_{item['id']}",
                            width="stretch",
                        ):
                            excluir_video(item)
