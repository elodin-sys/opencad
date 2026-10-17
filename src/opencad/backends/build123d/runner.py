"""build123d runner: `python -I -m opencad.backends.build123d.runner --entry main.py ...`."""

from opencad.backends.pyrunner import main

if __name__ == "__main__":
    raise SystemExit(main(ns_name="__b3d_main__"))
