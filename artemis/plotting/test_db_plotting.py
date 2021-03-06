import numpy as np
from artemis.plotting.db_plotting import dbplot, clear_dbplot
from artemis.plotting.plotting_backend import LinePlot, HistogramPlot, MovingPointPlot
import pytest
__author__ = 'peter'


def test_dbplot(n_steps = 3):

    arr = np.random.rand(10, 10)
    for i in xrange(n_steps):
        arr_sq=arr**2
        arr = arr_sq/np.mean(arr_sq)
        dbplot(arr, 'arr')
        for j in xrange(3):
            barr = np.random.randn(10, 2)
            dbplot(barr, 'barr', plot_type=lambda: LinePlot())
    clear_dbplot()


@pytest.mark.skipif('True', reason = 'Need to make matplotlib backend work with scales.')
def test_dbplot_logscale(n_steps = 3):

    arr = np.random.rand(10, 10)

    for i in xrange(n_steps):
        arr_sq=arr**2
        arr = arr_sq/np.mean(arr_sq)
        dbplot(arr, 'arr')
        for j in xrange(3):
            barr = np.random.randn(10, 2)
            kw = {"y_axis_type":"log"}
            dbplot(barr, 'barr', plot_type=lambda: LinePlot(y_axis_type='log'))
    clear_dbplot()


def test_particular_plot(n_steps = 3):

    for i in xrange(n_steps):
        r = np.random.randn(1)
        dbplot(r, plot_type=lambda: HistogramPlot(edges=np.linspace(-5, 5, 20)))
    clear_dbplot()


def test_history_plot_updating():
    """
    This test checks that we've fixed the bug mentioned in issue 1: https://github.com/QUVA-Lab/artemis/issues/1
    That was, when you are updating multiple plots with history in a loop, everytime any of the plots is updated, they
    all get updated with the most recent data.  You'll see this in plot 'c' - with the bug, it moves in steps, with 3
    of the same sample in a row.  If it works it should be spikey.
    """
    for i in xrange(10):
        dbplot(np.random.randn(20, 20), 'a')
        dbplot(np.random.randn(20, 20), 'b')
        dbplot(np.random.randn(), 'c', plot_type=lambda: MovingPointPlot())
    clear_dbplot()


def test_moving_point_multiple_points():

    for i in xrange(5):
        dbplot(np.sin([i/10., i/15.]), 'unlim buffer', plot_type = MovingPointPlot)
        dbplot(np.sin([i/10., i/15.]), 'lim buffer', plot_type = lambda: MovingPointPlot(buffer_len=20))


def test_same_object():
    """
    There was a bug where when you plotted two of the same array, you got "already seen object".  This tests makes
    sure it's gotten rid of.  If it's gone, both matrices should plot.  Otherwise you'll get "Already seen object" showing
    up on one of the plots.
    """
    a = np.random.randn(20, 20)
    for _ in xrange(5):
        dbplot(a, 'a')
        dbplot(a, 'b')
    clear_dbplot()


def test_multiple_figures():

    for _ in xrange(2):
        dbplot(np.random.randn(20, 20), 'a', fig='1')
        dbplot(np.random.randn(20, 20), 'b', fig='1')
        dbplot(np.random.randn(20, 20), 'c', fig='2')
        dbplot(np.random.randn(20, 20), 'd', fig='2')


def test_list_of_images():

    for _ in xrange(2):
        dbplot([np.random.randn(12, 30), np.random.randn(10, 10), np.random.randn(15, 10)])


if __name__ == '__main__':
    test_moving_point_multiple_points()
    test_list_of_images()
    test_multiple_figures()
    test_same_object()
    test_history_plot_updating()
    test_particular_plot()
    test_dbplot()
