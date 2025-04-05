from models.users import UserModel

user_data = UserModel()

def get_users_data():
    users = user_data.get_users()
    result = [dict(user) for user in users]
    return result

def get_user_data(user_id):
    user = user_data.get_user(user_id)
    if user:
        return dict(user)  
    return None 

def create_user_data(username, email):
    return user_data.create_user(username, email)


def update_user_data(user_id, username, email, password):
    return user_data.update_user(user_id, username, email, password)

def delete_user_data(user_id):
    return user_data.delete_user(user_id)
