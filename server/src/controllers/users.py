from models.users import UserModel
from fastapi import HTTPException
from fastapi import HTTPException

user_data = UserModel()

def get_users_data(where_conditions=None):
    response = user_data.get_users(where_conditions)
    
    if "error" in response:
        status_code = response.get("status_code", 500)
        raise HTTPException(status_code=status_code, detail=response["error"])
    
    # Ensure response has a "results" key with a list value
    if "results" in response and not isinstance(response["results"], list):
        response["results"] = [response["results"]] if response["results"] is not None else []
    
    return response
    
    if "error" in response:
        status_code = response.get("status_code", 500)
        raise HTTPException(status_code=status_code, detail=response["error"])
    
    return response

def get_user_data(userId):
    response = user_data.get_user(userId)
    
    if "error" in response:
        status_code = response.get("status_code", 500)
        raise HTTPException(status_code=status_code, detail=response["error"])
    
    # Ensure response has a "results" key with a list value
    if "results" in response and not isinstance(response["results"], list):
        response["results"] = [response["results"]] if response["results"] is not None else []
    
    response = response
    
    if "error" in response:
        status_code = response.get("status_code", 500)
        raise HTTPException(status_code=status_code, detail=response["error"])
    
    return response

def create_user_data(user_data_input):
    response = user_data.create_user(user_data_input)
    
    if "error" in response:
        status_code = response.get("status_code", 500)
        raise HTTPException(status_code=status_code, detail=response["error"])
    
    return response

def update_user_data(user_data_input, userId):
    response = user_data.update_user(user_data_input, userId)
    
    if "error" in response:
        status_code = response.get("status_code", 500)
        raise HTTPException(status_code=status_code, detail=response["error"])
    
    return response

def delete_user_data(userId):
    response = user_data.delete_user(userId)
    
    if "error" in response:
        status_code = response.get("status_code", 500)
        raise HTTPException(status_code=status_code, detail=response["error"])
    
    # Ensure response has a "results" key with a list value
    if "results" in response and not isinstance(response["results"], list):
        response["results"] = [response["results"]] if response["results"] is not None else []
    
    return response
    
    if "error" in response:
        status_code = response.get("status_code", 500)
        raise HTTPException(status_code=status_code, detail=response["error"])
    
    return response
