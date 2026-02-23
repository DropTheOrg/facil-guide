// POST /api/guide-request - stores guide requests in Supabase
export async function onRequestPost(context) {
  try {
    const body = await context.request.json();
    const { email, description, lang, slug } = body;

    if (!description) {
      return new Response(JSON.stringify({ error: 'missing description' }), {
        status: 400,
        headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
      });
    }

    const ip = context.request.headers.get('cf-connecting-ip') || '';

    const supabaseUrl = context.env.SUPABASE_URL || 'https://ksrbnzyyyzanqmqmfvtx.supabase.co';
    const supabaseKey = context.env.SUPABASE_SERVICE_KEY;

    if (supabaseKey) {
      const res = await fetch(`${supabaseUrl}/rest/v1/facil_guide_requests`, {
        method: 'POST',
        headers: {
          'apikey': supabaseKey,
          'Authorization': `Bearer ${supabaseKey}`,
          'Content-Type': 'application/json',
          'Prefer': 'return=minimal',
        },
        body: JSON.stringify({
          description,
          email: email || null,
          lang: lang || 'en',
          slug: slug || null,
          ip,
        }),
      });

      if (!res.ok) {
        const err = await res.text();
        console.error('Supabase error:', err);
        return new Response(JSON.stringify({ ok: false, error: 'db error' }), {
          status: 500,
          headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
        });
      }

      return new Response(JSON.stringify({ ok: true }), {
        headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
      });
    }

    // Fallback: KV
    const kv = context.env.FACIL_DATA;
    if (kv) {
      const id = Date.now().toString(36) + Math.random().toString(36).slice(2, 6);
      await kv.put(`request:${id}`, JSON.stringify({ email: email || '', description, lang: lang || 'en', ts: new Date().toISOString() }));
      const list = await kv.get('request:_index', 'json') || [];
      list.push(id);
      await kv.put('request:_index', JSON.stringify(list));
    }

    return new Response(JSON.stringify({ ok: true, stored: !!kv }), {
      headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
    });
  } catch (e) {
    return new Response(JSON.stringify({ error: e.message }), {
      status: 500,
      headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
    });
  }
}

export async function onRequestOptions() {
  return new Response(null, {
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    },
  });
}
