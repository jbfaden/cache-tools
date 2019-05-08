An incomplete implementation of a Python version of a HAPI cache writer.

# Tests

Execute `make all` to run all tests.

The tests can be modified to use a different cache writing program by modifying the `COMMAND` variable in `Makefile`.

# TODO

* Add test to ensure empty file is written when a day of data or more is missing
* Add support for binary
* Add ability to write gzip files

# Contact

Bob Weigel <rweigel@gmu.edu>