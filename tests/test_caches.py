# -*- coding: UTF-8 -*-
"""
Tests for caches
"""

from time import sleep

import pytest

from pydecor.caches import FIFOCache, LRUCache, TimedCache


class TestLRU:
    """Test the LRU cache"""

    def test_unsized(self):
        """Test that not specifying a size lets the cache grow"""
        cache = LRUCache()
        for i in range(500):
            cache[i] = i
        for i in range(500):
            assert i in cache
            assert cache[i] == i

    def test_sized_no_reuse(self):
        """Test basic LIFO functionality with all new values"""
        cache = LRUCache(max_size=5)
        for i in range(5):
            cache[i] = i
        for i in range(5):
            assert i in cache
            assert cache[i] == i
        for i in range(5, 10):
            cache[i] = i
            assert i in cache
            assert cache[i] == i
            assert i - 5 not in cache
            with pytest.raises(KeyError):
                assert cache[i - 5]

    def test_sized_with_reuse(self):
        """Test LRU functionality"""
        cache = LRUCache(max_size=3)
        for i in range(3):
            cache[i] = i
        # LRU: 0 1 2
        for i in range(3):
            assert i in cache
            assert cache[i] == i
        # LRU: 0 1 2

        cache[3] = 3
        # LRU: 1 2 3

        assert 0 not in cache
        with pytest.raises(KeyError):
            assert cache[0]

        for i in range(1, 4):
            assert i in cache
            assert cache[i] == i

        # Test re-ording with getitem
        assert cache[1]
        # LRU: 2 3 1

        cache[0] = 0
        # LRU: 3 1 0

        assert 2 not in cache
        with pytest.raises(KeyError):
            assert cache[2]

        for i in 3, 1, 0:
            assert i in cache
            assert cache[i] == i

        # Test re-ording with setitem
        cache[3] = 3
        # LRU: 1 0 3

        for i in 1, 0, 3:
            assert i in cache
            assert cache[i] == i

        cache[2] = 2
        # LRU: 0 3 2

        for i in 0, 3, 2:
            assert i in cache
            assert cache[i] == i

        assert 1 not in cache
        with pytest.raises(KeyError):
            assert cache[1]


class TestFIFO:
    """Test the LRU cache"""

    def test_unsized(self):
        """Test that not specifying a size lets the cache grow"""
        cache = FIFOCache()
        for i in range(500):
            cache[i] = i
        for i in range(500):
            assert i in cache
            assert cache[i] == i

    def test_sized_no_reuse(self):
        """Test basic LIFO functionality with all new values"""
        cache = FIFOCache(max_size=5)
        for i in range(5):
            cache[i] = i
        for i in range(5):
            assert i in cache
            assert cache[i] == i
        for i in range(5, 10):
            cache[i] = i
            assert i in cache
            assert cache[i] == i
            assert i - 5 not in cache
            with pytest.raises(KeyError):
                assert cache[i - 5]

    def test_sized_with_reuse(self):
        """Test LRU functionality"""
        cache = FIFOCache(max_size=3)
        for i in range(3):
            cache[i] = i
        # Cache: 0 1 2
        for i in range(3):
            assert i in cache
            assert cache[i] == i
        # Cache: 0 1 2

        cache[3] = 3
        # Cache: 1 2 3

        assert 0 not in cache
        with pytest.raises(KeyError):
            assert cache[0]

        for i in range(1, 4):
            assert i in cache
            assert cache[i] == i

        assert cache[1]
        # Cache: 1 2 3

        cache[0] = 0
        # Cache: 2 3 0

        assert 1 not in cache
        with pytest.raises(KeyError):
            assert cache[1]

        for i in 2, 3, 0:
            assert i in cache
            assert cache[i] == i


class TestTimedCache:

    def test_untimed(self):
        """Test that not specifying a size lets the cache grow"""
        cache = TimedCache()
        for i in range(500):
            cache[i] = i
        for i in range(500):
            assert i in cache
            assert cache[i] == i

    def test_timed(self):
        """Test that entries are removed if accessed after max_age"""
        time = 0.001
        cache = TimedCache(max_age=time)

        cache[1] = 1
        assert 1 in cache
        sleep(time)
        assert 1 not in cache
        with pytest.raises(KeyError):
            assert cache[1]

        for i in range(50):
            cache[i] = i
            assert i in cache
            assert cache[i] == i
        sleep(time)
        for i in range(50):
            assert i not in cache
            with pytest.raises(KeyError):
                assert cache[i]

    def test_timed_reset(self):
        """Test that resetting entries resets their time"""
        time = 0.005
        cache = TimedCache(max_age=time)

        cache[1] = 1
        assert 1 in cache
        assert cache[1] == 1
        sleep(time / 2)
        assert 1 in cache
        assert cache[1] == 1
        cache[1] = 1
        sleep(time / 2)
        assert 1 in cache
        assert cache[1] == 1
        sleep(time / 2)
        assert 1 not in cache
        with pytest.raises(KeyError):
            assert cache[1]
