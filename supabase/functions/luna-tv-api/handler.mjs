// Read-only TV gateway. No user, subscription or payment writes.
export function createHandler({ url, key, fetcher = fetch }) {
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'authorization, apikey, content-type',
    'Access-Control-Allow-Methods': 'GET, OPTIONS',
    'Content-Type': 'application/json; charset=utf-8',
    'Cache-Control': 'no-store',
    'X-Content-Type-Options': 'nosniff'
  };
  const reply = (status, body) => new Response(JSON.stringify(body), {status, headers});
  const premium = row => String(row.categoria || '').startsWith('Premium::');
  async function query(path, token = key) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 12000);
    try {
      const response = await fetcher(url + path, {
        headers: { apikey: key, Authorization: 'Bearer ' + token },
        signal: controller.signal
      });
      if (!response.ok) {
        const error = new Error('upstream');
        error.status = response.status;
        throw error;
      }
      return await response.json();
    } finally { clearTimeout(timer); }
  }
  return async function handle(req) {
    if (req.method === 'OPTIONS') return new Response(null, {status: 204, headers});
    if (req.method !== 'GET') return reply(405, {error: 'Método não permitido.'});
    if (!url || !key) return reply(503, {error: 'Serviço da TV ainda não configurado.'});
    const auth = req.headers.get('Authorization') || '';
    if (!/^Bearer \S+$/i.test(auth) || auth.length > 8192) return reply(401, {error: 'Entre na sua conta.'});
    let user;
    try {
      user = await query('/auth/v1/user', auth.slice(7));
      if (!user || !user.id) return reply(401, {error: 'Entre novamente na sua conta.'});
    } catch (e) {
      return reply(e.status === 401 || e.status === 403 ? 401 : 503,
        {error: e.status === 401 || e.status === 403 ? 'Sessão expirada. Entre novamente.' : 'Não foi possível verificar sua conta. Tente novamente.'});
    }
    try {
      const requested = new URL(req.url);
      const route = requested.pathname.split('/').pop();
      if (!['account', 'catalog', 'play', 'games'].includes(route)) return reply(404, {error: 'Página não encontrada.'});
      if (route === 'games') {
        const items = await query('/rest/v1/jogos_criados?select=id,title,kind,content,updated_at&user_id=eq.' + encodeURIComponent(user.id) + '&order=updated_at.desc&limit=100');
        return reply(200, {items});
      }
      const plans = await query('/rest/v1/assinaturas?select=plano,status&user_id=eq.' + encodeURIComponent(user.id) + '&limit=1');
      const plan = plans[0] || {plano: 'Grátis', status: 'inativo'};
      const active = plan.plano === 'Premium' && plan.status === 'ativo';
      if (route === 'account') return reply(200, {id: user.id, email: user.email, plano: plan.plano, status: plan.status, premium: active});
      if (route === 'catalog') {
        const offsetText = requested.searchParams.get('offset') || '0';
        if (!/^\d{1,6}$/.test(offsetText)) return reply(400, {error: 'Página inválida.'});
        const offset = Number(offsetText);
        const rows = await query('/rest/v1/videos?select=id,nome,categoria,capa_url,serie_nome,temporada,episodio,created_at&order=created_at.desc,id.desc&limit=100&offset=' + offset);
        return reply(200, {items: rows.map(row => ({...row, id: String(row.id), premium: premium(row), locked: premium(row) && !active})), next: rows.length === 100 ? offset + 100 : null});
      }
      const id = requested.searchParams.get('id') || '';
      if (!/^[1-9]\d{0,18}$/.test(id)) return reply(400, {error: 'Vídeo inválido.'});
      const rows = await query('/rest/v1/videos?select=id,nome,categoria,video_url&id=eq.' + id + '&limit=1');
      if (!rows.length) return reply(404, {error: 'Este vídeo não está mais no catálogo.'});
      const row = rows[0];
      if (premium(row) && !active) return reply(403, {error: 'Este vídeo precisa de uma assinatura Premium ativa.'});
      let media;
      try { media = new URL(row.video_url); } catch (_) { return reply(422, {error: 'O vídeo está sem um endereço válido.'}); }
      if (!['https:', 'http:'].includes(media.protocol) || media.username || media.password) return reply(422, {error: 'Endereço de vídeo não permitido.'});
      return reply(200, {id: String(row.id), nome: row.nome, url: media.href});
    } catch (_) { return reply(503, {error: 'Não foi possível carregar os dados. Tente novamente.'}); }
  };
}
