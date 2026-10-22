create table if not exists public.sesiones_revision(
 id bigint generated always as identity primary key,
 codigo_anonimo uuid not null,
 mensajes jsonb not null,
 dimensiones jsonb not null default '[]'::jsonb,
 orientacion text,
 retroalimentacion text,
 version text not null,
 revisada boolean not null default false,
 etiquetas_profesionales jsonb not null default '{}'::jsonb,
 propuesta_diccionario jsonb not null default '{}'::jsonb,
 created_at timestamptz not null default now()
);
alter table public.sesiones_revision enable row level security;
revoke all on public.sesiones_revision from anon,authenticated;
grant insert on public.sesiones_revision to anon;
create policy "insertar sesión autorizada" on public.sesiones_revision for insert to anon with check(true);
