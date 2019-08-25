test:
	python grids.py test

run:
	python grids.py

install:
	pip install --editable .

depends:
	conda env create
	conda activate grids
