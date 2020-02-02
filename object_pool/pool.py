"""
.. module:: pool
:platform: Unix, Windows
:synopsis: object pool creation class

.. moduleauthor:: Durai Pandian <dduraipandian@gmail.com>

"""

import datetime
from copy import deepcopy
from queue import Queue
from .exception import InvalidMinInitCapacity, InvalidMaxCapacity, InvalidClass
from .singleton_meta import SingletonMetaPoolRegistry


class ObjectPool(metaclass=SingletonMetaPoolRegistry):
    """
    This is singleton object pool class. It creates pool, checks expiry and validation of the resource.

    :param base_klass:  class for which pool will be created.

                        In the below example, Pool will be created for Browser class and used.

                        .. code-block:: python

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
                                    print("close connection object")

                                def check_invalid(self, **stats):
                                    '''Returns True if resource is valid, otherwise False'''
                                    return False

    :param lazy: by default, resources are created when initiated.
                 lazy option will skip resource creation on init and will create
                 when the pool item is requested.
    :param min_init: minimum resources will be created while initiating.

            .. note::
                When **lazy=True** is set, `min` option is not respected.

    :param max_capacity: Maximum capacity of the pool. Pool will be created with **min_init** capacity. But it go grow up to max_capacity.

            .. note::
                -   `max_capacity` is not a hard constraint to the pool. When the client request for a resource,
                    and no resources are available for client, new resource will be created and provided to the
                    client. But this extra resource will not be queue, it will be cleaned up without performing
                    any validation.
                -   pool is implemented using Queue. But maxsize is not provided to handle `max_capacity`.
                    This is a implementation choice.
                -   `As creation and cleaning up of additional resource performed when pool gets full,
                    This will slow down the program. This is a cue to check bottleneck on client processing.`

    :param max_reusable: maximum number of times resource can be reused. Once this exceeds,
                         respective resource will be destroyed and new resource will be created.
                         By default, 20 is set. You can disable this by setting to 0.
    :param expires: resource expiration in seconds.

                .. note::
                    **Example:** expires=600, Resource will be only alive for 10 minutes
                    from the creation.

    :param pre_check: resource validation is performed before requesting the resource.
                      This is disabled by default.
    :param post_check: resource expiration checked after resource is being used. This is the default option.

        .. note::
            Base class should define clean_up method when **expiry** is set or **max_reusable** is set
            or **check_valid** method is defined in the class. If the clean up such as closing
            database connection or closing browser are not performed, those process will run in the
            background and cause performance issue in the system.

    :param cloning: reserved resource will be created to create new resource, in case of resource expiration. Cloning is disabled by default. You can enable by passing cloning=True.

        .. note::
            Reserved resource will be created even **lazy=True** option provided to reduce
            the resource creation time.

        >>> class Browser: # Objective pool class
        ...     def __init__(self):
        ...         self._browser = "connected!"
        ...
        ...     def do_work(self):
        ...         return "job done!"
        ...
        ...     def clean_up(self, **stats):
        ...         print("stats contains resource stats")
        >>> # default ConnectionPool options
        >>> connection_pool = ObjectPool(Browser, max_capacity=20, min_init=3, max_reusable=20,
        ...             expires=600, lazy=False, pre_check=False, post_check=True, cloning=False)

    """

    def __init__(self, klass, max_capacity=20, min_init=3, max_reusable=20,
                 expires=600, lazy=False, pre_check=False, post_check=True, cloning=False):
        """
        Creates pool with given configuration
        """

        self.pool_name = getattr(klass, '__name__', None)

        if not self.pool_name:
            raise InvalidClass(klass)

        klass_check_invalid = getattr(klass, 'check_invalid', None)
        klass_cleanup = getattr(klass, 'clean_up', None)

        self.__pool = Queue()
        self.__cloning = cloning
        self.klass = klass
        self.min_init = min_init
        self.max_capacity = max_capacity
        self.max_reusable_count = max_reusable
        self.expire_in_secs = expires
        self.pre_check = pre_check
        self.post_check = post_check

        self.__check_func = klass_check_invalid or None
        self.__cleanup_func = klass_cleanup or None

        if self.min_init <= 0 and not lazy:
            raise InvalidMinInitCapacity(self.pool_name)

        if self.max_capacity < 0:
            raise InvalidMaxCapacity(self.pool_name)

        if self.max_capacity == 0:
            print(f'INFO:: {self.pool_name} Pool will have unlimited resources.')

        if self.expire_in_secs == 0:
            print(f'INFO:: {self.pool_name} Resources does not expire.')

        if not klass_cleanup:
            print(f'WARNING:: {self.pool_name} does not have cleanup method. '
                  f'If destroy method is called, clean up such as closing connection '
                  f'will not be performed. Thus will lead to system performance.')

        if self.__cloning:
            self.__reserved_resource = self.klass()

        if not lazy:
            self.__create_init_pool()
        else:
            print(f'INFO:: {self.pool_name}: pool items will be created on request.')

        print(f'INFO:: {self.pool_name}: {self.get_pool_size()} pool items are created.')

    def get(self):
        """
        Creates contextmanager instance and returns resource and stats

        >>> class Connection:
        ...     def __init__(self):
        ...         self._conn = "connected!"
        ...
        ...     def do_work(self):
        ...         print("job done!")
        ...
        >>> pool = ObjectPool(Connection, min_init=3)
        >>>
        >>> with pool.get() as (resource, resource_stats):
        ...     resource.do_work()
        job done!

        """
        return self.__class__.Executor(self)

    def get_pool_size(self):
        """
        Returns the size of the pool (queue).

        Any operation on the queue results in different output time to time
        as the resources are removed from queue and added back.

        >>> pool = ObjectPool(Connection, min_init=3)
        >>> print(pool.get_pool_size())
        3

        """

        return self.__pool.qsize()

    @staticmethod
    def pool_exists(klass):
        """Return True if the pool is already created, False otherwise.

        >>> pool = ObjectPool(Connection, min_init=3)
        >>> ObjectPool.pool_exists(Connection)
        True
        >>> ObjectPool.pool_exists(DummyConnection)
        False
        """
        return SingletonMetaPoolRegistry.registry_exists(klass)

    def destroy(self):
        """Removes pool from the registry and performs clean up.

        When the pool is destroyed and `cleanup_func` is provided or
        class has `clean_up` method defined while creating,
        respective clean up method is called to clean up on the object.

        **Example:** When the connection pool is destroyed, all the connection objects in the pool
        will be closed if the cleanup method is provided when creating the pool.

        >>> class Connection:
        ...     def __init__(self):
        ...         self._conn = "connected!"
        ...
        ...     def do_work(self):
        ...         return "job done!"
        ...
        ...     def clean_up(self, **resource_stats):
        ...         return "cleanup performed!"
        ...
        >>> pool = ObjectPool(Connection, min_init=1)
        >>> pool.destroy()
        cleanup performed!
        """

        klass = self.klass
        while True:
            if self.get_pool_size() == 0:
                break
            else:
                resource, stats = self.__pool.get()
                self.__resource_cleanup(resource, stats)

        SingletonMetaPoolRegistry.remove_registry(klass)

    def is_pool_full(self):
        """Return True if the pool is full, False otherwise.

        >>> pool = ObjectPool(Connection, min_init=3, max_capacity=3)
        >>> pool.is_pool_full()
        True


        .. note::

            This method will always return False when **max_capacity=0**, As the pool grow unlimited.

        """
        pool_size = self.get_pool_size()
        return self.max_capacity != 0 and pool_size >= self.max_capacity

    def _get_resource(self):
        """Returns pool if the pool is not empty else creates and sends pool to the client."""
        pool_size = self.get_pool_size()

        if pool_size == 0:
            obj = self.__create_new_pool_resource()
            obj_stats = self._get_default_stats()
        else:
            obj, obj_stats = self.__pool.get()
            if self.pre_check:
                obj, obj_stats = self.__check_and_get_resource(obj, obj_stats)

        return obj, obj_stats

    def _queue_resource(self, resource, resource_stats):
        """Once client release the resource, this method puts back to the queue to re-use."""

        is_pool_full = self.is_pool_full()

        if not is_pool_full:
            if self.post_check:
                resource, resource_stats = self.__check_and_get_resource(resource, resource_stats)

            self.__pool.put((resource, resource_stats))
        else:
            self.__resource_cleanup(resource, resource_stats)

    def _internal_invalid_check(self, **resource_stats):
        """Returns True if max reusable count, expiration and custom validation are valid else False"""

        created_at = resource_stats.get('created_at', None)
        count = resource_stats.get('count', None)

        expired_by_max_reuse = self._is_expired_by_max_reuse(count)
        expired_by_time = self._is_expired_by_time(created_at)

        if expired_by_max_reuse:
            print("resource expired by usage count.")
            return True

        if expired_by_time:
            print("resource expired by usage time.")
            return True

        return False

    def _is_expired_by_max_reuse(self, count):
        """Checks if resource expired by usage policy"""
        expired_by_max_reuse = self.max_reusable_count != 0 and count and self.max_reusable_count <= count
        return expired_by_max_reuse

    def _is_expired_by_time(self, created_at):
        """Checks if resource expired by expiry policy"""
        expires_at = self._get_expiry_time(created_at)
        expired_by_time = self.expire_in_secs != 0 and expires_at < datetime.datetime.now()
        return expired_by_time

    def _get_expiry_time(self, created_at):
        """provides expiring time of resource based on **expire_in_secs**"""

        if created_at:
            expires_at = created_at + datetime.timedelta(seconds=self.expire_in_secs)
        else:
            expires_at = datetime.datetime.now()

        return expires_at

    def _get_default_stats(self, new=True):
        """Returns resource stats.

        .. note::

            `new` param indicates that, resource is expired and recreated.
        """

        resource_stats = {
            'count': 0,
            'new': new,
            'created_at': datetime.datetime.now(),
            'last_used': datetime.datetime.now()
        }
        return resource_stats

    def __create_init_pool(self):
        """
        create pool upto min to put into the queue.
        """

        for i in range(self.min_init):
            resource = self.__create_new_pool_resource()
            resource_stats = self._get_default_stats()
            self.__pool.put((resource, resource_stats))

    def __create_new_pool_resource(self):
        """Creates new resource and returns it to client

            - Creates new resource by cloning the reserved instance if cloning=True
            - Creates new resource instance if cloning=False
        """

        if self.__cloning:
            resource = deepcopy(self.__reserved_resource)
        else:
            resource = self.klass()
        return resource

    def __check_and_get_resource(self, resource, resource_stats):
        """Updates stats and returns if the resource is valid else creates a new resource and returns.

            -   count- is updated as resource being used.
            -   last_used - is updated , when it is used last
            -   new - is updated after the time time use or recreated.
        """
        resource_stats = self.__update_resource_stats(resource_stats)
        invalid_resource = self.__check_func(resource, **resource_stats) if callable(self.__check_func) else False
        invalid_resource_internal = self._internal_invalid_check(**resource_stats)
        if invalid_resource or invalid_resource_internal:
            resource, resource_stats = self.__cleanup_and_get_resource(resource, resource_stats)

        return resource, resource_stats

    def __cleanup_and_get_resource(self, resource, resource_stats):
        """Cleans up expired resource and creates new resource and return"""

        self.__resource_cleanup(resource, resource_stats)
        resource = self.__create_new_pool_resource()
        resource_stats = self._get_default_stats(new=False)
        return resource, resource_stats

    def __resource_cleanup(self, resource, resource_stats):
        """Calls cleanup function if that is provided while creating pool."""

        if callable(self.__cleanup_func):
            self.__cleanup_func(resource, **resource_stats)

    def __update_resource_stats(self, resource_stats):
        """Updates the stats of the resource"""

        resource_stats['count'] = resource_stats['count'] + 1
        resource_stats['new'] = False
        resource_stats['last_used'] = datetime.datetime.now()
        return resource_stats

    class Executor:
        """
        This is context manager for **ObjectPool**
        """

        def __init__(self, klass):
            self.__pool = klass
            self.resource, self.resource_stats = None, None

        def __enter__(self):
            self.resource, self.resource_stats = self.__pool._get_resource()
            return self.resource, self.resource_stats

        def __exit__(self, exc_type, exc_val, exc_tb):
            self.__pool._queue_resource(self.resource, self.resource_stats)
