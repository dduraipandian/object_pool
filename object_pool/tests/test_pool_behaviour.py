import unittest
import time
from object_pool.pool import ObjectPool
from object_pool.tests.cls import Browser, Browser1


class ObjectPoolBehaviourTest(unittest.TestCase):

    def setUp(self):
        self.klass = Browser
        self.skip_teardown = False

    def test_with_non_expiry(self):
        self.pool = ObjectPool(self.klass, min_init=1, expires=0)

        with self.pool.get() as (item, item_stats):
            t = item_stats['created_at']

        time.sleep(13)

        with self.pool.get() as (item1, item_stats1):
            t1 = item_stats1['created_at']

        self.assertEqual(item, item1)

    def test_with_expire_true_pre_check(self):
        self.pool = ObjectPool(self.klass, min_init=1,
                               expires=10, pre_check=True,
                               post_check=False)

        with self.pool.get() as (item, item_stats):
            t = item_stats['created_at']

        time.sleep(13)

        with self.pool.get() as (item1, item_stats1):
            t1 = item_stats1['created_at']

        self.assertNotEqual(item, item1)

    def test_with_expire_true_post_check(self):
        self.pool = ObjectPool(self.klass, min_init=1, expires=10)

        with self.pool.get() as (item, item_stats):
            t = item_stats['created_at']

        time.sleep(13)

        with self.pool.get() as (item1, item_stats1):
            t1 = item_stats1['created_at']

        with self.pool.get() as (item2, item_stats2):
            t2 = item_stats2['created_at']

        if item1 is item:
            self.assertNotEqual(item2, item)
        else:
            self.assertEqual(item1, item)

    def test_with_expire_false_pre_check(self):
        self.pool = ObjectPool(self.klass, min_init=1, expires=10)

        with self.pool.get() as (item, item_stats):
            t = item_stats['created_at']

        time.sleep(13)

        with self.pool.get() as (item1, item_stats1):
            t1 = item_stats1['created_at']

        self.assertEqual(item1, item)

    def test_with_expire_false_post_check(self):
        self.pool = ObjectPool(self.klass, min_init=1, expires=10,
                               post_check=False, pre_check=True)

        with self.pool.get() as (item, item_stats):
            t = item_stats['created_at']

        time.sleep(13)

        with self.pool.get() as (item1, item_stats1):
            t1 = item_stats1['created_at']

        self.assertNotEqual(item1, item)

    def test_multiple_pool_invocation(self):

        self.pool = ObjectPool(self.klass, min_init=2)
        dpool = ObjectPool(Browser1, min_init=3)

        with self.pool.get() as (item, item_stats):
            t = item.do_work()

        with dpool.get() as (item1, item_stats1):
            t1 = item1.do_work()

        dpool.destroy()
        self.assertNotEqual(t1, t)

    def test_pool_size_growth(self):
        """pool size will grow up to max. This test case is a simulation of
        concurrent access and pool growth"""
        self.pool = ObjectPool(self.klass, min_init=1, max_capacity=1)

        p1, stats = self.pool._get_resource()

        p1_size = self.pool.get_pool_size()

        with self.pool.get() as (item, item_stats):
            t = item.do_work()

        p2_size = self.pool.get_pool_size()

        self.pool._queue_resource(p1, stats)

        p3_size = self.pool.get_pool_size()

        self.assertEqual(p3_size, 1)

    def test_pool_with_reusable(self):
        """pool size will grow up to max. This test case is a simulation of
        concurrent access and pool growth"""
        self.pool = ObjectPool(self.klass, min_init=1, max_capacity=1, max_reusable=2)

        with self.pool.get() as (item0, item_stats):
            t = item0.do_work()

        with self.pool.get() as (item, item_stats):
            t = item.do_work()

        with self.pool.get() as (item1, item_stats):
            t = item1.do_work()

        with self.pool.get() as (item2, item_stats):
            t = item2.do_work()

        self.assertEqual(item0, item)
        self.assertNotEqual(item1, item)
        self.assertEqual(item1, item2)

    def tearDown(self):
        if not self.skip_teardown:
            self.pool.destroy()
            self.klass = None
