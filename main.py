#Kadir Alat 15/04/2023
#JustDice Analytics Engineer Hiring Case

#importing libraries
import warnings
import pandas
import streamlit as st
import pandas as pd
from PIL import Image
import plotly.graph_objects as go
import plotly.express as px
import prophet
from prophet.plot import plot_plotly
import boto3
from dotenv import load_dotenv
import os


# Streamlit Page Setting
st.set_page_config(layout="wide")
with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
# ignore warning for console
warnings.simplefilter(action='ignore', category=FutureWarning)
# load .env file for aws credentials
load_dotenv()

#creating session for aws s3 to pull tas data
session = boto3.session.Session(
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_DEFAULT_REGION")
)
s_3 = session.resource("s3")

#Reading data from s3
def read_aws_data(data_object,dataframe_name):
    print(dataframe_name,' is being created .. \n')
    object_body_df = pd.read_csv(data_object['Body'],chunksize=50000)
    return_df= pd.DataFrame()
    total_chunk=0
    for chunk in object_body_df:
        return_df = return_df.append(chunk)
        total_chunk = total_chunk+50000
        print(total_chunk ,"rows are read")
    print("\n")
    return return_df

obj_adspend = s_3.Bucket('dataset-bucket-s3-demo').Object('adspend.csv').get()
obj_installs = s_3.Bucket('dataset-bucket-s3-demo').Object('installs.csv').get()
obj_payouts = s_3.Bucket('dataset-bucket-s3-demo').Object('payouts.csv').get()
obj_revenue = s_3.Bucket('dataset-bucket-s3-demo').Object('revenue.csv').get()

adspend_df = read_aws_data(obj_adspend,"Ad Spend Data Frame")
installs_df = read_aws_data(obj_installs, "Installs Data Frame")
payouts_df = read_aws_data(obj_payouts, "Payouts Data Frame")
revenue_df = read_aws_data(obj_revenue, "Revenue Data Frame")


#Importing CSV files
#adspend_df = pd.read_csv('adspend.csv')
#installs_df = pd.read_csv('installs.csv')
#payouts_df = pd.read_csv('payouts.csv')
#revenue_df = pd.read_csv('revenue.csv')


#splitting installs.csv for justdice apps and partner apps
jd_installs_df = pd.DataFrame()
partner_installs_df = pd.DataFrame()
justdice_apps_list=adspend_df['client_id'].unique()
all_apps_list = installs_df['app_id'].unique()
for value in all_apps_list:
    if value not in justdice_apps_list:
        partner_installs_df = partner_installs_df.append(installs_df.loc[installs_df['app_id'] == value],ignore_index=True)
    else:
        jd_installs_df = jd_installs_df.append(installs_df.loc[installs_df['app_id'] == value], ignore_index=True)

#Header

#Column Splitting
r11, r12 = st.columns((4,6))

image = Image.open('image.png')
r11.image(image,width=200)
r12.title("Annual Report 2022")
st.header("Company Overview")
st.markdown("Beginning in 2016, justDice is now the market leader in rewarded apps and games. Its fun, exciting, and rewarding (literally) products are published in over 100+ countries :sunglasses:")
st.markdown("In 'Annual Report 2022',  the main purpose is to share the company's data from last year with the newcomers through illustrative visuals, tables, and graphs. These data are coming from 4 main CSV files that are related to installation information, ad spending, payouts, and revenue.")
st.markdown("This report has three main parts:")
st.markdown("- **Company Overview** includes information about installation counts, produced apps, and the total revenue that the company made in 2022.")
st.markdown("- **User Acquisition** includes information about mediums, relationships between mediums, and ad spending.")
st.markdown("- **Financial Opportunities** includes actions for the future, opportunities, and predictions.")


#General Information
st.subheader("General Information")
st.markdown("Everyday, justDice apps were installed to the user's devices between 200-1400 times in total (Figure 1). ")
#Number of different apps
app_count = len(jd_installs_df['app_id'].unique())
#Total revenue
revenue_sum = revenue_df['value_usd'].sum()
#DataFrame for Total number of installation for each day
installation_count = jd_installs_df.groupby(['event_date'])['install_id'].count().reset_index(name='Installation Count')
installation_count.rename(columns={'event_date':'Event Date'},inplace=True)

r21, r22 = st.columns((7,3))

fig1 = px.line(installation_count,x='Event Date',y='Installation Count')
fig1.update_layout(width=800,height=300,margin=dict(l=0, r=0, b=0, t=0))
r21.plotly_chart(fig1)
r21.markdown("<p style='text-align: center;font-style: italic; color: grey;'>Figure 1 : Daily justDice Apps Installation Counts for 2022</p>", unsafe_allow_html=True)
r22.metric(":blue[Total Installations]",'In 2022, users installed justDice apps', ''+str(round(installation_count['Installation Count'].sum()/1000))+'k times')
r22.metric(str(":blue[Total Products]"),'So far justDice produced',''+str(str(app_count-2)+" Apps"))
r22.metric(":blue[Total Revenue]",'In 2022 justDice revenued ',str(''+str(round(revenue_sum,2))+'$'))
st.markdown("**Conclusion:** When monthly total installations are compared to each, it can be seen that March-April-May has the lowest and August has the highest installation number.")

