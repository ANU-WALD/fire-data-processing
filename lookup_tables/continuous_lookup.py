"""Create continuous lookup table."""
# coding: utf-8

# In[1]:


import pandas as pd


# In[20]:


data_set = pd.read_excel('repos/fire-data-processing/lookup_tables/resimulated'
                         '/LUTs_continuo.xlsx', sheetname=None)

data_set


# In[27]:


# read data
data_set = pd.read_excel('repos/fire-data-processing/lookup_tables/resimulated'
                         '/LUTs_continuo.xlsx', sheetname=None)

# add a landcover column to data
objects = []
for i, output in data_set.items():
    if not i.startswith('LUT'):
        continue
    output.insert(loc=0, column='landcover', value=i)
    objects.append(output)

# concat the data into one table
new_data_set = pd.concat(objects)
new_data_set

# In[67]:

# for item in dataset, create a set of the columns
list_of_sets = [set(data_set[i].columns) for i in data_set if 'LUT' in i]

# unpack list as a union and intersection
# get difference
union = set.union(*list_of_sets)
intersection = set.intersection(*list_of_sets)
difference = union.difference(intersection)

[s for s in intersection if not isinstance(s, int)]


# In[68]:


difference


# In[112]:


# New_data_set[['LAI', 405]]
# read data
data_set = pd.read_excel('repos/fire-data-processing/lookup_tables/resimulated'
                         '/LUTs_continuo.xlsx', sheetname=None)

# add a landcover column to data
objects = []
for i, output in data_set.items():
    if not i.startswith('LUT'):
        continue

    if i.lower().startswith('lut_a'):
        i = 'forest'
    elif i.lower().startswith('lut_p'):
        i = 'grass'
    elif i.lower().startswith('lut_m'):
        i = 'shrub'

    output.insert(loc=0, column='landcover', value=i)
    output.columns = [x.lower() if isinstance(x, str) else x
                      for x in output.columns]

    try:
        output.rename(columns={'suelo': 'soil'}, inplace=True)
    except Exception:
        pass

    objects.append(output)


# concat the data into one table
new_data_set = pd.concat(objects)

# drop 'unanmed: 7' because
# half of the data is missing, others are acronynms (?)
# new_data_set['unnamed: 7'].fillna('unknown').value_counts()
new_data_set.drop('unnamed: 7', axis=1, inplace=True)

new_data_set


# In[113]:


list(new_data_set.columns)


# In[114]:


new_data_set[['landcover']]


# In[115]:


new_data_set.to_csv('continuous_lookup.csv')
