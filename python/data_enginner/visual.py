import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib

transactions = pd.read_csv('transactions.csv', parse_dates=['date'])

# transactions.plot(x='date', y='transactions', kind='line')
transactions.set_index('date').plot()   # the same as x=date

plt.show()

plt.xlabel('date')
plt.ylabel('transactions')
plt.grid(True)

# NARROWING DOWN
transactions.set_index('date').loc['2013-01'].plot()

transactions.query('store_nbr == 44').set_index('date').loc['2013-01', 'transactions'].plot()

transactions.query("store_nbr in [44, 47]").pivot_table(index='date', columns='store_nbr').droplevel(0, axis=1).plot()


# COLORS, STYLE, APLHA (transperancy)

transations = (transactions
        .query('store_nbr in [44, 47] and date.dt.year == 2014')
        .pivot(index='date', columns='store_nbr', values='transactions')
        .plot(
            title='transactions',
            xlabel='date',
            ylabel='daily',
            color=['red', 'black'],
            alpha=.3,                       # transperency
            style=['-', '--'],
            grid=True
        )).legend(loc='center left')  # legend(bbox_to_anchor=(1, 1)       # move legend (box with explanation)


# Seaborn style (adds background) add before code ADN meplotlib background
sns.set_style('darkgrid')
matplotlib.style.use('fivethirtyeight')

transactions = pd.read_csv("../retail/transactions.csv")

stores_1234 = (transactions
                .loc[transactions["store_nbr"].isin([1, 2, 3, 4])]  #filter to stores 1, 2, 3, 4
                .pivot_table(index="date", columns="store_nbr") # Createa pivot table
                .droplevel(0, axis=1))  # drop outer layer of column axis

# SUBPLOTS breking dataframe into several charts
transations = (transactions
        .query('store_nbr in [44, 47] and date.dt.year == 2014')
        .pivot(index='date', columns='store_nbr', values='transactions')
        .plot(
            subplots = True,
            layout = (1, 2),     # one row, 2 charts
            sharey = True,       # both charts will share one number grid
            figsize = (10, 10)   # size of charts      
        ))


# CHART TYPES

# Bar
store_40s = list(range(40, 50))
(
transactions
    .query('store_nbr in @store_40s')
    .groupby(['store_nbr'])
    .agg({'transactions': 'sum'})
    .sort_values(by='transactions')
    .plot.bar(figsize=(10, 10))
)

# Grouped/Stacked Bar
store_40s = list(range(40, 50))
(
transactions
    .query('store_nbr in @store_40s and date.dt.month in [1, 2, 3]')
    .pivot_table(index=transactions['date'].dt.month,
                columns=transactions['store_nbr'],
                values='transactions',
                aggfunc='sum')
).plot.bar(stacked=True).legend(bbox_to_anchor=(1, 1))      # bar=vertical, barh=horizontal


stores_1234.index = stores_1234.index.astype("datetime64[ns]") 
stores_1234.sum().sort_values(ascending=False).plot.bar()

stores_1234_monthly = stores_1234.groupby(stores_1234.index.month).sum()
(stores_1234_monthly
 .sort_index(ascending=False)    # sort in ascending order so lowest comes first (technically this code is redundant)
 .plot.barh(stacked=True)        # created stacked bar chart (will stack by column names)
 .legend(bbox_to_anchor=(1, 1))  # Move legend to better location
)

# Scatterplots
stores_1234.plot.scatter(x=3, y=2) # you could have flipped x and y, not a problem

stores_1234.plot.scatter(x=3, 
                         y=2, 
                         c=stores_1234.index.month,  # color by month
                         colormap="Set2");           # specify colormap "Set2", choose your own!

# Pie
# Example pie chart for reference

(stores_1234
 .sum()                        # sums of stores
 .sort_values(ascending=True)  # Sort from low to high
 .plot 
 .pie(startangle=90)           # start first slice at 12 o'clock
)

# Histograms
# grab columns for stores 2 and 3, plot a histogram with transparency specified by alpha
stores_1234.loc[:, [2, 3]].plot.hist(alpha=.3)