#Apps Details
st.subheader("Apps Details")
st.markdown("Twenty-Seven apps produced by justDice. In this documentation, apps are represented by App IDs like 71,174,121, etc.")
st.markdown("The popularity percentages of apps are represented in a pie chart (Figure 2).  Also, a table that includes the total number of installations of each app (Figure 3).")
#DataFrame of Installation counts for each App
app_count_df = jd_installs_df.groupby(['app_id'])['install_id'].count().reset_index(name='count').sort_values(['count'],ascending=False)

r31, r32 = st.columns((5,5))

app_names = app_count_df.head(5)['app_id'].tolist()
app_names.append('other')
app_percentage = app_count_df.head(5)['count'].tolist()
app_percentage.append(app_count_df.tail(len(app_count_df.index)-5)['count'].sum())
pull = [0.1,0,0,0,0,0]
fig2 = go.Figure(data=[go.Pie(labels=app_names,values=app_percentage,pull=pull)])
fig2.update_layout(legend={'font': {'size': 15}, },width=500,height=500,margin=dict(l=0, r=0, b=0, t=50), autosize=False)
fig2.update_traces(textfont_size=20)
r31.markdown('**Percentage of Installation for Apps**')
r31.plotly_chart(fig2)
r31.markdown("<p style='text-align: left;font-style: italic; color: grey;'>Figure 2 : Installation Counts for each App</p>", unsafe_allow_html=True)

r32.markdown('**Apps & Installation Counts**')
fig3 = go.Figure(data=[go.Table(
    header=dict(values=['App ID','Total Installations'],height=30,font_size=15),
    cells=dict(values=[app_count_df['app_id'],app_count_df['count']],height=30)
)])
fig3.update_layout(height=450,width=550, margin=dict(l=0, r=0, b=0, t=0),paper_bgcolor='steelblue')
fig3.update_traces(cells_font=dict(size = 15))
r32.plotly_chart(fig3)
r32.markdown("<p style='text-align: center;font-style: italic; color: grey;'>Figure 3 : App ID - Installation Table</p>", unsafe_allow_html=True)
st.markdown("**Conclusion :** App 174, App 121, and App 94 were the most trending apps in 2022. More than 55% of installations belong to these three apps.")

#User Acquisition
st.header('User Acquisition')
st.subheader('Mediums')

r41, r42 = st.columns((5,5))

r41.markdown('**Users Reached Our Apps Through 4 Mediums**')
r41.markdown('There are four mediums: Medium 10, Medium 1111, Medium 26, and Medium 60, that justDice uses as channels to show the products to the users.')
r41.markdown('It is shown how many installations are made by these mediums (Figure 4).')
r41.markdown("**Conclusion:** Most of the installations were made through Medium 60 (around 50%) and then Medium 26 (around 34%).")
#Total installation for each medium
medium_count_df = jd_installs_df.groupby(['network_id'])['install_id'].count().reset_index(name='count')
#Converting medium names
medium_count_df_list1 = medium_count_df['network_id'].tolist()
medium_count_df_list2 = ['Medium-'+str(x) for x in medium_count_df_list1]

r42.markdown('**Total Installations for Mediums**')
fig4 = go.Figure(go.Bar(
    x = medium_count_df['count'],
    y = medium_count_df_list2,
    orientation='h'
))
fig4.update_layout(height=200,width=600, margin=dict(l=20, r=0, b=0, t=0))
r42.plotly_chart(fig4)
r42.markdown("<p style='text-align: center;font-style: italic; color: grey;'>Figure 4 : Mediums & Installation Counts</p>", unsafe_allow_html=True)


#Ad Spending for Medium 10 and Medium 60
st.subheader('Ad Spendings for Medium 10 and Medium 60')
st.markdown("In 2022, Ad spending was made through Medium 10 and Medium 60. There is no Ad Spending data for Medium 26 and Medium 1111.")
st.markdown("Ad spending is made for presenting justDice products to users. If the company reaches the customers through ads and makes them install the apps, that means products are successfully advertised.")
st.markdown("To analyze the success of the advertising, the relationship between daily ad spending and daily installation should be considered.")
st.markdown("In Figure 5 and Figure 6, daily ad spendings and total installation counts can be seen for each app **by clicking the app_id labels double times.**")
st.subheader(":blue[Medium 10]")

r51, r52 = st.columns((5,5))

#ad spending&total installations for each app on medium 10
adspend_mediums_df = adspend_df.groupby(['event_date','network_id','client_id'])['value_usd'].sum().unstack(fill_value=0).stack().reset_index(name='value_usd')
installation_count_network_app = jd_installs_df.groupby(['event_date','network_id','app_id'])['install_id'].count().unstack(fill_value=0).stack().reset_index(name='Installation Count')
installation_count_network_app.rename(columns={'Installation Count':'total_installation'},inplace=True)

r51.markdown('Daily Ad Spendings($)')
fig5 = px.line(adspend_mediums_df.loc[adspend_mediums_df['network_id']==10],x='event_date',y='value_usd',color='client_id')
fig5.update_layout(width=600, height=350, margin=dict(l=0, r=0, b=0, t=0))
r51.plotly_chart(fig5)
r51.markdown("<p style='text-align: center;font-style: italic; color: grey;'>Figure 5 : Mediums 10 Daily Ad Spendings</p>", unsafe_allow_html=True)
r52.markdown('Daily Total Installations')
fig6 = px.line(installation_count_network_app.loc[installation_count_network_app['network_id']==10],x='event_date',y='total_installation',color='app_id')
fig6.update_layout(width=600, height=350, margin=dict(l=0, r=0, b=0, t=0))
r52.plotly_chart(fig6)
r52.markdown("<p style='text-align: center;font-style: italic; color: grey;'>Figure 6 : Mediums 10 Daily Installations For Each App</p>", unsafe_allow_html=True)


