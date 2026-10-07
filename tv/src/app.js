(function () {
    'use strict';
    var content = document.getElementById('content');
    var session = null, account = null, catalog = null, catalogTime = 0;
    var revision = 0, history = [], renderCurrent = null, timers = [];
    var playing = false, nativePlayer = false, playerReady = false, playRevision = 0;
    var returnFocus = null, refreshQueue = null;
    var htmlVideo = document.getElementById('html-player');
    var apiUrl = TV_CONFIG.url + '/functions/v1/luna-tv-api/';
    var menuItems = [
        ['inicio', 'Início'], ['tv', 'Modo TV'], ['buscar', 'Buscar'],
        ['novidades', 'Novidades'], ['lista', 'Minha Lista'], ['recentes', 'Recentes'],
        ['conta', 'Minha conta'], ['planos', 'Planos'], ['premium', 'Premium'],
        ['enviar', 'Enviar vídeo'], ['infantil', 'Infantil'], ['filmes', 'Filmes'],
        ['series', 'Séries'], ['historias', 'Histórias da Luna'],
        ['ia', 'Criar vídeo com IA'], ['jogos', 'Jogos'],
        ['atividades', 'Atividades escolares'], ['criar-jogo', 'Faça seu próprio jogo'], ['gerenciar', 'Gerenciar']
    ];
    function el(tag, text, parent, className) {
        var node = document.createElement(tag);
        if (text !== null && text !== undefined) { node.textContent = text; }
        if (className) { node.className = className; }
        if (parent) { parent.appendChild(node); }
        return node;
    }
    function button(text, action, parent, className) {
        var b = el('button', text, parent || content, className);
        b.type = 'button'; b.onclick = action; return b;
    }
    function later(fn, ms) { var t = window.setTimeout(fn, ms); timers.push(t); return t; }
    function notice(text) {
        var n = document.getElementById('message');
        if (n) { n.textContent = text || ''; }
    }
    function firstFocus() {
        var n = content.querySelector('button:not([disabled]),input');
        if (n) { n.focus(); }
    }
    function header(title) {
        var bar = el('div', null, content, 'row');
        if (history.length) { button('← Voltar', back, bar); }
        button('Menu da TV', home, bar);
        el('h2', title, content);
        var m = el('div', '', content); m.id = 'message'; m.setAttribute('role', 'status');
    }
    function page(fn, push) {
        if (playing) { closePlayer(); }
        if (push !== false && renderCurrent) { history.push(renderCurrent); }
        revision++;
        for (var i = 0; i < timers.length; i++) { clearTimeout(timers[i]); }
        timers = [];
        if (window.speechSynthesis) { window.speechSynthesis.cancel(); }
        renderCurrent = fn; content.innerHTML = ''; content.scrollTop = 0;
        fn(); firstFocus();
    }
    function back() {
        if (playing) { closePlayer(); return; }
        if (history.length) { page(history.pop(), false); } else { home(); }
    }
    function home() {
        history = [];
        page(function () {
            el('h2', 'O que vamos descobrir hoje?', content);
            el('p', 'Filmes, histórias e diversão com a Luna.', content, 'muted');
            var grid = el('div', null, content, 'row menu');
            menuItems.forEach(function (item) {
                button(item[1], function () { route(item[0]); }, grid);
            });
            el('p', 'Use as setas e OK. Voltar retorna à tela anterior.', content, 'muted');
        }, false);
    }
    function route(slug) {
        if (slug === 'inicio') { home(); }
        else if (slug === 'conta') { page(showAccount); }
        else if (slug === 'historias') { page(stories); }
        else if (slug === 'jogos') { page(games); }
        else if (slug === 'criar-jogo') { page(myGames); }
        else if (slug === 'atividades') { page(activities); }
        else if (['planos', 'enviar', 'ia', 'gerenciar'].indexOf(slug) >= 0) { page(function () { companion(slug); }); }
        else { page(function () { showCatalog(slug); }); }
    }
    function xhr(method, url, body, token, done) {
        var request = new XMLHttpRequest(), finished = false;
        function finish(err, result, status) {
            if (finished) { return; } finished = true; done(err, result, status);
        }
        request.open(method, url, true); request.timeout = 20000;
        request.setRequestHeader('apikey', TV_CONFIG.key);
        if (token) { request.setRequestHeader('Authorization', 'Bearer ' + token); }
        if (body !== null) { request.setRequestHeader('Content-Type', 'application/json'); }
        request.onload = function () {
            var data;
            try { data = JSON.parse(request.responseText); }
            catch (_) { finish('O servidor não retornou uma resposta válida.', null, request.status); return; }
            if (request.status < 200 || request.status >= 300) {
                var message = data.error || data.msg || data.message || data.error_description;
                if (typeof message !== 'string') { message = 'Não foi possível concluir o pedido.'; }
                finish(message, null, request.status);
            } else { finish(null, data, request.status); }
        };
        request.onerror = function () { finish('Falha de conexão. Confira a internet e a data/hora da TV.', null, 0); };
        request.ontimeout = function () { finish('A conexão demorou demais. Tente novamente.', null, 0); };
        try { request.send(body === null ? null : JSON.stringify(body)); }
        catch (_) { finish('Não foi possível conectar ao serviço.', null, 0); }
    }
    function setSession(data) {
        session = {access_token: data.access_token, refresh_token: data.refresh_token,
            expires_at: Date.now() + Number(data.expires_in || 3600) * 1000};
    }
    function refresh(done) {
        if (!session) { done('Entre na sua conta.'); return; }
        if (refreshQueue) { refreshQueue.push(done); return; }
        refreshQueue = [done];
        var expected = session;
        xhr('POST', TV_CONFIG.url + '/auth/v1/token?grant_type=refresh_token',
            {refresh_token: session.refresh_token}, null, function (err, data, status) {
                if (session !== expected) { err = 'A conta foi alterada. Tente novamente.'; }
                else if (!err) { setSession(data); }
                else if (status === 400 || status === 401 || status === 403) { forgetSession(); }
                var queue = refreshQueue || []; refreshQueue = null;
                queue.forEach(function (fn) { fn(err); });
            });
    }
    function api(path, done, retried) {
        if (!session) { done('Entre na sua conta para acessar o catálogo.'); return; }
        if (!retried && session.expires_at < Date.now() + 30000) {
            refresh(function (err) { if (err) { done(err); } else { api(path, done, true); } }); return;
        }
        var expected = session;
        xhr('GET', apiUrl + path, null, session.access_token, function (err, data, status) {
            if (session !== expected) { done('A conta foi alterada. Tente novamente.'); return; }
            if (status === 401 && !retried) {
                refresh(function (e) { if (e) { done(e); } else { api(path, done, true); } }); return;
            }
            if (status === 401) { forgetSession(); }
            done(err, data);
        });
    }
    function accountLabel() {
        document.getElementById('accountLabel').textContent = account ?
            account.email + ' · ' + account.plano + ' (' + account.status + ')' : 'TV Samsung · Entre em Minha conta';
    }
    function forgetSession() { session = null; account = null; catalog = null; catalogTime = 0; accountLabel(); }
    function showAccount() {
        header('Minha conta');
        var ticket = revision;
        if (session) {
            notice('Conferindo sua assinatura…');
            api('account', function (err, data) {
                if (ticket !== revision) { return; }
                if (err) { notice(err); return; }
                account = data; accountLabel(); notice('Conta conectada.');
                el('p', data.email + ' — ' + data.plano + ' (' + data.status + ')', content);
            });
            button('Atualizar conta', function () { page(showAccount, false); });
            button('Ir para os vídeos', function () { route('tv'); });
            button('Sair da conta', function () {
                var oldToken = session && session.access_token;
                forgetSession();
                if (oldToken) { xhr('POST', TV_CONFIG.url + '/auth/v1/logout?scope=local', {}, oldToken, function () {}); }
                page(showAccount, false);
            });
            el('p', 'Sua senha não é guardada. Ao fechar o aplicativo, entre novamente.', content, 'muted');
            return;
        }
        el('p', 'Use o mesmo e-mail e senha do app no celular.', content);
        var form = el('form', null, content, 'panel');
        var emailLabel = el('label', 'E-mail', form);
        var email = el('input', null, emailLabel); email.type = 'email'; email.required = true; email.id = 'email'; email.autocomplete = 'username';
        var passLabel = el('label', 'Senha', form);
        var pass = el('input', null, passLabel); pass.type = 'password'; pass.required = true; pass.id = 'password'; pass.autocomplete = 'current-password';
        var submit = el('button', 'Entrar', form); submit.type = 'submit';
        var busy = false;
        form.onsubmit = function (event) {
            event.preventDefault(); if (busy) { return; } busy = true; submit.disabled = true;
            notice('Entrando…');
            xhr('POST', TV_CONFIG.url + '/auth/v1/token?grant_type=password',
                {email: email.value.replace(/^\s+|\s+$/g, ''), password: pass.value}, null,
                function (err, data, status) {
                    pass.value = ''; busy = false; submit.disabled = false;
                    if (ticket !== revision) { return; }
                    if (err) {
                        notice(status === 400 ? 'Confira o e-mail e a senha. Se necessário, recupere a senha no celular.' : err);
                        submit.focus(); return;
                    }
                    setSession(data); catalog = null;
                    page(showAccount, false);
                });
        };
        el('p', 'Cadastro e recuperação de senha: use Minha conta no celular ou notebook.', content, 'muted');
    }
    function localData() {
        var key = 'luna.tv.' + (account ? account.id : 'visitor');
        try { return JSON.parse(localStorage.getItem(key)) || {favorites: {}, recent: {}}; }
        catch (_) { return {favorites: {}, recent: {}}; }
    }
    function saveLocal(data) {
        try { localStorage.setItem('luna.tv.' + (account ? account.id : 'visitor'), JSON.stringify(data)); }
        catch (_) { notice('A TV não conseguiu guardar a lista neste aparelho.'); }
    }
    function getCatalog(ticket, done, force) {
        if (!session) { done('Entre em Minha conta para ver os vídeos.'); return; }
        if (!force && catalog && Date.now() - catalogTime < 30000) { done(null, catalog); return; }
        notice('Carregando seu catálogo…');
        api('account', function (err, data) {
            if (ticket !== revision) { return; }
            if (err) { done(err); return; }
            account = data; accountLabel();
            var all = [];
            function batch(offset) {
                api('catalog?offset=' + offset, function (error, response) {
                    if (ticket !== revision) { return; }
                    if (error) { done(error); return; }
                    all = all.concat(response.items);
                    if (response.next !== null && all.length < 10000) { batch(response.next); }
                    else { catalog = all; catalogTime = Date.now(); done(null, all); }
                });
            }
            batch(0);
        });
    }
    function baseCategory(v) { return String(v.categoria || '').replace(/^Premium::/, ''); }
    function plain(s) { return String(s).replace(/\*\*/g, ''); }
    function showCatalog(slug, force) {
        var names = {tv: 'Todos os vídeos', filmes: 'Filmes', series: 'Séries', infantil: 'Infantil', buscar: 'Buscar', novidades: 'Novidades', premium: 'Premium', lista: 'Minha Lista', recentes: 'Recentes'};
        header(names[slug] || 'Vídeos');
        var ticket = revision;
        if (!session) { notice('Entre na sua conta para carregar os vídeos.'); button('Entrar', function () { route('conta'); }); return; }
        button('Atualizar catálogo', function () { page(function () { showCatalog(slug, true); }, false); });
        if (slug === 'lista' || slug === 'recentes') { el('p', 'Esta lista é guardada apenas nesta TV, separada por conta.', content, 'muted'); }
        var search = null;
        if (slug === 'buscar') {
            var label = el('label', 'Título do vídeo ou série', content);
            search = el('input', null, label); search.type = 'search'; search.id = 'search';
        }
        var results = el('div', null, content, 'cards');
        getCatalog(ticket, function (err, items) {
            if (err) { notice(err); if (!session) { button('Entrar', function () { route('conta'); }); } return; }
            notice(items.length + ' vídeos no catálogo.');
            function draw() {
                results.innerHTML = '';
                var data = localData();
                var list = items.filter(function (v) {
                    if (slug === 'filmes' && baseCategory(v) !== 'Filmes') { return false; }
                    if (slug === 'series' && baseCategory(v) !== 'Séries') { return false; }
                    if (slug === 'infantil' && baseCategory(v) !== 'Infantil') { return false; }
                    if (slug === 'premium' && !v.premium) { return false; }
                    if (slug === 'lista' && !data.favorites[v.id]) { return false; }
                    if (slug === 'recentes' && !data.recent[v.id]) { return false; }
                    return !search || (v.nome + ' ' + (v.serie_nome || '')).toLowerCase().indexOf(search.value.toLowerCase()) >= 0;
                });
                if (slug === 'recentes') { list.sort(function (a, b) { return data.recent[b.id] - data.recent[a.id]; }); }
                if (slug === 'novidades') { list = list.slice(0, 20); }
                if (!list.length) { el('p', 'Nenhum vídeo nesta seleção.', results); }
                if (slug === 'series') { seriesGroups(list, results); }
                else { list.forEach(function (v) { videoCard(v, results); }); }
            }
            if (search) { search.oninput = draw; }
            draw();
        }, force);
    }
    function seriesGroups(list, parent) {
        var groups = {};
        list.forEach(function (v) { var name = v.serie_nome || v.nome || 'Série'; if (!groups[name]) { groups[name] = []; } groups[name].push(v); });
        Object.keys(groups).forEach(function (name) {
            button(name, function () {
                page(function () {
                    header(name);
                    var seasons = {};
                    groups[name].forEach(function (v) { var s = String(v.temporada || 1); if (!seasons[s]) { seasons[s] = []; } seasons[s].push(v); });
                    Object.keys(seasons).sort(function (a, b) { return Number(a) - Number(b); }).forEach(function (s) {
                        button('Temporada ' + s, function () {
                            page(function () {
                                header(name + ' · Temporada ' + s);
                                var grid = el('div', null, content, 'cards');
                                seasons[s].sort(function (a, b) { return (a.episodio || 1) - (b.episodio || 1); }).forEach(function (v) { videoCard(v, grid); });
                            });
                        });
                    });
                });
            }, parent, 'card');
        });
    }
    function videoCard(v, parent) {
        var b = button('', function () { page(function () { detail(v); }); }, parent, 'card');
        if (/^https?:\/\//i.test(v.capa_url || '')) {
            var img = el('img', null, b); img.alt = ''; img.src = v.capa_url;
            img.onerror = function () { this.style.display = 'none'; };
        }
        el('span', v.nome || 'Sem título', b);
        el('small', baseCategory(v) + (v.premium ? ' · Premium' : ' · Grátis'), b);
        if (baseCategory(v) === 'Séries') { el('small', 'Temporada ' + (v.temporada || 1) + ' · Episódio ' + (v.episodio || 1), b); }
    }
    function detail(v) {
        header(v.nome || 'Vídeo');
        el('p', baseCategory(v) + (v.premium ? ' · Premium' : ' · Grátis'), content);
        button('▶ Assistir', function () { openPlayer(v); });
        var data = localData();
        var favorite = button(data.favorites[v.id] ? 'Remover da Minha Lista' : 'Adicionar à Minha Lista', function () {
            var d = localData();
            if (d.favorites[v.id]) { delete d.favorites[v.id]; } else { d.favorites[v.id] = true; }
            saveLocal(d); favorite.textContent = d.favorites[v.id] ? 'Remover da Minha Lista' : 'Adicionar à Minha Lista';
        });
    }
    function playerStatus(message) { document.getElementById('playerStatus').textContent = message; }
    function closePlayer() {
        playRevision++; playing = false; playerReady = false;
        try { if (nativePlayer) { webapis.avplay.stop(); } } catch (_) {}
        try { if (nativePlayer) { webapis.avplay.close(); } } catch (_) {}
        htmlVideo.pause(); htmlVideo.removeAttribute('src'); htmlVideo.load();
        document.getElementById('player').style.display = 'none';
        document.body.className = ''; document.documentElement.style.background = '';
        if (returnFocus && document.body.contains(returnFocus)) { returnFocus.focus(); }
        nativePlayer = false;
    }
    function markRecent(v) { var d = localData(); d.recent[v.id] = Date.now(); saveLocal(d); }
    function openPlayer(v) {
        var ticket = revision;
        notice('Verificando acesso ao vídeo…');
        api('play?id=' + encodeURIComponent(v.id), function (err, data) {
            if (ticket !== revision || playing) { return; }
            if (err) { notice(err); return; }
            returnFocus = document.activeElement;
            playing = true; playerReady = false; var run = ++playRevision;
            document.body.className = 'playing'; document.documentElement.style.background = 'transparent';
            document.getElementById('player').style.display = 'block';
            document.getElementById('closePlayer').focus(); playerStatus('Preparando ' + v.nome + '…');
            nativePlayer = !!(window.webapis && webapis.avplay);
            htmlVideo.style.display = nativePlayer ? 'none' : 'block';
            document.getElementById('av-player').style.display = nativePlayer ? 'block' : 'none';
            var timeout = window.setTimeout(function () {
                if (run === playRevision && !playerReady) { playerStatus('O vídeo demorou para abrir. Use Voltar e tente outro vídeo.'); }
            }, 25000);
            function ready() {
                clearTimeout(timeout); if (run !== playRevision) { return; }
                playerReady = true; markRecent(v); playerStatus(v.nome + ' · Reproduzindo');
            }
            function failed() { clearTimeout(timeout); if (run === playRevision) { playerStatus('Não foi possível reproduzir este vídeo. O link ou o formato pode ser incompatível. Use Voltar.'); } }
            if (nativePlayer) {
                try {
                    webapis.avplay.open(data.url);
                    webapis.avplay.setDisplayRect(0, 0, 1920, 1080);
                    webapis.avplay.setListener({
                        onerror: failed,
                        onbufferingstart: function () { if (run === playRevision) { playerStatus('Carregando vídeo…'); } },
                        onbufferingcomplete: function () { if (run === playRevision) { playerStatus(v.nome); } },
                        onstreamcompleted: function () { if (run === playRevision) { closePlayer(); notice('Vídeo concluído.'); } }
                    });
                    webapis.avplay.prepareAsync(function () {
                        if (run !== playRevision || !playing) { return; }
                        try { webapis.avplay.play(); ready(); } catch (_) { failed(); }
                    }, failed);
                } catch (_) { failed(); }
            } else {
                htmlVideo.onplaying = ready; htmlVideo.onerror = failed;
                htmlVideo.onended = function () { closePlayer(); notice('Vídeo concluído.'); };
                htmlVideo.src = data.url;
                try { var promise = htmlVideo.play(); if (promise && promise.catch) { promise.catch(failed); } } catch (_) { failed(); }
            }
        });
    }
    function pausePlay(force) {
        if (!playing || !playerReady) { return; }
        try {
            var paused = nativePlayer ? webapis.avplay.getState() === 'PAUSED' : htmlVideo.paused;
            var shouldPlay = force === 'play' || (force !== 'pause' && paused);
            if (nativePlayer) { if (shouldPlay) { webapis.avplay.play(); } else { webapis.avplay.pause(); } }
            else if (shouldPlay) { var p = htmlVideo.play(); if (p && p.catch) { p.catch(function () { playerStatus('Não foi possível retomar. Use Voltar.'); }); } }
            else { htmlVideo.pause(); }
            playerStatus(shouldPlay ? 'Reproduzindo' : 'Pausado');
        } catch (_) { playerStatus('Não foi possível alterar a reprodução. Use Voltar.'); }
    }
    function seek(seconds) {
        if (!playing || !playerReady) { return; }
        try {
            if (nativePlayer) {
                var duration = webapis.avplay.getDuration();
                if (duration > 0) { webapis.avplay.seekTo(Math.max(0, Math.min(duration - 1000, webapis.avplay.getCurrentTime() + seconds * 1000))); }
            } else if (isFinite(htmlVideo.duration)) { htmlVideo.currentTime = Math.max(0, Math.min(htmlVideo.duration - 0.1, htmlVideo.currentTime + seconds)); }
        } catch (_) { playerStatus('Este vídeo não permite avançar neste momento.'); }
    }
    document.getElementById('playPause').onclick = function () { pausePlay(); };
    document.getElementById('rewind').onclick = function () { seek(-10); };
    document.getElementById('forward').onclick = function () { seek(10); };
    document.getElementById('closePlayer').onclick = closePlayer;
    function companion(slug) {
        var labels = {ia: 'Criar vídeo com IA', enviar: 'Enviar vídeo', gerenciar: 'Gerenciar', planos: 'Planos'};
        header(labels[slug]);
        el('p', 'Continue esta função no celular ou notebook, no mesmo app da Luna.', content, 'story');
        el('p', 'Abra o site e escolha “' + labels[slug] + '” no menu.', content);
        el('p', TV_CONFIG.site, content, 'link');
        el('p', 'Depois de enviar vídeos ou atualizar seu plano, volte à TV e escolha Atualizar catálogo.', content, 'muted');
        button('Ir para Minha conta', function () { route('conta'); });
    }
    function stories() {
        header('Histórias da Luna');
        TV_CONTENT.stories.forEach(function (s, i) { button(s.titulo, function () { page(function () { chapter(i, 0); }); }); });
    }
    function chapter(story, number) {
        var s = TV_CONTENT.stories[story], c = s.capitulos[number];
        header(s.titulo); el('h3', c[0], content); el('p', c[1], content, 'story');
        if (number > 0) { button('Capítulo anterior', function () { page(function () { chapter(story, number - 1); }, false); }); }
        if (number < s.capitulos.length - 1) { button('Próximo capítulo', function () { page(function () { chapter(story, number + 1); }, false); }); }
        if (window.speechSynthesis && window.SpeechSynthesisUtterance) {
            button('Ouvir história', function () {
                window.speechSynthesis.cancel(); var voice = new SpeechSynthesisUtterance(c[1]); voice.lang = 'pt-BR'; voice.rate = 0.9;
                voice.onerror = function () { notice('A narração não está disponível neste aparelho.'); };
                window.speechSynthesis.speak(voice);
            });
            button('Parar narração', function () { window.speechSynthesis.cancel(); });
        }
    }
    function games() {
        header('Jogos da Luna');
        button('Memória', function () { page(function () { memory(1); }); });
        button('Palavras', function () { page(wordAges); });
        button('Números', function () { page(function () { numbers(1, false); }); });
        button('Desafio Mágico', function () { page(function () { numbers(1, true); }); });
    }
    function shuffle(a) { for (var i = a.length - 1; i > 0; i--) { var j = Math.floor(Math.random() * (i + 1)), t = a[i]; a[i] = a[j]; a[j] = t; } return a; }
    function memory(level, custom) {
        header('Memória · Nível ' + level);
        var count = custom ? custom.content.items.length : Math.min(8, level + 2), deck = [], chosen = [], matched = {}, busy = false, hits = 0;
        var names = custom ? custom.content.items : ['LUA', 'SOL', 'FLOR', 'LUNA', 'GATO', 'LIVRO', 'BOLA', 'FADA'];
        if (custom) { el('h3', custom.title, content); }
        for (var i = 0; i < count; i++) { deck.push(names[i], names[i]); } shuffle(deck);
        var grid = el('div', null, content, 'row memory'), cards = [];
        deck.forEach(function (name, index) {
            var b = button('?', function () {
                if (busy || matched[index] || chosen.indexOf(index) >= 0) { return; }
                b.textContent = name; b.setAttribute('aria-label', name); chosen.push(index);
                if (chosen.length === 2) {
                    var a = chosen[0], c = chosen[1];
                    if (deck[a] === deck[c]) {
                        matched[a] = matched[c] = true; chosen = []; hits++;
                        notice('Par encontrado! ' + hits + ' de ' + count);
                        if (hits === count) {
                            notice('Você encontrou todos os pares!');
                            var next = button(custom ? 'Jogar novamente' : 'Próximo nível', function () { page(function () { memory(custom ? level : level + 1, custom); }, false); }); next.focus();
                        }
                    } else {
                        busy = true; notice('Observe as palavras e tente outro par.');
                        later(function () { cards[a].textContent = '?'; cards[c].textContent = '?'; cards[a].setAttribute('aria-label', 'Carta ' + (a + 1)); cards[c].setAttribute('aria-label', 'Carta ' + (c + 1)); chosen = []; busy = false; }, 1000);
                    }
                }
            }, grid);
            b.setAttribute('aria-label', 'Carta ' + (index + 1)); cards.push(b);
        });
        button('Novo jogo', function () { page(function () { memory(level, custom); }, false); });
    }
    function wordAges() {
        header('Palavras · Escolha a idade');
        Object.keys(TV_CONTENT.words).forEach(function (age) { button(age, function () { page(function () { wordQuestion(age, 0); }); }); });
    }
    function choices(question, options, correct, next) {
        el('p', plain(question), content, 'story');
        var solved = false;
        options.forEach(function (option) {
            button(String(option), function () {
                if (solved) { return; }
                if (String(option) === String(correct)) {
                    solved = true; notice('Muito bem! Você acertou.');
                    var b = button('Próxima fase', next); b.focus();
                } else { notice('Vamos tentar outra vez!'); }
            });
        });
    }
    function wordQuestion(age, index) {
        var questions = TV_CONTENT.words[age], q = questions[index % questions.length];
        header('Palavras · ' + age + ' · Fase ' + (index + 1));
        choices(q.pergunta, q.opcoes, q.correta, function () {
            if (index + 1 < questions.length) { page(function () { wordQuestion(age, index + 1); }, false); }
            else { page(function () { header('Parabéns!'); el('p', 'Você completou as palavras desta idade.', content); button('Jogar novamente', function () { page(function () { wordQuestion(age, 0); }, false); }); }, false); }
        });
    }
    function numbers(level, magic) {
        header((magic ? 'Desafio Mágico' : 'Números') + ' · Fase ' + level);
        var a = 1 + Math.floor(Math.random() * Math.min(30, 4 + level)), b = 1 + Math.floor(Math.random() * 5);
        var result = magic ? a + 3 * b : a + b;
        var q = magic ? 'Qual número continua a sequência? ' + a + ', ' + (a + b) + ', ' + (a + 2 * b) + ', …' : a + ' + ' + b + ' = ?';
        choices(q, shuffle([result, result + 1, result + 2]), result, function () { page(function () { numbers(level + 1, magic); }, false); });
    }
    function activities() {
        header('Atividades escolares · Escolha a idade');
        ['4–5 anos', '6–7 anos', '8–9 anos'].forEach(function (age) {
            button(age, function () {
                page(function () {
                    header('Atividades · ' + age);
                    TV_CONTENT.activities.forEach(function (group, index) {
                        if (group.idade === age) { button(group.materia, function () { page(function () { activity(index, 0); }); }); }
                    });
                });
            });
        });
    }
    function normalized(s) { return String(s).toLowerCase().replace(/^\s+|\s+$/g, '').replace(/[áàâã]/g,'a').replace(/[éê]/g,'e').replace(/[í]/g,'i').replace(/[óôõ]/g,'o').replace(/[ú]/g,'u').replace(/ç/g,'c'); }
    function activity(groupIndex, index) {
        var group = TV_CONTENT.activities[groupIndex], task = group.fases[index];
        header(group.materia + ' · ' + group.idade + ' · Fase ' + (index + 1));
        el('p', plain(task[0]), content, 'story');
        if (group.materia === 'Atividade para colorir') {
            el('p', task[4], content, 'story');
            el('p', 'Use papel e lápis de cor. Para imprimir, abra Atividades escolares no notebook.', content);
            button('Próxima atividade', advance); return;
        }
        if (task[1] === 'opcao') { choices(task[2], task[3][0], task[3][1], advance); return; }
        var form = el('form', null, content);
        var label = el('label', task[2], form), answer = el('input', null, label);
        answer.type = task[1] === 'numero' ? 'number' : 'text'; answer.required = true;
        var submit = el('button', 'Confirmar resposta', form); submit.type = 'submit';
        var solved = false;
        form.onsubmit = function (event) {
            event.preventDefault(); if (solved) { return; }
            var ok = task[1] === 'leitura' ? normalized(answer.value).indexOf(normalized(task[3])) >= 0 : task[1] === 'frase' ? answer.value.trim().split(/\s+/).length >= Number(task[3]) : normalized(answer.value) === normalized(task[3]);
            if (ok) { solved = true; notice('Muito bem! Resposta correta.'); var b = button('Próxima atividade', advance); b.focus(); }
            else { notice('Tente novamente. Você consegue!'); }
        };
        function advance() { if (index + 1 < group.fases.length) { page(function () { activity(groupIndex, index + 1); }, false); } else { page(function () { header('Atividades concluídas!'); button('Escolher outra atividade', function () { page(activities, false); }); }, false); } }
    }
    function myGames() {
        header('Faça seu próprio jogo');
        el('p', 'Crie no celular ou notebook, na aba Faça seu próprio jogo. Depois, jogue aqui com a mesma conta.', content);
        el('p', TV_CONFIG.site, content, 'link');
        if (!session) { button('Entrar na minha conta', function () { route('conta'); }); return; }
        button('Atualizar meus jogos', function () { page(myGames, false); });
        var ticket = revision;
        notice('Buscando seus jogos…');
        api('games', function (err, data) {
            if (ticket !== revision) { return; }
            if (err) { notice(err); return; }
            notice(data.items.length ? 'Escolha um jogo.' : 'Você ainda não salvou jogos nesta conta.');
            data.items.forEach(function (g) {
                button(g.title, function () {
                    page(function () {
                        if (g.kind === 'memory' && g.content && g.content.items && g.content.items.length >= 2 && g.content.items.length <= 12) { memory(1, g); }
                        else if (g.kind === 'quiz' && g.content && g.content.questions && g.content.questions.length) { customQuiz(g, 0); }
                        else { header('Jogo indisponível'); notice('Edite e salve novamente este jogo no celular.'); }
                    });
                });
            });
        });
    }
    function customQuiz(game, index) {
        var q = game.content.questions[index];
        header(game.title + ' · Pergunta ' + (index + 1));
        if (!q || !q.options || q.options[q.answer] === undefined) { notice('Esta pergunta precisa ser revisada no editor.'); return; }
        choices(q.prompt, q.options, q.options[q.answer], function () {
            if (index + 1 < game.content.questions.length) { page(function () { customQuiz(game, index + 1); }, false); }
            else { page(function () { header('Parabéns!'); el('p', 'Você concluiu o jogo.', content); button('Jogar novamente', function () { page(function () { customQuiz(game, 0); }, false); }); }, false); }
        });
    }
    function visibleControls() {
        var area = playing ? document.getElementById('playerBar') : content;
        return Array.prototype.filter.call(area.querySelectorAll('button,input'), function (n) { return !n.disabled && n.offsetWidth > 0 && n.offsetHeight > 0; });
    }
    function moveFocus(key) {
        var nodes = visibleControls(), current = document.activeElement, best = null, score = Infinity;
        if (!nodes.length) { return; }
        if (nodes.indexOf(current) < 0) { nodes[0].focus(); return; }
        var rect = current.getBoundingClientRect(), x = rect.left + rect.width / 2, y = rect.top + rect.height / 2;
        nodes.forEach(function (n) {
            if (n === current) { return; }
            var r = n.getBoundingClientRect(), dx = r.left + r.width / 2 - x, dy = r.top + r.height / 2 - y;
            if ((key === 37 && dx >= -5) || (key === 39 && dx <= 5) || (key === 38 && dy >= -5) || (key === 40 && dy <= 5)) { return; }
            var along = key === 37 || key === 39 ? Math.abs(dx) : Math.abs(dy);
            var across = key === 37 || key === 39 ? Math.abs(dy) : Math.abs(dx);
            var distance = along + across * 3;
            if (distance < score) { score = distance; best = n; }
        });
        if (best) {
            best.focus();
            var b = best.getBoundingClientRect(), c = content.getBoundingClientRect();
            if (!playing && (b.top < c.top || b.bottom > c.bottom)) { best.scrollIntoView(false); }
        }
    }
    document.addEventListener('keydown', function (event) {
        var key = event.keyCode, active = document.activeElement;
        if (key === 10009 || key === 27) {
            event.preventDefault();
            if (active && active.tagName === 'INPUT') { active.blur(); firstFocus(); } else { back(); }
            return;
        }
        if (playing && [415, 19, 10252, 413, 417, 412].indexOf(key) >= 0) {
            event.preventDefault();
            if (key === 413) { closePlayer(); }
            else if (key === 417 || key === 412) { seek(key === 417 ? 10 : -10); }
            else { pausePlay(key === 415 ? 'play' : key === 19 ? 'pause' : null); }
            return;
        }
        if (key >= 37 && key <= 40) {
            if (active && active.tagName === 'INPUT' && (key === 37 || key === 39)) { return; }
            event.preventDefault(); moveFocus(key);
        }
        // Native Enter activates buttons once; forms handle Enter in input fields.
    });
    document.addEventListener('visibilitychange', function () { if (document.hidden && playing) { pausePlay('pause'); } });
    window.addEventListener('pagehide', closePlayer);
    try {
        if (window.tizen && tizen.tvinputdevice) {
            ['MediaPlay','MediaPause','MediaPlayPause','MediaStop','MediaFastForward','MediaRewind'].forEach(function (key) { try { tizen.tvinputdevice.registerKey(key); } catch (_) {} });
        }
    } catch (_) {}
    accountLabel(); home();
})();
