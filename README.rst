===========
Readme File
===========

.. image:: https://travis-ci.com/dduraipandian/object_pool.svg?token=HYyTsSU9ynxiqecjxoc5&branch=master
    :target: https://travis-ci.com/dduraipandian/object_pool
    :alt: Travis CI

.. image:: https://codecov.io/gh/dduraipandian/object_pool/branch/master/graph/badge.svg?token=2JrmTQ7smU
  :target: https://codecov.io/gh/dduraipandian/object_pool
  :alt: codecov test coverage

.. image:: https://img.shields.io/badge/License-MIT-blue.svg
  :target: https://opensource.org/licenses/MIT
  :alt: MIT License

.. image:: https://readthedocs.org/projects/object-pool/badge/?version=latest
    :target: https://object-pool.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status


ObjectPool
----------
- `Explore the docs » <https://object-pool.readthedocs.io>`_
- `Source Code » <https://github.com/dduraipandian/object_pool/>`_
- `Report Bug » <https://github.com/dduraipandian/object_pool/issues>`_
- `Request Feature » <https://github.com/dduraipandian/object_pool/issues/>`_


.. contents:: Table of contents
    :local:

Object Pool
===========

.. inclusion-marker-do-not-remove-start

Object pool library creates a pool of resource class instance and use them in your project. Pool is implemented using python built in library `Queue <https://docs.python.org/3.6/library/queue.html>`_.

Let's say for example, you need multiple firefox browser object in headless mode to be available for client request to process or some testing or scraping.

-   Each time creating a new browser instance is time consuming task which will make client to wait.
-   If you have one browser instance and manage with browser tab, it will become cumbersome to maintain and debug in case of any issue arises.

Object Pool will help you to manage in that situation as it creates resource pool and provides to each client when it requests. Thus separating the process from one another without waiting or creating new instance on the spot.

.. inclusion-marker-do-not-remove-end


.. topic:: **How to install**

    .. code-block:: html

        pip install py-object-pool

.. topic:: **Source**

    Find the latest version on `GitHub - ObjectPool <https://github.com/dduraipandian/object_pool>`_.

    Feel free to fork and contribute!

.. topic:: **Requirements**

    Python 3.6 and above


Code Example
============

Below example will help you to understand how to create resource class for ObjectPool and use them in your project.

In the below example, `Browser` is a resource class and `ff_browser_pool` is a pool of Browser.

Please refer the user guide for more details.


Sample resource class
---------------------

.. code-block:: python

    from selenium.webdriver import Firefox, FirefoxProfile
    from selenium.webdriver.firefox.options import Options


    class FirefoxBrowser:
        """
        This is browser resource class for ObjectPool. This class demonstrate how to create resource class
        and implement methods described in the user guide section.
        """

        def __init__(self):
            self.browser = FirefoxBrowser.create_ff_browser()
            self.page_title = None

        @classmethod
        def create_ff_browser(cls):
            """Returns headless firefox browser object"""
            profile = FirefoxProfile().set_preference("intl.accept_languages", "es")
            opts = Options()
            opts.headless = True
            browser = Firefox(options=opts, firefox_profile=profile)
            return browser

        def get_page_title(self, url):
            """Returns page title of the url"""
            browser = self.browser
            browser.get(url)
            self.page_title = browser.title
            return self.page_title

        def clean_up(self, **stats):
            """quits browser and sets None, when this method is called"""
            self.browser.quit()
            self.browser = None

        def check_invalid(self, **stats):
            """Returns invalid=True if the browser accessed google web page, otherwise False"""
            if self.page_title == 'Google':
                return True
            return False



Sample client block
-------------------

.. code-block:: python

    from object_pool import ObjectPool

    ff_browser_pool = ObjectPool(FirefoxBrowser, min_init=2)

    with ff_browser_pool.get() as (browser, browser_stats):
        title = browser.get_page_title('https://www.google.co.in/')


Authors
=======

**Durai Pandian** - *Initial work* - `dduraipandian <https://github.com/dduraipandian>`_

License
=======

This project is licensed under the MIT License - see the `LICENSE <LICENSE>`_ file for details