st.markdown("With a cursory observation, it can be seen that for some apps, the Daily Total Installation chart has a similar shape to the  Daily Ad Spending chart.")
st.markdown("For example, App 94 has similar Daily Ad Spending and Daily Total Installation charts for Medium 10. However, for a more precise understanding, the similarity between Daily Ad Spending and Daily Total Installation charts should be calculated for each app.")
st.markdown("One of the solutions can be squeezing charts into the value range of 0 to 1 for each day of 2022. The total difference between their values may show the differences between the two charts. Therefore, a similarity rate can be calculated based on how far these values are from each other (Figure 9).")
st.markdown("**After Squeezing the graphs, they become as Figure 7 and Figure 8: (Double-click to intended app_id in each graph to clearly see the similarities separately.)**")

adspend_medium10_squeezed = adspend_mediums_df.loc[adspend_mediums_df['network_id']==10]
for value in justdice_apps_list:
    adspend_medium10_squeezed.loc[adspend_medium10_squeezed['client_id']==value,'value_usd'] = adspend_medium10_squeezed.loc[adspend_medium10_squeezed['client_id']==value,'value_usd'].div(adspend_medium10_squeezed.loc[adspend_medium10_squeezed['client_id']==value,'value_usd'].max() if adspend_medium10_squeezed.loc[adspend_medium10_squeezed['client_id']==value,'value_usd'].max() != 0 else 1)
#adspend_mediums_squeezed_df['value_usd'] = adspend_mediums_squeezed_df['value_usd'].div(adspend_mediums_squeezed_df['value_usd'].max())
installation_medium10_squeezed = installation_count_network_app.loc[(installation_count_network_app['network_id']==10)]
for value in app_count_df['app_id']:
    installation_medium10_squeezed.loc[installation_medium10_squeezed['app_id']==value,'total_installation'] = installation_medium10_squeezed.loc[installation_medium10_squeezed['app_id']==value,'total_installation'].div(installation_medium10_squeezed.loc[installation_medium10_squeezed['app_id']==value,'total_installation'].max() if installation_medium10_squeezed.loc[installation_medium10_squeezed['app_id']==value,'total_installation'].max() != 0 else 1 )
r61, r62 = st.columns((5,5))

r61.markdown('Daily Ad Spendings($)')
fig7 = px.line(adspend_medium10_squeezed,x='event_date',y='value_usd',color='client_id')
fig7.update_layout(width=600, height=350, margin=dict(l=0, r=0, b=0, t=0))
r61.plotly_chart(fig7)
r61.markdown("<p style='text-align: center;font-style: italic; color: grey;'>Figure 7 : Squeezed Mediums 10 Daily Ad Spendings</p>", unsafe_allow_html=True)
r62.markdown('Daily Total Installations')
fig8 = px.line(installation_medium10_squeezed,x='event_date',y='total_installation',color='app_id')
fig8.update_layout(width=600, height=350, margin=dict(l=0, r=0, b=0, t=0))
r62.plotly_chart(fig8)
r62.markdown("<p style='text-align: center;font-style: italic; color: grey;'>Figure 8 : Squeezed Mediums 10 Daily Installations For Each App</p>", unsafe_allow_html=True)


graph_similarity_df = pd.DataFrame()
graph_similarity_dict = {'app_id':[],'graph_similarity_metric':[]}
a=installation_count_network_app.loc[installation_count_network_app['network_id']==10]
b= a.groupby(['app_id','event_date'])['total_installation'].sum().reset_index(name='a')
c=  b.loc[b['a'] > 1]
d = c.groupby(['app_id'])['a'].count().reset_index(name='a')
f = d.loc[d['a']>30]
app_count_m10_df = jd_installs_df.loc[jd_installs_df['network_id']==10]
app_count_m10_df=app_count_m10_df.groupby(['app_id'])['install_id'].count().reset_index(name='count')
for name in f['app_id']:
    temp1 = installation_medium10_squeezed.loc[installation_medium10_squeezed['app_id']==name].iloc[:,[0,3]]
    temp2 = adspend_medium10_squeezed.loc[adspend_medium10_squeezed['client_id']==name].iloc[:, [0,3]]
    temp3 = pd.merge(temp1,temp2,on='event_date')
    temp3['difference']=abs(temp3['total_installation']-temp3['value_usd'])
    result = round(100-(temp3['difference'].sum()*100)/365,2)
    graph_similarity_dict['app_id'].append(name)
    graph_similarity_dict['graph_similarity_metric'].append(result)
graph_similarity_df = pd.DataFrame(graph_similarity_dict)
graph_similarity_df = graph_similarity_df.merge(app_count_m10_df,on='app_id')
graph_similarity_df=graph_similarity_df.sort_values(by='graph_similarity_metric', ascending=False)
r71, r72 = st.columns((5,5))


r71.markdown('**Similarity Rate Table For Medium 10**')
fig9 = go.Figure(data=[go.Table(
    header=dict(values=['App ID','Similarity Rate (%)','Total Count'],height=30,font_size=15),
    cells=dict(values=[graph_similarity_df['app_id'],graph_similarity_df['graph_similarity_metric'],graph_similarity_df['count']],height=30)
)])
fig9.update_layout(height=450,width=550, margin=dict(l=0, r=0, b=0, t=0),paper_bgcolor='steelblue')
fig9.update_traces(cells_font=dict(size = 15))
r71.plotly_chart(fig9)
r71.markdown("<p style='text-align: center;font-style: italic; color: grey;'>Figure 9 : Similarity Rates Between Daily Ad Spending and Daily Total Installations for Medium 10</p>", unsafe_allow_html=True)

