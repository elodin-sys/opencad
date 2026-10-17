"""CadQuery runner: `python -I -m opencad.backends.cadquery.runner --entry main.py ...`."""

from opencad.backends.pyrunner import main

if __name__ == "__main__":
    raise SystemExit(main(ns_name="__cq_main__"))
