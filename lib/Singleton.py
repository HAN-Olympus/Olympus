class Singleton(object):
	""" THe base singleton class for Olympus. """
	_instance = None
	def __new__(cls, *args, **kwargs):
		if not cls._instance:
			cls._instance = super(Singleton, cls).__new__(
								cls, *args, **kwargs)
								
		cls.instantiated = False
		""" Is true if this object has already been instantiated once. """
		return cls._instance