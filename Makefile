install:
	poetry install

activate:
	poetry shell

notebook:
	poetry shell
	jupyter notebook

output:
	sh scripts/execute_notebooks.sh

download:
	sh scripts/download.sh

dashboard:
	streamlit run src/visualize.py

.PHONY: output
