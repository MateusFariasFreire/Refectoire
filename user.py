class User:
    def __init__(self, id, name, balance,role):
        self.__id = id
        self.__name = name
        self.__balance = balance
        self.__role = role

    def getId(self):
        return self.__id

    def getName(self):
        return self.__name

    def getBalance(self):
        return self.__balance

    def getRole(self):
        return self.__role

    def setBalance(self, balance):
        self.__balance = balance

    def setRole(self, role):
        self.__role = role

    def setName(self, name):
        self.__name = name

    def addMoney(self, value_to_add):
        self.__balance += value_to_add