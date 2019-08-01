run:
	python grids.py

test:
	python grids.py --test

depends:
	conda env create
	conda activate grids
