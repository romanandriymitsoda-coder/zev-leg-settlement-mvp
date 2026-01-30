.PHONY: install run all

install:
\tpip install -r requirements.txt

run:
\tpython scripts/run_mvp.py

all: install run

