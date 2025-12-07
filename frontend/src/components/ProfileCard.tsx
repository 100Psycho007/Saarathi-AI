import { useState } from 'react';
import { UserProfile, EligibilityResponse } from '../types';
import { API_BASE_URL } from '../config';
import { formatIndianNumber, parseIndianNumber, getIncomePlaceholder } from '../utils/formatters';

interface ProfileCardProps {
  onProfileResolved: (profile: UserProfile, eligibilityResult: EligibilityResponse) => void;
}

export default function ProfileCard({ onProfileResolved }: ProfileCardProps) {
  const [formData, setFormData] = useState<UserProfile>({
    name: '',
    state: 'Karnataka',
    age: 0,
    gender: 'Prefer not to say',
    occupation: 'student',
    annual_income: 0,
    caste: 'General',
    disability: 'No',
  });

  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [incomeDisplayValue, setIncomeDisplayValue] = useState<string>('');

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    
    if (name === 'annual_income') {
      // Handle income formatting
      const numericValue = parseIndianNumber(value);
      setFormData(prev => ({
        ...prev,
        annual_income: numericValue,
      }));
      setIncomeDisplayValue(value);
    } else {
      setFormData(prev => ({
        ...prev,
        [name]: name === 'age' ? Number(value) : value,
      }));
    }
    
    // Clear validation error for this field
    if (validationErrors[name]) {
      setValidationErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[name];
        return newErrors;
      });
    }
  };

  const handleIncomeBlur = () => {
    // Format the income when user leaves the field
    if (formData.annual_income != null && formData.annual_income > 0) {
      setIncomeDisplayValue(formatIndianNumber(formData.annual_income));
    }
  };

  const handleIncomeFocus = () => {
    // Show raw number when user focuses on the field for easier editing
    if (formData.annual_income != null && formData.annual_income > 0) {
      setIncomeDisplayValue(formData.annual_income.toString());
    }
  };

  const validate = (): boolean => {
    const errors: Record<string, string> = {};

    if (!formData.name.trim()) {
      errors.name = 'Name is required';
    }

    if (formData.age <= 0 || formData.age >= 120) {
      errors.age = 'Age must be between 1 and 119';
    }

    if (formData.annual_income != null && formData.annual_income < 0) {
      errors.annual_income = 'Income cannot be negative';
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;

    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE_URL}/eligibility/check`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        throw new Error('Failed to fetch schemes');
      }

      const data: EligibilityResponse = await response.json();
      onProfileResolved(formData, data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="rounded-2xl bg-slate-900/60 backdrop-blur border border-white/10 p-6 shadow-xl">
      {error && (
        <div className="mb-4 p-3 bg-red-500/10 border border-red-500/30 rounded-lg text-red-300 text-sm">
          {error}
        </div>
      )}

      <div className="mb-6">
        <h3 className="text-2xl font-bold mb-2">Your Profile</h3>
        <p className="text-sm text-slate-400">
          We use this only to match you to schemes.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Name */}
        <div>
          <label htmlFor="name" className="block text-sm font-medium mb-2">
            Name
          </label>
          <input
            type="text"
            id="name"
            name="name"
            value={formData.name}
            onChange={handleChange}
            className="w-full px-4 py-2.5 bg-slate-800/50 border border-slate-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
            placeholder="Enter your name"
          />
          {validationErrors.name && (
            <p className="mt-1 text-xs text-red-400">{validationErrors.name}</p>
          )}
        </div>

        {/* State */}
        <div>
          <label htmlFor="state" className="block text-sm font-medium mb-2">
            State
          </label>
          <select
            id="state"
            name="state"
            value={formData.state}
            onChange={handleChange}
            className="w-full px-4 py-2.5 bg-slate-800/50 border border-slate-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
          >
            <option value="Karnataka">Karnataka</option>
            <option value="Central">Central</option>
            <option value="Other">Other</option>
          </select>
        </div>

        {/* Age */}
        <div>
          <label htmlFor="age" className="block text-sm font-medium mb-2">
            Age
          </label>
          <input
            type="number"
            id="age"
            name="age"
            value={formData.age || ''}
            onChange={handleChange}
            className="w-full px-4 py-2.5 bg-slate-800/50 border border-slate-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
            placeholder="Enter your age"
          />
          {validationErrors.age && (
            <p className="mt-1 text-xs text-red-400">{validationErrors.age}</p>
          )}
        </div>

        {/* Gender */}
        <div>
          <label htmlFor="gender" className="block text-sm font-medium mb-2">
            Gender
          </label>
          <select
            id="gender"
            name="gender"
            value={formData.gender || ''}
            onChange={handleChange}
            className="w-full px-4 py-2.5 bg-slate-800/50 border border-slate-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
          >
            <option value="Male">Male</option>
            <option value="Female">Female</option>
            <option value="Other">Other</option>
            <option value="Prefer not to say">Prefer not to say</option>
          </select>
        </div>

        {/* Occupation */}
        <div>
          <label htmlFor="occupation" className="block text-sm font-medium mb-2">
            Occupation
          </label>
          <select
            id="occupation"
            name="occupation"
            value={formData.occupation || ''}
            onChange={handleChange}
            className="w-full px-4 py-2.5 bg-slate-800/50 border border-slate-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
          >
            <option value="student">Student</option>
            <option value="farmer">Farmer</option>
            <option value="entrepreneur">Entrepreneur</option>
            <option value="other">Other</option>
          </select>
        </div>

        {/* Annual Income */}
        <div>
          <label htmlFor="annual_income" className="block text-sm font-medium mb-2">
            Annual Income (₹)
          </label>
          <input
            type="text"
            id="annual_income"
            name="annual_income"
            value={incomeDisplayValue}
            onChange={handleChange}
            onFocus={handleIncomeFocus}
            onBlur={handleIncomeBlur}
            className="w-full px-4 py-2.5 bg-slate-800/50 border border-slate-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
            placeholder={getIncomePlaceholder()}
          />
          {formData.annual_income != null && formData.annual_income > 0 && (
            <p className="mt-1 text-xs text-slate-400">
              {formData.annual_income >= 100000 
                ? `${Math.floor(formData.annual_income / 100000)} Lakh${formData.annual_income >= 200000 ? 's' : ''}`
                : formData.annual_income >= 10000000
                ? `${Math.floor(formData.annual_income / 10000000)} Crore${formData.annual_income >= 20000000 ? 's' : ''}`
                : `₹${formatIndianNumber(formData.annual_income)}`
              }
            </p>
          )}
          {validationErrors.annual_income && (
            <p className="mt-1 text-xs text-red-400">{validationErrors.annual_income}</p>
          )}
        </div>

        {/* Caste Category */}
        <div>
          <label htmlFor="caste" className="block text-sm font-medium mb-2">
            Caste Category
          </label>
          <select
            id="caste"
            name="caste"
            value={formData.caste || ''}
            onChange={handleChange}
            className="w-full px-4 py-2.5 bg-slate-800/50 border border-slate-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
          >
            <option value="General">General</option>
            <option value="SC">SC (Scheduled Caste)</option>
            <option value="ST">ST (Scheduled Tribe)</option>
            <option value="OBC">OBC (Other Backward Class)</option>
            <option value="Prefer not to say">Prefer not to say</option>
          </select>
        </div>

        {/* Disability Status */}
        <div>
          <label htmlFor="disability" className="block text-sm font-medium mb-2">
            Person with Disability
          </label>
          <select
            id="disability"
            name="disability"
            value={formData.disability || ''}
            onChange={handleChange}
            className="w-full px-4 py-2.5 bg-slate-800/50 border border-slate-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
          >
            <option value="No">No</option>
            <option value="Yes">Yes</option>
          </select>
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={loading}
          className="w-full py-3 px-6 bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600 disabled:from-slate-700 disabled:to-slate-700 disabled:cursor-not-allowed rounded-xl font-semibold transition-all duration-200 shadow-lg hover:shadow-xl"
        >
          {loading ? 'Finding schemes...' : 'Find My Schemes'}
        </button>
      </form>
    </div>
  );
}
