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


/* Jogo da memória */
[class*="st-key-memoria_carta_"] button {
    min-height: 72px !important;
    font-size: 2rem !important;
    border-radius: 16px !important;
    border: 2px solid #8b5cf6 !important;
    font-weight: 800 !important;
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
        min-height: 64px !important;
        padding: 0.35rem 0.25rem !important;
        font-size: 1.75rem !important;
        border-radius: 14px !important;
    }

    [class*="st-key-memoria_carta_"] + div[data-testid="stCaptionContainer"] {
        text-align: center !important;
    }
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
            st.image(item["capa_url"], use_container_width=True)

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
        st.video(item["video_url"])


def mostrar_card_horizontal(item, contexto, novo=False):
    """Card compacto para fileiras horizontais da Área Premium."""
    if item.get("capa_url"):
        st.image(item["capa_url"], width=170)
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


def mostrar_fileira_premium(titulo, itens, contexto, limite=12, marcar_novo=False):
    """Fileira horizontal com cards realmente pequenos (190 px)."""
    itens = list(itens)[:limite]
    if not itens:
        return

    st.markdown(
        f'<div class="secao-titulo-compacto">{titulo}</div>',
        unsafe_allow_html=True,
    )

    try:
        # Streamlit atual: cada card recebe largura fixa de 190 px.
        # A fileira não quebra e pode ser deslizada horizontalmente no celular.
        fileira = st.container(horizontal=True, wrap=False, gap="xsmall")
        for i, item in enumerate(itens):
            card = fileira.container(width=190, border=False)
            with card:
                mostrar_card_horizontal(item, f"{contexto}_{i}", novo=marcar_novo)
    except TypeError:
        # Compatibilidade com versões antigas do Streamlit.
        cols = st.columns(max(len(itens), 3), gap="xsmall", wrap=False)
        for i, (col, item) in enumerate(zip(cols, itens)):
            with col:
                mostrar_card_horizontal(item, f"{contexto}_{i}", novo=marcar_novo)


def mostrar_card_catalogo(item, contexto, novo=False):
    """Card compacto para fileiras horizontais da tela inicial."""
    if item.get("capa_url"):
        st.image(item["capa_url"], width=170)
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


def mostrar_fileira_catalogo(titulo, itens, contexto, limite=12, marcar_novo=False):
    """Fileira horizontal da tela inicial com cards de 190 px."""
    itens = list(itens)[:limite]
    if not itens:
        return

    st.markdown(
        f'<div class="secao-titulo-compacto">{titulo}</div>',
        unsafe_allow_html=True,
    )

    try:
        fileira = st.container(horizontal=True, wrap=False, gap="xsmall")
        for i, item in enumerate(itens):
            card = fileira.container(width=190, border=False)
            with card:
                mostrar_card_catalogo(item, f"{contexto}_{i}", novo=marcar_novo)
    except TypeError:
        cols = st.columns(max(len(itens), 3), gap="xsmall", wrap=False)
        for i, (col, item) in enumerate(zip(cols, itens)):
            with col:
                mostrar_card_catalogo(item, f"{contexto}_{i}", novo=marcar_novo)


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

# Aplica navegação pendente ANTES de criar o st.radio.
if "_menu_destino" in st.session_state:
    st.session_state["menu_principal"] = st.session_state.pop("_menu_destino")

