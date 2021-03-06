from artemis.general.should_be_builtins import itermap, reducemap
__author__ = 'peter'


def test_reducemap():
    assert reducemap(lambda a, b: a+b, [1, 2, -4, 3, 6, -7], initial=0) == [1, 3, -1, 2, 8, 1]
    assert reducemap(lambda a, b: a+b, [1, 2, -4, 3, 6, -7]) == [3, -1, 2, 8, 1]
    assert reducemap(lambda a, b: a+b, [1, 2, -4, 3, 6, -7], include_zeroth=True) == [1, 3, -1, 2, 8, 1]


def test_itermap():
    # See collatz conjecture
    assert itermap(lambda a: a/2 if a % 2==0 else a*3+1, initial = 12, stop_func=lambda x: x==1, include_zeroth=True) == [12, 6, 3, 10, 5, 16, 8, 4, 2, 1]
    assert itermap(lambda a: a/2 if a % 2==0 else a*3+1, initial = 1, n_steps=5, include_zeroth=True) == [1, 4, 2, 1, 4, 2]


if __name__ == '__main__':
    test_reducemap()
    test_itermap()
