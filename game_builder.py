from datetime import datetime, timezone
from uuid import UUID, uuid4

import streamlit as st

from game_builder_core import validate_game, game_html


BUCKET_IMAGENS = "jogos-imagens"

TIPOS_IMAGEM = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}

LIMITE_IMAGEM = 10 * 1024 * 1024


def enviar_imagens(client, usuario_id, arquivos):
    if len(arquivos) < 2:
        raise ValueError("Escolha pelo menos 2 imagens.")

    if len(arquivos) > 8:
        raise ValueError("Você pode usar no máximo 8 imagens.")

    caminhos = []

    try:
        for arquivo in arquivos:

            tipo = arquivo.type or ""

            if tipo not in TIPOS_IMAGEM:
                raise ValueError(
                    "Use somente imagens JPG, PNG ou WEBP."
                )

            dados = arquivo.getvalue()

            if len(dados) > LIMITE_IMAGEM:
                raise ValueError(
                    "Cada imagem pode ter no máximo 10 MB."
                )

            extensao = TIPOS_IMAGEM[tipo]

            nome_arquivo = (
                str(usuario_id)
                + "/"
                + uuid4().hex
                + extensao
            )

            client.storage.from_(
                BUCKET_IMAGENS
            ).upload(
                nome_arquivo,
                dados,
                {
                    "content-type": tipo,
                    "upsert": "false",
                },
            )

            caminhos.append(nome_arquivo)

        return caminhos

    except Exception:
        if caminhos:
            try:
                client.storage.from_(
                    BUCKET_IMAGENS
                ).remove(caminhos)
            except Exception:
                pass

        raise


def url_temporaria(client, caminho):
    try:
        resposta = (
            client.storage
            .from_(BUCKET_IMAGENS)
            .create_signed_url(
                caminho,
                900,
            )
        )

        if isinstance(resposta, dict):

            return (
                resposta.get("signedURL")
                or resposta.get("signedUrl")
                or resposta.get("signed_url")
            )

    except Exception:
        pass

    return None


