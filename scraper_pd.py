import pandas as pd


url = "https://cs.wikipedia.org/wiki/Pandemie_COVID-19_v_%C4%8Cesku"
data_table = pd.read_html(url, attrs={"class": "wikitable plainrowheaders sortable"})
print(data_table)