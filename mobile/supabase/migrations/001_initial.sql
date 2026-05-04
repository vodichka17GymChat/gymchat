-- GymChat initial schema for Supabase (PostgreSQL)
-- Run this in the Supabase SQL Editor to set up the database.
--
-- NOTE: Supabase manages auth via auth.users — we reference that table
-- rather than storing passwords ourselves. The users table here holds
-- the profile data (metrics, goals, etc.).

-- ============================================================
-- Enable UUID extension (used by Supabase auth)
-- ============================================================
create extension if not exists "uuid-ossp";

-- ============================================================
-- Users (profile data — auth is handled by Supabase auth.users)
-- ============================================================
create table if not exists public.users (
    user_id                     uuid primary key references auth.users(id) on delete cascade,
    email                       text unique not null,
    age                         integer,
    gender                      text,
    height_cm                   real,
    weight_kg                   real,
    training_experience_months  integer,
    fitness_level               text,
    athlete_type                text,
    primary_goal                text,
    created_at                  timestamptz not null default now(),
    updated_at                  timestamptz
);

-- Auto-create a users row when someone signs up via Supabase auth
create or replace function public.handle_new_user()
returns trigger language plpgsql security definer as $$
begin
  insert into public.users (user_id, email, created_at)
  values (new.id, new.email, now());
  return new;
end;
$$;

create or replace trigger on_auth_user_created
  after insert on auth.users
  for each row execute function public.handle_new_user();

-- ============================================================
-- Exercises (seeded library — read-only for users)
-- ============================================================
create table if not exists public.exercises (
    exercise_id     bigint generated always as identity primary key,
    exercise_name   text unique not null,
    muscle_group    text not null,
    exercise_type   text not null  -- 'compound' or 'isolation'
);

-- ============================================================
-- Workout sessions
-- ============================================================
create table if not exists public.workout_sessions (
    session_id          bigint generated always as identity primary key,
    user_id             uuid not null references public.users(user_id) on delete cascade,
    workout_type        text,
    gym_location        text,
    sleep_hours         real,
    energy_pre_workout  integer,
    start_time          timestamptz not null default now(),
    end_time            timestamptz,
    notes               text
);

-- ============================================================
-- Exercise executions (one per exercise per session)
-- ============================================================
create table if not exists public.exercise_executions (
    execution_id    bigint generated always as identity primary key,
    session_id      bigint not null references public.workout_sessions(session_id) on delete cascade,
    exercise_id     bigint not null references public.exercises(exercise_id),
    equipment_brand text,
    equipment_model text,
    execution_order integer not null default 1
);

-- ============================================================
-- Sets
-- ============================================================
create table if not exists public.sets (
    set_id          bigint generated always as identity primary key,
    execution_id    bigint not null references public.exercise_executions(execution_id) on delete cascade,
    set_number      integer not null,
    timestamp       timestamptz not null default now(),
    weight_kg       real not null,
    reps            integer not null,
    rpe             integer,
    rir             integer,
    rest_seconds    integer
);

-- ============================================================
-- Workout templates
-- ============================================================
create table if not exists public.workout_templates (
    template_id bigint generated always as identity primary key,
    user_id     uuid not null references public.users(user_id) on delete cascade,
    name        text not null,
    workout_type text,
    created_at  timestamptz not null default now()
);

create table if not exists public.template_exercises (
    template_exercise_id    bigint generated always as identity primary key,
    template_id             bigint not null references public.workout_templates(template_id) on delete cascade,
    exercise_id             bigint not null references public.exercises(exercise_id),
    equipment_brand         text,
    equipment_model         text,
    exercise_order          integer not null
);

-- ============================================================
-- Programs
-- ============================================================
create table if not exists public.programs (
    program_id  bigint generated always as identity primary key,
    user_id     uuid not null references public.users(user_id) on delete cascade,
    name        text not null,
    description text,
    cycles      integer not null default 1,
    created_at  timestamptz not null default now()
);

create table if not exists public.program_sessions (
    program_session_id  bigint generated always as identity primary key,
    program_id          bigint not null references public.programs(program_id) on delete cascade,
    position            integer not null,
    template_id         bigint not null references public.workout_templates(template_id)
);

create table if not exists public.program_enrollments (
    enrollment_id   bigint generated always as identity primary key,
    user_id         uuid not null references public.users(user_id) on delete cascade,
    program_id      bigint not null references public.programs(program_id) on delete cascade,
    enrolled_at     timestamptz not null default now(),
    next_position   integer not null default 1,
    current_cycle   integer not null default 1,
    status          text not null default 'active'
);

-- ============================================================
-- Indexes
-- ============================================================
create index if not exists idx_sessions_user      on public.workout_sessions(user_id);
create index if not exists idx_sessions_start     on public.workout_sessions(start_time desc);
create index if not exists idx_executions_session on public.exercise_executions(session_id);
create index if not exists idx_sets_execution     on public.sets(execution_id);
create index if not exists idx_templates_user     on public.workout_templates(user_id);
create index if not exists idx_programs_user      on public.programs(user_id);
create index if not exists idx_enrollments_user   on public.program_enrollments(user_id);

