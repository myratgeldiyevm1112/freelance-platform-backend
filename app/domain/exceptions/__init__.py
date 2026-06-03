
class AppError(Exception):
    """Base exception"""
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)

class NotFoundError(AppError):
    pass

class ForbiddenError(AppError):
    pass

class ConflictError(AppError): 
    pass

class ValidationError(AppError):
    pass

class UnauthorizedError(AppError):
    pass