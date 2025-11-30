"""
Social Authentication Providers
Token verification utilities for Google and Apple Sign-In
"""
import json
import jwt
import requests
from datetime import datetime, timedelta
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from flask import current_app
from functools import lru_cache


# ==================== Google Sign-In ====================

def verify_google_token(token_string):
    """
    Verify Google ID token and extract user information
    
    Args:
        token_string (str): Google ID token from client
    
    Returns:
        dict: User info with keys: user_id, email, name, verified_email
        None: If verification fails
    """
    try:
        client_id = current_app.config.get('GOOGLE_CLIENT_ID')
        
        if not client_id:
            print("⚠️  Google Client ID not configured")
            return None
        
        # Verify the token with Google
        idinfo = id_token.verify_oauth2_token(
            token_string, 
            google_requests.Request(), 
            client_id
        )
        
        # Verify the issuer
        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            print(f"⚠️  Invalid issuer: {idinfo['iss']}")
            return None
        
        # Token is valid, return user info
        return {
            'user_id': idinfo['sub'],  # Google user ID (unique)
            'email': idinfo.get('email', ''),
            'name': idinfo.get('name', ''),
            'verified_email': idinfo.get('email_verified', False)
        }
        
    except ValueError as e:
        # Invalid token
        print(f"❌ Google token verification failed: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error verifying Google token: {e}")
        return None


# ==================== Apple Sign-In ====================

@lru_cache(maxsize=1)
def get_apple_public_keys():
    """
    Fetch Apple's public keys for token verification
    Cached to avoid repeated API calls
    
    Returns:
        list: Apple's public keys
    """
    try:
        response = requests.get('https://appleid.apple.com/auth/keys', timeout=10)
        response.raise_for_status()
        return response.json()['keys']
    except Exception as e:
        print(f"❌ Failed to fetch Apple public keys: {e}")
        return []


def verify_apple_token(token_string):
    """
    Verify Apple identity token and extract user information
    
    Args:
        token_string (str): Apple identity token from client
    
    Returns:
        dict: User info with keys: user_id, email
        None: If verification fails
    """
    try:
        client_id = current_app.config.get('APPLE_CLIENT_ID')
        
        if not client_id:
            print("⚠️  Apple Client ID not configured")
            return None
        
        # Get Apple's public keys
        keys = get_apple_public_keys()
        if not keys:
            print("❌ Could not retrieve Apple public keys")
            return None
        
        # Decode the header to get the key ID
        header = jwt.get_unverified_header(token_string)
        kid = header.get('kid')
        
        if not kid:
            print("❌ Token missing 'kid' in header")
            return None
        
        # Find the matching public key
        key = next((k for k in keys if k['kid'] == kid), None)
        if not key:
            print(f"❌ No matching key found for kid: {kid}")
            return None
        
        # Convert JWK to PEM format for PyJWT
        from jwt.algorithms import RSAAlgorithm
        public_key = RSAAlgorithm.from_jwk(json.dumps(key))
        
        # Verify and decode the token
        decoded = jwt.decode(
            token_string,
            public_key,
            algorithms=['RS256'],
            audience=client_id,
            issuer='https://appleid.apple.com'
        )
        
        # Check expiration
        exp = decoded.get('exp')
        if exp and datetime.fromtimestamp(exp) < datetime.utcnow():
            print("❌ Apple token has expired")
            return None
        
        # Return user info
        return {
            'user_id': decoded['sub'],  # Apple user identifier (unique)
            'email': decoded.get('email', ''),  # May be private relay email
        }
        
    except jwt.ExpiredSignatureError:
        print("❌ Apple token has expired")
        return None
    except jwt.InvalidTokenError as e:
        print(f"❌ Invalid Apple token: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error verifying Apple token: {e}")
        return None


# ==================== Helper Functions ====================

def clear_apple_keys_cache():
    """Clear the cached Apple public keys (useful for testing)"""
    get_apple_public_keys.cache_clear()
    print("✅ Apple keys cache cleared")


def validate_social_auth_config():
    """
    Validate that social authentication configuration is set up correctly
    
    Returns:
        dict: Configuration status for each provider
    """
    google_configured = bool(current_app.config.get('GOOGLE_CLIENT_ID'))
    apple_configured = bool(
        current_app.config.get('APPLE_CLIENT_ID') and
        current_app.config.get('APPLE_TEAM_ID') and
        current_app.config.get('APPLE_KEY_ID')
    )
    
    return {
        'google': {
            'configured': google_configured,
            'client_id': current_app.config.get('GOOGLE_CLIENT_ID', '')[:20] + '...' if google_configured else 'Not set'
        },
        'apple': {
            'configured': apple_configured,
            'client_id': current_app.config.get('APPLE_CLIENT_ID', 'Not set')
        }
    }
