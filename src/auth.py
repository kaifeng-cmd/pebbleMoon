from .database import Database
from supabase_auth.errors import AuthApiError, AuthError


class Auth:
	def __init__(self) -> None:
		self.db = Database()

	def check_email_exists(self, email: str) -> bool:
		"""
		Check if an email is already registered using a sign-in attempt.
		This is the most reliable method when using an anon key.
		"""
		try:
			"""
			IMPORTANT: 
			The Supabase anon key is a public API key, not an authentication token, 
			and therefore cannot be used to check authentication or 
			identify a specific user (ex. check unique email).
			Since this's just a small app, so let it be.
			"""
			# Attempting to sign in with a dummy password.
			# If it raises "Invalid login credentials", the user does not exist.
			# For other auth errors (like "Email not confirmed"), the user exists.
			self.db.client.auth.sign_in_with_password({"email": email, "password": "dummy_password"})
			# If no error is raised, it implies the user exists.
			return True
		except AuthApiError as e:
			# Supabase returns "Invalid login credentials" for non-existent emails.
			if "invalid login credentials" in str(e).lower():
				return False  # Email does not exist.
			# Any other AuthApiError implies the user exists (e.g., "Email not confirmed").
			return True
		except Exception:
			# For any other unexpected error, assume the user exists to be safe.
			return True

	def sign_up(self, email: str, password: str):
		# First check if email already exists
		if self.check_email_exists(email):
			raise AuthError("This email is already registered. Please use a different email or try logging in.")
		
		try:
			# Attempt to sign up - let Supabase handle the registration
			result = self.db.client.auth.sign_up({"email": email, "password": password})
			return result
		except AuthApiError as e:
			error_msg = str(e).lower()
			# Provide more specific error messages for common registration issues
			if "email already registered" in error_msg or "email has already been taken" in error_msg:
				raise AuthError("This email is already registered. Please use a different email or try logging in.")
			elif "password is too weak" in error_msg:
				raise AuthError("Password is too weak. Please choose a stronger password.")
			elif "invalid email" in error_msg:
				raise AuthError("Invalid email address. Please enter a valid email.")
			else:
				raise AuthError(f"{e}")
		except Exception as e:
			raise AuthError(f"Unexpected error during registration: {e}")

	def sign_in(self, email: str, password: str):
		try:
			return self.db.client.auth.sign_in_with_password({"email": email, "password": password})
		except AuthApiError as e:
			raise AuthError(f"Invalid email or password")
		except Exception as e:
			raise AuthError(f"Unexpected error during login: {e}")

	def sign_out(self) -> None:
		try:
			self.db.client.auth.sign_out()
		except Exception as e:
			print(f"Error during sign out: {e}")

	def get_current_user(self):
		try:
			return self.db.client.auth.get_user()
		except Exception as e:
			print(f"Error getting current user: {e}")
			return None


class AuthError(Exception):
	pass
