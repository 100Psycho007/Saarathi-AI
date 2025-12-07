export interface UserProfile {
  name: string;
  state: string;
  age: number;
  gender?: string | null;
  occupation?: string | null;
  annual_income?: number | null;
  caste?: string | null;
  disability?: string | null;
}

export interface Scheme {
  id: number;
  name: string;
  short_description: string;
  category: string;
  state: string;
  official_link: string;
  application_process?: string;
  min_age?: number;
  max_age?: number;
  max_income?: number;
  occupation?: string;
  gender?: string;
  caste?: string;
  disability?: string;
}

export interface EligibilityResponse {
  eligible_schemes: Scheme[];
  ineligible_schemes: Scheme[];
  user_profile: UserProfile;
}
export interface AssistantResponse {
  answer: string;
  suggested_schemes?: Scheme[];
}

export interface AdminStats {
  totalSchemes: number;
  schemesByState: Record<string, number>;
  schemesByCategory: Record<string, number>;
}

export interface AIExtractionResult {
  scheme_id: number;
  scheme_name: string;
  status: 'success' | 'error' | 'skipped';
  extracted?: {
    min_age?: number;
    max_age?: number;
    min_income?: number;
    max_income?: number;
    occupation?: string;
  };
  reason?: string;
}

export interface SyncResult {
  status: string;
  state: string;
  inserted: number;
  updated: number;
}