class InvalidMinInitCapacity(Exception):
    def __init__(self, pool_name):
        self.message = f"ERROR:: {pool_name}: min_init can not be less than 0 with lazy=False option."


class InvalidMaxCapacity(Exception):
    def __init__(self, pool_name):
        self.message = f"ERROR:: {pool_name}: max capacity should not be negative number."


class InvalidClass(Exception):
    def __init__(self, klass):
        self.message = f"ERROR:: {klass} is not a valid class."