def render_game_builder(user_id, client):

    st.subheader(
        "🎨 Faça seu próprio jogo"
    )

    st.caption(
        "Crie jogos usando palavras ou suas próprias imagens."
    )

    if not user_id:

        st.info(
            "Entre em Minha conta para criar seu jogo."
        )

        return


    usuario_id = str(
        UUID(str(user_id))
    )


    if client is None:

        st.warning(
            "Entre novamente na sua conta."
        )

        return


    try:

        resposta = (
            client
            .table("jogos_criados")
            .select(
                "id,title,kind,content,updated_at"
            )
            .eq(
                "user_id",
                usuario_id
            )
            .order(
                "updated_at",
                desc=True
            )
            .limit(100)
            .execute()
        )

        jogos = resposta.data or []

    except Exception:

        st.error(
            "Não foi possível carregar seus jogos."
        )

        return


    opcoes = ["novo"]

    for jogo in jogos:
        opcoes.append(jogo["id"])


    jogos_id = {}

    for jogo in jogos:
        jogos_id[jogo["id"]] = jogo


    selecionado = st.selectbox(
        "Criar ou editar",
        opcoes,
        format_func=lambda valor:
            "➕ Novo jogo"
            if valor == "novo"
            else jogos_id[valor]["title"],
    )


    jogo_existente = jogos_id.get(
        selecionado
    )


    tipos = {
        "memory": "🧠 Jogo da Memória",
        "quiz": "❓ Perguntas e respostas",
    }


    tipo = st.selectbox(
        "Tipo de jogo",
        list(tipos.keys()),
        format_func=lambda x: tipos[x],
        index=(
            1
            if jogo_existente
            and jogo_existente["kind"]
            == "quiz"
            else 0
        ),
    )


    conteudo_antigo = {}

    if (
        jogo_existente
        and jogo_existente["kind"]
        == tipo
    ):
        conteudo_antigo = (
            jogo_existente.get(
                "content"
            )
            or {}
        )


    if tipo == "memory":

        modo_antigo = (
            conteudo_antigo.get(
                "mode",
                "text",
            )
        )


        modo = st.radio(
            "O que você quer usar nas cartas?",
            [
                "text",
                "images",
            ],
            format_func=lambda valor:
                "📝 Palavras"
                if valor == "text"
                else "🖼️ Minhas imagens",
            index=(
                1
                if modo_antigo
                == "images"
                else 0
            ),
            horizontal=True,
        )


        nome = st.text_input(
            "Nome do jogo",
            value=(
                jogo_existente["title"]
                if jogo_existente
                else ""
            ),
            placeholder="Ex: Memória da Família",
            max_chars=80,
        )


        if modo == "text":

            palavras_anteriores = (
                conteudo_antigo.get(
                    "items",
                    [
                        "Luna",
                        "Coelho",
                        "Castelo",
                    ],
                )
            )

            if (
                conteudo_antigo.get(
                    "mode"
                )
                == "images"
            ):
                palavras_anteriores = [
                    "Luna",
                    "Coelho",
                    "Castelo",
                ]


            palavras = st.text_area(
                "Escreva uma palavra por linha",
                value="\n".join(
                    palavras_anteriores
                ),
                height=180,
            )


            if st.button(
                "💾 Salvar meu jogo",
                key="salvar_memoria_palavras",
            ):

                try:

                    dados = {
                        "mode": "text",
                        "items":
                            palavras.splitlines(),
                    }


                    jogo_limpo = validate_game(
                        nome,
                        "memory",
                        dados,
                    )


                    jogo_limpo[
                        "updated_at"
                    ] = (
                        datetime.now(
                            timezone.utc
                        ).isoformat()
                    )


                    if jogo_existente:

                        resposta = (
                            client
                            .table(
                                "jogos_criados"
                            )
                            .update(
                                jogo_limpo
                            )
                            .eq(
                                "id",
                                jogo_existente[
                                    "id"
                                ],
                            )
                            .eq(
                                "user_id",
                                usuario_id,
                            )
                            .execute()
                        )

                    else:

                        jogo_limpo[
                            "user_id"
                        ] = usuario_id

                        resposta = (
                            client
                            .table(
                                "jogos_criados"
                            )
                            .insert(
                                jogo_limpo
                            )
                            .execute()
                        )


                    st.success(
                        "✅ Jogo salvo!"
                    )

                    st.markdown(
                        "### Testar jogo"
                    )

                    st.iframe(
                        game_html(
                            jogo_limpo
                        ),
                        height=600,
                    )

                except ValueError as erro:

                    st.warning(
                        str(erro)
                    )

                except Exception:

                    st.error(
                        "Não foi possível salvar o jogo."
                    )


        else:

            st.markdown(
                "### 🖼️ Escolha suas imagens"
            )

            st.write(
                "Você pode enviar de 2 até 8 imagens."
            )

            st.caption(
                "Aceitamos JPG, PNG e WEBP. "
                "Cada imagem pode ter até 10 MB."
            )


            caminhos_antigos = []

            if (
                conteudo_antigo.get(
                    "mode"
                )
                == "images"
            ):

                caminhos_antigos = (
                    conteudo_antigo.get(
                        "items",
                        [],
                    )
                )


            if caminhos_antigos:

                st.success(
                    str(
                        len(
                            caminhos_antigos
                        )
                    )
                    +
                    " imagens já estão salvas neste jogo."
                )


                urls = []

                for caminho in caminhos_antigos:

                    url = url_temporaria(
                        client,
                        caminho,
                    )

                    if url:
                        urls.append(url)


                if urls:
                    st.image(
                        urls,
                        width=140,
                    )


            arquivos = st.file_uploader(
                "Enviar minhas imagens",
                type=[
                    "jpg",
                    "jpeg",
                    "png",
                    "webp",
                ],
                accept_multiple_files=True,
            )


            if arquivos:

                st.write(
                    "Imagens escolhidas:"
                )

                st.image(
                    arquivos,
                    width=140,
                )


            if st.button(
                "💾 Salvar jogo com minhas imagens",
                key="salvar_memoria_imagens",
            ):

                novos_caminhos = []

                try:

                    if arquivos:

                        novos_caminhos = (
                            enviar_imagens(
                                client,
                                usuario_id,
                                arquivos,
                            )
                        )

                        caminhos_jogo = (
                            novos_caminhos
                        )

                    elif caminhos_antigos:

                        caminhos_jogo = (
                            caminhos_antigos
                        )

                    else:

                        raise ValueError(
                            "Escolha pelo menos 2 imagens."
                        )


                    dados = {
                        "mode": "images",
                        "items":
                            caminhos_jogo,
                    }


                    jogo_limpo = validate_game(
                        nome,
                        "memory",
                        dados,
                    )


                    jogo_limpo[
                        "updated_at"
                    ] = (
                        datetime.now(
                            timezone.utc
                        ).isoformat()
                    )


                    if jogo_existente:

                        resposta = (
                            client
                            .table(
                                "jogos_criados"
                            )
                            .update(
                                jogo_limpo
                            )
                            .eq(
                                "id",
                                jogo_existente[
                                    "id"
                                ],
                            )
                            .eq(
                                "user_id",
                                usuario_id,
                            )
                            .execute()
                        )

                    else:

                        jogo_limpo[
                            "user_id"
                        ] = usuario_id

                        resposta = (
                            client
                            .table(
                                "jogos_criados"
                            )
                            .insert(
                                jogo_limpo
                            )
                            .execute()
                        )


                    if (
                        novos_caminhos
                        and caminhos_antigos
                    ):

                        try:

                            client.storage.from_(
                                BUCKET_IMAGENS
                            ).remove(
                                caminhos_antigos
                            )

                        except Exception:
                            pass


                    st.success(
                        "✅ Jogo salvo com suas imagens!"
                    )

                    st.info(
                        "As imagens ficaram guardadas "
                        "na sua conta no Supabase."
                    )

                except ValueError as erro:

                    st.warning(
                        str(erro)
                    )

                except Exception:

                    if novos_caminhos:

                        try:

                            client.storage.from_(
                                BUCKET_IMAGENS
                            ).remove(
                                novos_caminhos
                            )

                        except Exception:
                            pass


                    st.error(
                        "Não foi possível salvar as imagens agora."
                    )


    else:

        nome = st.text_input(
            "Nome do Quiz",
            value=(
                jogo_existente["title"]
                if jogo_existente
                else ""
            ),
            max_chars=80,
        )


        perguntas_antigas = (
            conteudo_antigo.get(
                "questions",
                [],
            )
        )


        quantidade = int(
            st.number_input(
                "Quantidade de perguntas",
                min_value=1,
                max_value=20,
                value=max(
                    1,
                    len(
                        perguntas_antigas
                    ),
                ),
            )
        )


        perguntas = []


        for numero in range(
            quantidade
        ):

            antiga = (
                perguntas_antigas[
                    numero
                ]
                if numero
                < len(
                    perguntas_antigas
                )
                else {}
            )


            st.markdown(
                "### Pergunta "
                + str(
                    numero + 1
                )
            )


            pergunta = st.text_input(
                "Pergunta",
                value=antiga.get(
                    "prompt",
                    "",
                ),
                key=
                    "pergunta_"
                    + str(numero),
            )


            respostas_antigas = (
                antiga.get(
                    "options",
                    [
                        "",
                        "",
                        "",
                    ],
                )
            )


            respostas = []


            for resposta_numero in range(
                3
            ):

                valor = ""

                if (
                    resposta_numero
                    <
                    len(
                        respostas_antigas
                    )
                ):
                    valor = (
                        respostas_antigas[
                            resposta_numero
                        ]
                    )


                resposta = st.text_input(
                    "Resposta "
                    + str(
                        resposta_numero
                        + 1
                    ),
                    value=valor,
                    key=(
                        "resp_"
                        + str(numero)
                        + "_"
                        + str(
                            resposta_numero
                        )
                    ),
                )

                respostas.append(
                    resposta
                )


            correta = st.radio(
                "Qual resposta está correta?",
                [
                    0,
                    1,
                    2,
                ],
                format_func=lambda n:
                    "Resposta "
                    + str(
                        n + 1
                    ),
                key=
                    "correta_"
                    + str(numero),
            )


            perguntas.append(
                {
                    "prompt":
                        pergunta,

                    "options":
                        respostas,

                    "answer":
                        correta,
                }
            )


        if st.button(
            "💾 Salvar Quiz",
            key="salvar_quiz",
        ):

            try:

                jogo_limpo = validate_game(
                    nome,
                    "quiz",
                    {
                        "questions":
                            perguntas
                    },
                )


                jogo_limpo[
                    "updated_at"
                ] = (
                    datetime.now(
                        timezone.utc
                    ).isoformat()
                )


                if jogo_existente:

                    (
                        client
                        .table(
                            "jogos_criados"
                        )
                        .update(
                            jogo_limpo
                        )
                        .eq(
                            "id",
                            jogo_existente[
                                "id"
                            ],
                        )
                        .eq(
                            "user_id",
                            usuario_id,
                        )
                        .execute()
                    )

                else:

                    jogo_limpo[
                        "user_id"
                    ] = usuario_id

                    (
                        client
                        .table(
                            "jogos_criados"
                        )
                        .insert(
                            jogo_limpo
                        )
                        .execute()
                    )


                st.success(
                    "✅ Quiz salvo!"
                )


                st.iframe(
                    game_html(
                        jogo_limpo
                    ),
                    height=600,
                )


            except ValueError as erro:

                st.warning(
                    str(erro)
                )

            except Exception:

                st.error(
                    "Não foi possível salvar o Quiz."
                )


    st.markdown("---")

    st.info(
        "🔒 Cada cliente possui seus próprios jogos e imagens."
    )
