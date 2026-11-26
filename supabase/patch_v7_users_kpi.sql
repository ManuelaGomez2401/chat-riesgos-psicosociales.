begin;

create type public.app_role as enum ('participant', 'reviewer', 'admin');

create table if not exists public.profiles (
    id uuid primary key references auth.users(id) on delete cascade,
    display_name text,
    role public.app_role not null default 'participant',
    organization_code text,
    active boolean not null default true,
    created_at timestamptz not null default now(),
    last_login_at timestamptz
);

alter table public.sessions
    add column if not exists user_id uuid references auth.users(id) on delete set null;

create index if not exists idx_sessions_user_id on public.sessions(user_id);
create index if not exists idx_sessions_started_at on public.sessions(started_at);
create index if not exists idx_messages_session_id on public.messages(session_id);
create index if not exists idx_results_session_id on public.results(session_id);
create index if not exists idx_gemini_usage_created_at on public.gemini_usage(created_at);

create or replace function public.handle_new_user()
returns trigger
language plpgsql
security definer set search_path = public
as $$
begin
    insert into public.profiles(id, display_name, role)
    values (
        new.id,
        coalesce(new.raw_user_meta_data ->> 'display_name', split_part(new.email, '@', 1)),
        'participant'
    )
    on conflict (id) do nothing;
    return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
after insert on auth.users
for each row execute procedure public.handle_new_user();

insert into public.profiles(id, display_name)
select id, coalesce(raw_user_meta_data ->> 'display_name', split_part(email, '@', 1))
from auth.users
on conflict (id) do nothing;

create or replace function public.current_app_role()
returns public.app_role
language sql
stable
security definer set search_path = public
as $$
    select coalesce((select role from public.profiles where id = auth.uid() and active = true), 'participant'::public.app_role);
$$;

create or replace function public.is_reviewer_or_admin()
returns boolean
language sql
stable
security definer set search_path = public
as $$
    select public.current_app_role() in ('reviewer'::public.app_role, 'admin'::public.app_role);
$$;

alter table public.profiles enable row level security;

revoke all on public.profiles from anon;
grant select, update on public.profiles to authenticated;

create policy "profile_select_own"
on public.profiles for select
to authenticated
using (id = auth.uid());

create policy "profile_update_own_name"
on public.profiles for update
to authenticated
using (id = auth.uid())
with check (id = auth.uid());

-- El usuario solo ve sus sesiones. Reviewer/admin acceden desde el panel servidor con secret key.
drop policy if exists "sessions_select_own" on public.sessions;
create policy "sessions_select_own"
on public.sessions for select
to authenticated
using (user_id = auth.uid());

drop policy if exists "sessions_insert_authenticated" on public.sessions;
create policy "sessions_insert_authenticated"
on public.sessions for insert
to authenticated
with check (user_id = auth.uid());

grant select, insert on public.sessions to authenticated;
grant select on public.results to authenticated;

-- Results se filtra mediante la sesión propietaria.
drop policy if exists "results_select_own" on public.results;
create policy "results_select_own"
on public.results for select
to authenticated
using (
    exists (
        select 1 from public.sessions s
        where s.id = results.session_id
          and s.user_id = auth.uid()
    )
);

create or replace function public.get_my_kpis(p_start date, p_end date)
returns jsonb
language sql
stable
security definer set search_path = public
as $$
with mine as (
    select s.id, s.status, s.started_at, r.dimensions, r.orientation
    from public.sessions s
    left join public.results r on r.session_id = s.id
    where s.user_id = auth.uid()
      and s.started_at >= p_start::timestamptz
      and s.started_at < (p_end + 1)::timestamptz
), dim_counts as (
    select d, count(*)::int n
    from mine, lateral unnest(coalesce(dimensions, array[]::text[])) d
    group by d
), ori_counts as (
    select orientation o, count(*)::int n
    from mine
    where orientation is not null
    group by orientation
)
select jsonb_build_object(
    'total_sessions', (select count(*) from mine),
    'completed_sessions', (select count(*) from mine where status in ('completed','finished','fin')),
    'completion_rate', case when (select count(*) from mine)=0 then 0 else round(100.0*(select count(*) from mine where status in ('completed','finished','fin'))/(select count(*) from mine),1) end,
    'dimensions', coalesce((select jsonb_object_agg(d,n) from dim_counts), '{}'::jsonb),
    'orientations', coalesce((select jsonb_object_agg(o,n) from ori_counts), '{}'::jsonb)
);
$$;

grant execute on function public.get_my_kpis(date,date) to authenticated;

create or replace function public.get_admin_kpis(p_start date, p_end date)
returns jsonb
language plpgsql
stable
security definer set search_path = public
as $$
declare
    result jsonb;
begin
    if not public.is_reviewer_or_admin() then
        raise exception 'not authorized';
    end if;

    with scoped_sessions as (
        select s.id, s.user_id, s.status, s.started_at, r.dimensions, r.orientation
        from public.sessions s
        left join public.results r on r.session_id = s.id
        where s.started_at >= p_start::timestamptz
          and s.started_at < (p_end + 1)::timestamptz
    ), dim_counts as (
        select d, count(*)::int n
        from scoped_sessions, lateral unnest(coalesce(dimensions, array[]::text[])) d
        group by d
    ), ori_counts as (
        select orientation o, count(*)::int n
        from scoped_sessions where orientation is not null
        group by orientation
    ), gemini as (
        select count(*) total, count(*) filter (where success) ok
        from public.gemini_usage
        where created_at >= p_start::timestamptz
          and created_at < (p_end + 1)::timestamptz
    )
    select jsonb_build_object(
        'active_users', (select count(distinct user_id) from scoped_sessions where user_id is not null),
        'total_sessions', (select count(*) from scoped_sessions),
        'completed_sessions', (select count(*) from scoped_sessions where status in ('completed','finished','fin')),
        'completion_rate', case when (select count(*) from scoped_sessions)=0 then 0 else round(100.0*(select count(*) from scoped_sessions where status in ('completed','finished','fin'))/(select count(*) from scoped_sessions),1) end,
        'gemini_success_rate', case when (select total from gemini)=0 then 0 else round(100.0*(select ok from gemini)/(select total from gemini),1) end,
        'pending_proposals', (select count(*) from public.dictionary_proposals where status='pending'),
        'approved_proposals', (select count(*) from public.dictionary_proposals where status='approved'),
        'rejected_proposals', (select count(*) from public.dictionary_proposals where status='rejected'),
        'sessions_without_dimension', (select count(*) from scoped_sessions where coalesce(cardinality(dimensions),0)=0),
        'dimensions', coalesce((select jsonb_object_agg(d,n) from dim_counts), '{}'::jsonb),
        'orientations', coalesce((select jsonb_object_agg(o,n) from ori_counts), '{}'::jsonb)
    ) into result;
    return result;
end;
$$;

grant execute on function public.get_admin_kpis(date,date) to authenticated;

commit;
