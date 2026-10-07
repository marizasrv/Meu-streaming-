-- Games are private to the authenticated account. Existing tables are untouched.
create table public.jogos_criados (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references auth.users(id) on delete cascade,
    title text not null check (char_length(btrim(title)) between 1 and 80),
    kind text not null check (kind in ('memory', 'quiz')),
    content jsonb not null check (jsonb_typeof(content) = 'object' and octet_length(content::text) <= 65536),
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    constraint game_content_shape check (coalesce((
      (kind = 'memory' and jsonb_typeof(content->'items') = 'array'
       and jsonb_array_length(content->'items') between 2 and 12)
      or (kind = 'quiz' and jsonb_typeof(content->'questions') = 'array'
       and jsonb_array_length(content->'questions') between 1 and 20)
    ), false))
);
create index jogos_criados_owner_updated on public.jogos_criados (user_id, updated_at desc);
alter table public.jogos_criados enable row level security;
revoke all on public.jogos_criados from public, anon;
grant select, insert, update on public.jogos_criados to authenticated;
grant all on public.jogos_criados to service_role;
create policy games_read_own on public.jogos_criados for select to authenticated
  using ((select auth.uid()) = user_id);
create policy games_insert_own on public.jogos_criados for insert to authenticated
  with check ((select auth.uid()) = user_id);
create policy games_update_own on public.jogos_criados for update to authenticated
  using ((select auth.uid()) = user_id) with check ((select auth.uid()) = user_id);
