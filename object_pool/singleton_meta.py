"""
.. module:: singleton_meta
   :platform: Unix, Windows
   :synopsis: metaclass for creating singleton registry

.. moduleauthor:: Durai Pandian <dduraipandian@gmail.com>

"""
from .exception import InvalidClass


class SingletonMetaPoolRegistry(type):
    """Metaclass by inheriting type to create singleton pool class."""

    __registry = {}

    @classmethod
    def remove_registry(cls, klass):
        """
        Remove item from the registry

        :param klass: class for which pool is created
        :return: None
        """

        cls.__registry.pop(klass.__name__, None)

    @classmethod
    def registry_exists(cls, base_klass):
        """
        Return True if the item is in the registry, False otherwise.

        :param base_klass: class for which registry will be created
        :return: boolean
        """

        is_registered = base_klass.__name__ in cls.__registry
        return is_registered

    def __call__(cls, base_klass, force=False, **params):

        registry_name = getattr(base_klass, '__name__', None)

        if not registry_name:
            raise InvalidClass(base_klass)

        is_registered = cls.registry_exists(base_klass)

        if is_registered:
            return cls.__registry[registry_name]

        klass = super().__call__(base_klass, **params)
        cls.__registry[registry_name] = klass
        return klass
