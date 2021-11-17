import streamlit as st
import numpy as np
import pandas as pd
from sudoku import Sudoku

from st_aggrid import AgGrid

df_template = pd.DataFrame(
    0,
    index=range(9),
    columns=['0', '1', '2', '3', '4', '5', '6', '7', '8']
)

with st.form('sudoku_solver') as f:
    st.header('Sudoku solver')
    response = AgGrid(df_template, editable=True, fit_columns_on_grid_load=True)
    st.form_submit_button()

##st.write(response['data'])

# x = [[0, 2, 0, 0, 3, 0, 0, 4, 0],
#      [6, 0, 0, 0, 0, 0, 0, 0, 3],
#      [0, 0, 4, 0, 0, 0, 5, 0, 0],
#      [0, 0, 0, 8, 0, 6, 0, 0, 0],
#      [8, 0, 0, 0, 1, 0, 0, 0, 6],
#      [0, 0, 0, 7, 0, 5, 0, 0, 0],
#      [0, 0, 7, 0, 0, 0, 6, 0, 0],
#      [4, 0, 0, 0, 0, 0, 0, 0, 8],
#      [0, 3, 0, 0, 4, 0, 0, 2, 0]
#      ]

x = response['data'].values.tolist()
s = Sudoku(x)

st.dataframe(s.solution)