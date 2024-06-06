# import nbformat
# from nbconvert import PythonExporter
# import os

# def convert_notebook(notebook_path, output_path):
#     with open(notebook_path, 'r', encoding='utf-8') as f:
#         nb = nbformat.read(f, as_version=4)

#     exporter = PythonExporter()
#     source, _ = exporter.from_notebook_node(nb)

#     with open(output_path, 'w', encoding='utf-8') as f:
#         f.write(source)

# # Example usage
# notebook_path = os.path.join(os.path.dirname(__file__), 'script', 'Automated MeroKirana Scrape.ipynb')
# output_path = os.path.join(os.path.dirname(__file__), 'script', 'Automated MeroKirana Scrape.py')

# convert_notebook(notebook_path, output_path)
