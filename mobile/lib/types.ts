/**
 * Database types matching the Supabase schema.
 * These are the TypeScript equivalents of the SQL tables in
 * supabase/migrations/001_initial.sql
 */

export type Json = string | number | boolean | null | { [key: string]: Json } | Json[];

export interface Database {
  public: {
    Tables: {
      users: {
        Row: {
          user_id: number;
          email: string;
          age: number | null;
          gender: string | null;
          height_cm: number | null;
          weight_kg: number | null;
          training_experience_months: number | null;
          fitness_level: string | null;
          athlete_type: string | null;
          primary_goal: string | null;
          created_at: string;
          updated_at: string | null;
        };
        Insert: Omit<Database['public']['Tables']['users']['Row'], 'user_id' | 'created_at'>;
        Update: Partial<Database['public']['Tables']['users']['Insert']>;
      };
      exercises: {
        Row: {
          exercise_id: number;
          exercise_name: string;
          muscle_group: string;
          exercise_type: 'compound' | 'isolation';
        };
        Insert: Omit<Database['public']['Tables']['exercises']['Row'], 'exercise_id'>;
        Update: Partial<Database['public']['Tables']['exercises']['Insert']>;
      };
      workout_sessions: {
        Row: {
          session_id: number;
          user_id: number;
          workout_type: string | null;
          gym_location: string | null;
          sleep_hours: number | null;
          energy_pre_workout: number | null;
          start_time: string;
          end_time: string | null;
          notes: string | null;
        };
        Insert: Omit<Database['public']['Tables']['workout_sessions']['Row'], 'session_id'>;
        Update: Partial<Database['public']['Tables']['workout_sessions']['Insert']>;
      };
      exercise_executions: {
        Row: {
          execution_id: number;
          session_id: number;
          exercise_id: number;
          equipment_brand: string | null;
          equipment_model: string | null;
          execution_order: number;
        };
        Insert: Omit<Database['public']['Tables']['exercise_executions']['Row'], 'execution_id'>;
        Update: Partial<Database['public']['Tables']['exercise_executions']['Insert']>;
      };
      sets: {
        Row: {
          set_id: number;
          execution_id: number;
          set_number: number;
          timestamp: string;
          weight_kg: number;
          reps: number;
          rpe: number | null;
          rir: number | null;
          rest_seconds: number | null;
        };
        Insert: Omit<Database['public']['Tables']['sets']['Row'], 'set_id'>;
        Update: Partial<Database['public']['Tables']['sets']['Insert']>;
      };
      workout_templates: {
        Row: {
          template_id: number;
          user_id: number;
          name: string;
          workout_type: string | null;
          created_at: string;
        };
        Insert: Omit<Database['public']['Tables']['workout_templates']['Row'], 'template_id' | 'created_at'>;
        Update: Partial<Database['public']['Tables']['workout_templates']['Insert']>;
      };
      template_exercises: {
        Row: {
          template_exercise_id: number;
          template_id: number;
          exercise_id: number;
          equipment_brand: string | null;
          equipment_model: string | null;
          exercise_order: number;
        };
        Insert: Omit<Database['public']['Tables']['template_exercises']['Row'], 'template_exercise_id'>;
        Update: Partial<Database['public']['Tables']['template_exercises']['Insert']>;
      };
      programs: {
        Row: {
          program_id: number;
          user_id: number;
          name: string;
          description: string | null;
          cycles: number;
          created_at: string;
        };
        Insert: Omit<Database['public']['Tables']['programs']['Row'], 'program_id' | 'created_at'>;
        Update: Partial<Database['public']['Tables']['programs']['Insert']>;
      };
      program_sessions: {
        Row: {
          program_session_id: number;
          program_id: number;
          position: number;
          template_id: number;
        };
        Insert: Omit<Database['public']['Tables']['program_sessions']['Row'], 'program_session_id'>;
        Update: Partial<Database['public']['Tables']['program_sessions']['Insert']>;
      };
      program_enrollments: {
        Row: {
          enrollment_id: number;
          user_id: number;
          program_id: number;
          enrolled_at: string;
          next_position: number;
          current_cycle: number;
          status: 'active' | 'completed' | 'paused';
        };
        Insert: Omit<Database['public']['Tables']['program_enrollments']['Row'], 'enrollment_id' | 'enrolled_at'>;
        Update: Partial<Database['public']['Tables']['program_enrollments']['Insert']>;
      };
    };
  };
}

// Convenience row types
export type UserRow = Database['public']['Tables']['users']['Row'];
export type ExerciseRow = Database['public']['Tables']['exercises']['Row'];
export type WorkoutSessionRow = Database['public']['Tables']['workout_sessions']['Row'];
export type ExecutionRow = Database['public']['Tables']['exercise_executions']['Row'];
export type SetRow = Database['public']['Tables']['sets']['Row'];
export type TemplateRow = Database['public']['Tables']['workout_templates']['Row'];
export type ProgramRow = Database['public']['Tables']['programs']['Row'];
export type EnrollmentRow = Database['public']['Tables']['program_enrollments']['Row'];

// Rich joined types used by the UI
export type ExecutionWithExercise = ExecutionRow & {
  exercise_name: string;
  muscle_group: string;
  exercise_type: 'compound' | 'isolation';
};

export type SetWithMeta = SetRow & {
  exercise_name: string;
};
