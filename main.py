import streamlit as st
import pandas as pd
import plotly.express as px
from st_aggrid import AgGrid, GridOptionsBuilder

st.set_page_config(layout="centered",
                   page_title="Dashboard Creator",
                   page_icon="📊")

df = pd.DataFrame()

with st.sidebar:
  upload_type = st.radio("Upload Type", ['Live', 'Demo'], index=1)

if upload_type == 'Live':
  uploaded_file = st.file_uploader("Upload a file ",
                                   type=["csv", "xlsx", "xls"])

  if uploaded_file is not None:

    if uploaded_file.name.endswith('.csv'):
      df = pd.read_csv(uploaded_file)
    else:
      st.error('Invalid File Type')
elif upload_type == 'Demo':
  df = pd.read_csv('US_honey_dataset_updated.csv')

else:
  st.error('Invalid Upload Type')

if len(df) > 0:
  # Clean the data based upon the data type of the column
  def clean_data(df):
    for col in df.columns:
      if df[col].dtype == 'object':
        df[col] = df[col].fillna('NA')
      else:
        df[col] = df[col].fillna(df[col].mean())

        # Remove any columns that have "unnamed" in the name
        df = df[[col for col in df.columns if 'unnamed' not in col.lower()]]

    return df

  df = clean_data(df)
  
  dataset_title = st.header("Honey Production in the US") if upload_type == 'Demo' else st.empty()

  st.subheader(
    f"This dataset has {len(df)} rows and {len(df.columns)} columns.")

  st.markdown("---")

  # Show the distribution of the data
  st.write(f"""
    Columns: ***{", ".join(list(map(lambda x: x.replace("_", " " ).title(), df.columns)))}***
    """)
  try:
        # Configure the grid to display the dataframe
        gb = GridOptionsBuilder.from_dataframe(df)
        gb.configure_selection(selection_mode="multiple", use_checkbox=True)
        gb.configure_pagination()
        gb.configure_side_bar()
        gb.configure_default_column(groupable=True, value=True, enableRowGroup=True, editable=True, enablePivot=True, enableValue=True,
        allowedAggFuncs=['sum', 'avg', 'count', 'min', 'max'])
        gridOptions = gb.build()

        grid = AgGrid(df, key=df, gridOptions=gridOptions, theme='streamlit', allow_unsafe_jscode=True, data_return_mode='filtered_and_sorted')
  except Exception as e:
        st.error(e)
        st.dataframe(df)
    

  st.header('Histogram')
  value_to_check = st.selectbox(
    "Value to Check",
    df.columns,
    format_func=lambda x: x.replace("_", " ").title())

  fig = px.histogram(df, x=value_to_check, marginal='box', histfunc='count')

  st.plotly_chart(fig,
                  use_container_width=True,
                  theme="streamlit",
                  sharing="streamlit")

  # Based upon the distribution of the data, evaluate if the data is skewed or not - if skewed, then use standard scaler to scale the data
  # If not skewed, then use min max scaler to scale the data

  # Show the top 5 most correlated columns
  st.markdown('# Top 5 most correlated columns\n---')
  corr_df = df.corr()

  with st.expander('Show Correlation Matrix'):
    # Show the correlation matrix as a heatmap using px
    heat_fig = px.imshow(df.corr())
    st.plotly_chart(heat_fig, use_container_width=True, sharing='streamlit')
  for _, row in corr_df.iterrows():
    # Find the highest correlation value behind an absolute value of 1.
    # This is to avoid self-correlation
    max_corr = row[row != 1].abs().max()

    # If the max correlation is greater than 0.5, then we can say that the columns are correlated
    if max_corr > 0.5:
      st.markdown(
        f"<strong style='color: orange'>{row[row == max_corr].index[0].replace('_', ' ').title()}</strong> is <strong style='color: green'>positively</strong> correlated with <strong style='color: cyan'>{row.name.replace('_', ' ').title()}</strong>",
        unsafe_allow_html=True)
    elif max_corr < -0.5:
      st.markdown(
        f"<strong style='color: orange'>{row[row == max_corr].index[0].replace('_', ' ').title()}</strong> is <strong style='color: red'>negitively</strong> correlated with <strong style='color: cyan'>{row.name.replace('_', ' ').title()}</strong>",
        unsafe_allow_html=True)
else:
  st.info('Upload a file')
