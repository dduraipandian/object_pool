=========================
Object Pool documentation
=========================

.. raw:: html

   <hr/>


.. contents:: Table of contents
    :local:

.. raw:: html

   <hr/>

Introduction
============
.. include:: ../../README.rst
    :start-after: inclusion-marker-do-not-remove-start
    :end-before: inclusion-marker-do-not-remove-end

`New instance creation` will happen with ObjectPool but when no resources available in the pool for a client. ObjectPool will not fail in case resource is not available, but it will create one and provide to client. Thus keeping your system/process available at the cost of little performance.


Little about resource
=====================

    **Resource** is a class which will be pooled. Resource class can have following properties.

    -   Resource can have **check_invalid** method to provide custom validation. This method should return boolean values.
        This will be called while cleaning up of the resource. When this method is not defined, only

        .. code-block:: python

            def check_invalid(self, **stats):
                '''Returns True if the resource is valid, otherwise False'''
                return False

    -   Resource should have **clean_up** method to provide clean up process for resource. Since resource information is
        not available to object, how a resource should be clean up using this method. It is advised to keep clean up
        method mandatory as resource such as database connection or browser process will affect system performance.

        .. code-block:: python

                def clean_up(self, **stats):
                    self.browser.quit()
                    self.browser = None

    -   Resource methods check_invalid and clean_up will have keyword argument stats. Stats will be have below information
        regarding resource.

        -   count - resource usage count.
        -   last_used - last usage time of the resource.
        -   new - is updated after the time time use or recreated.

    **Example - Resource class**

    Let's have an example of Browser pool for clients. We have below browser class.
    perquisite for this testing are below.

    -   Selenium
    -   Geckodriver

    .. literalinclude:: ../../object_pool/tests/browser_test.py
        :language: python


Features
========

    Resources to client are provided by ObjectPool. Queueing and cleaning up are automatically taken care by
    ObjectPool.

        -   `get()` method used conjunction with **with statement**.
        -   `get()` removes resource from pool and provides to client.
        -   when client code exits with statement, utilized resource will be queued in the pool to use
            after validation.
        -   get() method provides two object, one is resource and respective stats in the pool.

                -   resource - resource class instance. Through this, you can call any method in the class
                    you defined.
                -   stats - resource statistics. This will be used for you to perform custom validation in
                    the resource class.

        .. code-block:: python

            from object_pool import ObjectPool
            browser_pool = ObjectPool(FirefoxBrowser)

            # browser will be created as it is lazy when get() method called.
            # browser will be placed in the queue when exits with statement.
            with browser_pool.get() as (browser, browser_stats):
                # you can call any method defined in the resource and perform operation
                title = browser.get_page_title('https://www.google.co.in/')

    Once you define a resource class, you can use below features to create the pool for the resource.

Lazy behaviour
--------------
**lazy=True** Resource pool will be created with zero resource when initiated. New resource will
be created when requested and pooled till it reach it's maximum capacity.

.. code-block:: python

    browser_pool = ObjectPool(FirefoxBrowser, lazy=True)

Unlimited resource
------------------
When **max_capacity=0** is set, pool grow unlimited. This option needs to be used with cautious and advised
used with expiry options, as resource grows without clean up which will lead to performance issue.

.. code-block:: python

    browser_pool = ObjectPool(FirefoxBrowser, max_capacity=0)

Resource Expiration
-------------------
Resource expiration methods can used to set resource expiry for a resource. Object pool refill the pool with
new resource.

Limited time resource
^^^^^^^^^^^^^^^^^^^^^
    When pool is created with **expires=600**, resource will be cleaned up and removed from
    the pool `after 10 mins`. `expires=0` resource will never expire.

    .. code-block:: python

        # each resource in the pool will expire in 10 mins from the created time.
        browser_pool = ObjectPool(FirefoxBrowser, expires=600)

Resource usage policy
^^^^^^^^^^^^^^^^^^^^^
    When **max_reusable=6**, resource can be used only 6 times by any client. After this usage limit, resource
    will be cleaned up and new resource will be created.

    .. code-block:: python

        # each resource in the pool will expire in 10 mins from the created time
        # or 20 times used by clients
        browser_pool = ObjectPool(FirefoxBrowser, max_reusable=20, expires=600)

Speed up creation
-----------------

When **cloning=True**, object_pool will create new resource by cloning reserved resource. This will
not fit for all resources. Best It should be tested by user, before using it. By default cloning is
disabled.

.. code-block:: python

    # new resource will be created by cloning reserved resource instance.
    browser_pool = ObjectPool(FirefoxBrowser, cloning=True)

.. code-block:: html

    Seleinum browser or db connection resources will not be able to use cloning. But If you have
    any custom object which performs long running calculation and creates instance, cloning will
    useful that time.

.. code-block:: html

    Reserved resource is a instance of resource class for cloning to create new resource.
    This reserved instance will not be part of the pool.

Custom validation
-----------------

User's custom validation can be defined in **check_invalid** in the resource class. This will be called while
cleaning up of the resource.


Lets say you dont want to access the google web page more than once in the same browser. You can
invalidate with **check_invalid** method and clean up the browser as below method.

.. code-block:: python

    def check_invalid(self, **stats):
        # invalidate browser which accessed google web page to create new resource in place.
        if self.page_title == 'Google':
            return True
        return False


.. toctree::
    :hidden:
    :caption: All Contents

    Home <self>
    dev_guide
    readme