# cache-tools
A collection of tools for reading, writing, and managing a cache of HAPI responses

# Proposed Specification

Issues:
* Should metadata (http headers) be cached as well?
* Should the scientist be able to lock the cache so that updates will not occur?

The following is a description of a recommended directory and file schema for programs that cache HAPI data.

`HAPI_DATA` should be the environment variable indicating the HAPI cache directory. If not specified, the [logic of Python's `tempfile` module](https://stackoverflow.com/questions/847850/cross-platform-way-of-getting-temp-directory-in-python) should be used to get the system temporary directory to which `hapi_data` should be appended, e.g., `/tmp/hapi_data` will be a common default.

While writing a file, a program should append `.writing.PID`, where `PID` is the writing programs process id, to the filename then move `filename.writing.PID` to `filename` when the write is complete.  `.writing.pid` files which appear to be idle (last modified greater than 1 hour ago), because a process was abandoned or failed, should be deleted by cache software.

Data directory naming: If `cadence` is given

* `cadence < PT1S` - files should contain 1 hour of data and be in subdirectory `DATASET_ID/$Y/$m/$d/`. File names should be `$Y$m$dT$H.VARIABLE.EXT`.
* `PT1S <= cadence <= PT1H` - files should contain 1 day of data and be in subdirectory `DATASET_ID/$Y/$m/`. File names should be `$Y$m$d.VARIABLE.EXT`.
* `cadence > PT1H` - files should contain 1 month of data of data and be in a subdirectory of `DATASET_ID/$Y/`. File names should be `$Y$m.VARIABLE.EXT`.

If `cadence` is not given, the caching software should make a guess at the cadence and choose the appropriate directory structure.  Likewise software using the cache should assume that other software may have different logic, and should check all resolutions.

Files should contain only data for the parameter, e.g., `19991201.Time.csv` will contain a single column with just the timestamps that are common to all parameters in the dataset. The file `19991201.Parameter1.csv` would not contain timestamps. If a user requests `Parameter1`, a program reading the cache will need to read two files, the `Time` file and the `Parameter1` file, to return the required data for `Parameter1`.

Directory structure for `PT1S <= cadence <= PT1H`:

```
hapi_data/
  # http://hapi-server.org/servers/SSCWeb/hapi
  http/
    hapi-server.org/
      servers/
        SSCWeb/
          hapi/
            capabilities.json
            catalog.json
            data/
            info/
              
  # https://cdaweb.gsfc.nasa.gov/hapi
  https/
    cdaweb.gsfc.nasa.gov/
          hapi/
            capabilities.json
            catalog.json
            data/
              A1_K0_MPA/2008/01/
                20080103.csv{.gz}         # All parameters   
                20080103.binary{.gz}      # All parameters       
                20080103.Time.csv{.gz}    # Single column 
                20080103.Time.binary{.gz}
                20080103.sc_pot.csv{.gz}  # Single column 
                20080103.sc_pot.binary{.gz} 
                ...
              AC_AT_DEF/2009/02/
              ...              
            info/
              A1_K0_MPA.json
              AC_AT_DEF.json
              ...
```
