from pathlib import Path
import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import hydra


@st.cache_data
def load(vital_filename, user_filename, sheet):

    df = pd.read_csv(vital_filename)

    users = pd.read_excel(user_filename, sheet_name=sheet)
    users = users[users['Test-Nr.'] == 1]

    df = pd.merge(df, users, left_on='customer', right_on='Pseudonym')

    df['day'] = pd.to_datetime(df['day'])
    df['days_since_start'] = (df['day'] - df['Testdatum']).dt.days
    df.rename(columns={'Gruppe\n[In = 0, Ko = 1] ': 'cohort'}, inplace=True)
    df.loc[df.cohort==0, 'cohort'] = 'Intervention'
    df.loc[df.cohort==1, 'cohort'] = 'Control'

    df['value'] = df['doubleValue'].fillna(0) + df['longValue'].fillna(0)

    return df

def aggregate(df, by, min_data_points):

    df = df.groupby(by).value.agg(['mean', 'median', 'std', 'count'])
    df['err'] = df['std'] / np.sqrt(df['count'])
    df = df[df['count'] >= min_data_points]

    return df

def select(df, reference, min_points):
    return aggregate(df, by=['type', reference, 'cohort'], min_data_points=min_points)

def ylimits(values, factor=.1):
    value_range = np.max(values) - np.min(values)
    ymin = np.min(values) - factor * value_range
    ymax = np.max(values) + factor * value_range
    return ymin, ymax

def draw_aggregate(df, x, y, vital_type, show_intervention, show_control):

    df = df.loc[vital_type][:-2].reset_index()
    ymin, ymax = ylimits(df[y])

    if not show_intervention:
        df = df[df.cohort != 'Intervention']
    if not show_control:
        df = df[df.cohort != 'Control']

    colormap = alt.Scale(
        domain=['Intervention', 'Control'],
        range=['#c0392b', '#34495e']
        )

    chart = (
        alt.Chart(df)
        .mark_line()
        .encode(
            x=x,
            y=alt.Y(y, scale=alt.Scale(domain=[ymin, ymax])),
            color=alt.Color('cohort', scale=colormap)
            )
        )

    return chart

def draw_individuals(df, x, pseudonyms, vital_type):

    df = df[df.customer.isin(pseudonyms) & (df.type == vital_type)]
    ymin, ymax = ylimits(df['value'])

    chart = (
        alt.Chart(df)
        .mark_line()
        .encode(
            x=x,
            y=alt.Y('value', scale=alt.Scale(domain=[ymin, ymax])),
            color='customer'
            )
        )

    return chart

@hydra.main(version_base=None, config_path='../config/', config_name='main.yaml')
def main(config):

    reference_keys = {True: 'days_since_start', False: 'day'}
    external_data = Path(config.data.external)
    raw_data = Path(config.data.raw)

    df = load(
        vital_filename=raw_data / config.data.files.vitals,
        user_filename=external_data / config.data.files.users.file,
        sheet=config.data.files.users.sheet
    )

    g = select(df, reference='day', min_points=10)

    # Setup the dashboard
    st.title('WATCH Data Explorer')
    vital = st.selectbox('Select vital type', g.reset_index().type.unique(), index=24)
    customers = st.multiselect('Select individual pseudonyms', df.customer.unique())
    min_points = st.slider('Minimum daily data points', 1, 20, 10)
    reference = st.toggle('Use start date as reference', value=False)
    intervention = st.toggle('Show intervention cohort', value=True)
    control = st.toggle('Show control cohort', value=False)

    # Compute aggregates for set minumum number of points and reference point
    reference = reference_keys[reference]
    g = select(df, reference=reference, min_points=min_points)

    # Draw vital data (cohort aggregates and individual time series)
    c = draw_aggregate(
        df=g,
        x=reference,
        y='median',
        vital_type=vital,
        show_intervention=intervention,
        show_control=control
    )
    if customers:
        ci = draw_individuals(
            df=df, x=reference,
            pseudonyms=customers,
            vital_type=vital
        )
        c = alt.layer(c, ci).resolve_scale(color='independent')
    st.altair_chart(c, use_container_width=True)

    # Draw number of users per day in each cohort
    c = draw_aggregate(
        df=g,
        x=reference,
        y='count',
        vital_type=vital,
        show_intervention=intervention,
        show_control=control
    )
    st.altair_chart(c, use_container_width=True)

if __name__ == '__main__':
    main()
