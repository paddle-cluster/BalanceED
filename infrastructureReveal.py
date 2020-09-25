#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# Process and categorize data from Wireshark
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns; sns.set(rc={'figure.figsize':(15, 10), 'font.size':8,'axes.titlesize':8,'axes.labelsize':16})
import tkinter as tk
from tkinter import filedialog
import re
import warnings
import pprint

warnings.filterwarnings("ignore")
sep = '.'

# Specify a CSV file exported from Wireshark
root = tk.Tk()
root.withdraw()
path = filedialog.askopenfilename(title = 'Select a Wireshark CSV file')
with open(path, encoding="utf8", errors='ignore') as file:
    raw = pd.read_csv(file, index_col=[0], dtype=object)
raw = raw.loc[raw['Protocol'] == 'TCP']
raw['Domain'] = raw['Source'] +" "+ raw['Destination']
raw['Domain'] = raw['Domain'].str.lower().str.split('.')
filename = path.split('/')[-1].split('.')[0]
print(filename+' selected')
count_row = raw.shape[0]
print(str(count_row)+' packets')

# Specify own internet provider or institutional domain name
own = input("Enter your institution's domain name: ")
own = own.split(sep, 1)[0]

schema = pd.read_csv('providers.csv')
new_row = {'Name': own, 'Category': 'Institutional', 'Domain': own}
schema = schema.append(new_row, ignore_index=True)

# Categorize the data
cat = raw.copy()
cat['Domain'] = cat['Domain'].apply(lambda x: [item for item in x if item in schema['Domain'].tolist()])
cat['Domain'] = cat['Domain'].astype(str)
cat['Domain'] = cat['Domain'].str.replace('[^\w\s]','')
cat = cat.merge(schema, how='left', on='Domain')
cat.drop(['Time', 'Source', 'Destination', 'Length', 'Info', 'Protocol'], axis=1, inplace=True)
cat = cat.sort_values(by ='Category' )

# Visualize the results of the categorization
ax = sns.countplot(x='Name', hue='Category', dodge=False, data=cat)
ax.set(xlabel='Provider', ylabel='Packets exchanged')
ax.set_title(filename, fontsize=20)
plt.show()

# List the unknown domain names leftover
print('Unknown domain names:')
raw['Domain'] = raw['Domain'].astype(str)
raw['Domain'] = raw['Domain'].str.replace('[^\w\s]','')
raw['Domain'] = raw['Domain'].str.replace('[0-9]','')
uni = raw.Domain.unique()
known = re.compile('|'.join([re.escape(word) for word in schema.Domain]))
unknown = [word for word in uni if not known.search(word)]
pp = pprint.PrettyPrinter(indent=0)
pp.pprint(unknown)


# In[ ]:


# Save files
fig = ax.get_figure()
fig.savefig(filename+'.png', dpi=720)

with open(filename+'_unknowns.txt', mode='wt', encoding='utf-8') as out:
    out.write('\n'.join(unknown))

