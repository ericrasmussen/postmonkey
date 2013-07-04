Contributing
============

Feature Additions/Requests
--------------------------
I'm very interested in discussing use cases that `PostMonkey`
doesn't cover.

If you have an idea you want to discuss further, ping me (erasmas) on freenode,
or feel free to open an issue/submit a pull request (tests included, please!).

If you would like to issue a pull request, I also ask that you make the request
from a new feature.<your feature> branch so that I can spend some time testing
the code before merging to master.


Notes on Testing
----------------
The test suite is written in a way that may be unusual to some, so if you submit
a patch I only ask that you follow the testing methodology employed here. On a
technical level it boils down to:

#. Parameterizing classes or functions that connect to outside systems
#. In tests, supplying dummy instances of those classes

In general for unit tests I prefer explicit dummies to mocking.

