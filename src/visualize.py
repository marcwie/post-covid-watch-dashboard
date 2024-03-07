import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

st.title('WATCH Data Explorer')

@st.cache_data
def load():

    df = pd.read_csv('data/01_raw/daily_part0001.csv')

    users = pd.read_excel('data/00_external/lc_watch_bus_data_2023_12_19.xlsx', sheet_name='Stand_2024_02_29')
    users = users[users['Test-Nr.'] == 1]

    df = pd.merge(df, users, left_on='customer', right_on='Pseudonym')

    df['day'] = pd.to_datetime(df['day'])
    df['days_since_start'] = (df['day'] - df['Testdatum']).dt.days
    df.rename(columns={'Gruppe\n[In = 0, Ko = 1] ': 'cohort'}, inplace=True)
    df.cohort[df.cohort==0] = 'Intervention'
    df.cohort[df.cohort==1] = 'Control'

    return df

def aggregate(df, by, min_data_points):

    df = df.groupby(by).longValue.agg(['mean', 'median', 'std', 'count'])
    df['err'] = df['std'] / np.sqrt(df['count'])
    df = df[df['count'] >= min_data_points]

    return df

def select(df, reference, min_points):
    return aggregate(df, by=['type', reference, 'cohort'], min_data_points=min_points)

def draw(df, key, vital, show_intervention, show_control):

    df = df.loc[vital][:-2].reset_index()
    range = df[key].max() - df[key].min()

    ymax = df[key].max() + .1 * range
    if key == 'median':
        ymin = df[key].min() - .1 * range
    else:
        ymin = 0

    if not show_intervention:
        df = df[df.cohort != 'Intervention']
    if not show_control:
        df = df[df.cohort != 'Control']

    c = (
    alt.Chart(df)
    .mark_line()
    .encode(
        x=reference,
        y=alt.Y(
            key,
            scale=alt.Scale(domain=[ymin, ymax])
            ),
        color=alt.Color(
            'cohort',
            scale=alt.Scale(domain=['Intervention', 'Control'], range=['#c0392b', '#34495e'])
            ),
        )
    )

    return c

df = load()
g = select(df, reference='day', min_points=10)

vital = st.selectbox('Select vital type', g.reset_index().type.unique(), index=19)
min_points = st.slider('Minimum daily data points', 1, 20, 10)

reference = st.toggle('Use start date as reference', value=False)
intervention = st.toggle('Show intervention cohort', value=True)
control = st.toggle('Show control cohort', value=False)

if reference:
    reference = 'days_since_start'
else:
    reference = 'day'

g = select(df, reference=reference, min_points=min_points)

c1 = draw(g, 'median', vital, show_intervention=intervention, show_control=control)
st.altair_chart(c1, use_container_width=True)

c2 = draw(g, 'count', vital, show_intervention=intervention, show_control=control)
st.altair_chart(c2, use_container_width=True)