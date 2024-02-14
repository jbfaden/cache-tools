I wanted to make notes about how a hit could be resolved, given our discussion
today.

Using URL, dataset, parameters, start, stop, and format:

1. does an exact match exist in the cache?  URL+dataset+parameters+start+stop.format
2. does a parameter superset exist in the cache?  URL+dataset+*+start+stop.format, extract the subset
3. does a time range superset exist in the cache?  URL+dataset+parameters+*+*.format, extract the subset
4. can I concatenate granules to cover the interval?
5. can I take a parameter subset of the granules?

"time range subset" means to read in the cache item, and extract only the records which are within a time range
"parameter subset" means to take A,B,C  and extract A,C

Note besides format, there is also with and without a header.  Jon suggests always cache the header, and then pop it
off if it is not needed.

# Cache miss
Can a cache item be extended to create a cache hit?  Yes->only request the extension.  Of course this is not done for granules.  Combine the two to make one cache item.  The time stamp is that of the old cache item.

Can a cache request be extended to an integer number of granules?  Yes->extend and request these granules.  If any of the granules are already in the cache, use them.

Is a parameter subset of a request in the cache already?  Yes->request the new set of parameters and delete (unload) the old set cache.


