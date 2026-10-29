-- Ejecutar una vez después de schema.sql.
-- Las tablas con columnas identity utilizan secuencias internas.
-- El rol anon necesita USAGE para insertar filas.
grant usage, select on all sequences in schema public to anon;

-- Mantener permisos de inserción requeridos por el prototipo académico.
grant insert on public.sessions to anon;
grant insert on public.messages to anon;
grant insert on public.results to anon;
grant insert on public.feedback to anon;
grant insert on public.dictionary_proposals to anon;
grant select on public.dictionary_entries to anon;

-- Las políticas se recrean de forma idempotente para evitar instalaciones parciales.
drop policy if exists "insert sessions" on public.sessions;
create policy "insert sessions" on public.sessions for insert to anon with check (true);

drop policy if exists "insert messages" on public.messages;
create policy "insert messages" on public.messages for insert to anon with check (true);

drop policy if exists "insert results" on public.results;
create policy "insert results" on public.results for insert to anon with check (true);

drop policy if exists "insert feedback" on public.feedback;
create policy "insert feedback" on public.feedback for insert to anon with check (true);

drop policy if exists "insert proposals" on public.dictionary_proposals;
create policy "insert proposals" on public.dictionary_proposals for insert to anon with check (true);

drop policy if exists "read active dictionary" on public.dictionary_entries;
create policy "read active dictionary" on public.dictionary_entries for select to anon using (status = 'active');
