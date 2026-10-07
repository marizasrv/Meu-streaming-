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
        raise ValueError(
            "Escolha pelo menos 2 imagens."
        )

    if len(arquivos) > 8:
        raise ValueError(
            "Você pode usar no máximo 8 imagens."
        )


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


            caminhos.append(
                nome_arquivo
            )


        return caminhos


    except Exception:

        if caminhos:

            try:

                client.storage.from_(
                    BUCKET_IMAGENS
                ).remove(
                    caminhos
                )

            except Exception:
                pass


        raise



def url_temporaria(
    client,
    caminho,
):

    try:

        resposta = (
            client
            .storage
            .from_(
                BUCKET_IMAGENS
            )
            .create_signed_url(
                caminho,
                3600,
            )
        )


        if isinstance(
            resposta,
            dict
        ):

            return (
                resposta.get(
                    "signedURL"
                )
                or
                resposta.get(
                    "signedUrl"
                )
                or
                resposta.get(
                    "signed_url"
                )
            )


        try:

            return (
                resposta.signed_url
            )

        except Exception:
            pass


    except Exception:
        pass


    return None



def montar_urls_imagens(
    client,
    caminhos,
):

    urls = {}


    for caminho in caminhos:

        url = url_temporaria(
            client,
            caminho,
        )


        if url:

            urls[
                caminho
            ] = url


    return urls



