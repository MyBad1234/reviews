class SelectExceptions(Exception):
    """exception for select sql query"""

    pass


class UpdateExceptions(Exception):
    """exception for update query"""

    pass


class InsertExceptions(Exception):
    """exception for insert query"""

    pass


class ProxyError(Exception):
    """if proxy is incorrect"""

    pass


class ReviewsNotFound(Exception):
    """if the company has no reviews"""

    pass


class EnvPathException(Exception):
    """if task is not fond"""

    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            print('Error when importing virtual environment variables: {0}'.format(self.message))
        else:
            print('Error when importing virtual environment variables.')
