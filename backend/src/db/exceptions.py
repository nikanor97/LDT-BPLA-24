from sqlalchemy.exc import SQLAlchemyError


class ResourceAlreadyExists(SQLAlchemyError):
    def __init__(self, *args):
        self.data = ", ".join(args)
