#!python
#cython: language_level=3
import cython
cimport cython

# increase this if generating siteswaps for periods > 32
DEF ASIZE = 32

@cython.boundscheck(False)
cpdef set all_siteswaps_between(int period, int balls, int max_throw, int start, int stop):
    start = max(0, start)
    stop = min(period * balls + 1, max_throw + 1, stop)

    if period == 1 and start <= balls and stop > balls:
        # when period is 1, return just number of balls
        return set('0123456789abcdefghijklmnopqrstuvwxyz'[balls])

    if stop <= start or stop < balls + 2:
        # start / stop wrong. return an empty set
        return set()

    cdef list a
    cdef list b
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
        # due to cyclicity of siteswaps e.g. '144' == '414' == '441'
        # and us preferring the bigger ordering '441',
        # we don't have to check all patterns
        #
        # instead start from the next siteswap after the siteswap
        # consisting of only average throws
        #
        # for example if period=3 and balls=3, average is '333'.
        # then => start from '423'
        a = [balls+1] + [balls-1] + [balls] * (period-2)
    else:
        # a more complicated case. 'start' is the first number
        a = [start] + [0] * (period-1)
        j = period - 1

        # the rest of the sum
        s = period * balls - start

        # continue redistributing the sum so that the
        # next biggest number is the rightmost
        while s != 0:
            d = min(s, start-1)
            s -= d
            a[j] = d
            j -= 1

    # initialize indices. i < j
    i = period - 2
    j = period - 1

    while True:
        # siteswap collision check
        balls_dont_collide = True
        taken[:] = [0] * ASIZE

        for k, x in enumerate(a):
            check = (x+k) % period
            if taken[check] == 1:
                balls_dont_collide = False
                break
            taken[check] = 1

        if balls_dont_collide:
            # cycle the siteswap until we have the biggest ordering. e.g. '144' => '441'
            b = max([a[k:] + a[:k] for k in range(period)])
            if a == b:
                # it's fastest to do the next test with a string here.
                # also we want to ultimately return the siteswap as a string
                siteswap = ''.join(['0123456789abcdefghijklmnopqrstuvwxyz'[x] for x in a])
                # test if this siteswap has periodic sub-patterns
                if (siteswap+siteswap).find(siteswap, 1, -1) == -1:
                    # all good, add
                    siteswaps.add(siteswap)

        while a[j] > 0 and a[i] < a[0]:
            # add to i, subtract from j. e.g. '3122' => '3131'
            a[i] += 1
            a[j] -= 1

            # siteswap collision check
            balls_dont_collide = True
            taken[:] = [0] * ASIZE

            for k, x in enumerate(a):
                check = (x+k) % period
                if taken[check] == 1:
                    balls_dont_collide = False
                    break
                taken[check] = 1
            
            if balls_dont_collide:
                # cycle the siteswap until we have the biggest ordering. e.g. '144' => '441'
                b = max([a[k:] + a[:k] for k in range(period)])
                if a == b:
                    # it's fastest to do the next test with a string here.
                    # also we want to ultimately return the siteswap as a string
                    siteswap = ''.join(['0123456789abcdefghijklmnopqrstuvwxyz'[x] for x in a])
                    # test if this siteswap has periodic sub-patterns
                    if (siteswap+siteswap).find(siteswap, 1, -1) == -1:
                        # all good, add
                        siteswaps.add(siteswap)

            # if (i, j) are not the two rightmost indexes,
            # we might have to move i and j here
            if j != period - 1:
                i += 1
                j += 1

        # move i until we are in a spot we can increase
        while (
            i != 0 and a[i] + 1 > a[0]
            or a[i] == max_throw
            or a[i+1] == 0
        ):
            i -= 1

        if i == -1:
            break

        # increase a[i]
        a[i] += 1

        if a[0] == stop:
            break

        # move j until we are in a spot we can decrease from
        while a[j] == 0:
            j -= 1

        # decrease a[j] and move j back to rightmost
        a[j] -= 1
        j = period - 1
        
        while i < j:
            i += 1
            # swap a[i] and a[j]
            a[i], a[j] = a[j], a[i]
            j -= 1

        # move i until we are in a spot we can increase
        while a[i+1] != max_throw and i != period - 2:
            i += 1
        # move j
        j = i + 1

    return siteswaps
