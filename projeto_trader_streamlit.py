# -*- coding: utf-8 -*-
"""Projeto_Trader_Streamlit.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1uCBNV1TvB287HBjhQpmJbb9vCm9WhHFO
"""

''' projeto do grupo MErcado Financeiro no Streamlit'''

import pandas as pd
import numpy as np
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

df = yf.download(tickers = ticker,
                 start = '2021-01-01',
                 end = '2022-04-19',
                 interval = '1h',
                 ajusted = True)

def criar_rsi(df):
    n = 20
    def rma(x, n, y0):
        a = (n-1) / n
        ak = a**np.arange(len(x)-1, -1, -1)
        return np.r_[np.full(n, np.nan), y0, np.cumsum(ak * x) / ak / n + y0 * a**np.arange(1, len(x)+1)]

    df['change'] = df['Adj Close'].diff()
    df['gain'] = df.change.mask(df.change < 0, 0.0)
    df['loss'] = -df.change.mask(df.change > 0, -0.0)
    df['avg_gain'] = rma(df.gain[n+1:].to_numpy(), n, np.nansum(df.gain.to_numpy()[:n+1])/n)
    df['avg_loss'] = rma(df.loss[n+1:].to_numpy(), n, np.nansum(df.loss.to_numpy()[:n+1])/n)
    df['rs'] = df.avg_gain / df.avg_loss
    df['rsi'] = 100 - (100 / (1 + df.rs))
    return df

def criar_bollinger(df):
  # calculando a média móvel e limites superior e inferiror
  # limites com base em 2 desvios padrão
  mid = df['Adj Close'].rolling(20).mean()
  std = df['Adj Close'].rolling(20).std()
  up = mid + std
  low = mid - std

  # criando features para a média e os limites
  df['upper'] = up
  df['mid'] = mid
  df['low'] = low
  df['bbp'] = (df['Adj Close'] - df['low'])/(df['upper'] - df['low'])
  df.dropna(inplace=True)
  return df

# definindo a função de resistencia
def is_resistance(df,i):
  resistance = (df['High'][i] > df['High'][i-1]
                and df['High'][i] > df['High'][i+1]
                and df['High'][i+1] > df['High'][i+2]
                and df['High'][i-1] > df['High'][i-2])
  return resistance

# definindo a função de suporte
def is_support(df,i):
  support = (df['Low'][i] < df['Low'][i-1]
             and df['Low'][i] < df['Low'][i+1]
             and df['Low'][i+1] < df['Low'][i+2]
             and df['Low'][i-1] < df['Low'][i-2])
  return support

def suporte_resistencia(df):
  # resistência verdadeiro -> 1 (vender)
  # suporte verdadeiro -> 0 (comprar)
  # outros (2)

  # criando feature com valores 2
  df['suport_resistencia'] = 2

  # definindo os valores 1 e 0
  for i in range(2, df.shape[0] - 2):
    if is_resistance(df,i):
      df['suport_resistencia'][i] = 1 # definindo 1 para resistência
    elif is_support(df,i):
      df['suport_resistencia'][i] = 0 # definindo 0 para suporte
  return df

def lta_ltb(df):
  df2 = df.reset_index()
  df['corr'] = (df2['Adj Close'].rolling(20).corr(pd.Series(df2.index))).tolist()
  df.dropna(inplace=True)

  def condition(x):
      if x<=-0.5:
          return -1
      elif x>-0.5 and x<0.5:
          return 0
      else:
          return 1
  df['corr_class'] = df['corr'].apply(condition)

  return df

def target(df):

  # criando feature com 1h de defasagem (pegando a linha de cima)
  df['def_1'] = df['Adj Close'].shift(1)
  # criando feature comparando valor atual com o defasado
  df['subt'] = df['Adj Close'] - df['def_1']

  # criando a target de subida ou descida do valor da ação
  #0 -> caiu (com relação ao anterior)
  #1 -> subiu (com relação ao anterior)
  #2 -> igual ao anterior

  df['target'] = df['subt'].apply(lambda x: 0 if x<0 else 1 if x>0 else 2)

  return df

def constroi_features_defasadas(df,lista_features,defasagem_maxima):
    # Constrói features defasadas com base na base original
    # Copia a base
    df_cop = df.copy()
    for feat in lista_features:       
        for i in range(1,defasagem_maxima+1):
            df_cop[str(feat)+'_def_'+str(i)] = df_cop[feat].shift(i)
    
    df_cop.dropna(inplace=True)
    return df_cop

def constroi_features_futuras(df,feature,defasagem):
    # Constrói features defasadas com base na base original
    # Copia a base
    df_cop = df.copy()

    df_cop[str(feature)+'_fut_'+str(defasagem)] = df_cop[feature].shift(-defasagem)
    df_cop['target_fut_'+str(defasagem)] = df_cop[str(feature)+'_fut_'+str(defasagem)].diff().apply(lambda x: 0 if x<=0 else 1)
    df_cop.dropna(inplace=True)

    
    return df_cop

df = criar_rsi(df)
df = criar_bollinger(df)
df = suporte_resistencia(df)
df = lta_ltb(df)
df = target(df)

df.dropna(inplace=True)
df = df[['target', 'Adj Close', 'Volume', 'rsi', 'bbp', 'suport_resistencia', 'corr_class']]
df = constroi_features_defasadas(df,['Adj Close'],20)
df = constroi_features_futuras(df,'target',1)
df.drop('target', axis=1, inplace=True)

st.dataframe(df)
