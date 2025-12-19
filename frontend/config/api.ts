export const API_URL = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000';

// Define API endpoints
export const ENDPOINTS = {
  LOGIN: '/api/v1/auth/login/',              
  USER_INFO: '/api/v1/auth/user/',
  TEST: '/api/test/string/',                        
  REGISTER: '/api/v1/auth/registration/',
  LOGOUT: '/api/v1/auth/logout/',
  ME: '/api/profiles/me/',
  CALCULATE_MACROS: '/api/profiles/calculate/',
  RECIPES: '/api/recipes/',
  RATINGS: '/api/recommendations/ratings/',
  MEAL_PLANS: "/api/recommendations/meal-plans/",
};