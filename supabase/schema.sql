create table if not exists public.resultados_prueba (
  id bigint primary key generated always as identity,
  codigo_anonimo uuid not null,
  dimensiones jsonb not null default '[]'::jsonb,
  frecuencia text not null,
  duracion text not null,
  impactos jsonb not null default '[]'::jsonb,
  orientacion text not null,
  comprension text,
  utilidad integer check (utilidad between 1 and 5),
  claridad integer check (claridad between 1 and 5),
  pregunta_incomoda text,
  version_sistema text not null,
  created_at timestamptz not null default now()
);

alter table public.resultados_prueba enable row level security;

revoke all on public.resultados_prueba from anon, authenticated;
grant insert on public.resultados_prueba to anon;

create policy "anon puede insertar resultados"
on public.resultados_prueba for insert to anon
with check (true);
