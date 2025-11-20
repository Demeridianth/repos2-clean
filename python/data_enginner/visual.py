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
