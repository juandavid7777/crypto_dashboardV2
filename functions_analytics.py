import streamlit as strl

import pathlib
from bs4 import BeautifulSoup
import logging
import shutil

def inject_ga():
    GA_ID = "google_analytics"

    GA_JS = """
    <!-- Global site tag (gtag.js) - Google Analytics -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-JLYYFBB2ZD"></script>
    <script>
        window.dataLayer = window.dataLayer || [];
        function gtag(){dataLayer.push(arguments);}
        gtag('js', new Date());

        gtag('config', 'G-JLYYFBB2ZD', { 'debug_mode':true });
    </script>
    """

    # Insert the script in the head tag of the static template inside your virtual
    index_path = pathlib.Path(strl.__file__).parent / "static" / "index.html"
    logging.info(f'editing {index_path}')
    soup = BeautifulSoup(index_path.read_text(), features="html.parser")
    if not soup.find(id=GA_ID): 
        bck_index = index_path.with_suffix('.bck')
        if bck_index.exists():
            shutil.copy(bck_index, index_path)  
        else:
            shutil.copy(index_path, bck_index)  
        html = str(soup)
        new_html = html.replace('<head>', '<head>\n' + GA_JS)
        index_path.write_text(new_html)