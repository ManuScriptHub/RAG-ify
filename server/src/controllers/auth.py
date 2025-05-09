from models.auth import AuthModel
from fastapi import HTTPException

auth_model = AuthModel()

def register_user_controller(user_data):
    """
    Controller function to register a new user.
    
    Args:
        user_data (dict): Dictionary containing username, email, and password
        
    Returns:
        dict: Response with user data or error message
    """
    if not user_data or not isinstance(user_data, dict):
        raise HTTPException(status_code=400, detail="Invalid user data format")
    
    username = user_data.get("username")
    email = user_data.get("email")
    password = user_data.get("password")
    
    if not username or not email or not password:
        raise HTTPException(status_code=400, detail="Username, email, and password are required")
    
    response = auth_model.register_user(username, email, password)
    
    if "error" in response:
        status_code = response.get("status_code", 500)
        raise HTTPException(status_code=status_code, detail=response["error"])
    
    return response

def login_user_controller(login_data):
    """
    Controller function to authenticate a user.
    
    Args:
        login_data (dict): Dictionary containing email and password
        
    Returns:
        dict: Response with user data or error message
    """
    if not login_data or not isinstance(login_data, dict):
        raise HTTPException(status_code=400, detail="Invalid login data format")
    
    email = login_data.get("email")
    password = login_data.get("password")
    
    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password are required")
    
    response = auth_model.login_user(email, password)
    
    if "error" in response:
        status_code = response.get("status_code", 500)
        raise HTTPException(status_code=status_code, detail=response["error"])
    
    return response

def change_password_controller(change_data):
    """
    Controller function to change a user's password.
    
    Args:
        change_data (dict): Dictionary containing userId, currentPassword, and newPassword
        
    Returns:
        dict: Response with success message or error
    """
    if not change_data or not isinstance(change_data, dict):
        raise HTTPException(status_code=400, detail="Invalid data format")
    
    user_id = change_data.get("userId")
    current_password = change_data.get("currentPassword")
    new_password = change_data.get("newPassword")
    
    if not user_id or not current_password or not new_password:
        raise HTTPException(status_code=400, detail="User ID, current password, and new password are required")
    
    response = auth_model.change_password(user_id, current_password, new_password)
    
    if "error" in response:
        status_code = response.get("status_code", 500)
        raise HTTPException(status_code=status_code, detail=response["error"])
    
    return response

def reset_password_request_controller(reset_data):
    """
    Controller function to request a password reset.
    
    Args:
        reset_data (dict): Dictionary containing email
        
    Returns:
        dict: Response with success message
    """
    if not reset_data or not isinstance(reset_data, dict):
        raise HTTPException(status_code=400, detail="Invalid data format")
    
    email = reset_data.get("email")
    
    if not email:
        raise HTTPException(status_code=400, detail="Email is required")
    
    response = auth_model.reset_password_request(email)
    
    if "error" in response:
        status_code = response.get("status_code", 500)
        raise HTTPException(status_code=status_code, detail=response["error"])
    
    return response