class AlreadyExists(Exception):
    def __init__(self, message = "Username has already been used."):
        super().__init__(message)

class InvalidUsername(Exception):
    def __init__(self, message = "Username cannot be this short/long."):
        super().__init__(message)

class InvalidPassword(Exception):
    def __init__(self, message = "Invalid password."):
        super().__init__(message)

class NonexistentCategory(Exception):
    def __init__(self, message = "This option does not exist."):
        super().__init__(message)

class AlreadyAsked(Exception):
    def __init__(self, message="This question has already been asked. We recommend looking it up and reading the provided answers."):
        super().__init__(message)
        
class QuesNonex(Exception):
    def __init__(self, message = "Question does not exist."):
        super().__init__(message)

class PermissionDenied(Exception):
    def __init__(self, message = "Cannot delete a question or reply not made by you."):
        super().__init__(message)

class UserNotFound(Exception):
    def __init__(self, message = "User not found"):
        super().__init__(message)