r72.markdown("**Similarity Rate Table - Medium 10**")
r72.markdown("Similarity rates give an idea of how close these data points are. For this analysis, the default similarity rate is 85%. Similarity rates above 85% show advertisement success, and similarity rates below 85% show advertisements unsuccess. ")
r72.markdown("The Similarity Rate Table is created by taking differences between data points for each day and then summing them up, after that, it is divided by 365 and taking the percentage of it.")
r72.markdown("The result will show the distance rate between the two charts. To get the success rate result subtracted from 100.")
r72.markdown("**To create a similarity table, this formula should be applied for each App ID:**")
r72.markdown("$100-\sum_{n=0}^{365}|day^{adspending}_n - day^{totalinstall}_n| * 100 / 365 $ ")
r72.markdown("Advertisements were generally successful for medium 10. This success can be increased by analyzing the relationship between total installations and similarity rates. It can be useful to see the opportunities for the next year.")
st.markdown("**Conclusion :** Applications with more than a 98% similarity rate can be regarded as chances for the next year to make more advertisements. App 122 has a 99.8% similarity between ad spending and total installation. Also, this app has been installed around 1.2k times (around 5% of total installation for Medium 10) in 2022. App 189 and App 97 are in similar situations. For the next year, the applications with high Similarity Rate and high Total Count on the table for Medium 10 should be advertised more.")
st.markdown("**Conclusion :** App 94 was the most installed app through Medium 10 . It has quite a number of installations (around 30% of total installation for Medium 10). However, after some specific point, the effects of advertisement on installation number does not change enough as in App 122, App 189, App 97, and App 275. To have an optimum success rate, ad spending can be decreased for apps with a relatively low similarity rate and the ad budget can be allocated for apps with more similarity rate.")




st.subheader(":blue[Medium 60]")

adspend_medium60_squeezed = adspend_mediums_df.loc[adspend_mediums_df['network_id']==60]
for value in justdice_apps_list:
    adspend_medium60_squeezed.loc[adspend_medium60_squeezed['client_id']==value,'value_usd'] = adspend_medium60_squeezed.loc[adspend_medium60_squeezed['client_id']==value,'value_usd'].div(adspend_medium60_squeezed.loc[adspend_medium60_squeezed['client_id']==value,'value_usd'].max() if adspend_medium60_squeezed.loc[adspend_medium60_squeezed['client_id']==value,'value_usd'].max() != 0 else 1)
#adspend_mediums_squeezed_df['value_usd'] = adspend_mediums_squeezed_df['value_usd'].div(adspend_mediums_squeezed_df['value_usd'].max())
installation_medium60_squeezed = installation_count_network_app.loc[(installation_count_network_app['network_id']==60)]
for value in app_count_df['app_id']:
    installation_medium60_squeezed.loc[installation_medium60_squeezed['app_id']==value,'total_installation'] = installation_medium60_squeezed.loc[installation_medium60_squeezed['app_id']==value,'total_installation'].div(installation_medium60_squeezed.loc[installation_medium60_squeezed['app_id']==value,'total_installation'].max() if installation_medium60_squeezed.loc[installation_medium60_squeezed['app_id']==value,'total_installation'].max() != 0 else 1 )



r81, r82 = st.columns((5,5))

r81.markdown('Daily Ad Spendings($)')
fig10 = px.line(adspend_medium60_squeezed,x='event_date',y='value_usd',color='client_id')
fig10.update_layout(width=600, height=350, margin=dict(l=0, r=0, b=0, t=0))
r81.plotly_chart(fig10)
r81.markdown("<p style='text-align: center;font-style: italic; color: grey;'>Figure 10 : Squeezed Mediums 60 Daily Ad Spendings</p>", unsafe_allow_html=True)
r82.markdown('Daily Total Installations')
fig11 = px.line(installation_medium60_squeezed,x='event_date',y='total_installation',color='app_id')
fig11.update_layout(width=600, height=350, margin=dict(l=0, r=0, b=0, t=0))
r82.plotly_chart(fig11)
r82.markdown("<p style='text-align: center;font-style: italic; color: grey;'>Figure 11 : Squeezed Mediums 60 Daily Installations For Each App</p>", unsafe_allow_html=True)

st.markdown("Just like Medium 10, Medium 60 has also similarity between data points on Daily Ad Spending and Dailty total insatllation tables . Here there are just squeezed versions of tables. Again, Similarity rate table can be created.")


graph_similarity_df2 = pd.DataFrame()
graph_similarity_dict = {'app_id':[],'graph_similarity_metric':[]}
a=installation_count_network_app.loc[installation_count_network_app['network_id']==60]
b= a.groupby(['app_id','event_date'])['total_installation'].sum().reset_index(name='a')
c=  b.loc[b['a'] > 1]
d = c.groupby(['app_id'])['a'].count().reset_index(name='a')
f = d.loc[d['a']>30]
app_count_m60_df = jd_installs_df.loc[jd_installs_df['network_id']==60]
app_count_m60_df=app_count_m60_df.groupby(['app_id'])['install_id'].count().reset_index(name='count')


