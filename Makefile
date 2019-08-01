run:
	python grids.py

test:
	python grids.py test

install:
	pip install --editable .

depends:
	conda env create
	conda activate grids
