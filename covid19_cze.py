from requests import get
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit


def fit_func(x_values, a, b):
    return a * np.exp(b * x_values)


def parse_date(str_date):
    months_dict = {
        " března": "3.",
        " dubna": "4.",
        " května": "5."
    }
    for i in months_dict:
        str_date = str_date.replace(i, months_dict.get(i))
    return str_date


url = "https://cs.wikipedia.org/wiki/Pandemie_COVID-19_v_%C4%8Cesku"
response = get(url)
html = BeautifulSoup(response.text, 'html.parser')
prediction_horizon = 1  # days
data_dict = {"date": [],
             "infected_day": [],
             "infected_total": [],
             "recovered_day": [],
             "recovered_total": [],
             "deaths_day": [],
             "deaths_total": [],
             "tested_day": [],
             "tested_total": []
             }
data = []
table = html.find("table", {"class": "wikitable plainrowheaders sortable"})
table_body = table.find("tbody")
days = table_body.find_all("a")

for day in days:
    day_str = day.string
    data_dict["date"].append(day_str.replace(u"\xa0", u" "))

rows = table_body.find_all("tr")
for row in rows:
    cols = row.find_all("td")
    cols = [ele.text.strip() for ele in cols]
    data.append([ele for ele in cols if ele])

for day_data in data[2:]:
    for idx, value in enumerate(day_data[1:]):
        value = value.replace(u"\xa0", u"")
        try:
            if idx == 0:
                data_dict["infected_total"].append(int(value))
            elif idx == 2:
                data_dict["recovered_total"].append(int(value))
            elif idx == 4:
                data_dict["deaths_total"].append(int(value))
            elif idx == 6:
                data_dict["tested_total"].append(int(value))
        except ValueError:
            pass

data_dict["tested_day"] = [j-i for i, j in zip(data_dict["tested_total"][:-1], data_dict["tested_total"][1:])]
data_dict["tested_day"].insert(0, 11)
data_dict["deaths_day"] = [j-i for j, i in zip(data_dict["deaths_total"][:-1], data_dict["deaths_total"][1:])]
data_dict["deaths_day"].insert(0, 0)
data_dict["recovered_day"] = [j-i for i, j in zip(data_dict["recovered_total"][:-1], data_dict["recovered_total"][1:])]
data_dict["recovered_day"].insert(0, 0)
data_dict["infected_day"] = [j-i for i, j in zip(data_dict["infected_total"][:-1], data_dict["infected_total"][1:])]
data_dict["infected_day"].insert(0, 3)
x = range(len(data_dict["infected_total"]))
opt_params, pcov = curve_fit(fit_func, x, data_dict["infected_total"])


plt.plot(data_dict["infected_total"], "s", marker="+", label="Detected cases")
for j, k in zip(x, data_dict["infected_total"]):
    label = "{:.0f}".format(k)
    plt.annotate(label,  # this is the text
                 (j, k),  # this is the point to label
                 textcoords="offset points",  # how to position the text
                 xytext=(0, -20),  # distance from text to points (x,y)
                 ha='center')  # horizontal alignment can be left, right or center

plt.plot(x, fit_func(x, *opt_params), "r-",
         label="Fitted curve a * exp(b*day).\na={0:.4f}, b={1:.4f}".format(opt_params[0], opt_params[1]))
plt.grid()
plt.xlabel("day idx since 01/03/2020 [-]")
plt.ylabel("number of infected [-]")

prediction_ts = range(len(x) + prediction_horizon)
x_prediction = prediction_ts[-prediction_horizon:]
plt.plot(x_prediction,
         fit_func(x_prediction, *opt_params), "g.", label="prediction")
for j, k in zip(x_prediction, fit_func(x_prediction, *opt_params)):

    label = "{:.0f}".format(k)
    plt.annotate(label,  # this is the text
                 (j, k),  # this is the point to label
                 textcoords="offset points",  # how to position the text
                 xytext=(0, -20),  # distance from text to points (x,y)
                 ha='center')  # horizontal alignment can be left, right or center

plt.xticks(prediction_ts, [parse_date(str_date) for str_date in data_dict["date"]])
plt.legend()
plt.show()
