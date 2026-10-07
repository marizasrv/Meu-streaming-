"""Validação e visualização dos jogos criados."""

import json


def validate_game(title, kind, content):

    title = str(title).strip()

    if not 1 <= len(title) <= 80:
        raise ValueError(
            "Escreva um nome de até 80 caracteres para o jogo."
        )


    # =========================================================
    # JOGO DA MEMÓRIA
    # =========================================================

    if kind == "memory":

        mode = content.get(
            "mode",
            "text",
        )


        # -----------------------------------------------------
        # MEMÓRIA COM IMAGENS
        # -----------------------------------------------------

        if mode == "images":

            items = []

            for item in content.get(
                "items",
                [],
            ):

                item = str(
                    item
                ).strip()

                if item:
                    items.append(
                        item
                    )


            if not 2 <= len(items) <= 8:

                raise ValueError(
                    "Use entre 2 e 8 imagens no jogo da memória."
                )


            if len(set(items)) != len(items):

                raise ValueError(
                    "Use imagens diferentes para formar os pares."
                )


            for item in items:

                if len(item) > 500:

                    raise ValueError(
                        "Uma das imagens não é válida."
                    )


                if ".." in item:

                    raise ValueError(
                        "Uma das imagens não é válida."
                    )


                if "/" not in item:

                    raise ValueError(
                        "Uma das imagens não é válida."
                    )


            clean = {

                "mode":
                    "images",

                "items":
                    items,

            }


        # -----------------------------------------------------
        # MEMÓRIA COM PALAVRAS
        # -----------------------------------------------------

        else:

            items = []

            for item in content.get(
                "items",
                [],
            ):

                item = str(
                    item
                ).strip()

                if item:
                    items.append(
                        item
                    )


            if not 2 <= len(items) <= 12:

                raise ValueError(
                    "Use entre 2 e 12 palavras ou pares."
                )


            for item in items:

                if len(item) > 40:

                    raise ValueError(
                        "Cada palavra ou frase pode ter até 40 caracteres."
                    )


            palavras_unicas = set()

            for item in items:

                palavras_unicas.add(
                    item.casefold()
                )


            if len(
                palavras_unicas
            ) != len(items):

                raise ValueError(
                    "Escreva cada palavra uma vez. "
                    "O jogo cria o par automaticamente."
                )


            clean = {

                "mode":
                    "text",

                "items":
                    items,

            }


    # =========================================================
    # QUIZ
    # =========================================================

    elif kind == "quiz":

        questions = content.get(
            "questions",
            [],
        )


        if not 1 <= len(questions) <= 20:

            raise ValueError(
                "O jogo precisa de 1 a 20 perguntas."
            )


        clean_questions = []


        for number, question in enumerate(
            questions,
            1,
        ):

            prompt = str(
                question.get(
                    "prompt",
                    "",
                )
            ).strip()


            options = []

            for option in question.get(
                "options",
                [],
            ):

                options.append(
                    str(
                        option
                    ).strip()
                )


            answer = question.get(
                "answer"
            )


            if not 1 <= len(prompt) <= 300:

                raise ValueError(
                    "Pergunta "
                    + str(number)
                    + ": escreva um enunciado de até 300 caracteres."
                )


            if not 2 <= len(options) <= 4:

                raise ValueError(
                    "Pergunta "
                    + str(number)
                    + ": use de 2 a 4 respostas."
                )


            for option in options:

                if not option:

                    raise ValueError(
                        "Pergunta "
                        + str(number)
                        + ": preencha todas as respostas."
                    )


                if len(option) > 100:

                    raise ValueError(
                        "Pergunta "
                        + str(number)
                        + ": cada resposta pode ter até 100 caracteres."
                    )


            respostas_unicas = set()

            for option in options:

                respostas_unicas.add(
                    option.casefold()
                )


            if len(
                respostas_unicas
            ) != len(options):

                raise ValueError(
                    "Pergunta "
                    + str(number)
                    + ": as respostas precisam ser diferentes."
                )


            if type(answer) is not int:

                raise ValueError(
                    "Pergunta "
                    + str(number)
                    + ": escolha a resposta correta."
                )


            if not 0 <= answer < len(options):

                raise ValueError(
                    "Pergunta "
                    + str(number)
                    + ": escolha a resposta correta."
                )


            clean_questions.append({

                "prompt":
                    prompt,

                "options":
                    options,

                "answer":
                    answer,

            })


        clean = {

            "questions":
                clean_questions,

        }


    else:

        raise ValueError(
            "Escolha Memória ou Perguntas e respostas."
        )


    return {

        "title":
            title,

        "kind":
            kind,

        "content":
            clean,

    }



# =============================================================
# HTML DO JOGO
# =============================================================

