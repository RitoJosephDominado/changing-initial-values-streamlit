import streamlit as st
import pandas as pd
import numpy as np
import time
import os
import matplotlib.pyplot as plt
from parsing import extract_rate_df
from parsing import extract_steady_state_df
from ivp import Solver

st.set_page_config(layout="wide")

file = 'crntoolbox_results_aug_15/legewi_wild_higher_deficiency.rtf'

def update_ivp_df_list(
        start_point, end_point, num_points,
        initial_value_df, rate_df,
        species_initial_value_changed, varied_initial_values
):
    iv_df = initial_value_df.copy(deep = True)
    df_list = []
    for iv in varied_initial_values:
        iv_df.loc[iv_df['species'] == species_initial_value_changed, 'concentration'] = iv
        sol = Solver(iv_df, rate_df)
        sol.solve(num_points, start_point, end_point)
        df_list.append(sol.get_solution_df())
    st.session_state['ivp_df_list'] = df_list

def plot_species_across_initial_values(species_observed):
    df_list = st.session_state.ivp_df_list
    vec_list = [df_list[x].loc[:, species_observed] for x in range(len(df_list))]
    fig, ax = plt.subplots(figsize=(15, 8))
    for x in vec_list:
        ax.plot(x, '-o')

    ax.set_title(species_observed + ' Concentrations Across Varying Initial Values for ' + species_initial_value_changed)
    ax.legend([species_initial_value_changed + " = " + str(sp) for sp in varied_initial_values])
    return(fig, ax)

if 'steady_state_df' not in st.session_state:
    st.session_state['steady_state_df'] = extract_steady_state_df(file)

if 'initial_value_df' not in st.session_state:
    steady_state_df = extract_steady_state_df(file)
    st.session_state['initial_value_df'] = pd.DataFrame({
        'species': steady_state_df.species,
        'concentration': np.repeat(20, 13)
    })

if 'rate_df' not in st.session_state:
    st.session_state['rate_df'] = extract_rate_df(file)

if 'ivp_df_list' not in st.session_state:
    st.session_state['ivp_df_list'] = []

col1, col2, col3 = st.columns(3)
with col1:
    st.header('Rate constants')
    rdf = st.data_editor(st.session_state.rate_df)

with col2:
    st.header('Initial Values')
    ivdf = st.data_editor(st.session_state.initial_value_df)

with col3:
    st.write('### Steady States from CRNToolBox')
    st.table(st.session_state.steady_state_df)

row2_col1, row2_col2, row2_col3, row2_col4 = st.columns(4)

with row2_col1:
    species_initial_value_changed = st.selectbox('Species with Changing Initial Values', st.session_state.initial_value_df.species, index=3)

with row2_col2:
    starting_initial_value = st.number_input('Range Start', min_value=0, value=0)
with row2_col3:
    ending_initial_value = st.number_input('Range End', min_value = 0, value=200)
with row2_col4:
    num_initial_values = st.number_input('Number of Initial Values', min_value=0, value=5)

varied_initial_values = np.linspace(
    starting_initial_value, ending_initial_value,
    num_initial_values
)
st.write('Initial Values to Use:')
st.write(str(varied_initial_values))

start_point = 0
end_point = 20
num_points = 21

run_btn = st.button('Run', on_click=update_ivp_df_list, args = (
    start_point, end_point, num_points,
    st.session_state.initial_value_df, st.session_state.rate_df,
    species_initial_value_changed, varied_initial_values
))

st.header('Results')

if len(st.session_state['ivp_df_list']) > 0:
    iv_df = st.session_state.initial_value_df.copy(deep = True)
    species_observed = st.selectbox('Species to Observe', iv_df.species, index=9)
    st.write('You selected to observe: ', species_observed)
    st.pyplot(plot_species_across_initial_values(species_observed)[0])
    ivp_results_dict = {}
    for i, x in enumerate(varied_initial_values):
        ivp_results_dict[species_initial_value_changed + '=' + str(x)] = st.session_state['ivp_df_list'][i].loc[:, species_observed]
    ivp_results_df = pd.DataFrame(ivp_results_dict)
    st.table(ivp_results_df)
    st.divider()
    st.write('Initial Values used')
    st.table(st.session_state.initial_value_df)
