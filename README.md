## justDice Analytics Engineer Hiring Case

### You can open the report via the link below:

#### https://kadiralat-analitic-engineer-task-main-z0hhp6.streamlit.app/

### Notes

#### NOTE 1

Null Value Checking
There is no null values in adspend.csv,installs.csv,payouts.csv,revenue.csv
```python
print(adspend.isnull().values.any()) -> False
print(installs.isnull().values.any()) -> False
print(payouts.isnull().values.any()) -> False
print(revenue.isnull().values.any()) -> False
```

Duplication Check:
For Adspending there is no duplication

For Payouts and Revenue, there are duplications but when the CSV file is examinated,
it can be seen that there are also different payout prices for the same day and same installation_id.
That means there can be many charges or revenues for the same day so,
duplications sould not be removed from dataframes for payouts and revenue.

For Installation:
There is only one duplication in installs dataframe.
If duplicated data generated by a mistake, it can be removed.
However, in another scenario installing same app under same network,country,os etc. might be the reason of duplication.
It can be considered that install_id values might be generated based on all other attributes in installs.csv:
-country_id
-app_id
-network_id
-event_date
-device_os_version
So that, if the user installs a specific app twice in his/her phone throughout same medium and same day, same install_id
can be generated.(Numerically it is possible and more unique install_id can be generated than install.csv already has)
Hypothesis 1: Each unique country_id-app_id-network_id-event_date-device_os_version combination generates a unique installation_id.
It can be tested by asking the question:
(q1)Is there anymore installation_id's under same condition as the duplicated installation_id? 
If the answer is yes, hypothesis 1 becomes false. If the answer is no, it still cannot be said that hypothesis 1 is true.
That just means that there is no extra data according to duplicated data's condition.
Additionally these questions should be asked:
(q2)How many unique add_ip-network_id-event_date-country_id combination are there?
(q3)How many unique install_id's are generated under same conditions?
Then the probability of truth of hypothesis 1 can be calculated.

q1: Yes, there are 8 output and 2 of installation_id are same so, Hypothesis 1 is false according to output of:
print("installs.loc[(installs['country_id']==1) & (installs['app_id']==71)
      & (installs['network_id']==60)
      & (installs['event_date']=='2022-08-20') & (installs['device_os_version']=='12') ])
      
If q1's answer was no, q2-q3 can be asked and answers can be found as below:     

q2-q3 : There are 67986 unique combinations and in average every unique combination has 3 installation id :

x= installs.groupby(['app_id','network_id','event_date','device_os_version','country_id'])['install_id'].count().reset_index(name='count').sort_values(['count'],ascending=False)
print(len(x)) -> 67986
print(x['count'].sum()/len(x)) -> around 3.5

That means in average 3.5 installation_id have proper condition to be same over 65k combination and only 2 installation_id
become same for only 1 combination. So, probably(more than 99%) hypothesis 1 is false even though question1(q1)'s answer is no.
