import unittest
import subprocess
import time
import os
from object_pool.pool import ObjectPool
from object_pool.tests.browser_test import FirefoxBrowser

skip_browser_test = False if os.environ.get('SKIP_BROWSER_TEST', 'True').lower() == 'false' else True


class ObjectPoolBehaviourTest(unittest.TestCase):

    def setUp(self):
        self.klass = FirefoxBrowser
        self.skip_test = False
        self.skip_teardown = False

    def get_process_count(self, key='firefox'):
        ff_process = subprocess.Popen(['ps', '-ef'], stdout=subprocess.PIPE)
        grep_process = subprocess.Popen(['grep', key], stdin=ff_process.stdout,
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        awk_process = subprocess.Popen(['awk', '{print $2}'], stdin=grep_process.stdout,
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        wc_process = subprocess.Popen(['wc', '-l'], stdin=awk_process.stdout,
                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        ff_process.stdout.close()
        grep_process.stdout.close()
        awk_process.stdout.close()

        cnt, err = wc_process.communicate()

        if cnt:
            try:
                cnt = int(cnt.decode().strip()) if cnt.decode().strip() else 0
            except:
                cnt = 0

        return cnt

    @unittest.skipIf(skip_browser_test, "to test as a stand alone test")
    def test_browser(self):
        starting_ff_count = self.get_process_count()
        print(starting_ff_count)
        self.pool = ObjectPool(self.klass, min_init=1, expires=0)
        time.sleep(10)
        after_ff_count = self.get_process_count()
        print(after_ff_count)
        final_count = after_ff_count - starting_ff_count
        self.assertEqual(final_count, 1)

    @unittest.skipIf(skip_browser_test, "to test as a stand alone test")
    def test_browser_without_cloning(self):
        starting_ff_count = self.get_process_count()
        self.pool = ObjectPool(self.klass, min_init=2, expires=0)
        after_ff_count = self.get_process_count()
        final_count = after_ff_count - starting_ff_count

        with self.pool.get() as (browser, browser_stats):
            title = browser.get_page_title('https://www.google.co.in/')

        with self.pool.get() as (browser1, browser_stats):
            title1 = browser1.get_page_title('https://www.facebook.com/')

        self.assertNotEqual(browser, browser1)

    def tearDown(self):
        if not self.skip_teardown:
            self.pool.destroy()
            self.klass = None
