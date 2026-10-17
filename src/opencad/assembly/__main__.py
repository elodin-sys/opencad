from opencad.assembly.cli import main

if __name__ == "__main__":  # a multiprocessing child that imports __main__ must not run the CLI
    raise SystemExit(main())
