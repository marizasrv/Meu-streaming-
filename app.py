<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Assistente Criador - Mundo da Luna</title>
<style>
*{box-sizing:border-box}html,body{margin:0;min-height:100%;font-family:Arial,sans-serif;background:#27103f;color:#fff}body{padding:18px 28px 36px}h1{color:#ffdf91;margin:12px 0;font-size:34px}h2{font-size:24px}p{line-height:1.4}.sub{color:#e8c7ff}.panel{max-width:1150px;margin:14px auto;padding:22px;background:#411b66;border:2px solid #c39bdf;border-radius:16px}.controls{display:flex;gap:12px;flex-wrap:wrap}.btn{background:#7842a3;color:white;border:4px solid #d9b558;border-radius:12px;padding:14px 20px;min-height:65px;font-size:19px;font-weight:bold;cursor:pointer}.btn:focus,.btn.sel,input:focus,select:focus,textarea:focus{background:#b277d7;color:#200a35;outline:5px solid #fff1b3}input,select,textarea{display:block;width:100%;max-width:900px;padding:12px;font-size:20px;margin:8px 0 17px;border:3px solid #a77cc6;border-radius:8px;color:#250e3b;background:#fff}textarea{min-height:90px}label{display:block;font-size:19px;font-weight:bold;margin-top:12px}.result{white-space:pre-wrap;overflow-wrap:anywhere;background:#210b35;border:2px solid #d9b558;border-radius:10px;padding:18px;font-size:19px;line-height:1.55;min-height:65px}.note{color:#eed9ff;font-size:17px}#state{color:#ffe3a2;font-size:18px}
</style>
</head>
<body>
<div class="panel">
<h1>✨ Assistente Criador — Mundo da Luna</h1>
<p class="sub">Crie histórias, roteiros, narrações e prompts de animação para usar no seu gerador de vídeo.</p>
<div class="controls"><button class="btn" onclick="voltar()">← VOLTAR AO MENU</button><button class="btn" onclick="limpar()">LIMPAR</button></div>
<p id="state" role="status">Use as setas e OK do controle. Esta versão funciona sem conexão com IA.</p>
<label>Escolha Infantil ou Adulto</label>
<div class="controls"><button class="btn" id="infantilBtn" onclick="escolherPublico('infantil')">🐰 INFANTIL</button><button class="btn" id="adultoBtn" onclick="escolherPublico('adulto')">🌙 ADULTO</button></div>
<select id="publico" style="display:none" tabindex="-1"><option value="infantil">Infantil</option><option value="adulto">Adulto</option></select>
<label for="tema">Tema da história</label><input id="tema" type="text" value="O livro encantado e a floresta mágica" maxlength="180" placeholder="Ex.: uma aventura no castelo" oninput="guardarTema()" onchange="guardarTema()" onblur="guardarTema()">
<p class="note" id="temaSalvo">O tema será salvo enquanto você escreve.</p>
<div class="controls"><button class="btn" id="confirmarHistoria" onclick="confirmarHistoria()">✅ CONFIRMAR HISTÓRIA E CRIAR</button></div>
<p class="note">Depois de escrever o tema, use as setas até CONFIRMAR HISTÓRIA E CRIAR e aperte OK. No teclado, Enter no campo Tema também confirma.</p>
<label for="cenas">Quantidade de cenas</label><select id="cenas"><option value="3">3 cenas</option><option value="5" selected>5 cenas</option><option value="10">10 cenas</option></select>
<div class="controls"><button class="btn" onclick="criar()">✨ CRIAR ROTEIRO E PROMPTS</button><button class="btn" onclick="selecionarTexto()">SELECIONAR TEXTO</button></div>
<p class="note">Os textos abaixo são modelos criados neste aparelho, não vídeos nem respostas de uma IA online. Para gerar imagens ou vídeos, copie o prompt para um serviço de geração.</p>
<h2>🎬 Transformar roteiro em cenas de vídeo</h2>
<p class="note">Prepare prompts para gerar clipes em um serviço de vídeo IA no celular ou notebook. O aplicativo não gera MP4 sozinho nesta atualização.</p>
<div class="controls"><button class="btn" onclick="prepararVideos()">🎬 PREPARAR VÍDEOS</button><button class="btn" onclick="salvarProjeto()">💾 SALVAR PROJETO</button><button class="btn" onclick="carregarProjeto()">📂 ABRIR SALVO</button><button class="btn" onclick="exportarProjeto()">⬇ EXPORTAR TEXTO</button></div>
<label for="cenaVideo">Cena para copiar</label><select id="cenaVideo" onchange="exibirCena()"><option value="">Primeiro crie o roteiro</option></select>
<div id="promptVideo" class="result" tabindex="0">Crie uma história e selecione PREPARAR VÍDEOS.</div>
<textarea id="promptCopiar" aria-label="Prompt de vídeo para copiar" style="min-height:130px" placeholder="Prompt da cena selecionada"></textarea>
<div class="controls"><button class="btn" onclick="selecionarPromptVideo()">📋 SELECIONAR PROMPT</button></div>
<p class="note">Para gerar o vídeo de verdade, copie o prompt e a imagem de referência para o gerador de vídeos IA que você utiliza. Não informe sua chave secreta de API na TV.</p>
<h2>Seu roteiro</h2><div id="resultado" class="result" tabindex="0">Escolha o tema e aperte CRIAR ROTEIRO E PROMPTS.</div>
<textarea id="textoParaCopiar" aria-label="Texto pronto para copiar" style="min-height:130px" placeholder="O roteiro também aparecerá aqui para copiar no notebook ou celular."></textarea>
<button class="btn" onclick="voltar()">← VOLTAR AO MENU</button>
</div>
<script>
var alvo=0;var cenasPreparadas=[];
function el(id){return document.getElementById(id);}
function voltar(){window.location.href='index.html';}
function limpar(){el('tema').value='';guardarTema();el('resultado').textContent='Escolha um tema e crie seu roteiro.';el('textoParaCopiar').value='';cenasPreparadas=[];el('promptVideo').textContent='Crie um roteiro primeiro.';el('promptCopiar').value='';el('state').textContent='Campos limpos.';}
function guardarTema(){
 var tema=el('tema').value;
 try{localStorage.setItem('luna_tema_rascunho',tema);}catch(erro){}
 el('temaSalvo').textContent=tema?'Tema guardado: '+tema:'Escreva o tema da história.';
}
function confirmarHistoria(){
 guardarTema();criar();
 try{el('resultado').scrollIntoView(true);}catch(erro){}
}
function criar(){
 var tema=el('tema').value.replace(/^\s+|\s+$/g,'') || 'Uma aventura mágica';
 var infantil=el('publico').value==='infantil',n=parseInt(el('cenas').value,10);
 var base=infantil?'Luna, menina de 6 anos, cabelos castanhos, acompanhada de seu coelhinho branco. Manter exatamente os mesmos personagens e o mesmo estilo visual em todas as cenas.':'Uma protagonista adulta em um conto de fantasia misterioso. Preservar a identidade visual dos personagens em todas as cenas.';
 var locais=infantil?['quarto acolhedor com o livro encantado','caminho da floresta mágica','clareira iluminada por vagalumes','portões de um castelo encantado','jardim do castelo com uma princesa']:['rua de uma vila antiga','floresta sob a lua','salão do castelo','corredor de portas fechadas','terraço sob as estrelas'];
 var falas=infantil?['Luna: Vamos descobrir o que o livro guarda!','Luna: Coelhinho, veja aquele caminho!','Luna: Que lugar maravilhoso!','Luna: Será que podemos entrar?','Luna: Nossa aventura está só começando!']:['Protagonista: Há algo estranho neste lugar.','Protagonista: Preciso descobrir a verdade.','Protagonista: Escute esse sussurro.','Protagonista: A resposta está adiante.','Protagonista: Finalmente compreendi o mistério.'];
 var partes=['TEMA: '+tema,'PÚBLICO: '+(infantil?'Infantil':'Adulto'),'PERSONAGENS E CONSISTÊNCIA: '+base,''];
 for(var i=0;i<n;i++){
  var lugar=locais[i%locais.length];
  partes.push('CENA '+(i+1)+' — '+lugar);
  partes.push('NARRAÇÃO: Em mais um capítulo de "'+tema+'", a aventura continua em '+lugar+'. O cenário revela uma nova pista para a próxima descoberta.');
  partes.push('FALA: '+falas[i%falas.length]);
  partes.push('PROMPT DE IMAGEM: '+base+' Cena em '+lugar+'. Animação 3D cinematográfica, iluminação suave, enquadramento amplo, detalhes nítidos. Sem letras na imagem.');
  partes.push('PROMPT DE MOVIMENTO: Câmera avança lentamente, movimento discreto do cabelo e roupas, expressão natural e piscadas suaves. Preservar personagens e cenário. Sem cortes bruscos.');
  partes.push('');
 }
 partes.push('OBSERVAÇÃO: Este é um roteiro-base editável. Reveja as falas e a progressão narrativa antes de publicar.');
 var texto=partes.join('\n');el('resultado').textContent=texto;el('textoParaCopiar').value=texto;el('state').textContent='Roteiro criado com '+n+' cenas. Agora selecione PREPARAR VÍDEOS.';prepararVideos();
}
function selecionarTexto(){el('textoParaCopiar').focus();el('textoParaCopiar').select();el('state').textContent='Texto selecionado. Use Copiar no notebook, se disponível.';}

function prepararVideos(){
 var texto=el('textoParaCopiar').value;
 if(!texto){el('state').textContent='Primeiro aperte CRIAR ROTEIRO E PROMPTS.';return;}
 var partes=texto.split(/\n(?=CENA \d+ — )/),base=partes[0],resultados=[];
 for(var i=0;i<partes.length;i++){
  if(!/^CENA \d+ — /.test(partes[i]))continue;
  var trecho=partes[i].split('\nOBSERVAÇÃO:')[0];
  var prompt='VÍDEO IA — '+trecho.split('\n')[0]+'\n'+
   'Duração sugerida: 5 segundos por clipe. Formato: 16:9, horizontal para TV.\n'+
   'Manter os personagens e figurinos da imagem de referência sem alterações.\n'+
   'Movimentos suaves, câmera lenta, iluminação consistente, sem textos e sem cortes bruscos.\n\n'+
   'REFERÊNCIA DOS PERSONAGENS:\n'+base+'\n\nDETALHES DESTA CENA:\n'+trecho;
  resultados.push(prompt);
 }
 cenasPreparadas=resultados;
 var escolha=el('cenaVideo');escolha.innerHTML='';
 for(var j=0;j<resultados.length;j++){
  var o=document.createElement('option');o.value=String(j);o.textContent='Cena '+(j+1);escolha.appendChild(o);
 }
 exibirCena();el('state').textContent=resultados.length+' prompts de vídeo preparados. Escolha a cena e copie para seu gerador IA.';
}
function exibirCena(){
 var i=parseInt(el('cenaVideo').value,10),prompt=cenasPreparadas[i]||'Crie um roteiro primeiro.';
 el('promptVideo').textContent=prompt;el('promptCopiar').value=prompt;
}
function selecionarPromptVideo(){el('promptCopiar').focus();el('promptCopiar').select();el('state').textContent='Prompt selecionado. No notebook, use Ctrl+C para copiar.';}
function salvarProjeto(){
 try{localStorage.setItem('luna_criador_projeto_v1',JSON.stringify({tema:el('tema').value,publico:el('publico').value,cenas:el('cenas').value,roteiro:el('textoParaCopiar').value,video:cenasPreparadas}));el('state').textContent='Projeto salvo nesta TV. Para ter uma cópia fora da TV, use EXPORTAR TEXTO.';}
 catch(e){el('state').textContent='Não foi possível salvar na TV. Use EXPORTAR TEXTO no notebook.';}
}
function carregarProjeto(){
 try{var raw=localStorage.getItem('luna_criador_projeto_v1');if(!raw){el('state').textContent='Nenhum projeto salvo neste aparelho.';return;}
 var d=JSON.parse(raw);el('tema').value=d.tema||'';el('publico').value=d.publico||'infantil';el('cenas').value=d.cenas||'5';
 el('textoParaCopiar').value=d.roteiro||'';el('resultado').textContent=d.roteiro||'';prepararVideos();el('state').textContent='Projeto salvo carregado.';
 }catch(e){el('state').textContent='Não foi possível ler o projeto salvo.';}
}
function exportarProjeto(){
 var texto=el('textoParaCopiar').value;if(!texto){el('state').textContent='Primeiro crie o roteiro.';return;}
 var todos=texto+'\n\n=== PROMPTS DE VÍDEO ===\n\n'+cenasPreparadas.join('\n\n');
 try{var arquivo=new Blob([todos],{type:'text/plain;charset=utf-8'});var url=URL.createObjectURL(arquivo);var a=document.createElement('a');a.href=url;a.download='roteiro_luna_videos.txt';document.body.appendChild(a);a.click();document.body.removeChild(a);setTimeout(function(){URL.revokeObjectURL(url);},1000);el('state').textContent='Download solicitado. Algumas TVs não permitem salvar arquivos; use notebook se necessário.';}
 catch(e){el('state').textContent='Esta TV não suporta exportação. Selecione o texto para copiar no notebook.';}
}

/* Navegação da TV Samsung: foco visual sem abrir o teclado automaticamente. */
var indiceTV=0;
function escolherPublico(tipo){
 el('publico').value=tipo;
 el('infantilBtn').style.background=tipo==='infantil'?'#b277d7':'#7842a3';
 el('adultoBtn').style.background=tipo==='adulto'?'#b277d7':'#7842a3';
 el('state').textContent='Modo escolhido: '+(tipo==='infantil'?'Infantil':'Adulto');
}
function itensTV(){
 var todos=document.querySelectorAll('button,input,select,textarea');var lista=[];
 for(var i=0;i<todos.length;i++){
  var item=todos[i];if(item.id==='publico'||item.disabled||item.style.display==='none')continue;
  lista.push(item);
 }
 return lista;
}
function selecionarTV(i){
 var itens=itensTV();if(!itens.length)return;
 indiceTV=(i+itens.length)%itens.length;
 for(var j=0;j<itens.length;j++)itens[j].className=itens[j].className.replace(/\s*selecionadoTV/g,'');
 var atual=itens[indiceTV];atual.className+=' selecionadoTV';
 /* Só botões recebem foco durante a navegação, para não abrir o teclado. */
 if(atual.tagName==='BUTTON')try{atual.focus();}catch(erro){}
 try{atual.scrollIntoView(false);}catch(erro){}
 var nome=atual.textContent||atual.placeholder||atual.id;
 el('statusControle').textContent='Selecionado: '+nome.replace(/\s+/g,' ').slice(0,55);
}
function controleTV(e){
 var k=e.keyCode||e.which;
 if(k!==37&&k!==38&&k!==39&&k!==40&&k!==13&&k!==10009&&k!==461&&k!==27&&k!==8)return;
 var ativo=document.activeElement;
 var editando=ativo&&(ativo.tagName==='INPUT'||ativo.tagName==='TEXTAREA');
 if(editando){
  /* Back fecha o campo sem sair da página; conserva o texto. */
  if(k===10009||k===461||k===27){
   if(ativo.id==='tema')guardarTema();
   if(e.preventDefault)e.preventDefault();
   if(e.stopImmediatePropagation)e.stopImmediatePropagation();
   ativo.blur();
   var campos=itensTV();var alvo=-1;
   for(var j=0;j<campos.length;j++)if(campos[j].id==='confirmarHistoria'){alvo=j;break;}
   if(alvo>=0)setTimeout(function(){selecionarTV(alvo);},80);
   return;
  }
  /* O teclado virtual da Samsung precisa controlar as outras teclas. */
  return;
 }
 if(e.preventDefault)e.preventDefault();
 if(e.stopImmediatePropagation)e.stopImmediatePropagation();
 if(k===10009||k===461||k===27||k===8){voltar();return;}
 if(k===38||k===37){selecionarTV(indiceTV-1);return;}
 if(k===40||k===39){selecionarTV(indiceTV+1);return;}
 if(k===13){
  var item=itensTV()[indiceTV];if(!item)return;
  if(item.tagName==='BUTTON'){item.click();return;}
  if(item.tagName==='SELECT'){
   item.selectedIndex=(item.selectedIndex+1)%item.options.length;
   if(item.onchange)item.onchange();return;
  }
  /* OK no campo ativa a edição; não gera roteiro por engano. */
  item.focus();if(item.click)item.click();
 }
}
var estiloTV=document.createElement('style');
estiloTV.textContent='.selecionadoTV{outline:6px solid #fff2a5!important;box-shadow:0 0 0 4px #d9b558!important}#confirmarHistoria{min-height:82px;background:#673098!important;border-color:#fff2a5!important}';
document.head.appendChild(estiloTV);
window.addEventListener('keydown',controleTV,true);
window.onload=function(){
 var status=document.createElement('p');status.id='statusControle';status.style.cssText='padding:8px;font-size:20px;color:#ffedaf';
 el('state').parentNode.insertBefore(status,el('state').nextSibling);
 try{var r=localStorage.getItem('luna_tema_rascunho');if(r!==null)el('tema').value=r;}catch(erro){}
 guardarTema();escolherPublico('infantil');selecionarTV(0);
};
</script>
</body></html>
