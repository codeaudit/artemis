import matplotlib
matplotlib.use('agg')
from artemis.plotting.db_plotting import dbplot
from artemis.plotting.plotting_server import setup_web_plotting
import numpy as np
from matplotlib import pyplot as plt


__author__ = 'peter'


def test_plotting_server():
    setup_web_plotting()

    for i in xrange(100):
        dbplot(np.random.randn(10, 10, 3), 'noise')
        dbplot(np.random.randn(20, 2), 'lines')
        plt.pause(1)

    import pdb; pdb.set_trace()

if __name__ == '__main__':
    test_plotting_server()