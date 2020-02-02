import unittest
from object_pool.pool import ObjectPool
from object_pool.tests.cls import Browser


class ObjectPoolFunctionTest(unittest.TestCase):

    def setUp(self):
        self.klass = Browser
        self.skip_teardown = False

    def test_is_full_with_same_min_max(self):
        """testing is_pool_full with same min_init and max"""
        self.pool = ObjectPool(self.klass, min_init=2, max_capacity=2)
        self.assertTrue(self.pool.is_pool_full())

    def test_is_full_with_not_same_min_max(self):
        """testing is_pool_full method with max > min_init"""
        self.pool = ObjectPool(self.klass, min_init=1, max_capacity=2)
        self.assertFalse(self.pool.is_pool_full())

    def test_is_full_with_max_zero(self):
        """when max_capacity=0, is_pool_full always return False."""
        self.pool = ObjectPool(self.klass, min_init=3, max_capacity=0)
        self.assertFalse(self.pool.is_pool_full())

    def test_destroy(self):
        """after destroy, pool should not be available or exist."""
        self.pool = ObjectPool(self.klass, min_init=1, expires=0)
        self.pool.destroy()
        self.assertFalse(ObjectPool.pool_exists(self.klass))

    def test_exists(self):
        """pool become available after it created."""
        self.pool = ObjectPool(self.klass, min_init=1, expires=0)
        exists = ObjectPool.pool_exists(self.klass)
        self.assertTrue(exists)

    def test_not_exist(self):
        """pool will not be available if that is not created for a class"""
        self.skip_teardown = True
        exists = ObjectPool.pool_exists(Browser)
        self.assertFalse(exists)

    def tearDown(self):
        if not self.skip_teardown:
            self.pool.destroy()
            self.klass = None
