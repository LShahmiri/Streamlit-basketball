import streamlit as st
import pandas as pd
import base64
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

st.title('NBA Player Stats Explorer')

st.markdown("""
This app performs simple webscraping of NBA player stats data!
* **Python libraries:** base64, pandas, streamlit
* **Data source:** [Basketball-reference.com](https://www.basketball-reference.com/).
""")

st.sidebar.header('User Input Features')
selected_year = st.sidebar.selectbox('Year', list(reversed(range(1950, 2020))))

# Web scraping of NBA player stats
@st.cache_data  # ← جدیدتر و بدون هشدار
def load_data(year):
    url = f"https://www.basketball-reference.com/leagues/NBA_{year}_per_game.html"
    html = pd.read_html(url, header=0)
    df = html[0]
    raw = df.drop(df[df.Age == 'Age'].index)  # Deletes repeating headers
    raw = raw.fillna(0)
    if 'Rk' in raw.columns:
        raw = raw.drop(['Rk'], axis=1)
    return raw

playerstats = load_data(selected_year)

# 🔹 تشخیص خودکار نام ستون تیم ('Tm' یا 'Team')
team_col = 'Tm' if 'Tm' in playerstats.columns else ('Team' if 'Team' in playerstats.columns else None)
if team_col is None:
    st.error("❌ No team column found ('Tm' or 'Team'). The website structure may have changed.")
    st.stop()

# Sidebar - Team selection
# 🔹 رفع خطای TypeError با تبدیل همه مقادیر به رشته
sorted_unique_team = sorted(playerstats[team_col].astype(str).unique())
selected_team = st.sidebar.multiselect('Team', sorted_unique_team, sorted_unique_team)

# Sidebar - Position selection
unique_pos = ['C', 'PF', 'SF', 'PG', 'SG']
selected_pos = st.sidebar.multiselect('Position', unique_pos, unique_pos)

# Filtering data
df_selected_team = playerstats[
    (playerstats[team_col].astype(str).isin(selected_team)) &
    (playerstats['Pos'].isin(selected_pos))
]

st.header('Display Player Stats of Selected Team(s)')
st.write(f'Data Dimension: {df_selected_team.shape[0]} rows and {df_selected_team.shape[1]} columns.')
st.dataframe(df_selected_team)

# Download NBA player stats data
def filedownload(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="playerstats.csv">Download CSV File</a>'
    return href

st.markdown(filedownload(df_selected_team), unsafe_allow_html=True)

# Heatmap
if st.button('Intercorrelation Heatmap'):
    st.header('Intercorrelation Matrix Heatmap')
    df_selected_team.to_csv('output.csv', index=False)
    df = pd.read_csv('output.csv')

    corr = df.corr(numeric_only=True)
    mask = np.zeros_like(corr)
    mask[np.triu_indices_from(mask)] = True
    with sns.axes_style("white"):
        f, ax = plt.subplots(figsize=(7, 5))
        ax = sns.heatmap(corr, mask=mask, vmax=1, square=True, cmap='coolwarm')
    st.pyplot(f)
