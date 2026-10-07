"""Per-account game creator for the existing authenticated Streamlit app."""
from datetime import datetime, timezone
from uuid import UUID
import streamlit as st
from game_builder_core import validate_game, game_html


def render_game_builder(user_id, client):
    st.subheader('🎨 Faça seu próprio jogo')
    st.caption('Crie sem programar. Seus jogos ficam na sua conta e podem ser abertos na TV.')
    if not user_id:
        st.info('Entre em Minha conta para criar e guardar seus jogos.')
        return
    # Identity comes from the app's authenticated session, never a form field.
    owner = str(UUID(str(user_id)))
    if client is None:
        st.warning('Entre novamente na sua conta para acessar seus jogos.')
        return
    try:
        games = (client.table('jogos_criados').select('id,title,kind,content,updated_at')
                 .eq('user_id', owner).order('updated_at', desc=True).limit(100).execute().data or [])
    except Exception:
        st.error('Não foi possível carregar seus jogos. Tente novamente em instantes.')
        return
    ids = ['novo'] + [g['id'] for g in games]
    by_id = {g['id']: g for g in games}
    selected = st.selectbox('Criar ou editar', ids,
                            format_func=lambda value: '➕ Novo jogo' if value == 'novo' else by_id[value]['title'],
                            key='criador_selecao_' + owner)
    existing = by_id.get(selected)
    suffix = owner + '_' + selected
    kind_names = {'memory': 'Memória', 'quiz': 'Perguntas e respostas'}
    kind = st.selectbox('Tipo de jogo', list(kind_names),
                        index=1 if existing and existing['kind'] == 'quiz' else 0,
                        format_func=kind_names.get, key='criador_tipo_' + suffix)
    old_content = existing['content'] if existing and existing['kind'] == kind else {}
    old_questions = old_content.get('questions', [])
    count = int(st.number_input('Quantidade de perguntas', min_value=1, max_value=20,
                               value=max(1, len(old_questions)), key='criador_n_' + suffix)) if kind == 'quiz' else 0
    with st.form('criador_form_' + suffix + kind):
        title = st.text_input('Nome do jogo', value=existing['title'] if existing else '', max_chars=80)
        payload = {}
        if kind == 'memory':
            st.write('Escreva uma palavra ou frase por linha. O jogo cria dois cartões iguais para cada uma.')
            words = st.text_area('Palavras dos pares (2 a 12)', value='\n'.join(old_content.get('items', ['Luna', 'Coelho', 'Castelo'])), height=180, max_chars=600)
            payload = {'items': words.splitlines()}
        else:
            questions = []
            for i in range(count):
                old = old_questions[i] if i < len(old_questions) else {}
                st.markdown(f'**Pergunta {i + 1}**')
                prompt = st.text_input('Pergunta', value=old.get('prompt', ''), max_chars=300, key=f'criador_p_{suffix}_{i}')
                previous = old.get('options', ['', '', ''])
                options = [st.text_input(f'Resposta {j + 1}', value=previous[j] if j < len(previous) else '', max_chars=100,
                                         key=f'criador_o_{suffix}_{i}_{j}') for j in range(3)]
                answer = st.radio('Qual resposta está correta?', [0, 1, 2], index=min(2, old.get('answer', 0)),
                                  format_func=lambda n: f'Resposta {n + 1}', horizontal=True, key=f'criador_a_{suffix}_{i}')
                questions.append({'prompt': prompt, 'options': options, 'answer': answer})
            payload = {'questions': questions}
        submitted = st.form_submit_button('💾 Salvar meu jogo')
    if submitted:
        try:
            clean = validate_game(title, kind, payload)
            clean['updated_at'] = datetime.now(timezone.utc).isoformat()
            if existing:
                response = (client.table('jogos_criados').update(clean)
                            .eq('id', existing['id']).eq('user_id', owner).execute())
            else:
                clean['user_id'] = owner
                response = client.table('jogos_criados').insert(clean).execute()
            if not response.data:
                st.error('O jogo não foi salvo. Entre novamente e tente outra vez.')
                return
            st.success('Jogo salvo na sua conta! Na TV, abra Faça seu próprio jogo e Atualizar meus jogos.')
            st.markdown('### Testar meu jogo')
            st.iframe(game_html(clean), height=600)
        except ValueError as exc:
            st.warning(str(exc))
        except Exception:
            st.error('Não foi possível salvar. Seu jogo anterior foi preservado. Tente novamente.')
    elif existing:
        st.markdown('### Jogar a versão salva')
        st.iframe(game_html(existing), height=600)
    st.info('Primeira versão: jogos de palavras no Memória e perguntas com 3 respostas. Projetos do GDevelop e jogos com imagens não são importados aqui.')
