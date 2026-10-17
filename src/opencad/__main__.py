from opencad.cli import main

if __name__ == "__main__":  # never run the CLI on import (multiprocessing children re-import __main__)
    raise SystemExit(main())
