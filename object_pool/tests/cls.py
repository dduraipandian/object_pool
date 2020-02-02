class Browser:
    def __init__(self):
        self.browser = self.__class__.__create_connection()

    @staticmethod
    def __create_connection():
        obj = "connection_object"
        return obj

    def do_work(self):
        return True

    def clean_up(self, **stats):
        print("connection object is closed")

    def check_invalid(self, **stats):
        '''Returns True if resource is valid, otherwise False'''
        return False


class Browser1:
    def __init__(self):
        self.browser = self.__class__.__create_connection()

    @staticmethod
    def __create_connection():
        obj = "connection_object"
        return obj

    def do_work(self):
        return False

    def clean_up(self, **stats):
        print("connection object is closed")

    def check_invalid(self, **stats):
        '''Returns True if resource is valid, otherwise False'''
        print(stats)
        return False