for name in f['app_id']:
    temp1 = installation_medium60_squeezed.loc[installation_medium60_squeezed['app_id']==name].iloc[:,[0,3]]
    temp2 = adspend_medium60_squeezed.loc[adspend_medium60_squeezed['client_id']==name].iloc[:, [0,3]]
    temp3 = pd.merge(temp1,temp2,on='event_date')
    temp3['difference']=abs(temp3['total_installation']-temp3['value_usd'])
    result = round(100-(temp3['difference'].sum()*100)/365,2)
    graph_similarity_dict['app_id'].append(name)
    graph_similarity_dict['graph_similarity_metric'].append(result)
graph_similarity_df2 = pd.DataFrame(graph_similarity_dict)
graph_similarity_df2 = graph_similarity_df2.merge(app_count_m60_df,on='app_id')
graph_similarity_df2=graph_similarity_df2.sort_values(by='graph_similarity_metric', ascending=False)


r91, r92 = st.columns((5,5))



r91.markdown('**Total Installations for Medium 60**')
fig12 = go.Figure(data=[go.Table(
    header=dict(values=['App ID','Similarity Rate (%)','Total Count'],height=30,font_size=15),
    cells=dict(values=[graph_similarity_df2['app_id'],graph_similarity_df2['graph_similarity_metric'],graph_similarity_df2['count']],height=30)
)])
fig12.update_layout(height=350,width=550, margin=dict(l=0, r=0, b=0, t=0),paper_bgcolor='steelblue')
fig12.update_traces(cells_font=dict(size = 15))
r91.plotly_chart(fig12)
r91.markdown("<p style='text-align: center;font-style: italic; color: grey;'>Figure 12 : Similarity Rates Between Daily Ad Spending and Daily Total Installations for Medium 60</p>", unsafe_allow_html=True)
r92.markdown("**Similarity Rate Table - Medium 60**")
r92.markdown("**Conclusion :** Except for App 71 and App 189, general advertising for Medium 60 was successful. App 71 and App 189 had opposite behavior in terms of ad spending amount. ")
r92.markdown("**Conclusion :** More than 50% of installations were made under a 90% similarity rate. However, there is an opportunity for App 380, App 374, App 302, and App 154. These apps have high similarity rates and relatively high installation counts so, ad spending for App 189 and App 71 might be decreased and extra ad spending budget can be transferred to the apps with high similarity rates and high installation numbers.")


st.markdown("**Additional Conclusions for Medium 10 & Medium 60**")
st.markdown("There is no ad spending for Medium 1111 and Medium 26. However, some conclusions from Medium 10 and Medium 60 can be useful for further ad spending for these mediums :")
st.markdown("- For App 71 and App 180, Medium 10 and Medium 60 had different behaviour on ad spending. Ad spending was successful for these apps on Medium 10 but not on the Medium 60.")
st.markdown("- App 390 has quite a positive proportional relationship with the ad spending on Medium 10 and Medium 60 so, it can be suggested that App 390 can be presented to the users through other mediums.")
st.markdown("- Users installed justDice products through Medium 26 more than Medium 10 (Figure 4) so, it might be an efficient channel to advertise justDice products.")




st.header('Financial Opportunities')
st.markdown('By taking the right decisions, a positive contribution is made to the financial resources of the company. In the previous section, user acquisition opportunities are shown. However, the country-wise ad spending opportunities, fees, incomes from partner apps, support costs for mobile devices, and revenue predictions should also be taken into account.')
st.subheader("Country-Wise Ad Spending")
r101, r102 = st.columns((5,5))
r101.markdown("In 2022, justDice advertised the products in four countries: Country 1, Country 17, Country 109, and Country 213   (Figure 12).")
r101.markdown("- Country 1: Over 95% of ad spending and around 60% of the total installation.")
r101.markdown("- Country 17: Around %0.1 of spending and around 5% of the total installation.")
r101.markdown("- Country 109: Around 3% of ad spending and around 28% of the total installation.")
r101.markdown("- Country 213: Around 0.2% of ad spending and around 4% of the total installation.")
r101.markdown("**Conclusion:**  It seems the company paid a lot of ad spending for Country 1. For the next year, there should be more ad spending on Country 17, Country 109, and Country 213.")
adspend_country = adspend_df.groupby(['country_id'])['value_usd'].sum().reset_index(name = 'value_usd')
installation_country = installs_df.groupby(['country_id'])['install_id'].count().reset_index(name='total_installation')
adspend_install_country = pd.merge(adspend_country,installation_country,on='country_id')
countries = ['Country-'+str(x) for x in adspend_install_country['country_id']]
adspend_install_country['adspend_rate'] = round(100*adspend_install_country['value_usd']/adspend_install_country['value_usd'].sum(),4)
adspend_install_country['installation'] = round(100*adspend_install_country['total_installation']/adspend_install_country['total_installation'].sum(),4)
fig13 = fig = go.Figure(
    data=[
        go.Bar(name='Adspend Rate (%)', x=countries, y=adspend_install_country['adspend_rate']),
        go.Bar(name='Installation Rate (%)', x=countries, y=adspend_install_country['installation'])
    ],
layout={
        'yaxis': {'title': 'Rate (%)'},
        'xaxis': {'title': 'Countries'}

    }
)
fig13.update_layout(height=300,width=600, margin=dict(l=0, r=0, b=0, t=0))
r102.plotly_chart(fig13)
r102.markdown("<p style='text-align: center;font-style: italic; color: grey;'>Figure 13 : Country-Wise Ad Spending Rate </p>", unsafe_allow_html=True)

