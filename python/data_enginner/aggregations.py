import pandas as pd
import numpy as np


# aggregation functions
p_league = pd.read_excel('project_data/premier_league_games.xlsx')

p_league.loc[:, ['HomeGoals', 'AwayGoals']].mean().sum()


# GROUPBY
p_league.groupby('AwayTeam')['AwayGoals'].mean()        # gouping a column and an aggregation (like in SQL)
# will return a Series

p_league.groupby('AwayTeam')[['AwayGoals']].mean()      # with 2 brackets will return a dataframe

# groupby by multi-columns
ag_league = p_league.groupby(['season', 'HomeTeam'], as_index=False)[['HomeGoals']].sum().query("HomeTeam == 'Arsenal'")

# By taking the entire line in paranthesis, you can write it into multiple lines
# (transactions
# .groupby(['store_nbr', 'month'])[['transactions']]
#  .sum().sort_values(
#      ['month', 'transactions'], ascending=[True, False]))


# MULTI-INDEXES; rarely used
# 		                
# season	    HomeTeam	    Homegoals
# 2008/2009	  Arsenal	            31
#             Aston Villa	        27
#             Blackburn Rovers	    22
#             Bolton Wanderers	    21
#             Chelsea	            33

ag_league.loc[('2008/2009', 'Arsenal'):('2008/2009', 'Bolton Wanderers')]

ag_league =  p_league.groupby(['season', 'HomeTeam']).agg({'HomeGoals': ['sum', 'mean']})
ag_league.loc['2010/2011', ('HomeGoals', 'mean')]


# MODIFYING MULTI-INDICES
ag_league.reset_index()     # goes back to basic dataframe
ag_league.swaplevel()
ag_league.droplevel()

ag_league.droplevel(0, axis=1).reset_index()        # to drop extra layers and go back to basic df


# AGG METHOD
# lets you aggregate all compatible columns

# specify wich columns to agg in dictionary forms, will create multilevels
(p_league.
 groupby(['season', 'HomeTeam'], as_index=False)
 .agg({'HomeGoals': ['sum', 'mean'],
      'AwayGoals': ['sum', 'sum']}))

# OR specify new_columns which will have "sum" or "mean", NO MULTILEVELS !!!
(p_league.
 groupby(['season', 'HomeTeam'], as_index=False)
 .agg(home_goals_sum = ('HomeGoals', 'sum'),
      away_goals_sum = ('AwayGoals', 'sum')))
