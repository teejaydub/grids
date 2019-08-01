run:
	python grids.py

test:
	python grids.py --test

install:
	easy_install .

depends:
	conda env create
	conda activate grids