def render_game_builder(
    user_id,
    client,
):

    st.subheader(
        "🎨 Faça seu próprio jogo"
    )


    st.caption(
        "Crie jogos de memória e quiz. "
        "Você também pode usar suas próprias imagens."
    )


    if not user_id:

        st.info(
            "Entre em Minha conta para criar e guardar seus jogos."
        )

        return


    usuario_id = str(
        UUID(
            str(user_id)
        )
    )


    if client is None:

        st.warning(
            "Entre novamente na sua conta para acessar seus jogos."
        )

        return


    try:

        resposta = (
            client
            .table(
                "jogos_criados"
            )
            .select(
                "id,title,kind,content,updated_at"
            )
            .eq(
                "user_id",
                usuario_id,
            )
            .order(
                "updated_at",
                desc=True,
            )
            .limit(
                100
            )
            .execute()
        )


        jogos = (
            resposta.data
            or []
        )


    except Exception:

        st.error(
            "Não foi possível carregar seus jogos. "
            "Tente novamente em instantes."
        )

        return



    opcoes = [
        "novo"
    ]


    jogos_por_id = {}


    for jogo in jogos:

        opcoes.append(
            jogo["id"]
        )

        jogos_por_id[
            jogo["id"]
        ] = jogo



    selecionado = st.selectbox(
        "Criar ou editar",
        opcoes,
        format_func=lambda valor:
            "➕ Novo jogo"
            if valor == "novo"
            else jogos_por_id[
                valor
            ]["title"],
    )


    jogo_existente = (
        jogos_por_id.get(
            selecionado
        )
    )


    tipos = {
        "memory":
            "🧠 Jogo da Memória",

        "quiz":
            "❓ Perguntas e respostas",
    }


    indice_tipo = 0


    if (
        jogo_existente
        and
        jogo_existente[
            "kind"
        ] == "quiz"
    ):

        indice_tipo = 1


    tipo = st.selectbox(
        "Tipo de jogo",
        list(
            tipos.keys()
        ),
        index=indice_tipo,
        format_func=lambda valor:
            tipos[valor],
    )


    conteudo_antigo = {}


    if (
        jogo_existente
        and
        jogo_existente[
            "kind"
        ] == tipo
    ):

        conteudo_antigo = (
            jogo_existente.get(
                "content"
            )
            or {}
        )



    # =========================================================
    # JOGO DA MEMÓRIA
    # =========================================================

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
                jogo_existente[
                    "title"
                ]
                if jogo_existente
                else ""
            ),
            placeholder=
                "Ex: Memória da Família",
            max_chars=80,
        )



        # =====================================================
        # MEMÓRIA COM PALAVRAS
        # =====================================================

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
                key=
                    "salvar_memoria_palavras",
            ):

                try:

                    dados = {
                        "mode":
                            "text",

                        "items":
                            palavras.splitlines(),
                    }


                    jogo_limpo = (
                        validate_game(
                            nome,
                            "memory",
                            dados,
                        )
                    )


                    jogo_limpo[
                        "updated_at"
                    ] = (
                        datetime.now(
                            timezone.utc
                        ).isoformat()
                    )


                    if jogo_existente:

                        resposta_salvar = (
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


                        resposta_salvar = (
                            client
                            .table(
                                "jogos_criados"
                            )
                            .insert(
                                jogo_limpo
                            )
                            .execute()
                        )


                    if not resposta_salvar.data:

                        st.error(
                            "O jogo não foi salvo."
                        )

                        return


                    st.success(
                        "✅ Jogo salvo!"
                    )


                    st.markdown(
                        "### ▶ Testar meu jogo"
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



        # =====================================================
        # MEMÓRIA COM IMAGENS
        # =====================================================

        else:

            st.markdown(
                "### 🖼️ Minhas imagens"
            )


            st.write(
                "Escolha de 2 até 8 imagens."
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



            # MOSTRAR IMAGENS JÁ SALVAS

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


                mapa_antigo = (
                    montar_urls_imagens(
                        client,
                        caminhos_antigos,
                    )
                )


                imagens_preview = []


                for caminho in caminhos_antigos:

                    url = mapa_antigo.get(
                        caminho
                    )

                    if url:

                        imagens_preview.append(
                            url
                        )


                if imagens_preview:

                    st.image(
                        imagens_preview,
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
                key=
                    "upload_imagens_jogo",
            )



            if arquivos:

                st.markdown(
                    "### Imagens escolhidas"
                )


                st.image(
                    arquivos,
                    width=140,
                )



            if st.button(
                "💾 Salvar jogo com minhas imagens",
                key=
                    "salvar_memoria_imagens",
            ):

                novos_caminhos = []


                try:

                    # Se o usuário escolheu novas imagens,
                    # fazemos novo upload.

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


                    # Caso não escolha novas imagens,
                    # preservamos as já salvas.

                    elif caminhos_antigos:

                        caminhos_jogo = (
                            caminhos_antigos
                        )


                    else:

                        raise ValueError(
                            "Escolha pelo menos 2 imagens."
                        )



                    dados = {
                        "mode":
                            "images",

                        "items":
                            caminhos_jogo,
                    }



                    jogo_limpo = (
                        validate_game(
                            nome,
                            "memory",
                            dados,
                        )
                    )


                    jogo_limpo[
                        "updated_at"
                    ] = (
                        datetime.now(
                            timezone.utc
                        ).isoformat()
                    )



                    if jogo_existente:

                        resposta_salvar = (
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


                        resposta_salvar = (
                            client
                            .table(
                                "jogos_criados"
                            )
                            .insert(
                                jogo_limpo
                            )
                            .execute()
                        )



                    if not resposta_salvar.data:

                        raise RuntimeError(
                            "Jogo não foi salvo."
                        )



                    # Depois que o jogo foi salvo,
                    # removemos imagens antigas apenas
                    # se novas imagens substituíram as anteriores.

                    if (
                        novos_caminhos
                        and
                        caminhos_antigos
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
                        "na sua conta."
                    )



                    # =========================================
                    # GERAR LINKS TEMPORÁRIOS PARA TESTAR
                    # =========================================

                    urls_jogo = (
                        montar_urls_imagens(
                            client,
                            caminhos_jogo,
                        )
                    )


                    if (
                        len(
                            urls_jogo
                        )
                        ==
                        len(
                            caminhos_jogo
                        )
                    ):

                        st.markdown(
                            "### ▶ Testar meu jogo"
                        )


                        st.iframe(
                            game_html(
                                jogo_limpo,
                                image_urls=
                                    urls_jogo,
                            ),
                            height=650,
                        )


                    else:

                        st.warning(
                            "O jogo foi salvo, mas alguma imagem "
                            "não pôde ser aberta no teste."
                        )



                except ValueError as erro:

                    st.warning(
                        str(erro)
                    )


                except Exception:

                    # Se o jogo falhar antes de salvar,
                    # removemos as novas imagens que acabaram
                    # de ser enviadas.

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



        # =====================================================
        # MOSTRAR VERSÃO SALVA
        # =====================================================

        if jogo_existente:

            st.markdown(
                "---"
            )


            st.markdown(
                "### 🎮 Versão salva"
            )


            conteudo_salvo = (
                jogo_existente.get(
                    "content"
                )
                or {}
            )


            if (
                conteudo_salvo.get(
                    "mode"
                )
                == "images"
            ):

                caminhos_salvos = (
                    conteudo_salvo.get(
                        "items",
                        [],
                    )
                )


                urls_salvas = (
                    montar_urls_imagens(
                        client,
                        caminhos_salvos,
                    )
                )


                if urls_salvas:

                    st.iframe(
                        game_html(
                            jogo_existente,
                            image_urls=
                                urls_salvas,
                        ),
                        height=650,
                    )


            else:

                st.iframe(
                    game_html(
                        jogo_existente
                    ),
                    height=600,
                )



    # =========================================================
    # QUIZ
    # =========================================================

    else:

        nome = st.text_input(
            "Nome do Quiz",
            value=(
                jogo_existente[
                    "title"
                ]
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
                <
                len(
                    perguntas_antigas
                )
                else {}
            )


            st.markdown(
                "### Pergunta "
                +
                str(
                    numero + 1
                )
            )


            pergunta = st.text_input(
                "Pergunta",
                value=
                    antiga.get(
                        "prompt",
                        "",
                    ),
                max_chars=300,
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
                    +
                    str(
                        resposta_numero
                        + 1
                    ),
                    value=valor,
                    max_chars=100,
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


            resposta_antiga = (
                antiga.get(
                    "answer",
                    0,
                )
            )


            if resposta_antiga not in [
                0,
                1,
                2,
            ]:

                resposta_antiga = 0


            correta = st.radio(
                "Qual resposta está correta?",
                [
                    0,
                    1,
                    2,
                ],
                index=
                    resposta_antiga,
                format_func=lambda n:
                    "Resposta "
                    +
                    str(
                        n + 1
                    ),
                horizontal=True,
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
            key=
                "salvar_quiz",
        ):

            try:

                jogo_limpo = (
                    validate_game(
                        nome,
                        "quiz",
                        {
                            "questions":
                                perguntas
                        },
                    )
                )


                jogo_limpo[
                    "updated_at"
                ] = (
                    datetime.now(
                        timezone.utc
                    ).isoformat()
                )


                if jogo_existente:

                    resposta_salvar = (
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


                    resposta_salvar = (
                        client
                        .table(
                            "jogos_criados"
                        )
                        .insert(
                            jogo_limpo
                        )
                        .execute()
                    )



                if not resposta_salvar.data:

                    st.error(
                        "O Quiz não foi salvo."
                    )

                    return


                st.success(
                    "✅ Quiz salvo!"
                )


                st.markdown(
                    "### ▶ Testar meu Quiz"
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



        elif jogo_existente:

            st.markdown(
                "### 🎮 Jogar a versão salva"
            )


            st.iframe(
                game_html(
                    jogo_existente
                ),
                height=600,
            )



    st.markdown(
        "---"
    )


    st.info(
        "🔒 Cada cliente vê apenas os próprios jogos e imagens."
    )
