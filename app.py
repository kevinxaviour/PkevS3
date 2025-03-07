import streamlit as st
import pandas as pd
import io
import requests
from typing import List, Dict, Callable, Any

# Set page title and configuration
st.set_page_config(
    page_title="Porkallam Season 3",
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
            # st.success("Team mapping loaded successfully")
            return team_mapping
            
    except Exception as e:
        st.error(f"Error fetching team mapping file: {str(e)}")
        return pd.DataFrame()

# Statistics functions
def Goals_stats(df: pd.DataFrame) -> pd.DataFrame:
    df_summary = df.groupby(['team', 'playerid', 'Player_FN']).agg(
        Matches=('matchid', 'nunique'),
        Goals=('Goals', 'sum')
    ).reset_index()
    df_summary = df_summary.sort_values(by=['Goals', 'Matches'], ascending=[False, True])
    df_summary['Rank'] = df_summary['Goals'].rank(method='dense', ascending=False).astype(int)
    df_summary = df_summary[['Rank', 'Player_FN', 'team', 'Goals']].rename(columns={'Player_FN': 'Name','team':'Team'})
    df_summary['Name'] = df_summary['Name'].str.title()
    df_summary = df_summary.reset_index(drop=True)
    df_summary = df_summary[df_summary['Goals'] != 0]
    return df_summary

def Assists_stats(df: pd.DataFrame) -> pd.DataFrame:
    df_summary = df.groupby(['playerid', 'Player_FN', 'team']).agg(
        Matches=('matchid', 'nunique'), 
        Assists=('Assists', 'sum') 
    ).reset_index()
    df_summary = df_summary.sort_values(by=['Assists', 'Matches'], ascending=[False, True])
    df_summary['Rank'] = df_summary['Assists'].rank(method='dense', ascending=False).astype(int)
    df_summary = df_summary[['Rank', 'Player_FN','team', 'Assists',]].rename(columns={'Player_FN': 'Name','team':'Team'})
    df_summary['Name'] = df_summary['Name'].str.title()
    df_summary = df_summary.reset_index(drop=True)
    df_summary = df_summary[df_summary['Assists'] != 0]
    return df_summary

def GA(df: pd.DataFrame) -> pd.DataFrame:
    df_summary = df.groupby(['playerid', 'Player_FN', 'team'], as_index=False).agg(
        Matches=('matchid', 'nunique'),
        Goals=('Goals', 'sum'),
        Assists=('Assists', 'sum')
    )
    
    df_summary['GA'] = df_summary['Goals'] + df_summary['Assists']
    df_summary = df_summary[df_summary['GA'] != 0]  # Remove players with 0 GA
    
    df_summary = df_summary.sort_values(by=['GA', 'Matches'], ascending=[False, True])
    df_summary['Rank'] = df_summary['GA'].rank(method='dense', ascending=False).astype(int)
    
    df_summary = df_summary[['Rank', 'Player_FN', 'team', 'GA']].rename(columns={'Player_FN': 'Name', 'team': 'Team','GA':'Goals + Assists'})
    df_summary['Name'] = df_summary['Name'].str.title()  # Convert names to title case
    df_summary = df_summary.reset_index(drop=True)
    return df_summary

def cc(df: pd.DataFrame) -> pd.DataFrame:
    df_summary = df.groupby(['playerid', 'Player_FN', 'team']).agg(
        Matches=('matchid', 'nunique'),  
        Chances=('chances_created', 'sum') 
    ).reset_index()
    df_summary = df_summary.sort_values(by=['Chances', 'Matches'], ascending=[False, True])
    df_summary['Rank'] = df_summary['Chances'].rank(method='dense', ascending=False).astype(int)
    df_summary = df_summary[df_summary['Chances'] != 0]
    df_summary = df_summary[['Rank', 'Player_FN','team', 'Chances']].rename(
        columns={'Player_FN': 'Name', 'Chances': 'Chances Created','team':'Team'})
    df_summary['Name'] = df_summary['Name'].str.title()
    df_summary = df_summary.reset_index(drop=True)
    df_summary = df_summary.drop(columns=['Rank'])
    return df_summary

def shot_accuracy(df: pd.DataFrame) -> pd.DataFrame:
    df_summary = df.groupby(['playerid', 'Player_FN', 'team']).agg(
        Matches=('matchid', 'nunique'), 
        Shots_On_Target=('shots_on_target', 'sum'),  
        Shots=('shots', 'sum')  
    ).reset_index()

    df_summary['Shot_Accuracy'] = (df_summary['Shots_On_Target'] / df_summary['Shots']) * 100
    df_summary['Shot_Accuracy'] = df_summary['Shot_Accuracy'].fillna(0).round(1)
    df_summary = df_summary.sort_values(by='Shot_Accuracy', ascending=False)
    df_summary = df_summary[['Player_FN','team','Shots', 'Shot_Accuracy']].rename(columns={'Player_FN': 'Name','team':'Team'})
    df_summary['Name'] = df_summary['Name'].str.title()
    df_summary = df_summary[(df_summary['Shots'] >= df_summary['Shots'].mean()) & (df_summary['Shot_Accuracy'] != 0)]
    df_summary = df_summary.reset_index(drop=True)
    return df_summary

def fouls_stats(df: pd.DataFrame) -> pd.DataFrame:
    df_summary = df.groupby(['playerid', 'Player_FN', 'team']).agg(
        Matches=('matchid', 'nunique'), 
        Fouls=('fouls', 'sum') 
    ).reset_index()
    df_summary = df_summary.sort_values(by='Fouls', ascending=False)
    df_summary['Rank'] = df_summary['Fouls'].rank(method='dense', ascending=False).astype(int)
    df_summary = df_summary[['Rank', 'Player_FN','team', 'Fouls']].rename(columns={'Player_FN': 'Name','team':'Team'})
    df_summary['Name'] = df_summary['Name'].str.title()
    df_summary = df_summary.reset_index(drop=True)
    df_summary = df_summary[df_summary['Fouls'] != 0]
    return df_summary

def yc_stats(df: pd.DataFrame) -> pd.DataFrame:
    df_summary = df.groupby(['playerid', 'Player_FN', 'team']).agg(
        Yellow=('yellow_cards', 'sum') 
    ).reset_index()
    df_summary = df_summary.sort_values(by='Yellow', ascending=False)
    df_summary = df_summary[['Player_FN','team', 'Yellow']].rename(
        columns={'Player_FN': 'Name', 'Yellow': 'Yellow Cards','team':'Team'})
    df_summary['Name'] = df_summary['Name'].str.title()
    df_summary = df_summary.reset_index(drop=True)
    df_summary = df_summary[df_summary['Yellow Cards'] != 0]
    return df_summary

def rc_stats(df: pd.DataFrame) -> pd.DataFrame:
    df_summary = df.groupby(['playerid', 'Player_FN', 'team']).agg( 
        Red=('red_cards', 'sum') 
    ).reset_index()
    df_summary = df_summary.sort_values(by='Red', ascending=False)
    df_summary = df_summary[['Player_FN','team', 'Red']].rename(
        columns={'Player_FN': 'Name', 'Red': 'Red Cards','team':'Team'})
    df_summary['Name'] = df_summary['Name'].str.title()
    df_summary = df_summary.reset_index(drop=True)
    df_summary = df_summary[df_summary['Red Cards'] != 0]
    return df_summary

def offsides_stats(df: pd.DataFrame) -> pd.DataFrame:
    df_summary = df.groupby(['playerid', 'Player_FN', 'team']).agg(
        Offside=('offsides', 'sum') 
    ).reset_index()
    df_summary = df_summary.sort_values(by='Offside', ascending=False)
    df_summary = df_summary[['Player_FN','team', 'Offside']].rename(columns={'Player_FN': 'Name','team':'Team'})
    df_summary['Name'] = df_summary['Name'].str.title()
    df_summary = df_summary.reset_index(drop=True)
    df_summary = df_summary[df_summary['Offside'] != 0]
    return df_summary

def tackles_90(df: pd.DataFrame) -> pd.DataFrame:
    df_summary = df.groupby(['playerid', 'Player_FN', 'team']).agg(
        Matches=('matchid', 'nunique'),  
        Tackles=('tackles', 'sum') 
    ).reset_index()
    df_summary['Tackles_per90'] = df_summary['Tackles'] / df_summary['Matches']
    df_summary['Tackles_per90'] = df_summary['Tackles_per90'].round(1)
    df_summary = df_summary.sort_values(by='Tackles_per90', ascending=False)
    df_summary = df_summary[df_summary['Tackles_per90'] != 0]
    df_summary = df_summary[['Player_FN','team', 'Tackles_per90']].rename(
        columns={'Player_FN': 'Name', 'Tackles_per90': 'Tackles Per Match','team':'Team'})
    df_summary['Name'] = df_summary['Name'].str.title()
    df_summary = df_summary.reset_index(drop=True)
    return df_summary

def inter_90(df: pd.DataFrame) -> pd.DataFrame:
    df_summary = df.groupby(['playerid', 'Player_FN', 'team']).agg(
        Matches=('matchid', 'nunique'),  
        Tackles=('interceptions', 'sum') 
    ).reset_index()
    df_summary['Tackles_per90'] = df_summary['Tackles'] / df_summary['Matches']
    df_summary['Tackles_per90'] = df_summary['Tackles_per90'].round(1)
    df_summary = df_summary.sort_values(by='Tackles_per90', ascending=False)
    df_summary = df_summary[df_summary['Tackles_per90'] != 0]
    df_summary = df_summary[['Player_FN','team', 'Tackles_per90']].rename(
        columns={'Player_FN': 'Name', 'Tackles_per90': 'Interceptions Per Match','team':'Team'})
    df_summary['Name'] = df_summary['Name'].str.title()
    df_summary = df_summary.reset_index(drop=True)
    return df_summary

def blocks_90(df: pd.DataFrame) -> pd.DataFrame:
    df_summary = df.groupby(['playerid', 'Player_FN', 'team']).agg(
        Matches=('matchid', 'nunique'),  
        Tackles=('blocks', 'sum') 
    ).reset_index()
    df_summary['Tackles_per90'] = df_summary['Tackles'] / df_summary['Matches']
    df_summary['Tackles_per90'] = df_summary['Tackles_per90'].round(1)
    df_summary = df_summary.sort_values(by='Tackles_per90', ascending=False)
    df_summary = df_summary[df_summary['Tackles_per90'] != 0]
    df_summary = df_summary[['Player_FN','team', 'Tackles_per90']].rename(
        columns={'Player_FN': 'Name', 'Tackles_per90': 'Blocks Per Match','team':'Team'})
    df_summary['Name'] = df_summary['Name'].str.title()
    df_summary = df_summary.reset_index(drop=True)
    return df_summary

def GK_Saves(df: pd.DataFrame) -> pd.DataFrame:
    df_summary = df.groupby(['playerid', 'Player_FN', 'team']).agg(
        Matches=('matchid', 'nunique'),  
        Tackles=('saves', 'sum') 
    ).reset_index()
    df_summary = df_summary.sort_values(by='Tackles', ascending=False)
    df_summary = df_summary[df_summary['Tackles'] != 0]
    df_summary = df_summary[['Player_FN','team', 'Tackles']].rename(
        columns={'Player_FN': 'Name', 'Tackles': 'Saves','team':'Team'})
    df_summary['Name'] = df_summary['Name'].str.title()
    df_summary = df_summary.reset_index(drop=True)
    return df_summary

def GK_cs(df: pd.DataFrame) -> pd.DataFrame:
    df_summary = df[df['position'] == 'GK'].groupby(['playerid', 'Player_FN', 'team']).agg(
        Matches=('matchid', 'nunique'),  
        Tackles=('clean_sheets', 'sum')  
    ).reset_index()
    df_summary = df_summary.sort_values(by='Tackles', ascending=False)
    df_summary = df_summary[df_summary['Tackles'] != 0]
    df_summary = df_summary[['Player_FN','team', 'Tackles']].rename(
        columns={'Player_FN': 'Name', 'Tackles': 'Clean Sheets','team':'Team'})
    df_summary['Name'] = df_summary['Name'].str.title()
    df_summary = df_summary.reset_index(drop=True)
    return df_summary

def savesp(df: pd.DataFrame) -> pd.DataFrame:
    df_summary = df[df['position'] == 'GK'].groupby(['playerid', 'Player_FN', 'team']).agg(
        Saves=('saves', 'sum'),  
        Shots_faced=('shots_faced', 'sum')   
    ).reset_index()

    df_summary['save%'] = (df_summary['Saves'] / df_summary['Shots_faced']) * 100
    df_summary['save%'] = df_summary['save%'].fillna(0).round(1)
    df_summary = df_summary.sort_values(by='save%', ascending=False)
    df_summary = df_summary[df_summary['Saves'] > df_summary['Saves'].mean()]
    df_summary = df_summary[['Player_FN','team', 'Saves', 'save%']].rename(
        columns={'Player_FN': 'Name', 'save%': 'Save Percentage','team':'Team'})
    df_summary['Name'] = df_summary['Name'].str.title()
    df_summary = df_summary.reset_index(drop=True)
    return df_summary

# Dictionary mapping function names to functions and their descriptions
STAT_FUNCTIONS = {
    "Goals": {"func": Goals_stats, "desc": "Player goal statistics"},
    "Assists": {"func": Assists_stats, "desc": "Player assist statistics"},
    "Goals + Assists": {"func": GA, "desc": "Player Goals+Assists statistics"},
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

# Initialize session state
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame()
if 'team_mapping' not in st.session_state:
    st.session_state.team_mapping = pd.DataFrame()

# Main app
def main():
    #st.title("Porkallam Season 3")
    
    # Load data and team mapping
    if not st.session_state.data_loaded:
        st.session_state.df = fetch_csv_files_from_github()
        st.session_state.team_mapping = fetch_team_mapping()
        
        if not st.session_state.df.empty and not st.session_state.team_mapping.empty:
            st.session_state.data_loaded = True
            st.success("Data and team mapping loaded successfully!")
    
    # Merge team IDs into main dataframe
    if st.session_state.data_loaded:
        # Ensure 'team' column exists in both dataframes
        if 'team' in st.session_state.df.columns and 'Team Id' in st.session_state.team_mapping.columns:
            # Perform the merge
            st.session_state.df = pd.merge(st.session_state.df, st.session_state.team_mapping, left_on='team', right_on='Team Id', how='left')
            # Optionally drop the redundant 'Team Id' column
            st.session_state.df.drop('Team Id', axis=1, inplace=True)
        else:
            #st.error("Required 'team' or 'Team Id' column missing in dataframes.")
        
        # Statistics selection
        st.sidebar.header("Statistics Options")
        selected_stat = st.sidebar.selectbox("Select statistic", options=list(STAT_FUNCTIONS.keys()))
        
        # Alignment selection
        alignment = st.sidebar.radio("Text Alignment:", ["Left", "Center"])
        
        if st.session_state.data_loaded:
            stat_function = STAT_FUNCTIONS[selected_stat]["func"]
            description = STAT_FUNCTIONS[selected_stat]["desc"]
            
            # Center the title and description
            st.markdown(
                f"""
                <style>
                .reportview-container .main .block-container{{
                    max-width: 95%;
                    padding-top: 5rem;
                    padding-right: 5rem;
                    padding-left: 5rem;
                    padding-bottom: 5rem;
                }}
                .stApp {{
                    text-align: center;
                }}
                </style>
                """,
                unsafe_allow_html=True,
            )
            st.subheader(f"{selected_stat} Statistics")
            st.write(description)
            
            # Apply the selected statistic function
            try:
                result_df = stat_function(st.session_state.df.copy())
                
                # Create column configuration with alignment
                column_config = {}
                for col in result_df.columns:
                    # Set alignment based on user selection
                    if alignment == "Center":
                        # For center alignment, we use custom CSS
                        column_config[col] = st.column_config.Column(
                            width="auto",
                            help=f"",  # Empty help text
                        )
                    else:
                        # For left alignment (default)
                        column_config[col] = st.column_config.Column(width="auto")
                
                # Apply CSS for center alignment if needed
                if alignment == "Center":
                    st.markdown("""
                    <style>
                    .stDataFrame td, .stDataFrame th {
                        text-align: center !important;
                    }
                    </style>
                    """, unsafe_allow_html=True)
                else:
                    # Reset to default left alignment
                    st.markdown("""
                    <style>
                    .stDataFrame td, .stDataFrame th {
                        text-align: left !important;
                    }
                    </style>
                    """, unsafe_allow_html=True)
                
                # Display the dataframe with configured columns
                st.dataframe(
                    result_df,
                    height=500,
                    use_container_width=True,
                    hide_index=True,
                    column_config=column_config
                )
            
                # Download button
                csv = result_df.to_csv(index=False)
                st.download_button(
                    label="Download current selection as CSV",
                    data=csv,
                    file_name=f'{selected_stat.replace(" ", "_")}_stats.csv',
                    mime='text/csv',
                )
            except Exception as e:
                st.error(f"Error calculating statistics: {str(e)}")
        else:
            st.info("Please load data first.")

# Run the app
if __name__ == "__main__":
    main()
