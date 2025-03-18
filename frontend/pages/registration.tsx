import React, { useState } from 'react';
import Layout from '../components/Layout';

const Registration: React.FC = () => {
  const [formState, setFormState] = useState({
    fullName: '',
    email: '',
    password: '',
    confirmPassword: '',
    role: '',
    sport: '',
    agreeToTerms: false
  });

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitSuccess, setSubmitSuccess] = useState(false);

  const sportOptions = [
    'Soccer',
    'Basketball',
    'Volleyball',
    'Swimming',
    'Athletics',
    'Tennis',
    'Badminton',
    'Gymnastics',
    'Martial Arts',
    'Other'
  ];

  const roleOptions = [
    { value: 'athlete', label: 'Athlete' },
    { value: 'coach', label: 'Coach' },
    { value: 'organization', label: 'Sports Organization' },
    { value: 'academy', label: 'Sports Academy' },
    { value: 'parent', label: 'Parent/Guardian' },
    { value: 'other', label: 'Other' }
  ];

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    const isCheckbox = type === 'checkbox';
    
    setFormState({
      ...formState,
      [name]: isCheckbox ? (e.target as HTMLInputElement).checked : value
    });

    // Clear error when user starts typing
    if (errors[name]) {
      setErrors({
        ...errors,
        [name]: ''
      });
    }
  };

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    // Required fields
    if (!formState.fullName.trim()) newErrors.fullName = 'Name is required';
    if (!formState.email.trim()) newErrors.email = 'Email is required';
    if (!formState.password) newErrors.password = 'Password is required';
    if (!formState.confirmPassword) newErrors.confirmPassword = 'Please confirm your password';
    if (!formState.role) newErrors.role = 'Please select your role';
    if (!formState.sport) newErrors.sport = 'Please select your primary sport';
    if (!formState.agreeToTerms) newErrors.agreeToTerms = 'You must agree to the terms and conditions';

    // Email format
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (formState.email && !emailRegex.test(formState.email)) {
      newErrors.email = 'Please enter a valid email address';
    }

    // Password strength (at least 8 characters, 1 uppercase, 1 lowercase, 1 number)
    const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$/;
    if (formState.password && !passwordRegex.test(formState.password)) {
      newErrors.password = 'Password must be at least 8 characters and include uppercase, lowercase, and numbers';
    }

    // Password match
    if (formState.password !== formState.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) return;
    
    setIsSubmitting(true);
    
    try {
      // This would normally be an API call to register the user
      await new Promise(resolve => setTimeout(resolve, 1500)); // Simulate API call
      
      // If successful
      setSubmitSuccess(true);
      
      // Reset form
      setFormState({
        fullName: '',
        email: '',
        password: '',
        confirmPassword: '',
        role: '',
        sport: '',
        agreeToTerms: false
      });
    } catch (error) {
      console.error('Registration error:', error);
      setErrors({
        ...errors,
        form: 'An error occurred during registration. Please try again.'
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Layout title="Join 3&7 - Registration">
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-2xl mx-auto">
          <h1 className="text-3xl font-bold mb-6 text-center">Join 3&7</h1>
          <p className="text-lg text-gray-600 mb-8 text-center">
            Be a part of the generational development in sport. 
            Register now to access our training management tools and performance analytics.
          </p>

          {submitSuccess ? (
            <div className="bg-green-50 border border-green-200 text-green-800 rounded-lg p-6 mb-8 text-center">
              <h2 className="text-xl font-semibold mb-3">Registration Successful!</h2>
              <p className="mb-4">Thank you for joining 3&7. Please check your email to verify your account.</p>
              <a 
                href="/login" 
                className="inline-block bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-6 rounded-lg transition-colors"
              >
                Proceed to Login
              </a>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="bg-white shadow-md rounded-lg p-6">
              {errors.form && (
                <div className="bg-red-50 border border-red-200 text-red-800 rounded p-3 mb-4">
                  {errors.form}
                </div>
              )}

              <div className="mb-4">
                <label htmlFor="fullName" className="block font-medium mb-1">Full Name</label>
                <input
                  type="text"
                  id="fullName"
                  name="fullName"
                  value={formState.fullName}
                  onChange={handleChange}
                  className={`w-full p-3 border rounded-md ${errors.fullName ? 'border-red-500' : 'border-gray-300'}`}
                  placeholder="Your full name"
                />
                {errors.fullName && <p className="text-red-500 text-sm mt-1">{errors.fullName}</p>}
              </div>

              <div className="mb-4">
                <label htmlFor="email" className="block font-medium mb-1">Email Address</label>
                <input
                  type="email"
                  id="email"
                  name="email"
                  value={formState.email}
                  onChange={handleChange}
                  className={`w-full p-3 border rounded-md ${errors.email ? 'border-red-500' : 'border-gray-300'}`}
                  placeholder="your.email@example.com"
                />
                {errors.email && <p className="text-red-500 text-sm mt-1">{errors.email}</p>}
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                <div>
                  <label htmlFor="role" className="block font-medium mb-1">I am a</label>
                  <select
                    id="role"
                    name="role"
                    value={formState.role}
                    onChange={handleChange}
                    className={`w-full p-3 border rounded-md ${errors.role ? 'border-red-500' : 'border-gray-300'}`}
                  >
                    <option value="">Select your role</option>
                    {roleOptions.map(option => (
                      <option key={option.value} value={option.value}>{option.label}</option>
                    ))}
                  </select>
                  {errors.role && <p className="text-red-500 text-sm mt-1">{errors.role}</p>}
                </div>

                <div>
                  <label htmlFor="sport" className="block font-medium mb-1">Primary Sport</label>
                  <select
                    id="sport"
                    name="sport"
                    value={formState.sport}
                    onChange={handleChange}
                    className={`w-full p-3 border rounded-md ${errors.sport ? 'border-red-500' : 'border-gray-300'}`}
                  >
                    <option value="">Select your sport</option>
                    {sportOptions.map(sport => (
                      <option key={sport} value={sport}>{sport}</option>
                    ))}
                  </select>
                  {errors.sport && <p className="text-red-500 text-sm mt-1">{errors.sport}</p>}
                </div>
              </div>

              <div className="mb-4">
                <label htmlFor="password" className="block font-medium mb-1">Password</label>
                <input
                  type="password"
                  id="password"
                  name="password"
                  value={formState.password}
                  onChange={handleChange}
                  className={`w-full p-3 border rounded-md ${errors.password ? 'border-red-500' : 'border-gray-300'}`}
                  placeholder="Create a strong password"
                />
                {errors.password ? (
                  <p className="text-red-500 text-sm mt-1">{errors.password}</p>
                ) : (
                  <p className="text-gray-500 text-xs mt-1">
                    Password must be at least 8 characters with uppercase, lowercase, and numbers
                  </p>
                )}
              </div>

              <div className="mb-6">
                <label htmlFor="confirmPassword" className="block font-medium mb-1">Confirm Password</label>
                <input
                  type="password"
                  id="confirmPassword"
                  name="confirmPassword"
                  value={formState.confirmPassword}
                  onChange={handleChange}
                  className={`w-full p-3 border rounded-md ${errors.confirmPassword ? 'border-red-500' : 'border-gray-300'}`}
                  placeholder="Confirm your password"
                />
                {errors.confirmPassword && <p className="text-red-500 text-sm mt-1">{errors.confirmPassword}</p>}
              </div>

              <div className="mb-6">
                <label className="flex items-start">
                  <input
                    type="checkbox"
                    name="agreeToTerms"
                    checked={formState.agreeToTerms}
                    onChange={handleChange}
                    className="mt-1 mr-2"
                  />
                  <span className={`text-sm ${errors.agreeToTerms ? 'text-red-500' : 'text-gray-700'}`}>
                    I agree to the <a href="/terms" className="text-blue-600 hover:underline">Terms of Service</a> and <a href="/privacy" className="text-blue-600 hover:underline">Privacy Policy</a>
                  </span>
                </label>
                {errors.agreeToTerms && <p className="text-red-500 text-sm mt-1">{errors.agreeToTerms}</p>}
              </div>

              <button
                type="submit"
                disabled={isSubmitting}
                className={`w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-4 rounded-lg transition-colors ${isSubmitting ? 'opacity-70 cursor-not-allowed' : ''}`}
              >
                {isSubmitting ? 'Processing...' : 'Create Account'}
              </button>

              <p className="text-center mt-6 text-gray-600">
                Already have an account? <a href="/login" className="text-blue-600 hover:underline">Log in</a>
              </p>
            </form>
          )}
        </div>
      </div>
    </Layout>
  );
};

export default Registration; 