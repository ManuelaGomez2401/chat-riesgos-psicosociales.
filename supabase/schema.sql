create extension if not exists pgcrypto;
create table if not exists public.sessions(id uuid primary key default gen_random_uuid(), public_code uuid not null unique default gen_random_uuid(), app_version text not null, consent_store boolean not null default false, consent_ai boolean not null default false, consent_learning boolean not null default false, status text not null default 'active', started_at timestamptz not null default now(), ended_at timestamptz);
create table if not exists public.messages(id bigint generated always as identity primary key, session_id uuid not null references public.sessions(id) on delete cascade, role text not null check(role in('user','assistant')), anonymized_text text not null, stage text not null, used_ai boolean not null default false, sequence_no integer not null, created_at timestamptz not null default now());
create table if not exists public.results(session_id uuid primary key references public.sessions(id) on delete cascade, relationship text, dimensions jsonb not null default '[]', frequency text, duration text, impacts jsonb not null default '[]', orientation text, rule_version text, created_at timestamptz not null default now());
create table if not exists public.feedback(id bigint generated always as identity primary key, session_id uuid not null references public.sessions(id) on delete cascade, understood text, clarity integer check(clarity between 1 and 5), usefulness integer check(usefulness between 1 and 5), comment text, created_at timestamptz not null default now());
create table if not exists public.dictionary_entries(id bigint generated always as identity primary key, expression text not null unique, variants text not null default '', dimension text not null, question text not null, status text not null default 'active', source text not null default 'manual', reviewed_by text, reviewed_at timestamptz, created_at timestamptz not null default now());
create table if not exists public.dictionary_proposals(id bigint generated always as identity primary key, session_id uuid references public.sessions(id) on delete set null, expression text not null, dimensions jsonb not null default '[]', evidence text, status text not null default 'pending', reviewed_by text, reviewed_at timestamptz, created_at timestamptz not null default now());

alter table public.sessions enable row level security;alter table public.messages enable row level security;alter table public.results enable row level security;alter table public.feedback enable row level security;alter table public.dictionary_entries enable row level security;alter table public.dictionary_proposals enable row level security;
revoke all on all tables in schema public from anon,authenticated;
grant insert on public.sessions,public.messages,public.results,public.feedback,public.dictionary_proposals to anon;
grant select on public.dictionary_entries to anon;
create policy "insert sessions" on public.sessions for insert to anon with check(true);
create policy "insert messages" on public.messages for insert to anon with check(true);
create policy "insert results" on public.results for insert to anon with check(true);
create policy "insert feedback" on public.feedback for insert to anon with check(true);
create policy "insert proposals" on public.dictionary_proposals for insert to anon with check(true);
create policy "read active dictionary" on public.dictionary_entries for select to anon using(status='active');

insert into public.dictionary_entries(expression,variants,dimension,question) values
('no doy abasto','no doi abasto|no alcanzo|no me da el tiempo','carga laboral','¿Qué tareas o plazos están generando mayor presión?'),
('mis horarios son muy largos','trabajo muchas horas|tengo jornadas largas|salgo muy tarde','jornada y desconexión','¿Qué tan extensa suele ser tu jornada?'),
('me tratan mal','me hablan mal|me humillan|me gritan|me hostiga','relaciones y liderazgo','¿Qué comportamientos concretos han ocurrido?'),
('no me escuchan','no me apoyan|me ignoran','apoyo social y liderazgo','¿Qué apoyo solicitaste y qué respuesta recibiste?')
on conflict(expression) do nothing;
