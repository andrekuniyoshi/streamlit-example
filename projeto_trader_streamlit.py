# -*- coding: utf-8 -*-
"""Projeto_Trader_Streamlit.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1uCBNV1TvB287HBjhQpmJbb9vCm9WhHFO
"""

''' projeto do grupo MErcado Financeiro no Streamlit'''

import pandas as pd
import yfinance as yf
import streamlit as st
import datetime as dt
import plotly.graph_objects as go
from plotly.subplots import make_subplots

symbols = ['AAPL', 'AMZN']

ticker = st.sidebar.selectbox(
    'Escolha uma ação',
     symbols)

stock = yf.Ticker(ticker)

start = '2021-01-01',
end = '2022-04-19',
interval = '1h',

df = yf.download(ticker, start, end, ajusted = True)
st.dataframe(df)
