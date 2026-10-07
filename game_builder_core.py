"""Validation shared by the game editor and its tests; no credentials or I/O."""
import json


def validate_game(title, kind, content):
    title = str(title).strip()
    if not 1 <= len(title) <= 80:
        raise ValueError('Escreva um nome de até 80 caracteres para o jogo.')
    if kind == 'memory':
        items = [str(item).strip() for item in content.get('items', []) if str(item).strip()]
        if not 2 <= len(items) <= 12:
            raise ValueError('Use entre 2 e 12 palavras ou pares.')
        if any(len(item) > 40 for item in items):
            raise ValueError('Cada palavra ou frase pode ter até 40 caracteres.')
        if len({item.casefold() for item in items}) != len(items):
            raise ValueError('Escreva cada palavra uma vez. O jogo cria o par automaticamente.')
        clean = {'items': items}
    elif kind == 'quiz':
        questions = content.get('questions', [])
        if not 1 <= len(questions) <= 20:
            raise ValueError('O jogo precisa de 1 a 20 perguntas.')
        clean_questions = []
        for number, question in enumerate(questions, 1):
            prompt = str(question.get('prompt', '')).strip()
            options = [str(option).strip() for option in question.get('options', [])]
            answer = question.get('answer')
            if not 1 <= len(prompt) <= 300:
                raise ValueError(f'Pergunta {number}: escreva um enunciado de até 300 caracteres.')
            if not 2 <= len(options) <= 4 or any(not option or len(option) > 100 for option in options):
                raise ValueError(f'Pergunta {number}: preencha de 2 a 4 respostas, com até 100 caracteres cada.')
            if len({option.casefold() for option in options}) != len(options):
                raise ValueError(f'Pergunta {number}: as respostas precisam ser diferentes.')
            if type(answer) is not int or not 0 <= answer < len(options):
                raise ValueError(f'Pergunta {number}: escolha a resposta correta.')
            clean_questions.append({'prompt': prompt, 'options': options, 'answer': answer})
        clean = {'questions': clean_questions}
    else:
        raise ValueError('Escolha Memória ou Perguntas e respostas.')
    return {'title': title, 'kind': kind, 'content': clean}


def game_html(game):
    """Preview renders untrusted text using textContent only, in a component iframe."""
    clean = validate_game(game['title'], game['kind'], game['content'])
    data = json.dumps(clean, ensure_ascii=True).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')
    return '''<!doctype html><html lang="pt-BR"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<style>body{font:18px Arial;background:#28123f;color:#fff;padding:12px}button{font:18px Arial;background:#d7b8f5;color:#24103f;padding:16px;margin:6px;border:3px solid #b794d6;border-radius:12px}button:focus{outline:4px solid gold}#board{display:flex;flex-wrap:wrap}#status{min-height:30px;color:#ffe490}.card{width:135px;min-height:85px}</style>
<h2 id="title"></h2><p id="status" role="status"></p><div id="board"></div><button id="restart">Novo jogo</button>
<script>var game=''' + data + ''';
var board=document.getElementById('board'),statusEl=document.getElementById('status'),generation=0;
document.getElementById('title').textContent=game.title;
function button(text,fn){var b=document.createElement('button');b.type='button';b.textContent=text;b.onclick=fn;board.appendChild(b);return b;}
function start(){generation++;board.innerHTML='';statusEl.textContent='';if(game.kind==='memory'){memory();}else{quiz(0);}}
function memory(){var run=generation,deck=game.content.items.concat(game.content.items),picked=[],matched={},busy=false,hits=0,cards=[];
for(var i=deck.length-1;i>0;i--){var j=Math.floor(Math.random()*(i+1)),t=deck[i];deck[i]=deck[j];deck[j]=t;}
deck.forEach(function(word,index){var b=button('?',function(){if(busy||matched[index]||picked.indexOf(index)>=0)return;b.textContent=word;picked.push(index);if(picked.length===2){var a=picked[0],c=picked[1];if(deck[a]===deck[c]){matched[a]=matched[c]=true;picked=[];hits++;statusEl.textContent=hits===game.content.items.length?'Parabéns! Todos os pares encontrados.':'Par encontrado!';}else{busy=true;setTimeout(function(){if(run!==generation)return;cards[a].textContent=cards[c].textContent='?';picked=[];busy=false;},1000);}}});b.className='card';cards.push(b);});}
function quiz(index){board.innerHTML='';statusEl.textContent='';var q=game.content.questions[index],p=document.createElement('p'),solved=false;p.textContent=q.prompt;p.style.width='100%';board.appendChild(p);q.options.forEach(function(text,i){button(text,function(){if(solved)return;if(i!==q.answer){statusEl.textContent='Tente novamente!';return;}solved=true;statusEl.textContent='Você acertou!';button(index+1<game.content.questions.length?'Próxima pergunta':'Concluir',function(){if(index+1<game.content.questions.length){quiz(index+1);}else{board.innerHTML='';statusEl.textContent='Parabéns! Você concluiu o jogo.';}}).focus();});});}
document.getElementById('restart').onclick=start;start();</script></html>'''
