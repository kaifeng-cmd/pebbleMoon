from .database import Database
from supabase_auth.errors import AuthApiError, AuthError


class Auth:
	def __init__(self) -> None:
		self.db = Database()

	def check_email_exists(self, email: str) -> bool:
		"""Check if an email is already registered by attempting to sign in"""
		try:
			# Try to sign in with the email and a dummy password
			# If the email exists, we'll get either a successful login or an email verification error
			# If the email doesn't exist, we'll get "invalid credentials" error
			self.db.client.auth.sign_in_with_password({"email": email, "password": "dummy_check"})
			return True  # Email exists and is verified
		except AuthApiError as e:
			error_msg = str(e).lower()
			# If we get "email not confirmed" error, the email exists but isn't verified
			if "email not confirmed" in error_msg or "email confirmation" in error_msg:
				return True  # Email exists but needs verification
			# If we get "invalid credentials" error, the email doesn't exist
			elif "invalid credentials" in error_msg or "invalid email or password" in error_msg:
				return False  # Email doesn't exist
			else:
				# For other errors, we'll assume the email might exist to be safe
				return True
		except Exception as e:
			# For unexpected errors, we'll assume the email might exist to be safe
			print(f"Unexpected error checking email existence: {e}")
			return True

	def sign_up(self, email: str, password: str):
		# First check if email already exists
		if self.check_email_exists(email):
			raise AuthError("This email is already registered. Please use a different email or try logging in.")
		
		try:
			return self.db.client.auth.sign_up({"email": email, "password": password})
		except AuthApiError as e:
			raise AuthError(f"Registration failed: {e}")
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
