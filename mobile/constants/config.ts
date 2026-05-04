/** App-wide constants — mirrors Python config.py */

export const APP_NAME = 'GymChat';

export const WORKOUT_TYPES = [
  'Push', 'Pull', 'Legs', 'Upper', 'Lower', 'Full Body', 'Other',
] as const;

export const MUSCLE_GROUPS = [
  'Chest', 'Back', 'Shoulders', 'Biceps', 'Triceps',
  'Quads', 'Hamstrings', 'Glutes', 'Calves', 'Core',
] as const;

export const EXERCISE_TYPES = ['compound', 'isolation'] as const;

export const ATHLETE_TYPES = [
  'Powerlifter',
  'Bodybuilder / Hypertrophy',
  'General strength',
  'CrossFit / Conditioning',
  'Endurance athlete',
  'General fitness',
] as const;

export const PRIMARY_GOALS = [
  'Muscle Growth (Hypertrophy)',
  'Strength',
  'Endurance',
  'Weight Loss',
  'General Fitness',
] as const;

export const FITNESS_LEVELS = [
  'Beginner', 'Intermediate', 'Advanced', 'Elite',
] as const;

export const GENDERS = ['Male', 'Female', 'Other'] as const;

// Validation ranges
export const WEIGHT_KG_MIN = 0;
export const WEIGHT_KG_MAX = 500;
export const REPS_MIN = 1;
export const REPS_MAX = 100;
export const RPE_MIN = 1;
export const RPE_MAX = 10;
export const RIR_MIN = 0;
export const RIR_MAX = 10;
export const DEFAULT_REST_SECONDS = 90;
