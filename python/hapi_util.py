def standardISO8601(isostr):
    """Convert HAPI ISO8601 time strings to $Y-$m-$dT$H:$M:$S.$(subsec,places=9)Z format

    Usage
    --------
    standardISO8601(str), where str is a restricted ISO 8601 string [1]
    returns a string of the form $Y-$m-$dT$H:$M:$S.$(subsec,places=9)Z

    Examples
    --------
        >>> standardISO8601('2009')
        '2009-01-01T00:00:00.000000000Z'

        >>> standardISO8601('2009-01-01T01:00Z')
        '2009-01-01T01:00:00.000000000Z'

        >>> standardISO8601('2009-001T01:00Z')
        '2009-01-01T01:00:00.000000000Z'

        >>> standardISO8601('2009-150T01:00Z')
        '2009-05-30T01:00:00.000000000Z'

        >>> standardISO8601('2000-150T01:00Z')
        '2000-05-29T01:00:00.000000000Z'

    Reference
    ---------
    [1] `<https://github.com/hapi-server/data-specification/blob/master/hapi-dev/HAPI-data-access-spec-dev.md#representation-of-time>`_
    """

    l = len(isostr)
    if l == 4:
        isostr = isostr + '-01-01'
    elif l == 7:
        isostr = isostr + '-01'
    elif l < 8:
        raise ValueError("isostr appears to be malformed: " + isostr)
    if isostr[7] != '-':
        import datetime
        jan1 = datetime.datetime(int(isostr[0:4]), 1, 1)
        jjj = int(isostr[5:8])
        result = jan1 + datetime.timedelta(days=(jjj-1))
        isostr = '%04d-%02d-%02d' % (result.year, result.month, result.day) + isostr[8:]
    norm = '0000-01-01T00:00:00.000000000Z'
    if isostr[-1] == 'Z':
        return isostr[0:-1] + norm[len(isostr)-1:]
    else:
        return isostr + norm[len(isostr):]

if __name__ == "__main__":
    import sys
    pairs = [
                '2009', '2009-01-01T00:00:00.000000000Z',
                '2009-01-01T01:00Z', '2009-01-01T01:00:00.000000000Z',
                '2009-001T01:00Z', '2009-01-01T01:00:00.000000000Z',
                '2009-150T01:00Z', '2009-05-30T01:00:00.000000000Z',
                '2000-150T01:00Z', '2000-05-29T01:00:00.000000000Z'
             ]

    for p in range(0, len(pairs), 2):
        sys.stdout.write("Testing %s -> %s" % (pairs[p], pairs[p+1]))
        assert standardISO8601(pairs[p]) == pairs[p+1]
        sys.stdout.write(" Pass\n")