st.subheader("Medium Fees")

st.markdown("When a user installs one of justDice products through mediums that advertise the products, those mediums charge a fee to the company. The fee amount is determined by the company and it can be increased or decreased according to how much effect the medium has on installation numbers or the user acquisition process.  ")
st.markdown("In 2022, justDice used Medium 10 and Medium 60 for advertising the products.  There were different amounts of payouts for each app and each medium. For this analysis, the unit payouts for each app on Medium 10 and Medium 60 are shown (Figure 14 and Figure 15). It is fine to have more unit payout for some specific apps that bring users/ installation. On the other hand, some mediums might be underpaid for some specific apps and that might be an opportunity for the next year for acquiring more users.")
st.markdown("\n\n\n")
r111, r112 = st.columns((5,5))
r111.markdown("**:blue[Medium 10]**")
payouts_grouped_df1 = payouts_df.groupby(['install_id'])['value_usd'].sum().reset_index(name='value_usd')
medium_fee1 = pd.merge(jd_installs_df,payouts_grouped_df1,on=['install_id'],how='left')
medium_fee1 = medium_fee1.groupby(['app_id','network_id'])['value_usd'].sum().unstack(fill_value=0).stack().reset_index(name='value_usd')
medium_fee1 = medium_fee1.loc[medium_fee1['network_id']==10 ]
medium_fee1 = medium_fee1.groupby(['app_id'])['value_usd'].sum().reset_index(name='value_usd')

installation_count_fee1 = jd_installs_df.groupby(['app_id','network_id'])['install_id'].count().reset_index(name='count')
installation_count_fee1 = installation_count_fee1.loc[installation_count_fee1['network_id']==10 ]
installation_count_fee1 = installation_count_fee1.groupby(['app_id'])['count'].sum().reset_index(name='count')

merge_installation_medium_fee1 = pd.merge(medium_fee1,installation_count_fee1,on='app_id')
merge_installation_medium_fee1['unit fee'] = merge_installation_medium_fee1['value_usd']/merge_installation_medium_fee1['count']
merge_installation_medium_fee1 = merge_installation_medium_fee1.sort_values(by=['unit fee'],ascending=False)
fig14 = go.Figure(data=[go.Table(
    header=dict(values=['App Id','Total Installation','Total Payout','Unit Payout'],height=30,font_size=15),
    cells=dict(values=[merge_installation_medium_fee1['app_id'],merge_installation_medium_fee1['count'],round(merge_installation_medium_fee1['value_usd'],3),round(merge_installation_medium_fee1['unit fee'],3)],height=30)
)])
fig14.update_layout(height=400,width=550, margin=dict(l=0, r=0, b=0, t=0),paper_bgcolor='steelblue')
fig14.update_traces(cells_font=dict(size = 15))
r111.plotly_chart(fig14)
r111.markdown("<p style='text-align: center;font-style: italic; color: grey;'>Figure 14 : App ID & Unit Payout Graph for Medium 10 </p>", unsafe_allow_html=True)


r112.markdown("**:blue[Medium 60]**")
payouts_grouped_df2 = payouts_df.groupby(['install_id'])['value_usd'].sum().reset_index(name='value_usd')
medium_fee2 = pd.merge(jd_installs_df,payouts_grouped_df2,on=['install_id'],how='left')
medium_fee2 = medium_fee2.groupby(['app_id','network_id'])['value_usd'].sum().unstack(fill_value=0).stack().reset_index(name='value_usd')
medium_fee2 = medium_fee2.loc[medium_fee2['network_id']== 60]
medium_fee2 = medium_fee2.groupby(['app_id'])['value_usd'].sum().reset_index(name='value_usd')

installation_count_fee2 = jd_installs_df.groupby(['app_id','network_id'])['install_id'].count().reset_index(name='count')
installation_count_fee2 = installation_count_fee2.loc[installation_count_fee2['network_id']== 60]
installation_count_fee2 = installation_count_fee2.groupby(['app_id'])['count'].sum().reset_index(name='count')

merge_installation_medium_fee2 = pd.merge(medium_fee2,installation_count_fee2,on='app_id')
merge_installation_medium_fee2['unit fee'] = merge_installation_medium_fee2['value_usd']/merge_installation_medium_fee2['count']
merge_installation_medium_fee2 = merge_installation_medium_fee2.sort_values(by=['unit fee'],ascending=False)
fig15 = go.Figure(data=[go.Table(
    header=dict(values=['App Id','Total Installation','Total Payout','Unit Payout'],height=30,font_size=15),
    cells=dict(values=[merge_installation_medium_fee2['app_id'],merge_installation_medium_fee2['count'],round(merge_installation_medium_fee2['value_usd'],3),round(merge_installation_medium_fee2['unit fee'],3)],height=30)
)])
fig15.update_layout(height=400,width=550, margin=dict(l=0, r=0, b=0, t=0),paper_bgcolor='steelblue')
fig15.update_traces(cells_font=dict(size = 15))
r112.plotly_chart(fig15)
r112.markdown("<p style='text-align: center;font-style: italic; color: grey;'>Figure 15 : App ID & Unit Payout Graph for Medium 60 </p>", unsafe_allow_html=True)

