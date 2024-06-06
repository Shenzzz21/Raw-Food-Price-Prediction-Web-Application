from celery import shared_task
import subprocess
import os
# from .convert_notebook import convert_notebook

@shared_task
def run_scraping_script():
    print('Running code yayyy~')
    # notebook_path = os.path.join(os.path.dirname(__file__), 'script', 'Automated MeroKirana Scrape.ipynb')
    output_path = os.path.join(os.path.dirname(__file__), 'script', 'Automated MeroKirana Scrape.py')
    # convert_notebook(notebook_path, output_path)
    result = subprocess.run(["python", output_path], check=True)
    print("Scraping script finished with return code:", result.returncode)

