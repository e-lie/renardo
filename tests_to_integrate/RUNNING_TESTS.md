

## Testing FoxDot/Renardo

This package, the Supercollider music backend for Renardo is the standard/legacy music backend used in FoxDot, just made modular.

One of the goal of Renardo is to stay compatible with FoxDot music code while the whole software is progressively split, rewritten, simplified, and made modular.
This process usually involve a lot of testing to avoid regression. But how to test a music software like FoxDot/Renardo ?

**Unit tests** are always a good idea when there are simple/stable enough functions to test against to ensure stability. We do / want to do more unit tests but for now the functions are really moved around and the original software has a kinda entangled architecture that make unit testing uneasy.

**Functional tests** are a good idea when there is a reproducible way of interacting with the software from the outside. But when the result is music it looks non standard to test (but maybe we haven't dug enough). So we are using a custom way to look for reproducible output : recording then verifying OSC messages sent to scsynth server by the python code to see if it sends the right music instructions.

Both test types are complementary and we will do partially both in the future but for now we will show the functional test strategy proposed.

### Using Functional tests to compare output

```sh
RENARDO_TEST_MODE=record pytest test_functional_renardo_sc.py -v
# this will record OSC message for different renardo/foxdot code in json file called session (last session is not overwritten)


RENARDO_TEST_MODE=verify pytest test_functional_renardo_sc.py -v
# this will replay music code and compare the messages with the last recorded session
```

This strategy is kinda hard to stabilise as there may be slight differences in IDs and parameters that lead tests to fail. Need to work further on more stable comparison method and maybe reworking the backend message generation.

### Disabling exception catching and using pass_through mode

The functional tests have a third `pass_through` mode that just disable the proxy to let the message go to scsynth producting sound. We can then check by ear if every tests produce the right music.

Another strategy is to let the tests fail by the exceptions emitted during execution. Usually FoxDot/Renardo catches most exceptions to avoid crashing during music performance. But we can disable this catching to let the code crash on bug making functions failing.

### Write new tests

```