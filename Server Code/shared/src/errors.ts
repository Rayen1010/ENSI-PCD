export enum ERRORS {
  TOKEN_EXPIRED = 'Token expired',
  BAD_TOKEN = 'Bad token',

  USER_NOT_FOUND = 'User not found',
  USER_REQUIRED_FIELDS = 'Email, username, and password are required',
  DUPLICATE_EMAIL = 'An account with this email already exists',
  DUPLICATE_USERNAME = 'An account with this username already exists',
  
  PASSWORD_INCORRECT = 'Password incorrect'
}