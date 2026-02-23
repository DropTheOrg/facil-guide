// POST /api/feedback - stores guide feedback in Supabase
export async function onRequestPost(context) {
  try {
    const body = await context.request.json();
    const { slug, vote, lang } = body;

    if (!slug || !vote || !['yes', 'no'].includes(vote)) {
      return new Response(JSON.stringify({ error: 'missing or invalid fields' }), {
        status: 400,
        headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
      });
    }


    const supabaseUrl = context.env.SUPABASE_URL || 'https://ksrbnzyyyzanqmqmfvtx.supabase.co';
    const supabaseKey = context.env.SUPABASE_SERVICE_KEY;

    if (supabaseKey) {
      const res = await fetch(`${supabaseUrl}/rest/v1/facil_feedback`, {
        method: 'POST',
        headers: {
          'apikey': supabaseKey,
          'Authorization': `Bearer ${supabaseKey}`,
          'Content-Type': 'application/json',
          'Prefer': 'return=minimal',
        },
        body: JSON.stringify({
          slug,
          vote,
          lang: lang || 'en',
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
      const key = `feedback:${slug}`;
      const existing = await kv.get(key, 'json') || { yes: 0, no: 0 };
      existing[vote] = (existing[vote] || 0) + 1;
      await kv.put(key, JSON.stringify(existing));
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