st.markdown("**Conclusion :** On Medium 10, App 189, and App 275 have a low unit payout (0.003,0.004) but their installation counts are not low as most of the other products. Additionally, it can be seen that App 189 and App 275 are successfully advertised through Medium 10 (Figure 9). So, the amount of payout fee conditions for App 189 and App 275 should be reconsidered.")
st.markdown("**Conclusion :** On Medium 60, App 154, and App 380 have a low unit payout (0.047,0.032) but their installation counts are not low as most of the other products and they are successfully advertised through Medium 60 with a high similarity rate (Figure 12).")
st.markdown("**Conclusion :** App 94 has a high unit fee for Medium 10 and Medium 60.  However, this fee amount become successful for Medium 10 with a high similarity rate between ad spending and total installation number. However, for Medium 60, the unit fee amount might be decreased.")



st.subheader("Partner App Incomes")
st.markdown("When users download justDice products to their mobile devices, they see an option to download partner apps on the screen. When users download the partner apps, the partner apps pay a certain amount of fee to JustDice.")
st.markdown("Networks that show partner apps are Medium 26 and Medium 1111. Total installation counts and unit fees for Medium 26 and Medium 1111 are shown in Figure 16 and Figure 17 below:")

r121, r122 = st.columns((5,5))
r121.markdown("**:blue[Medium 26]**")
r122.markdown("**:blue[Medium 1111]**")
for value in [26,1111]:
    dd =partner_installs_df.loc[partner_installs_df['network_id']==value]
    revenue_group=revenue_df.groupby(['install_id'])['value_usd'].sum().reset_index(name='total_value_usd')
    dd1 = pd.merge(dd,revenue_group,on='install_id',how='left')
    dd2=dd1.groupby(['app_id'])['total_value_usd'].sum().reset_index(name='total_value_usd')
    dd3 = dd1.groupby(['app_id'])['install_id'].count().reset_index(name='count')
    dd3['total_value_usd'] = dd2['total_value_usd']
    dd3['unit income'] = dd3['total_value_usd']/dd3['count']
    dd3 = dd3.sort_values(['unit income'],ascending=False)
    figx = go.Figure(data=[go.Table(
        header=dict(values=['App Id', 'Total Installation', 'Total Fee', 'Unit Fee'], height=30, font_size=15),
        cells=dict(values=[dd3['app_id'], dd3['count'],
                           round(dd3['total_value_usd'], 3),
                           round(dd3['unit income'], 3)], height=30)
    )])
    figx.update_layout(height=150, width=550, margin=dict(l=0, r=0, b=0, t=0))
    figx.update_traces(cells_font=dict(size=15))
    if value == 26:
        r121.plotly_chart(figx)
    else:
        r122.plotly_chart(figx)

r121.markdown("<p style='text-align: center;font-style: italic; color: grey;'>Figure 16 : App ID & Unit Fee Graph for Medium 26 </p>", unsafe_allow_html=True)
r122.markdown("<p style='text-align: center;font-style: italic; color: grey;'>Figure 17 : App ID & Unit Fee Graph for Medium 1111 </p>", unsafe_allow_html=True)


st.markdown("**Conclusion:** Although App 408 did not have the highest counts of installations, App 408 brought the highest fees for Medium 26. App 237 and App 277 have almost twice the amount installations of App148 but they are paid half price. As a result, promoting more App408 in justDice apps can generate higher incomes. App 404 and App 405 are in a similar situation.")
st.markdown("**Conclusion:** Only App 217 was promoted on Medium 1111 and it does not have a high unit fee. Medium 1111 can be a good channel for the promotion of partner apps App 408, App 405, and App 404  with high unit fees for the next year.")

#Sixth Row

st.subheader('OS Compatability')
st.markdown("When users install an application to their mobile device, that application must be compatible with the device. Every year, with the developing technology, operating systems are updated and new versions are released like justDice products. Since some users use older operating systems, apps also need to be compatible with older systems. It is not an easy process for employees to make applications compatible with all operating systems and the company may stop its support on some older operating systems in order to make applications compatible with newly released operating systems.")
st.markdown("For 2022, the graph of how many different apps were used on which operating systems can be seen (Figure 18). The revenue rate of justDice over operating systems can also be seen (Figure 19).")
os_n = jd_installs_df.groupby(['app_id','device_os_version'])['install_id'].count().reset_index(name='count').sort_values(['app_id'],ascending=False)
os_n['app_id'] = 'App-'+os_n['app_id'].apply(str)
print(os_n['app_id'].unique())
os_n['device_os_version'] = os_n['device_os_version'].str.split('.').str[0]+'.x'
print(os_n)
os_total_download = os_n.groupby(['app_id','device_os_version']).count().reset_index()
os_names = os_total_download['device_os_version'].unique()
temp_df = pd.DataFrame()
for os in os_names:
    a=os_total_download.loc[os_total_download['device_os_version']==os].groupby(['device_os_version'])['app_id'].count().reset_index(name='count').sort_values(['count'],ascending=False)
    temp_df=temp_df.append(a)

r131, r132 = st.columns((5,5))

fig16 = go.Figure(data=[go.Table(
    header=dict(values=['Device OS Verison','Number of Different Apps'],height=30,font_size=15),
    cells=dict(values=[temp_df['device_os_version'],temp_df['count']],height=30)
)])
fig16.update_layout(height=250,width=550, margin=dict(l=0, r=0, b=0, t=0),paper_bgcolor='steelblue')
fig16.update_traces(cells_font=dict(size = 15))
r131.plotly_chart(fig16)
r131.markdown("<p style='text-align: center;font-style: italic; color: grey;'>Figure 18 : Device OS & Number of Different Apps Graph </p>", unsafe_allow_html=True)


