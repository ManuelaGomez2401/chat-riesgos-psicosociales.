-- Ejecutar después de schema.sql y patch_storage_fix.sql.
-- Registro de uso de Gemini para respetar límites académicos.
create table if not exists public.gemini_usage (
  id bigint generated always as identity primary key,
  session_id uuid references public.sessions(id) on delete set null,
  stage text not null,
  model text not null,
  input_chars integer not null default 0,
  output_chars integer not null default 0,
  success boolean not null default true,
  created_at timestamptz not null default now()
);
alter table public.gemini_usage enable row level security;
revoke all on public.gemini_usage from anon, authenticated;
-- No se crean políticas públicas. Solo la secret/service role puede leer y escribir esta tabla.

grant usage, select on all sequences in schema public to anon;
