
def standardISO8601( isostr ):
    'convert HAPI yyyy-doy strings to yyyy-mm-dd strings, if necessary.  The result will be'
    '$Y-$m-$dT$H:$M:$S.$(subsec,places=9)'
    l= len(isostr)
    if ( l==4 ):
        isostr= isostr + '-01-01'
    elif ( l==7 ):
        isostr= isostr + '-01'
    elif ( l<8 ):
        raise Exception( "isostr appears to be malformed: "+isostr )
    if ( isostr[7]!='-' ):
        import datetime
        jan1= datetime.datetime(int(isostr[0:4]),1,1)
        jjj= int(isostr[5:8])
        result= jan1 + datetime.timedelta(days=(jjj-1))
        isostr= '%04d-%02d-%02d' % ( result.year, result.month, result.day ) + isostr[8:]
    norm= '0000-01-01T00:00:00.000000000Z'
    if ( isostr[-1]=='Z' ):
        return isostr[0:-1] + norm[len(isostr)-1:]
    else:
        return isostr + norm[len(isostr):]
        
#print standardISO8601('2009')
#print standardISO8601('2009-01-01T01:00Z')
#print standardISO8601('2009-001T01:00Z')
#print standardISO8601('2009-150T01:00Z')
#print standardISO8601('2000-150T01:00Z')