os_install = jd_installs_df.groupby(['install_id','device_os_version'])['install_id'].count().reset_index(name='count')
revenue_n = revenue_df.groupby(['install_id'])['value_usd'].sum().reset_index(name='total_value_usd')
merge_os_revenue = pandas.merge(os_install,revenue_n,on='install_id',how='left')
merge_os_revenue['total_value_usd'] = merge_os_revenue['total_value_usd'].fillna(0)
os_revenue = merge_os_revenue.groupby(['device_os_version'])['total_value_usd'].sum().reset_index(name='total_value_usd').sort_values(['device_os_version'])
os_revenue['device_os_version']=os_revenue['device_os_version'].str.split('.').str[0]+'.x'
total_value_usd = os_revenue['total_value_usd'].tolist()
summation = sum(total_value_usd)
revenue_percent=[]
for value in total_value_usd:
    revenue_percent.append(round(value*100/summation,2))

fig17 = go.Figure(
    data=[
        go.Bar(name='Adspend Rate (%)', x=os_revenue['device_os_version'], y=revenue_percent)
    ],
layout={
        'yaxis': {'title': 'Revenue Percent (%)'},
        'xaxis': {'title': 'OS Versions'}

    }
)
r132.markdown('**Revenue Sharing(%) / OS Version**')
fig17.update_layout(height=200,width=600, margin=dict(l=20, r=0, b=0, t=0))
r132.plotly_chart(fig17)
r132.markdown("<p style='text-align: center;font-style: italic; color: grey;'>Figure 19 : Revenue Sharing & OS Grapgh </p>", unsafe_allow_html=True)

st.markdown("**Conclusion:** It takes some time for the latest operating system versions to become widespread. Therefore, the numbers for new operating system versions like 15.x and 16.x can be ignored. However, it can be seen that not all justDice apps were installed in the old OS versions such as 5.x and 6.x (Figure 18). That might mean that these apps are not compatible with 5.x and 6.x OS or the company stop supporting these apps for 5.x and 6.x OS.")
st.markdown("**Conclusion:** The biggest part of justDice's profit comes from 12.x operating system. That means the contribution to the profit of the company increases as operating systems move from the old ones to the new ones (Figure 19).")
st.markdown("In order to decide which operating systems' support should be reduced or stopped for which apps, it should be analyzed that how often the applications are used in the operating systems. In Figure 20, which applications are used and how often for each operating system can be examined.")


figx = px.histogram(os_n, x=os_n['app_id'], y=os_n['count'],
             color=os_n['device_os_version'], barmode='group',
             height=400,
                    width=1200)
st.plotly_chart(figx)
st.markdown("<p style='text-align: center;font-style: italic; color: grey;'>Figure 20: OS Versions & Installed Apps Graph </p>", unsafe_allow_html=True)

st.markdown("If the number of installations of the apps is not high enough for the old operating systems, justDice may stop the operating system support for these apps and focus on the compatibility of the apps with the new operating systems.")
st.markdown("Operating system support may be withdrawn from some apps. Especially less-used apps that are installed in old operating systems.")
st.markdown("**Conclusion:** In total, 5% of the company's revenu comes from the applications installed in the 5.x, 6.x, 7.x, 8.x, and 9.x operating systems. Especially for apps that are rarely used (less than 50 installations over 2022) in these operating systems, operating system support can be withdrawn and support for new operating systems can be given importance. For example :")
st.markdown("- **For OS 5.x:** All apps except: App 121 and App 174")
st.markdown("- **For OS 6.x:** All apps except: App 121, App 174, and App 95")
st.markdown("- **For OS 7.x:** App 402, App 390, App 374, App 110 and App 98")
st.markdown("- **For OS 8.x:** App 402, App 390, App 325, App 183, App 110 and App 98")
st.markdown("- **For OS 9.x:** App 402, App 390, App 325, App 183, App 152, App 98, and App 110")



st.subheader('Revenue Forecasting')
st.markdown("It is possible to predict revenues for the beginning of 2023 based on the change in daily revenue in 2022. In Figure 21, information about the daily revenues for 2022 and a revenue prediction for the beginning of 2023 are shown:")

x=revenue_df.groupby(['event_date'])['value_usd'].sum().reset_index(name='value_usd')
x['event_date'] = pd.to_datetime(x['event_date'])
x.columns = ['ds','y']
m= prophet.Prophet(yearly_seasonality=True,daily_seasonality=True)
m.fit(x)
future = m.make_future_dataframe(periods=30)
forecast = m.predict(future)
figxxx = plot_plotly(m,forecast)
figxxx.update_layout(height=400,width=1100, margin=dict(l=20, r=0, b=0, t=0))
st.plotly_chart(figxxx)
st.markdown("<p style='text-align: center;font-style: italic; color: grey;'>Figure 21: Revenue Prediction Graph </p>", unsafe_allow_html=True)
st.markdown("**Conclusion:** An increase in revenue can be expected at the beginning of 2023 compared to the last weeks of 2022. Especially at the end of 2022, while the daily average revenue is between 500 USD and 1000 USD , it can be predicted that the average daily profit will be between 1000 USD and 1500 USD for the first weeks of 2023.")
st.markdown("For the revenue prediction, the financial opportunities mentioned before were not included.")

st.markdown("**©️ 2023 justDice**")