def game_html(
    game,
    image_urls=None,
):

    clean = validate_game(
        game["title"],
        game["kind"],
        game["content"],
    )


    payload = {

        "game":
            clean,

        "image_urls":
            image_urls or {},

    }


    data = json.dumps(
        payload,
        ensure_ascii=True,
    )


    data = data.replace(
        "<",
        "\\u003c",
    )

    data = data.replace(
        ">",
        "\\u003e",
    )

    data = data.replace(
        "&",
        "\\u0026",
    )


    html = """
<!doctype html>

<html lang="pt-BR">

<head>

<meta charset="utf-8">

<meta
name="viewport"
content="width=device-width, initial-scale=1"
>

<style>

body {

    font-family: Arial, sans-serif;

    background: #28123f;

    color: white;

    padding: 12px;

    text-align: center;

}


button {

    font-family: Arial, sans-serif;

    font-size: 18px;

    background: #d7b8f5;

    color: #24103f;

    padding: 16px;

    margin: 6px;

    border: 3px solid #b794d6;

    border-radius: 12px;

    cursor: pointer;

}


button:focus {

    outline: 4px solid gold;

}


#board {

    display: flex;

    flex-wrap: wrap;

    justify-content: center;

}


#status {

    min-height: 30px;

    color: #ffe490;

}


.card {

    width: 135px;

    min-height: 95px;

}


.card img {

    max-width: 100px;

    max-height: 70px;

    border-radius: 8px;

}

</style>

</head>


<body>


<h2 id="title"></h2>


<p
id="status"
role="status">
</p>


<div id="board"></div>


<button id="restart">

Novo jogo

</button>


<script>


var payload =
""" + data + """;


var game =
payload.game;


var urlMap =
payload.image_urls || {};


var board =
document.getElementById(
    "board"
);


var statusEl =
document.getElementById(
    "status"
);


var generation =
0;


document.getElementById(
    "title"
).textContent =
game.title;



function button(
    text,
    fn
) {

    var b =
    document.createElement(
        "button"
    );


    b.type =
    "button";


    b.textContent =
    text;


    b.onclick =
    fn;


    board.appendChild(
        b
    );


    return b;

}



function showCard(
    elemento,
    item
) {

    elemento.innerHTML =
    "";


    if (
        game.kind === "memory"
        &&
        game.content.mode
        === "images"
    ) {

        var img =
        document.createElement(
            "img"
        );


        img.alt =
        "Imagem do jogo";


        img.src =
        urlMap[item]
        || "";


        elemento.appendChild(
            img
        );

    }

    else {

        elemento.textContent =
        item;

    }

}



function start() {

    generation++;


    board.innerHTML =
    "";


    statusEl.textContent =
    "";


    if (
        game.kind
        ===
        "memory"
    ) {

        memory();

    }

    else {

        quiz(0);

    }

}



function memory() {

    var run =
    generation;


    var deck =
    game.content.items.concat(
        game.content.items
    );


    var picked =
    [];


    var matched =
    {};


    var busy =
    false;


    var hits =
    0;


    var cards =
    [];


    var i;


    for (
        i = deck.length - 1;
        i > 0;
        i--
    ) {

        var j =
        Math.floor(
            Math.random()
            *
            (i + 1)
        );


        var temp =
        deck[i];


        deck[i] =
        deck[j];


        deck[j] =
        temp;

    }


    deck.forEach(
        function(
            item,
            index
        ) {


            var b =
            button(
                "?",
                function() {


                    if (
                        busy
                        ||
                        matched[index]
                        ||
                        picked.indexOf(
                            index
                        ) >= 0
                    ) {

                        return;

                    }


                    showCard(
                        b,
                        item
                    );


                    picked.push(
                        index
                    );


                    if (
                        picked.length
                        ===
                        2
                    ) {

                        var a =
                        picked[0];


                        var c =
                        picked[1];


                        if (
                            deck[a]
                            ===
                            deck[c]
                        ) {

                            matched[a] =
                            true;


                            matched[c] =
                            true;


                            picked =
                            [];


                            hits++;


                            if (
                                hits
                                ===
                                game.content.items.length
                            ) {

                                statusEl.textContent =
                                "Parabéns! Todos os pares encontrados.";

                            }

                            else {

                                statusEl.textContent =
                                "Par encontrado!";

                            }

                        }

                        else {

                            busy =
                            true;


                            setTimeout(
                                function() {


                                    if (
                                        run
                                        !==
                                        generation
                                    ) {

                                        return;

                                    }


                                    cards[a]
                                    .innerHTML =
                                    "?";


                                    cards[c]
                                    .innerHTML =
                                    "?";


                                    picked =
                                    [];


                                    busy =
                                    false;


                                },
                                1000
                            );

                        }

                    }

                }
            );


            b.className =
            "card";


            cards.push(
                b
            );

        }
    );

}



function quiz(
    index
) {

    board.innerHTML =
    "";


    statusEl.textContent =
    "";


    var q =
    game.content.questions[
        index
    ];


    var p =
    document.createElement(
        "p"
    );


    var solved =
    false;


    p.textContent =
    q.prompt;


    p.style.width =
    "100%";


    board.appendChild(
        p
    );


    q.options.forEach(
        function(
            text,
            i
        ) {


            button(
                text,
                function() {


                    if (
                        solved
                    ) {

                        return;

                    }


                    if (
                        i
                        !==
                        q.answer
                    ) {

                        statusEl.textContent =
                        "Tente novamente!";


                        return;

                    }


                    solved =
                    true;


                    statusEl.textContent =
                    "Você acertou!";


                    var textoBotao =
                    "Concluir";


                    if (
                        index + 1
                        <
                        game.content.questions.length
                    ) {

                        textoBotao =
                        "Próxima pergunta";

                    }


                    var proximo =
                    button(
                        textoBotao,
                        function() {


                            if (
                                index + 1
                                <
                                game.content.questions.length
                            ) {

                                quiz(
                                    index + 1
                                );

                            }

                            else {

                                board.innerHTML =
                                "";


                                statusEl.textContent =
                                "Parabéns! Você concluiu o jogo.";

                            }

                        }
                    );


                    proximo.focus();

                }
            );

        }
    );

}



document.getElementById(
    "restart"
).onclick =
start;


start();


</script>


</body>

</html>
"""


    return html
