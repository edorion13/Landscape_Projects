from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title = "TAKT Time Calculator",
                   page_icon=":bar_chart:")
st.sidebar.header("Filter Data")
takt_path = Path("takt.csv")
takt_df = pd.read_csv(takt_path, infer_datetime_format=True)

st.title("TAKT Time Calculator")
TA = st.sidebar.number_input("Enter Time Available:")
EF = st.sidebar.number_input("Enter efficentcy: ")
VI = st.sidebar.number_input("Enter Volume Increse")

def clean_df(takt_df, TA, VI):
    # declare helper functions

    def hours_to_minutes(hours):
        hour, minute, second = map(int, hours.split(':'))
        return (hour * 60) + minute
    
    def minutes_to_hours(minutes):
        return minutes / 60
    
    takt_df[['Planned End Date', 'Routed Hours']] = takt_df['Planned End Date,Routed Hours'].str.split(',', expand=True)
    takt_df.drop('Planned End Date,Routed Hours', axis=1, inplace=True)
    takt_df['Routed Minutes'] = takt_df['Routed Hours'].apply(hours_to_minutes)
    if VI > 0:
        takt_df['Routed Minutes'] = (takt_df['Routed Minutes'] * .10) + takt_df['Routed Minutes']
    else: 
        None
    takt_df['Routed Hours Converted'] = takt_df['Routed Minutes'].apply(minutes_to_hours)

    TA = TA
    time_avail = TA
    takt_df['TAKT time'] = time_avail/ takt_df['Routed Minutes']
    takt_df['Routed Minutes / TA'] = takt_df['Routed Minutes'] / time_avail

    takt_df['Routed Hours Converted'] = takt_df['Routed Minutes'] / 60
    ranges = [0, 3, 5, 8, 11, 15, float('inf')]
    labels = ['0 - 3', '3 - 5', '5 - 8', '8 - 11', '11 - 15', '16+']
    takt_df['Routed Hours Range'] = pd.cut(takt_df['Routed Hours Converted'], bins=ranges, labels=labels, right=False)
    takt_df['Planned End Date'] = pd.to_datetime(takt_df['Planned End Date'])
    takt_df = takt_df.sort_values(by='Planned End Date')
    return takt_df

takt_df = clean_df(takt_df, TA, VI)


def create_vlaues_df(takt_df, TA, EF):

    count1 = (takt_df['Routed Hours Range'] == '0 - 3').sum()
    count2 = (takt_df['Routed Hours Range'] == '3 - 5').sum()
    count3 = (takt_df['Routed Hours Range'] == '5 - 8').sum()
    count4 = (takt_df['Routed Hours Range'] == '8 - 11').sum()
    count5 = (takt_df['Routed Hours Range'] == '11 - 15').sum()
    count6 = (takt_df['Routed Hours Range'] == '16+').sum()

    index_ranges = [
        '0 - 3',
        '3 - 5',
        '5 - 8',
        '8 - 11',
        '11 - 15',
        '16+'
    ]

    df = pd.DataFrame(index=index_ranges, columns=['Days per Range'])

    df['Days per Range'] = [
        count1,
        count2,
        count3,
        count4,
        count5,
        count6
    ]
    df['Percent of Days'] = (df['Days per Range'] / 323 * 100).round(decimals=0)
    averages = takt_df.groupby('Routed Hours Range')['Routed Minutes'].mean()
    df['Average Routed Minutes'] = averages
    df['TAKT (mins/trd min)'] = TA / df['Average Routed Minutes']
    df['TAKT (mins/trd sec)'] = df['TAKT (mins/trd min)'] * 60
    EF = EF
    df['temp'] = ((100 -EF) * .01)
    df['Cycle Time'] = df['Average Routed Minutes'] + (df['Average Routed Minutes'] * df['temp'])
    df['Cycle Time'] = df['Cycle Time'].round(decimals=2)
    df['Operators'] = df['Cycle Time'] / TA
    df['Operators'] = df['Operators'].round(decimals=2)
    return df

df2 = create_vlaues_df(takt_df, TA, EF)

st.dataframe(df2)
st.dataframe(takt_df)

selected_date = st.sidebar.date_input("Select a date", min_value=takt_df['Planned End Date'].min().date(), max_value=takt_df['Planned End Date'].max().date(), value=takt_df['Planned End Date'].min().date())
