import streamlit as st
import pandas as pd
import io
import requests
from typing import List, Dict, Callable, Any

# Set page title and configuration
st.set_page_config(
    page_title="Football Statistics Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# GitHub repository information
GITHUB_REPO = "PkevS3"
GITHUB_USER = "kevinxaviour"  
CSV_DIR = "csvfiles"
EXCEL_DIR = "impfiles"
TEAM_MAPPING_FILE = "Team IDs.xlsx"

# Function to fetch all CSV files from GitHub repository directory
def fetch_csv_files_from_github() -> pd.DataFrame:
    """Fetch and merge all CSV files from the GitHub repository's csvfiles directory."""
    # API URL to get directory contents
    api_url = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents/{CSV_DIR}"
    
    try:
        # Get directory listing
        response = requests.get(api_url)
        response.raise_for_status()
        
        # Extract file information
        files_info = response.json()
        
        # Filter for CSV files
        csv_files = [file_info for file_info in files_info if file_info['name'].lower().endswith('.csv')]
        
        if not csv_files:
            st.error(f"No CSV files found in {CSV_DIR} directory.")
            return pd.DataFrame()
        
        # Fetch and merge all CSV files
        all_dfs = []
        for file_info in csv_files:
            with st.spinner(f"Loading {file_info['name']}..."):
                # Get raw content URL
                download_url = file_info['download_url']
                
                # Fetch file content
                file_response = requests.get(download_url)
                file_response.raise_for_status()
                
                # Read CSV from response content
                try:
                    df = pd.read_csv(io.StringIO(file_response.content.decode('ISO-8859-1')))
                    all_dfs.append(df)
                   # st.success(f"Loaded {file_info['name']}")
                except Exception as e:
                    st.warning(f"Error reading {file_info['name']}: {str(e)}")
        
        if all_dfs:
            # Concatenate all DataFrames
            merged_df = pd.concat(all_dfs, ignore_index=True)
            return merged_df
        else:
            st.error("Failed to load any CSV files.")
            return pd.DataFrame()
            
    except Exception as e:
        st.error(f"Error accessing GitHub repository: {str(e)}")
        return pd.DataFrame()

# Function to fetch team mapping from GitHub
def fetch_team_mapping() -> pd.DataFrame:
    """Fetch team mapping Excel file from GitHub repository."""
    # Raw content URL for the Excel file
    excel_url = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/main/{EXCEL_DIR}/{TEAM_MAPPING_FILE}"
    
    try:
        with st.spinner(f"Loading team mapping file..."):
            # Fetch file content
            response = requests.get(excel_url)
            response.raise_for_status()
            
            # Read Excel from response content
            team_mapping = pd.read_excel(io.BytesIO(response.content))
            st.success("Team mapping loaded successfully")
            return team_mapping
            
    except Exception as e:
        st.error(f"Error fetching team mapping file: {str(e)}")
        return pd.DataFrame()

# Statistics functions
def Goals_stats(df: pd.DataFrame) -> pd.DataFrame:
    df_summary = df.groupby(['playerid', 'Player_FN']).agg(
        Matches=('matchid', 'nunique'),
        Goals=('Goals', 'sum')
    ).reset_index()
    df_summary = df_summary.sort_values(by=['Goals', 'Matches'], ascending=[False, True])
    df_summary['Rank'] = df_summary['Goals'].rank(method='dense', ascending=False).astype(int)
    df_summary = df_summary[['Rank', 'Player_FN', 'Matches', 'Goals']].rename(columns={'Player_FN': 'Name'})
    df_summary['Name'] = df_summary['Name'].str.title()
    df_summary = df_summary.reset_index(drop=True)
    df_summary = df_summary[df_summary['Goals'] != 0]
    return df_summary

def Assists_stats(df: pd.DataFrame) -> pd.DataFrame:
    df_summary = df.groupby(['playerid', 'Player_FN']).agg(
        Matches=('matchid', 'nunique'), 
        Assists=('Assists', 'sum') 
    ).reset_index()
    df_summary = df_summary.sort_values(by=['Assists', 'Matches'], ascending=[False, True])
    df_summary['Rank'] = df_summary['Assists'].rank(method='dense', ascending=False).astype(int)
    df_summary = df_summary[['Rank', 'Player_FN', 'Matches', 'Assists']].rename(columns={'Player_FN': 'Name'})
    df_summary['Name'] = df_summary['Name'].str.title()
    df_summary = df_summary.reset_index(drop=True)
    df_summary = df_summary[df_summary['Assists'] != 0]
    return df_summary

def cc(df: pd.DataFrame) -> pd.DataFrame:
    df_summary = df.groupby(['playerid', 'Player_FN']).agg(
        Matches=('matchid', 'nunique'),  
        Chances=('chances_created', 'sum') 
    ).reset_index()
    df_summary = df_summary.sort_values(by=['Chances', 'Matches'], ascending=[False, True])
    df_summary['Rank'] = df_summary['Chances'].rank(method='dense', ascending=False).astype(int)
    df_summary = df_summary[df_summary['Chances'] != 0]
    df_summary = df_summary[['Rank', 'Player_FN', 'Matches', 'Chances']].rename(
        columns={'Player_FN': 'Name', 'Chances': 'Chances Created'})
    df_summary['Name'] = df_summary['Name'].str.title()
    df_summary = df_summary.reset_index(drop=True)
    return df_summary

def shot_accuracy(df: pd.DataFrame) -> pd.DataFrame:
    df_summary = df.groupby(['playerid', 'Player_FN']).agg(
        Matches=('matchid', 'nunique'), 
        Shots_On_Target=('shots_on_target', 'sum'),  
        Shots=('shots', 'sum')  
    ).reset_index()

    df_summary['Shot_Accuracy'] = (df_summary['Shots_On_Target'] / df_summary['Shots']) * 100
    df_summary['Shot_Accuracy'] = df_summary['Shot_Accuracy'].fillna(0).round(1)
    df_summary = df_summary.sort_values(by='Shot_Accuracy', ascending=False)
    df_summary = df_summary[['Player_FN', 'Matches', 'Shots', 'Shot_Accuracy']].rename(columns={'Player_FN': 'Name'})
    df_summary['Name'] = df_summary['Name'].str.title()
    df_summary = df_summary[(df_summary['Shots'] >= df_summary['Shots'].mean()) & (df_summary['Shot_Accuracy'] != 0)]
    df_summary = df_summary.reset_index(drop=True)
    return df_summary

def fouls_stats(df: pd.DataFrame) -> pd.DataFrame:
    df_summary = df.groupby(['playerid', 'Player_FN']).agg(
        Matches=('matchid', 'nunique'), 
        Fouls=('fouls', 'sum') 
    ).reset_index()
    df_summary = df_summary.sort_values(by='Fouls', ascending=False)
    df_summary['Rank'] = df_summary['Fouls'].rank(method='dense', ascending=False).astype(int)
    df_summary = df_summary[['Rank', 'Player_FN', 'Matches', 'Fouls']].rename(columns={'Player_FN': 'Name'})
    df_summary['Name'] = df_summary['Name'].str.title()
    df_summary = df_summary.reset_index(drop=True)
    df_summary = df_summary[df_summary['Fouls'] != 0]
    return df_summary

def yc_stats(df: pd.DataFrame) -> pd.DataFrame:
    df_summary = df.groupby(['playerid', 'Player_FN']).agg(
        Yellow=('yellow_cards', 'sum') 
    ).reset_index()
    df_summary = df_summary.sort_values(by='Yellow', ascending=False)
    df_summary = df_summary[['Player_FN', 'Yellow']].rename(
        columns={'Player_FN': 'Name', 'Yellow': 'Yellow Cards'})
    df_summary['Name'] = df_summary['Name'].str.title()
    df_summary = df_summary.reset_index(drop=True)
    df_summary = df_summary[df_summary['Yellow Cards'] != 0]
    return df_summary

def rc_stats(df: pd.DataFrame) -> pd.DataFrame:
    df_summary = df.groupby(['playerid', 'Player_FN']).agg( 
        Red=('red_cards', 'sum') 
    ).reset_index()
    df_summary = df_summary.sort_values(by='Red', ascending=False)
    df_summary = df_summary[['Player_FN', 'Red']].rename(
        columns={'Player_FN': 'Name', 'Red': 'Red Cards'})
    df_summary['Name'] = df_summary['Name'].str.title()
    df_summary = df_summary.reset_index(drop=True)
    df_summary = df_summary[df_summary['Red Cards'] != 0]
    return df_summary

def offsides_stats(df: pd.DataFrame) -> pd.DataFrame:
    df_summary = df.groupby(['playerid', 'Player_FN']).agg(
        Offside=('offsides', 'sum') 
    ).reset_index()
    df_summary = df_summary.sort_values(by='Offside', ascending=False)
    df_summary = df_summary[['Player_FN', 'Offside']].rename(columns={'Player_FN': 'Name'})
    df_summary['Name'] = df_summary['Name'].str.title()
    df_summary = df_summary.reset_index(drop=True)
    df_summary = df_summary[df_summary['Offside'] != 0]
    return df_summary

def tackles_90(df: pd.DataFrame) -> pd.DataFrame:
    df_summary = df.groupby(['playerid', 'Player_FN']).agg(
        Matches=('matchid', 'nunique'),  
        Tackles=('tackles', 'sum') 
    ).reset_index()
    df_summary['Tackles_per90'] = df_summary['Tackles'] / df_summary['Matches']
    df_summary['Tackles_per90'] = df_summary['Tackles_per90'].round(1)
    df_summary = df_summary.sort_values(by='Tackles_per90', ascending=False)
    df_summary = df_summary[df_summary['Tackles_per90'] != 0]
    df_summary = df_summary[['Player_FN', 'Tackles_per90']].rename(
        columns={'Player_FN': 'Name', 'Tackles_per90': 'Tackles Per Match'})
    df_summary['Name'] = df_summary['Name'].str.title()
    df_summary = df_summary.reset_index(drop=True)
    return df_summary

def inter_90(df: pd.DataFrame) -> pd.DataFrame:
    df_summary = df.groupby(['playerid', 'Player_FN']).agg(
        Matches=('matchid', 'nunique'),  
        Tackles=('interceptions', 'sum') 
    ).reset_index()
    df_summary['Tackles_per90'] = df_summary['Tackles'] / df_summary['Matches']
    df_summary['Tackles_per90'] = df_summary['Tackles_per90'].round(1)
    df_summary = df_summary.sort_values(by='Tackles_per90', ascending=False)
    df_summary = df_summary[df_summary['Tackles_per90'] != 0]
    df_summary = df_summary[['Player_FN', 'Tackles_per90']].rename(
        columns={'Player_FN': 'Name', 'Tackles_per90': 'Interceptions Per Match'})
    df_summary['Name'] = df_summary['Name'].str.title()
    df_summary = df_summary.reset_index(drop=True)
    return df_summary

def blocks_90(df: pd.DataFrame) -> pd.DataFrame:
    df_summary = df.groupby(['playerid', 'Player_FN']).agg(
        Matches=('matchid', 'nunique'),  
        Tackles=('blocks', 'sum') 
    ).reset_index()
    df_summary['Tackles_per90'] = df_summary['Tackles'] / df_summary['Matches']
    df_summary['Tackles_per90'] = df_summary['Tackles_per90'].round(1)
    df_summary = df_summary.sort_values(by='Tackles_per90', ascending=False)
    df_summary = df_summary[df_summary['Tackles_per90'] != 0]
    df_summary = df_summary[['Player_FN', 'Tackles_per90']].rename(
        columns={'Player_FN': 'Name', 'Tackles_per90': 'Blocks Per Match'})
    df_summary['Name'] = df_summary['Name'].str.title()
    df_summary = df_summary.reset_index(drop=True)
    return df_summary

def GK_Saves(df: pd.DataFrame) -> pd.DataFrame:
    df_summary = df.groupby(['playerid', 'Player_FN']).agg(
        Matches=('matchid', 'nunique'),  
        Tackles=('saves', 'sum') 
    ).reset_index()
    df_summary = df_summary.sort_values(by='Tackles', ascending=False)
    df_summary = df_summary[df_summary['Tackles'] != 0]
    df_summary = df_summary[['Player_FN', 'Tackles']].rename(
        columns={'Player_FN': 'Name', 'Tackles': 'Saves'})
    df_summary['Name'] = df_summary['Name'].str.title()
    df_summary = df_summary.reset_index(drop=True)
    return df_summary

def GK_cs(df: pd.DataFrame) -> pd.DataFrame:
    df_summary = df[df['position'] == 'GK'].groupby(['playerid', 'Player_FN']).agg(
        Matches=('matchid', 'nunique'),  
        Tackles=('clean_sheets', 'sum')  
    ).reset_index()
    df_summary = df_summary.sort_values(by='Tackles', ascending=False)
    df_summary = df_summary[df_summary['Tackles'] != 0]
    df_summary = df_summary[['Player_FN', 'Tackles']].rename(
        columns={'Player_FN': 'Name', 'Tackles': 'Clean Sheets'})
    df_summary['Name'] = df_summary['Name'].str.title()
    df_summary = df_summary.reset_index(drop=True)
    return df_summary

def savesp(df: pd.DataFrame) -> pd.DataFrame:
    df_summary = df[df['position'] == 'GK'].groupby(['playerid', 'Player_FN']).agg(
        Saves=('saves', 'sum'),  
        Shots_faced=('shots_faced', 'sum')   
    ).reset_index()

    df_summary['save%'] = (df_summary['Saves'] / df_summary['Shots_faced']) * 100
    df_summary['save%'] = df_summary['save%'].fillna(0).round(1)
    df_summary = df_summary.sort_values(by='save%', ascending=False)
    df_summary = df_summary[df_summary['Saves'] > df_summary['Saves'].mean()]
    df_summary = df_summary[['Player_FN', 'Saves', 'save%']].rename(
        columns={'Player_FN': 'Name', 'save%': 'Save Percentage'})
    df_summary['Name'] = df_summary['Name'].str.title()
    df_summary = df_summary.reset_index(drop=True)
    return df_summary

# Dictionary mapping function names to functions and their descriptions
STAT_FUNCTIONS = {
    "Goals": {"func": Goals_stats, "desc": "Player goal statistics"},
    "Assists": {"func": Assists_stats, "desc": "Player assist statistics"},
    "Chances Created": {"func": cc, "desc": "Chances created by players"},
    "Shot Accuracy": {"func": shot_accuracy, "desc": "Player shot accuracy statistics"},
    "Fouls": {"func": fouls_stats, "desc": "Fouls committed by players"},
    "Yellow Cards": {"func": yc_stats, "desc": "Yellow cards received by players"},
    "Red Cards": {"func": rc_stats, "desc": "Red cards received by players"},
    "Offsides": {"func": offsides_stats, "desc": "Offside statistics by players"},
    "Tackles Per Match": {"func": tackles_90, "desc": "Average tackles per match by players"},
    "Interceptions Per Match": {"func": inter_90, "desc": "Average interceptions per match by players"},
    "Blocks Per Match": {"func": blocks_90, "desc": "Average blocks per match by players"},
    "Goalkeeper Saves": {"func": GK_Saves, "desc": "Total saves by goalkeepers"},
    "Goalkeeper Clean Sheets": {"func": GK_cs, "desc": "Clean sheets by goalkeepers"},
    "Goalkeeper Save Percentage": {"func": savesp, "desc": "Save percentage by goalkeepers"}
}

# Main app
def main():
    st.title("Football Statistics Dashboard")
    
    # Initialize session state for dataframe if not exists
    if 'df' not in st.session_state:
        st.session_state.df = None
        st.session_state.data_loaded = False
    
    # Load data 
    if not st.session_state.data_loaded:
        with st.spinner("Loading data from GitHub repository..."):
            # Fetch and merge CSV files
            merged_df = fetch_csv_files_from_github()
            
            if not merged_df.empty:
                st.session_state.df = merged_df
                
                # Process data similar to original script
                st.session_state.df['Player_FN'] = st.session_state.df['Player_FN'].fillna(st.session_state.df.get('player', ''))
                
                # Drop 'team' column if it exists
                if 'team' in st.session_state.df.columns:
                    st.session_state.df.drop(columns=['team'], inplace=True)
                
                st.session_state.data_loaded = True
            else:
                st.error("Failed to load data.")

    # Statistic selection
    if st.session_state.data_loaded:
        stat_names = list(STAT_FUNCTIONS.keys())
        selected_stat = st.selectbox("Select a statistic to display", stat_names)

        # Display statistics
        if selected_stat:
            with st.spinner(f"Calculating {selected_stat} statistics..."):
                stat_function = STAT_FUNCTIONS[selected_stat]["func"]
                stat_df = stat_function(st.session_state.df.copy())  # Pass a copy to avoid modifying the original dataframe
                st.dataframe(stat_df.set_index(stat_df.columns[0])) # Display dataframe without index

if __name__ == "__main__":
    main()
