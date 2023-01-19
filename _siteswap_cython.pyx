#!python
#cython: language_level=3
import cython
cimport cython

DEF ASIZE = 32

@cython.boundscheck(False)
cpdef set all_siteswaps_between(int period, int balls, int max_throw, int start, int stop):
    start = max(0, start)
    stop = min(period * balls + 1, max_throw + 1, stop)

    if period == 1 and start <= balls and stop > balls:
        return set('0123456789abcdefghijklmnopqrstuvwxyz'[balls])

    if stop <= start or stop < balls + 2:
        return set()

    cdef list a
    cdef int i
    cdef int j
    cdef int s
    cdef int d

    cdef bint balls_dont_collide
    cdef int k
    cdef int x
    cdef int check
    cdef int taken[ASIZE]

    cdef str siteswap

    cdef set siteswaps = set()

    if start <= balls:
        a = [balls+1] + [balls-1] + [balls] * (period-2)
    else:
        a = [start] + [0] * (period-1)
        j = period - 1

        s = period * balls - start

        while s != 0:
            d = min(s, start-1)
            s -= d
            a[j] = d
            j -= 1

    balls_dont_collide = True
    taken[:] = [0] * ASIZE

    for k, x in enumerate(a):
        check = (x+k) % period
        if taken[check] == 1:
            balls_dont_collide = False
            break
        taken[check] = 1
    
    if balls_dont_collide:
        siteswap = ''.join(['0123456789abcdefghijklmnopqrstuvwxyz'[x] for x in max([a[k:] + a[:k] for k in range(period)])])
        if len(siteswap) == 1 or (siteswap+siteswap).find(siteswap, 1, -1) == -1:
            siteswaps.add(siteswap)

    i = period - 2
    j = period - 1

    while True:
        while a[j] > 0 and a[i] < a[0]:
            a[i] += 1
            a[j] -= 1

            balls_dont_collide = True
            taken[:] = [0] * ASIZE

            for k, x in enumerate(a):
                check = (x+k) % period
                if taken[check] == 1:
                    balls_dont_collide = False
                    break
                taken[check] = 1
            
            if balls_dont_collide:
                siteswap = ''.join(['0123456789abcdefghijklmnopqrstuvwxyz'[x] for x in max([a[k:] + a[:k] for k in range(period)])])
                if len(siteswap) == 1 or (siteswap+siteswap).find(siteswap, 1, -1) == -1:
                    siteswaps.add(siteswap)

            if j != period - 1:
                i += 1
                j += 1

        while (
            i != 0 and a[i] + 1 > a[0]
            or a[i] == max_throw
            or a[i+1] == 0
        ):
            i -= 1

        if i == -1:
            break

        a[i] += 1

        if a[0] == stop:
            break

        while a[j] == 0:
            j -= 1

        a[j] -= 1
        j = period - 1
        
        while i < j:
            i += 1
            a[i], a[j] = a[j], a[i]
            j -= 1

        balls_dont_collide = True
        taken[:] = [0] * ASIZE

        for k, x in enumerate(a):
            check = (x+k) % period
            if taken[check] == 1:
                balls_dont_collide = False
                break
            taken[check] = 1
        
        if balls_dont_collide:
            siteswap = ''.join(['0123456789abcdefghijklmnopqrstuvwxyz'[x] for x in max([a[k:] + a[:k] for k in range(period)])])
            if len(siteswap) == 1 or (siteswap+siteswap).find(siteswap, 1, -1) == -1:
                siteswaps.add(siteswap)

        while a[i+1] != max_throw and i != period - 2:
            i += 1
        j = i + 1

    return siteswaps
