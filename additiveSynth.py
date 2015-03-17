from pyo import *

class GenWaveForm(pyoTableObject):
    """
    This class .

    Generates square waveforms made up of fixed number of harmonics.

    :Parent: :py:class:`PyoTableObject`

    :Args:

        order : int, optional
            Number of harmonics square waveform is made of. The waveform will
            contains `order` odd harmonics. Defaults to 10.
        size : int, optional
            Table size in samples. Defaults to 8192.

    >>> s = Server().boot()
    >>> s.start()
    >>> t = TriTable(order=15).normalize()
    >>> a = Osc(table=t, freq=[199,200], mul=.2).out()

    """
    def __init__(self, order, odd = True, size=8192):
        PyoTableObject.__init__(self, size)
        self._order = order
        self._table = HarmTable(self._create_list(order), size)
        self._base_objs = self._tri_table.getBaseObjects()

    def _create_list(self, order):
        # internal method used to compute the harmonics's weight
        if odd:
	        l = []
	        for i in range(1,order*2):
	            if i % 2 == 0:
	                l.append(0)
	            else:
	                l.append(1 / (i*i))
	        return l
	    else:
	    	l = []
	        for i in range(1,order*2):
	            if i % 2 == 0:
	               	l.append(1 / (i*i))
	            else:
	            	l.append(0)
	        return l

    def setOrder(self, x):
        """
        Change the `order` attribute and redraw the waveform.

        :Args:

            x : int
                New number of harmonics

        """
        self._order = x
        self._table.replace(self._create_list(x))
        self.normalize()
        self.refreshView()

    @property
    def order(self):
        """int. Number of harmonics triangular waveform is made of."""
        return self._order
    @order.setter
    def order(self, x): self.setOrder(x)
