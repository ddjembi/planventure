from flask_jwt_extended import create_access_token, create_refresh_token
from datetime import timedelta
from typing import Dict, Optional


def generate_tokens(user_id: int, additional_claims: Optional[Dict] = None) -> Dict[str, str]:
    """
    Generate access and refresh tokens for a user.
    
    Args:
        user_id: The user's ID
        additional_claims: Optional additional claims to include in the token
        
    Returns:
        Dictionary containing access_token and refresh_token
    """
    identity = str(user_id)
    
    # Create access token (1 hour)
    access_token = create_access_token(
        identity=identity,
        additional_claims=additional_claims or {},
        expires_delta=timedelta(hours=1)
    )
    
    # Create refresh token (30 days)
    refresh_token = create_refresh_token(
        identity=identity,
        additional_claims=additional_claims or {},
        expires_delta=timedelta(days=30)
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "Bearer"
    }


def generate_access_token(user_id: int, additional_claims: Optional[Dict] = None) -> str:
    """
    Generate only an access token for a user.
    
    Args:
        user_id: The user's ID
        additional_claims: Optional additional claims to include in the token
        
    Returns:
        Access token string
    """
    identity = str(user_id)
    return create_access_token(
        identity=identity,
        additional_claims=additional_claims or {},
        expires_delta=timedelta(hours=1)
    )
