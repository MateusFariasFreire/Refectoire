import json
from user import User

default_meal_price = 6
student_meal_price = 4
teacher_meal_price = 3.8
administration_meal_price = 3.25

class RefectoryManager:
    def __init__(self, users_data_file_name):

        self.__users_data_file_name = users_data_file_name

        with open(users_data_file_name) as users_data_file:
            self.__users_data = json.load(users_data_file)

    def updateUsersData(self):
        with open(self.__users_data_file_name) as users_data_file:
            self.__users_data = json.load(users_data_file)

    def getAllUsers(self):
        return self.__users_data['accounts']

    def saveUsersData(self):
        with open(self.__users_data_file_name, 'w') as users_data_file :
            json.dump(self.__users_data, users_data_file, indent=2)

        self.updateUsersData()

    def findUser(self, user_name):
        for user_data in self.__users_data['accounts']:
            if user_data['name'] == user_name :
                return User(user_data['id'], user_data['name'], user_data['balance'], user_data['role'])
            else :
                continue

        return None

    def findUserByID(self, user_id):
        for user_data in self.__users_data['accounts']:
            if user_data['id'] == user_id :
                return User(user_data['id'], user_data['name'], user_data['balance'], user_data['role'])
            else :
                continue

        return None

    def saveUserData(self, user):
        self.updateUsersData()
        for user_data in self.__users_data['accounts']:
            if user_data['id'] == user.getId():
                user_data['name'] = user.getName()
                user_data['balance'] = user.getBalance()
                user_data['role'] = user.getRole()
                break

        self.saveUsersData()

    def payMeal(self, user):
        mealPrice = default_meal_price
        match user.getRole():
            case "student":
                mealPrice = student_meal_price
            case "teacher":
                mealPrice = teacher_meal_price
            case "administration":
                mealPrice = administration_meal_price

        self.updateUsersData()
        if mealPrice > user.getBalance():
            return False

        user.setBalance(round(user.getBalance() - mealPrice,2))
        self.saveUserData(user)
        return True

    def addUser(self, user_name, user_role):
        self.updateUsersData()
        last_id = self.__users_data['accounts'][-1]["id"]
        self.__users_data['accounts'].append({"id": last_id+1,"name": user_name,"balance": 0,"role": user_role})
        self.saveUsersData()
        return last_id+1