menu = st.sidebar.radio(
    "Menu",
    [
        "🏠 Início",
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
            use_container_width=True,
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
                use_container_width=True,
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
                use_container_width=True,
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

elif menu == "🕒 Recentes":
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
        st.warning(
            "Entre na sua conta para acessar a Área Premium."
        )

        st.button(
            "👤 Entrar / Criar conta",
            key="premium_ir_login",
            on_click=mudar_menu,
            args=("👤 Entrar / Minha conta",),
            use_container_width=True,
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
            use_container_width=True,
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

            render_html(
                f"""
                <div class="premium-stats">
                    <div class="premium-stat">
                        <div class="premium-stat-num">{total_premium}</div>
                        <div class="premium-stat-label">💎 Exclusivos</div>
                    </div>

                    <div class="premium-stat">
                        <div class="premium-stat-num">{len(infantil_premium)}</div>
                        <div class="premium-stat-label">🧸 Infantil</div>
                    </div>

                    <div class="premium-stat">
                        <div class="premium-stat-num">{len(filmes_premium)}</div>
                        <div class="premium-stat-label">🎬 Filmes</div>
                    </div>

                    <div class="premium-stat">
                        <div class="premium-stat-num">{len(series_premium)}</div>
                        <div class="premium-stat-label">📺 Séries</div>
                    </div>
                </div>
                """
            )

            st.markdown(
                '<div class="dica-deslize">'
                'Deslize para o lado para ver mais vídeos. 💜'
                '</div>',
                unsafe_allow_html=True,
            )

            # Último vídeo Premium assistido
            ultimo_premium = ultimo_assistido(exclusivos)

            if ultimo_premium:
                mostrar_fileira_premium(
                    "▶ Continuar assistindo",
                    [ultimo_premium],
                    "premium_continuar",
                    limite=1,
                )

            # Favoritos Premium
            favoritos_premium = [
                v for v in exclusivos
                if bool(v.get("favorito", False))
            ]

            if favoritos_premium:
                mostrar_fileira_premium(
                    "❤️ Minha Lista Premium",
                    favoritos_premium,
                    "premium_favoritos",
                    limite=12,
                )

            # Novidades Premium
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

        video = st.file_uploader(
            "Escolha um vídeo da galeria",
            type=["mp4", "mov", "m4v"],
            key="video_upload",
            max_upload_size=500,
            help="Você pode enviar vídeos de até 500 MB."
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
            use_container_width=True,
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
            use_container_width=True,
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
                    use_container_width=True,
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
        use_container_width=True,
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
            use_container_width=True,
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
            "Encontre os pares iguais. "
            "As cartas se ajustam automaticamente ao tamanho da tela."
        )

        # Reinicia o jogo quando a faixa etária mudar.
        if st.session_state.get("memoria_faixa") != faixa:
            st.session_state["memoria_faixa"] = faixa
            for chave in [
                "memoria_cartas",
                "memoria_selecionadas",
                "memoria_pares",
                "memoria_tentativas",
                "memoria_erro_pendente",
            ]:
                st.session_state.pop(chave, None)

        quantidade_pares = {
            "4–5 anos": 3,
            "6–7 anos": 4,
            "8–9 anos": 6,
            "10–12 anos": 8,
            "13–15 anos": 10,
        }[faixa]

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

        st.info(
            f"🏆 Pares: {len(pares) // 2}/{quantidade_pares}  •  "
            f"🎯 Tentativas: {st.session_state['memoria_tentativas']}"
        )

        if faixa in ["4–5 anos", "6–7 anos"]:
            colunas_memoria = 3
        else:
            colunas_memoria = 4

        for linha in range(0, len(cartas), colunas_memoria):
            cols = st.columns(
                colunas_memoria,
                gap="small",
                wrap=True,
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
                        key=f"memoria_carta_{indice}",
                        use_container_width=True,
                        disabled=(
                            indice in pares
                            or erro_pendente
                        ),
                    )

                    if esta_aberta:
                        st.caption(carta["nome"])
                    else:
                        st.caption("Carta")

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

        if st.session_state[
            "memoria_erro_pendente"
        ]:
            st.warning(
                "💜 Essas duas cartas são diferentes. "
                "Observe bem antes de virar novamente."
            )

            if st.button(
                "🔄 Virar as cartas e continuar",
                key="memoria_continuar",
                use_container_width=True,
            ):
                st.session_state[
                    "memoria_selecionadas"
                ] = []

                st.session_state[
                    "memoria_erro_pendente"
                ] = False

                st.rerun()

        if (
            len(
                st.session_state["memoria_pares"]
            )
            == len(cartas)
        ):
            st.success(
                "🎉 Parabéns! Você encontrou "
                f"todos os {quantidade_pares} pares!"
            )
            st.balloons()

        if st.button(
            "🎲 Novo jogo da memória",
            key="memoria_novo_jogo",
            use_container_width=True,
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

        if faixa == "4–5 anos":
            st.write("Complete a palavra: **L _ N A**")
            resposta_palavra = st.radio(
                "Qual letra está faltando?",
                ["A", "U", "O"],
                key="jogo_palavra_45",
                horizontal=True,
            )
            correta_palavra = resposta_palavra == "U"
            mensagem_correta = "🎉 Muito bem! A palavra é LUNA."

        elif faixa == "6–7 anos":
            st.write("Complete a palavra: **C _ E L H O**")
            resposta_palavra = st.radio(
                "Qual letra está faltando?",
                ["A", "O", "U"],
                key="jogo_palavra_67",
                horizontal=True,
            )
            correta_palavra = resposta_palavra == "O"
            mensagem_correta = "🎉 Muito bem! A palavra é COELHO."

        elif faixa == "8–9 anos":
            st.write("Complete a frase: **Luna abriu o ____ mágico.**")
            resposta_palavra = st.radio(
                "Escolha a palavra correta:",
                ["livro", "sapato", "bolo"],
                key="jogo_palavra_89",
            )
            correta_palavra = resposta_palavra == "livro"
            mensagem_correta = "🎉 Certo! Luna abriu o livro mágico."

        elif faixa == "10–12 anos":
            st.write(
                "Qual palavra completa melhor a frase? "
                "**Luna ficou ____ ao perceber que o caminho havia mudado.**"
            )
            resposta_palavra = st.radio(
                "Escolha:",
                ["intrigada", "adormecida", "invisível"],
                key="jogo_palavra_1012",
            )
            correta_palavra = resposta_palavra == "intrigada"
            mensagem_correta = (
                "✨ Isso! 'Intrigada' combina com alguém curioso diante de um mistério."
            )

        else:
            st.write(
                "Qual alternativa apresenta um **sinônimo** de 'misterioso'?"
            )
            resposta_palavra = st.radio(
                "Escolha:",
                ["enigmático", "barulhento", "veloz"],
                key="jogo_palavra_1315",
            )
            correta_palavra = resposta_palavra == "enigmático"
            mensagem_correta = (
                "✨ Certo! 'Enigmático' é um sinônimo de 'misterioso'."
            )

        if st.button(
            "✅ Conferir palavra",
            key=f"conferir_palavra_{faixa}",
            use_container_width=True,
        ):
            if correta_palavra:
                st.success(mensagem_correta)
            else:
                st.warning("💜 Quase! Tente outra opção.")

    # =========================================================
    # NÚMEROS
    # =========================================================
    elif jogo_escolhido == "🔢 Números":
        st.markdown("### 🔢 Brincando com números")

        if faixa == "4–5 anos":
            st.write("Conte as estrelas: ⭐ ⭐ ⭐ ⭐")
            resposta_correta_num = 4
            maximo_num = 10

        elif faixa == "6–7 anos":
            st.write(
                "🐰 O coelhinho encontrou **3 cenouras** e depois mais **2**. "
                "Quantas cenouras ele tem?"
            )
            resposta_correta_num = 5
            maximo_num = 20

        elif faixa == "8–9 anos":
            st.write(
                "🏰 No castelo havia **12 estrelas**. **5 apagaram**. "
                "Quantas ficaram acesas?"
            )
            resposta_correta_num = 7
            maximo_num = 30

        elif faixa == "10–12 anos":
            st.write(
                "🔮 Luna encontrou **6 cristais**. Cada cristal vale **4 pontos**. "
                "Quantos pontos ela conseguiu?"
            )
            resposta_correta_num = 24
            maximo_num = 100

        else:
            st.write(
                "🧩 Um portal exige **3 chaves**, e cada chave tem **7 símbolos**. "
                "Se Luna encontrou 2 portais completos, quantos símbolos há ao todo?"
            )
            resposta_correta_num = 42
            maximo_num = 200

        resposta_numero = st.number_input(
            "Digite sua resposta:",
            min_value=0,
            max_value=maximo_num,
            step=1,
            key=f"jogo_numero_{faixa}",
        )

        if st.button(
            "⭐ Conferir resposta",
            key=f"conferir_numero_{faixa}",
            use_container_width=True,
        ):
            if int(resposta_numero) == resposta_correta_num:
                st.success("🎉 Acertou! Muito bem!")
            else:
                st.warning("💜 Quase! Pense mais um pouco.")

    # =========================================================
    # DESAFIO MÁGICO
    # =========================================================
    else:
        st.markdown("### 🌟 Desafio mágico")

        if faixa == "4–5 anos":
            st.write("🟣 Qual é a cor deste círculo?")
            resposta_desafio = st.radio(
                "Escolha:",
                ["Roxo", "Amarelo", "Verde"],
                key="desafio_45",
            )
            correta_desafio = resposta_desafio == "Roxo"
            sucesso_desafio = "✨ Isso! O círculo é roxo."

        elif faixa == "6–7 anos":
            st.write("🔺 Qual é o nome desta forma?")
            resposta_desafio = st.radio(
                "Escolha:",
                ["Triângulo", "Quadrado", "Círculo"],
                key="desafio_67",
            )
            correta_desafio = resposta_desafio == "Triângulo"
            sucesso_desafio = "✨ Certo! Essa forma é um triângulo."

        elif faixa == "8–9 anos":
            st.write("Complete a sequência mágica:")
            st.markdown("## ⭐ 🌙 ⭐ 🌙 ❓")
            resposta_desafio = st.radio(
                "O que vem depois?",
                ["⭐ Estrela", "🌙 Lua", "🐰 Coelho"],
                key="desafio_89",
            )
            correta_desafio = resposta_desafio == "⭐ Estrela"
            sucesso_desafio = (
                "✨ Muito bem! A sequência alterna estrela e lua."
            )

        elif faixa == "10–12 anos":
            st.write(
                "🧠 Qual número completa a sequência? **2, 4, 8, 16, __**"
            )
            resposta_desafio = st.radio(
                "Escolha:",
                ["20", "24", "32"],
                key="desafio_1012",
            )
            correta_desafio = resposta_desafio == "32"
            sucesso_desafio = (
                "✨ Certo! Cada número é o dobro do anterior."
            )

        else:
            st.write(
                "🧩 Se todos os portais azuis são mágicos e este portal é azul, "
                "qual conclusão é logicamente correta?"
            )
            resposta_desafio = st.radio(
                "Escolha:",
                [
                    "Este portal é mágico",
                    "Todo portal mágico é azul",
                    "Nenhum portal azul é mágico",
                ],
                key="desafio_1315",
            )
            correta_desafio = resposta_desafio == "Este portal é mágico"
            sucesso_desafio = (
                "✨ Exato! Essa conclusão segue diretamente das informações dadas."
            )

        if st.button(
            "🌟 Conferir desafio",
            key=f"conferir_desafio_{faixa}",
            use_container_width=True,
        ):
            if correta_desafio:
                st.success(sucesso_desafio)
            else:
                st.warning("💜 Quase! Observe mais uma vez.")

    st.markdown("---")
    st.caption(
        "🌙 Os jogos são educativos e não usam créditos de IA."
    )

elif menu == "📚 Atividades escolares":
    st.markdown("## 📚 Atividades escolares")
    st.caption("Atividades educativas por idade, com correção na hora e opção para baixar.")

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

    st.markdown("### ✏️ Atividade do dia")

    atividade_baixar = ""
    resposta_correta = None

    if materia == "Alfabetização":
        if idade == "4–5 anos":
            st.write("Complete a palavra: **L _ N A**")
            resposta = st.text_input("Digite a letra que falta:", key="resp_alf_45").strip().upper()
            resposta_correta = resposta == "U"
            atividade_baixar = "ALFABETIZAÇÃO 4–5 ANOS\nComplete: L _ N A\nCircule as vogais da palavra LUNA."
        elif idade == "6–7 anos":
            st.write("Complete a palavra: **C _ E L H O**")
            resposta = st.text_input("Digite a letra que falta:", key="resp_alf_67").strip().upper()
            resposta_correta = resposta == "O"
            atividade_baixar = "ALFABETIZAÇÃO 6–7 ANOS\nComplete: C _ E L H O\nSepare a palavra COELHO em sílabas."
        else:
            st.write("Escreva uma frase usando as palavras **Luna**, **livro** e **floresta**.")
            resposta = st.text_area("Sua frase:", key="resp_alf_89")
            resposta_correta = len(resposta.strip().split()) >= 5
            atividade_baixar = "ALFABETIZAÇÃO 8–9 ANOS\nEscreva uma frase usando: Luna, livro e floresta."

    elif materia == "Leitura":
        texto_leitura = (
            "Luna abriu seu livro mágico. Uma luz roxa apareceu e, de repente, "
            "ela e o coelhinho chegaram a uma floresta encantada."
        )
        st.info(texto_leitura)
        pergunta = "Onde Luna e o coelhinho chegaram?"
        st.write(f"**Pergunta:** {pergunta}")
        resposta = st.text_input("Resposta:", key=f"resp_leitura_{idade}")
        resposta_correta = "floresta" in resposta.lower()
        atividade_baixar = (
            f"LEITURA {idade}\n\n{texto_leitura}\n\n"
            f"Pergunta: {pergunta}\nResposta: ________________________"
        )

    elif materia == "Matemática":
        if idade == "4–5 anos":
            st.write("⭐ ⭐ + ⭐ = ?")
            correta = 3
        elif idade == "6–7 anos":
            st.write("🐰 Luna encontrou 4 cenouras e ganhou mais 3. Quantas cenouras ela tem?")
            correta = 7
        else:
            st.write("🏰 No castelo havia 12 estrelas. 5 apagaram. Quantas ficaram acesas?")
            correta = 7

        resposta = st.number_input(
            "Sua resposta:",
            min_value=0,
            max_value=100,
            step=1,
            key=f"resp_mat_{idade}",
        )
        resposta_correta = int(resposta) == correta
        if idade == "4–5 anos":
            atividade_baixar = (
                f"MATEMÁTICA {idade}\n"
                "Conte as estrelas: 2 estrelas + 1 estrela = ?\n"
                "Resposta: __________"
            )
        elif idade == "6–7 anos":
            atividade_baixar = (
                f"MATEMÁTICA {idade}\n"
                "Luna encontrou 4 cenouras e ganhou mais 3. "
                "Quantas cenouras ela tem?\n"
                "Resposta: __________"
            )
        else:
            atividade_baixar = (
                f"MATEMÁTICA {idade}\n"
                "No castelo havia 12 estrelas. 5 apagaram. "
                "Quantas ficaram acesas?\n"
                "Resposta: __________"
            )

    elif materia == "Cores e formas":
        st.write("🟣 Qual é a cor deste círculo?")
        resposta = st.radio(
            "Escolha:",
            ["Roxo", "Amarelo", "Verde"],
            key=f"resp_cores_{idade}",
            horizontal=True,
        )
        resposta_correta = resposta == "Roxo"
        atividade_baixar = f"CORES E FORMAS {idade}\nPinte um círculo de roxo e desenhe um quadrado amarelo."

    elif materia == "Animais":
        st.write("🐰 Qual é o animal que acompanha Luna?")
        resposta = st.radio(
            "Escolha:",
            ["Coelho", "Gato", "Cachorro"],
            key=f"resp_animais_{idade}",
            horizontal=True,
        )
        resposta_correta = resposta == "Coelho"
        atividade_baixar = f"ANIMAIS {idade}\nEscreva o nome do animal que acompanha Luna: __________________"

    else:
        st.write("🎨 Desenhe Luna, o coelhinho e um castelo. Depois pinte do seu jeito.")
        st.write("⭐ Desafio: acrescente 5 estrelas no céu.")
        atividade_baixar = (
            f"ATIVIDADE PARA COLORIR {idade}\n\n"
            "Desenhe Luna, o coelhinho e um castelo.\n"
            "Acrescente 5 estrelas no céu e pinte a cena."
        )

    if materia != "Atividade para colorir":
        if st.button(
            "✅ Conferir atividade",
            key=f"conferir_atividade_{idade}_{materia}",
            use_container_width=True,
        ):
            if resposta_correta:
                st.success("🎉 Muito bem! Resposta correta!")
            else:
                st.warning("💜 Quase! Tente novamente.")

    nome_arquivo_base = (
        f"atividade_{materia.lower().replace(' ', '_')}_"
        f"{idade.replace('–','-')}"
    )

    try:
        pdf_atividade = criar_pdf_atividade(
            idade,
            materia,
            atividade_baixar,
        )

        st.download_button(
            label="Baixar folha em PDF",
            icon="📄",
            data=pdf_atividade,
            file_name=f"{nome_arquivo_base}.pdf",
            mime="application/pdf",
            width="stretch",
            key=f"baixar_pdf_atividade_{idade}_{materia}",
        )
    except Exception as e:
        st.warning(
            "Não consegui preparar o PDF agora. "
            "O arquivo de texto continua disponível abaixo."
        )
        with st.expander("Ver detalhe do PDF"):
            st.code(str(e))

    with st.expander("Baixar versão simples em texto"):
        st.download_button(
            label="Baixar atividade em texto",
            icon="⬇️",
            data=atividade_baixar.encode("utf-8"),
            file_name=f"{nome_arquivo_base}.txt",
            mime="text/plain",
            width="stretch",
            key=f"baixar_txt_atividade_{idade}_{materia}",
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
        st.subheader("💎 Gerenciar créditos de vídeo")
        st.caption(
            "Use esta área para adicionar créditos depois de conferir uma compra na Kiwify. "
            "Quando o webhook de créditos estiver ligado, isso poderá ser automático."
        )

        email_creditos = st.text_input(
            "E-mail do cliente para créditos",
            key="admin_email_creditos",
            placeholder="cliente@exemplo.com",
        )

        qtd_creditos = st.selectbox(
            "Quantidade de créditos",
            [1, 5, 15, 30],
            index=1,
            key="admin_qtd_creditos",
        )

        if st.button(
            "💎 Adicionar créditos",
            key="admin_adicionar_creditos",
            use_container_width=True,
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