-- ============================================================
-- Row Level Security
-- ============================================================
alter table public.users                enable row level security;
alter table public.workout_sessions     enable row level security;
alter table public.exercise_executions  enable row level security;
alter table public.sets                 enable row level security;
alter table public.workout_templates    enable row level security;
alter table public.template_exercises   enable row level security;
alter table public.programs             enable row level security;
alter table public.program_sessions     enable row level security;
alter table public.program_enrollments  enable row level security;

-- Exercises are public (read-only for all authenticated users)
alter table public.exercises enable row level security;
create policy "Exercises are readable by all" on public.exercises for select using (true);

-- Users can only see and edit their own profile
create policy "Users: own row only" on public.users
  for all using (auth.uid() = user_id);

-- Workout data: own rows only
create policy "Sessions: own rows" on public.workout_sessions
  for all using (auth.uid() = user_id);

create policy "Executions: own sessions" on public.exercise_executions
  for all using (
    session_id in (select session_id from public.workout_sessions where user_id = auth.uid())
  );

create policy "Sets: own executions" on public.sets
  for all using (
    execution_id in (
      select ex.execution_id from public.exercise_executions ex
      join public.workout_sessions s on ex.session_id = s.session_id
      where s.user_id = auth.uid()
    )
  );

-- Templates and programs: own rows only
create policy "Templates: own rows" on public.workout_templates
  for all using (auth.uid() = user_id);

create policy "Template exercises: own templates" on public.template_exercises
  for all using (
    template_id in (select template_id from public.workout_templates where user_id = auth.uid())
  );

create policy "Programs: own rows" on public.programs
  for all using (auth.uid() = user_id);

create policy "Program sessions: own programs" on public.program_sessions
  for all using (
    program_id in (select program_id from public.programs where user_id = auth.uid())
  );

create policy "Enrollments: own rows" on public.program_enrollments
  for all using (auth.uid() = user_id);

-- ============================================================
-- Seed exercises (66 from the Streamlit prototype)
-- ============================================================
insert into public.exercises (exercise_name, muscle_group, exercise_type) values
  ('Barbell Bench Press','Chest','compound'),
  ('Dumbbell Bench Press','Chest','compound'),
  ('Incline Barbell Bench Press','Chest','compound'),
  ('Incline Dumbbell Press','Chest','compound'),
  ('Decline Bench Press','Chest','compound'),
  ('Chest Fly Machine','Chest','isolation'),
  ('Cable Chest Fly','Chest','isolation'),
  ('Dumbbell Fly','Chest','isolation'),
  ('Push-ups','Chest','compound'),
  ('Barbell Row','Back','compound'),
  ('Dumbbell Row','Back','compound'),
  ('Lat Pulldown','Back','compound'),
  ('Pull-ups','Back','compound'),
  ('Chin-ups','Back','compound'),
  ('Seated Cable Row','Back','compound'),
  ('T-Bar Row','Back','compound'),
  ('Deadlift','Back','compound'),
  ('Face Pulls','Back','isolation'),
  ('Overhead Press','Shoulders','compound'),
  ('Dumbbell Shoulder Press','Shoulders','compound'),
  ('Lateral Raises','Shoulders','isolation'),
  ('Front Raises','Shoulders','isolation'),
  ('Rear Delt Fly','Shoulders','isolation'),
  ('Arnold Press','Shoulders','compound'),
  ('Cable Lateral Raise','Shoulders','isolation'),
  ('Barbell Curl','Biceps','isolation'),
  ('Dumbbell Curl','Biceps','isolation'),
  ('Hammer Curl','Biceps','isolation'),
  ('Preacher Curl','Biceps','isolation'),
  ('Cable Curl','Biceps','isolation'),
  ('Concentration Curl','Biceps','isolation'),
  ('Tricep Pushdown','Triceps','isolation'),
  ('Overhead Tricep Extension','Triceps','isolation'),
  ('Skull Crushers','Triceps','isolation'),
  ('Close Grip Bench Press','Triceps','compound'),
  ('Dips','Triceps','compound'),
  ('Barbell Squat','Quads','compound'),
  ('Front Squat','Quads','compound'),
  ('Leg Press','Quads','compound'),
  ('Leg Extension','Quads','isolation'),
  ('Bulgarian Split Squat','Quads','compound'),
  ('Hack Squat','Quads','compound'),
  ('Romanian Deadlift','Hamstrings','compound'),
  ('Leg Curl','Hamstrings','isolation'),
  ('Good Mornings','Hamstrings','compound'),
  ('Nordic Curls','Hamstrings','compound'),
  ('Hip Thrust','Glutes','compound'),
  ('Glute Bridge','Glutes','compound'),
  ('Cable Kickbacks','Glutes','isolation'),
  ('Standing Calf Raise','Calves','isolation'),
  ('Seated Calf Raise','Calves','isolation'),
  ('Plank','Core','compound'),
  ('Crunches','Core','isolation'),
  ('Russian Twists','Core','isolation'),
  ('Leg Raises','Core','isolation'),
  ('Cable Crunches','Core','isolation')
on conflict (exercise_name) do nothing;
