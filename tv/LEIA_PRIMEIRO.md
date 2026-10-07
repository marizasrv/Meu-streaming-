# Mundo da Luna TV 0.3.0 — versão para teste na Samsung

O app da TV agora usa telas próprias, sem carregar o Streamlit dentro de um iframe.
O site do celular/notebook continua em `app.py`.

## Instalar no projeto que já está na sua TV

1. Faça uma cópia dos seus arquivos atuais `index.html` e `config.xml`.
2. Substitua os dois arquivos no projeto **MundodalunaTV** pelos desta pasta.
3. Mantenha seu `icon.png` e o certificado que já usa. Os IDs do aplicativo foram preservados.
4. No Tizen Studio, selecione **UN55MU6100**, depois **Run As > Tizen Web Application**.
5. Abra **Minha conta** na TV e use seu e-mail e senha habituais.
6. Teste **Filmes > um vídeo > Assistir > Voltar ao catálogo**.
7. Teste uma série, escolhendo temporada e episódio.

Se o Tizen Studio fechar com erro do Java ao salvar, isso ainda precisa ser corrigido no notebook.
Não há pacote `.wgt` assinado nesta entrega: a assinatura/instalação usa seu certificado no Tizen.

## Faça seu próprio jogo

No celular ou notebook:

1. Entre no site: https://ixezjhaxppbzpmjpit6gee.streamlit.app/
2. Escolha **Faça seu próprio jogo**.
3. Escolha **Memória** (2 a 12 palavras) ou **Perguntas e respostas** (1 a 20 perguntas).
4. Dê um nome, preencha o conteúdo e toque em **Salvar meu jogo**.
5. Teste logo abaixo do editor. Para alterar depois, escolha o jogo em **Criar ou editar**.

Na TV, entre com a mesma conta e abra **Faça seu próprio jogo > Atualizar meus jogos**.
Cada conta vê apenas seus jogos. Esta versão não compartilha jogos entre contas.
Não há importação de GDevelop, editor de fases com arrastar, imagens enviadas ou criação por IA.
Cobrança pelo aluguel, planos específicos de criador, equipes e personalização de marca não foram implementados.

## Recursos da TV

- Login por e-mail/senha e consulta da assinatura existente.
- Catálogo atualizado do Supabase; filmes, infantil, novidades e busca.
- Séries por nome, temporada e episódio.
- Verificação de Premium no servidor antes de fornecer o endereço de reprodução.
- Reprodução AVPlay na Samsung; fallback HTML5 no computador.
- Memória, Palavras, Números, Desafio Mágico, três histórias e atividades do app.
- Minha Lista e Recentes locais, separados por conta nesta TV; não sincronizam com o site.
- Enviar vídeo, IA, Gerenciar e Planos orientam continuar no celular/notebook.
- A senha não é armazenada. A sessão fica apenas em memória e encerra quando o app fecha.

## Limites de validação

Testes automáticos do editor, validação de dados, controles e servidor passaram.
Testes do banco verificaram isolamento entre duas contas com dados temporários revertidos.
O teste visual e de navegação usou Chromium de computador, com login, catálogo e AVPlay simulados.
A API publicada respondeu OPTIONS 204 e recusou pedido sem sessão (401).
Ainda é necessário validar login real, certificados/TLS, teclado virtual e reprodução na UN55MU6100.
Não é uma garantia de funcionamento em todas as TVs. Formatos e codecs dependem do aparelho.
Narração só aparece quando a API de voz existe no navegador; pode não haver voz instalada.

## Antes de comercializar

O bucket `videos` já era público no projeto. A nova API verifica assinatura,
mas um endereço público de mídia já conhecido pode ser acessado diretamente.
Para proteção completa dos arquivos pagos, é preciso migrar a mídia Premium
para armazenamento privado com URLs temporárias, incluindo os players do site.
Esta entrega não muda o bucket para evitar interromper os vídeos existentes.

A função de pagamentos `processar_compra_kiwify` foi restrita ao servidor
(service_role); usuários e visitantes não podem chamá-la diretamente.
O webhook existente mantém acesso. Não foi realizada nenhuma compra de teste.

## Arquivos e verificação técnica

- `tv/src/`: JavaScript ES5 e conteúdo da TV.
- `python3 tv/build.py`: gera `tv/index.html`, sem dependências npm.
- `game_builder.py` e `game_builder_core.py`: editor no Streamlit e validação.
- `supabase/functions/luna-tv-api/`: API somente de leitura para a TV; JWT obrigatório.
- `supabase/migrations/`: histórico das duas alterações de banco.
- `node --test tv/tests/api.test.mjs`: testes de autorização e API.
- `python3 -m unittest discover -s tv/tests -p 'test_*.py'`: editor e validação; requer Streamlit 1.62.0 ou posterior.
- `node tv/tests/ui.cjs`: teste de navegador com Playwright; suporta LUNA_CHROMIUM_PATH e LUNA_CHROMIUM_ARGS.

A chave no HTML é publicável, não administrativa. A chave de servidor permanece nas variáveis de ambiente da Edge Function.
