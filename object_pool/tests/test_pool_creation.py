import unittest
from object_pool.pool import ObjectPool
from object_pool.exception import InvalidMinInitCapacity, InvalidMaxCapacity, InvalidClass
from object_pool.tests.cls import Browser, Browser1


class ObjectPoolCreationTest(unittest.TestCase):

    def setUp(self):
        self.klass = Browser
        self.skip_teardown = False

    def test_with_default_values(self):
        """pool should be created with default values"""
        self.pool = ObjectPool(self.klass)
        self.assertIsNotNone(self.pool)

    def test_multiple_pool_creation(self):
        self.pool = ObjectPool(self.klass, min_init=2)
        dpool = ObjectPool(Browser1, min_init=3)

        self.assertNotEqual(self.pool, dpool)
        dpool.destroy()

    def test_with_lazy_option(self):
        """lazy pool will be created with zero resources upon creation"""
        self.pool = ObjectPool(self.klass, lazy=True)
        self.assertEqual(self.pool.get_pool_size(), 0)

    def test_without_cloning_option(self):
        """resource will be created by cloning the instance"""
        self.pool = ObjectPool(self.klass, min_init=2, cloning=False)
        self.assertEqual(self.pool.get_pool_size(), 2)

    def test_with_min_zero(self):
        """min_init can not be 0 with lazy=False option else exception will be raised"""
        self.skip_teardown = True
        self.assertRaises(InvalidMinInitCapacity, ObjectPool, self.klass, min_init=0)

    def test_with_max(self):
        """max_capacity should be positive number else exception will be raised"""
        self.skip_teardown = True
        self.assertRaises(InvalidMaxCapacity, ObjectPool, self.klass, max_capacity=-1)

    def test_with_invalid_class(self):
        """max_capacity should be positive number else exception will be raised"""
        self.skip_teardown = True
        a = 2
        self.assertRaises(InvalidClass, ObjectPool, a, max_capacity=-1)

    def test_with_max_zero(self):
        """pool size should be same as min_init right after creation"""
        self.pool = ObjectPool(self.klass, min_init=3, max_capacity=0)
        self.assertEqual(self.pool.get_pool_size(), 3)

    def test_creation_same_pool(self):
        """pool size should be same as min_init right after creation"""
        self.pool = ObjectPool(self.klass)
        self.pool1 = ObjectPool(self.klass)
        self.assertEqual(self.pool, self.pool1)
        self.pool1.destroy()

    def tearDown(self):
        if not self.skip_teardown:
            self.pool.destroy()
            self.klass = None
