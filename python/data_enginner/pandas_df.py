import pandas as pd
import numpy as np


""" DATAFRAMES """

# base python into dataframe, rarely used

dt = pd.DataFrame(
    {
        'item_id': [1, 2],
        'item_name': ['item_1', 'item_2'],

    }
)

dt.shape
dt.index
dt.columns
dt.columns = ['id', 'name']     # changed name of the columns
dt.axes         # number of lines and names of columns
dt.head()       # firts five lines
dt.tail()       # last five lines
dt.sample()     # random sample
dt.info()
dt.info(show_counts=True)       # if more then 1.7 min lines, u need this to display the NaN values
dt.describe()       # will, show mean, max, min etc.
dt.describe(include='all').round()       # even MORE info !

dt.isna().sum()         # count NaN
dt['id']                # get column
dt[['id', 'name']]      # get 2 columns


# iloc STOP POINT NOT INCLUSIVE !!!
dt.iloc[:5, :1]         # first axis is rows, second is column, works with numerical indexes
dt.iloc[:, -1]          # will grab data_series
dt.iloc[:, [-1]]          # will grab data_frame


# loc STOP POINT IS INCLUSIVE !!!
dt.loc[:, 'id']             # [ROWS, COLUMNS]
dt.loc[:, 'id': 'name']     # get slice
dt.loc[:, ['id', 'name']]   # get all data from columns

oil = pd.read_csv('oil.csv')
oil.columns = ['data', 'price']     # rename columns
oil['euro price'] = oil['price'] * 1.1      # create new column
print(oil.head())


# drop
oil.drop('price', axis=1)                           # will not change/save dataframe
oil.euro = oil.drop('price', axis=1)                # will create a var with a new data frame
oil.drop('price', axis=1, inplace=True)             # WILL  change/save dataframe
oil = pd.concat([oil, oil.iloc[[-1]]], ignore_index=True)       # duplicates the last row


# duplicates
oil.duplicated()        # return True on duplicates
oil.duplicated(subset='price').sum()        # count duplicates
oil.drop_duplicates(subset=['price'], keep='last', ignore_index=True)       # delete duplicates, subset=keep last duplicate, ingonre_index = removes gaps


# NaN
oil.isna().sum()        # count Null values
oil.fillna(0)           # fill missing values with 0
oil.fillna({'price':0}) # fill missing values in a column 'price'
oil['price'].fillna(0)
oil.dropna()            # drop missing values


# filtering
oil.loc[oil['price'] > 100]

oil['benchmark'] = 100      # creating new column
oil.loc[oil['price'] > oil['benchmark']]        # use it for filtering

oil.loc[oil['date'].str[:4] == '2013']      # slice off year using str() and use it as a filter

mask = ([oil['price'] > oil['benchmark']])

mask = (oil['dcoilwtico'] > oil['benchmark']) & (oil['date'].str[:4] == '2013')     # multiple conditions filter
oil[mask]


# filtering with QUARY()
oil = pd.read_csv('oil.csv', parse_dates=['date'])      # parse_dates will make dates datetime64 dtype
oil.query('dcoilwtico > benchmark and date.dt.year == 2013')
smokers_southeast = dt.query('smoker == "yes" and region == "southeast"')       # column names dont have "", values DO
# transactions.query("store_nbr in [25, 31] and date.str[6] in ['5', '6'] and transactions < 2000").sum().iloc[2]
oil.query('price > 93')['date']         # can add filter to grab one column



# sorting
oil.sort_index(ascending=False)         #from highest to lowest
oil.sort_index(axis=1)         # axis 1 will sort column name

oil.sort_values(['month', 'dcoilwtico'], ascending=[True, False])       # date by 2 columns, and giving them different ascending values


# renaming
oil.columns = ['new name', 'another_new_name']
oil.columns = [column.upper() for column in oil.columns]        # make all columns UPPER_CASE

oil.rename(columns={'old name': 'new name', 'old name': 'new name'})
oil.rename(columns=lambda x: x.upper())         # upper


# reorder
oil.reindex(labels=['order', 'of', 'columns'], axis=1)


# create new columns
oil['bench_ratio'] = oil.loc[:, 'dcoilwtico'] / oil.loc[:, 'benchmark'] * 100

oil['buy'] = (oil.loc[:, 'bench_ratio'] < 80) * (1000000 / oil.loc[:, 'dcoilwtico'])        # add * to add boolean columns
                    # boolean                           execute if true

oil['buy'] = np.where(oil['price'] > 100, 'Too High', 'Buy')        # using numpy 'where'


# create a new column on multiple conditions with multiple values
conditions = [
    (oil['price'] > 100),
    (oil['price'] <= 100) & (oil['price'] > 50),
    (oil['price'] <= 50)
]

choices = ['Dont Buy', 'Buy', 'Strong Buy']         # name for values

oil['buy'] = np.select(conditions, choices, default='Missing')          # default will fill NaN
oil['date'].dt.day


# create multiple columns with assign()  VERY USEFULL!
retail = pd.read_csv('retail.csv')
sample_df = retail.sample(5, random_state=22)

sample_df.assign(
    onpromotion_flag = sample_df['onpromotion'] > 0,
    family_abbrev = sample_df['family'].str[:3],
    onpromotion_ratio = sample_df['sales'] / sample_df['onpromotion'],
    sales_target = lambda x: x['onpromotion_ratio'] > 100       # can create new columns using columns u just created within assign()
).query('sales_target == True')

df = pd.read_csv('insurance_data.csv')
new_df = df.assign(
    sex_abbrev = df['sex'].str[0],
    high_risk = lambda x: (x['sex_abbrev'] == 'm') & (df['bmi'] > 27.5)     # need to use lambda to use newly created columns
)


# mapping
product_dict = {
    'PRODUCE': 'Grocery',
    'POULTRY': 'Grocery',
    'GROCERY I': 'Grocery',
    'GROCERY II': 'Grocery',
    'EGGS': 'Grocery'}

retail.loc[:, 'family'].map(product_dict)
# 0              NaN
# 1              NaN
# 2              NaN
# 3              NaN
# 4              NaN
#             ...   
# 1054939    Grocery
# 1054940        NaN
# 1054941    Grocery
# 1054942        NaN
# 1054943        NaN
# Name: family, Length: 1054944, dtype: object


# 'category' datatype, will save memory
retail = retail.astype({'family': 'category'})          # converting a column into category datatype
# in the background every family text value is assigned to an integer
# usefull for big df


# converting datatypes astype()
retail['sales_int'] = retail['sales'].astype('int')         # creating a new column with diff dtype

retail = retail.astype({'date': 'datetime64[as]', 'onpro': 'float'})        # convert 2 columns at once


# memory usage
retail.info(memory_usage='deep')                # memory info
retail.drop('id', axis=1, inplace=True)         # drop columns to save memory
retail.astype({'date': 'datetime64[ns]'})       # conver dtypes to save memory
retail['sales'] = retail['sales'].replace('-', np.nan).str.strip('$').astype('float')
                                                # remove symbols in order to convert dtype
retail.astype({'sales': 'int8'})                # replace bit size, SHOULD BE CAREFULL !!!
retail = retail.astype({'family': 'category'})  # use category dtype when there is not a lot of values in column



