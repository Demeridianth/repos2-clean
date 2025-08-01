import pandas as pd
import matplotlib.pyplot as plt


transactions = pd.read_csv('oil.csv', parse_dates=['date']).dropna(subset=['dcoilwtico'])

transactions.plot(x='date', y='dcoilwtico', kind='line')
transactions.set_index('date').plot()   # the same as x=date

plt.show()

plt.xlabel('date')
plt.ylabel('dcoilwtico')
plt.grid(True)

# NARROWING DOWN
transactions.set_index('date').loc['2013-01'].plot()

transactions.query('store_nbr == 44').set_index('date').loc['2013-01', 'transactions'].plot()

transactions.query("store_nbr in [44, 47]").pivot_table(index='date', columns='store_nbr').droplevel(0, axis=1).plot()




