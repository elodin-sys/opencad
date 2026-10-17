# std::runtime
Functions for debugging and interacting with the runtime system.
### exit !exp
`exit()`
Remember to always remove the call to `exit()` after debugging is complete.
When `exit()` is used in an imported module, only the imported module exits early. Because imported modules execute concurrently, `exit()` in one module does not affect other modules.
