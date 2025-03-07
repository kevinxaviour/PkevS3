import streamlit as st
import pandas as pd
import io
import requests
from typing import List, Dict, Callable, Any
import os

# Set page title and configuration
st.set_page_config(
    page_title="Football Statistics Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Function to fetch CSV files from GitHub csvfiles directory
def fetch_csv_from_github(repo_url: str) -> pd.DataFrame:
    """Fetch and merge all CSV files from GitHub repository's csvfiles directory."""
    all_dfs = []
    
    # Convert GitHub repo URL to API URL to get contents
    if repo_url.endswith('/'):
        repo_url = repo_url[:-1]
    
    # Extract owner and repo name from URL
    parts = repo_url.split('/')
    if 'github.com' in repo_url and len(parts) >= 5:
        owner = parts[-2]
        repo = parts[-1]
        
        # Get contents of csvfiles directory using GitHub API
        api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/csvfiles"
        
        try:
            response = requests.get(api_url)
            response.raise_for_status()
            
            # Get list of files in the directory
            files = response.json()
            
            # Process each CSV file
            for file in files:
                if file['name'].endswith('.csv'):
                    # Get raw content URL
                    download_url = file['download_url']
                    
                    try:
                        file_response = requests.get(download_url)
                        file_response.raise_for_status()
                        
                        # Read CSV from response content
                        df = pd.read_csv(io.StringIO(file_response.content.decode('ISO-8859-1')))
                        all_dfs.append(df)
                        st.sidebar.success(f"Loaded: {file['name']}")
                        
                    except Exception as e:
                        st.sidebar.error(f"Error loading {file['name']}: {str(e)}")
            
        except Exception as e:
            st.error(f"Error accessing repository: {str(e)}")
    else:
        st.error("Invalid GitHub repository URL. Please provide a URL in the format: https://github.com/username/repository")
    
    if all_dfs:
        # Concatenate all DataFrames
        merged_df = pd.concat(all_dfs, ignore_index=True)
        return merged_df
    else:
        return pd.DataFrame()

# Function to fetch team mapping from GitHub impfiles directory
def fetch_team_mapping(repo_url: str) -> pd.DataFrame:
    """Fetch team mapping Excel file from GitHub repository's impfiles directory."""
    # Convert GitHub repo URL to API URL to get contents
    if repo_url.endswith('/'):
        repo_url = repo_url[:-1]
    
    # Extract owner and repo name from URL
    parts = repo_url.split('/')
    if 'github.com' in repo_url and len(parts) >= 5:
        owner = parts[-2]
        repo = parts[-1]
        
        # Get contents of impfiles directory using GitHub API
        api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/impfiles"
        
        try:
            response = requests.get(api_url)
            response.raise_for_status()
            
            # Get list of files in the directory
            files = response.json()
            
            # Find the Team IDs Excel file
            for file in files:
                if file['name'].lower().endswith('.xlsx') and 'team' in file['name'].lower():
                    # Get raw content URL
                    download_url = file['download_url']
                    
                    try:
                        file_response = requests.get(download_url)
                        file_response.raise_for_status()
                        
                        # Read Excel from response content
                        team_mapping = pd.read_excel(io.BytesIO(file_response.content))
                        st.sidebar.success(f"Loaded team mapping: {file['name']}")
                        return team_mapping
                        
                    except Exception as e:
                        st.sidebar.error(f"Error loading {file['name']}: {str(e)}")
            
            st.sidebar.warning("No team mapping Excel file found in impfiles directory.")
            return pd.DataFrame()
            
        except Exception as e:
            st.error(f"Error accessing repository: {str(e)}")
            return pd.DataFrame()
    else:
        st.error("Invalid GitHub repository URL")
        return pd.DataFrame()

# Statistics functions
def Goals_stats(df: pd.DataFrame) -> pd.DataFrame:
    df_summary = df.groupby(['playerid', 'Player_FN', 'team']).agg(
        Matches=('matchid', 'nunique'),
        Goals=('Goals', 'sum')
    ).reset_index()
    df_summary = df_summary.sort_values(by=['Goals', 'Matches'], ascending=[False, True])
    df_summary['Rank'] = df_summary['Goals'].rank(method='dense', ascending=False).astype(int)
    df_summary = df_summary[['Rank', 'Player_FN', 'team', 'Matches', 'Goals']].rename(columns={'Player_FN': 'Name'})
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
    df_summary = df_summary[['Rank', 'Player_FN', 'team', 'Matches', 'Assists']].rename(columns={'Player_FN': 'Name'})
    df_summary['Name'] = df_summary['Name'].str.title()
    df_summary = df_summary.reset_index(drop=True)
    df_summary = df_summary[df_summary['Assists'] != 0]
    return df_summary

def cc(df: pd.DataFrame) -> pd.DataFrame:
    df_summary = df.groupby(['playerid', 'Player_FN', 'team']).agg(
        Matches=('matchid', 'nunique'),  
        Chances=('chances_created', 'sum') 
    ).reset_index()
    df_summary = df_summary.sort_values(by=['Chances', 'Matches'], ascending=[False, True])
    df_summary['Rank'] = df_summary['Chances'].rank(method='dense', ascending=False).astype(int)
    df_summary = df_summary[df_summary['Chances'] != 0]
    df_summary = df_summary[['Rank', 'Player_FN', 'team', 'Matches', 'Chances']].rename(
        columns={'Player_FN': 'Name', 'Chances': 'Chances Created'})
    df_summary['Name'] = df_summary['Name'].str.title()
    df_summary = df_summary.reset_index(drop=True)
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
    df_summary = df_summary[['Player_FN', 'team', 'Matches', 'Shots', 'Shot_Accuracy']].rename(columns={'Player_FN': 'Name'})
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
    df_summary = df_summary[['Rank', 'Player_FN', 'team', 'Matches', 'Fouls']].rename(columns={'Player_FN': 'Name'})
    df_summary['Name'] = df_summary['Name'].str.title()
    df_summary = df_summary.reset_index(drop=True)
    df_summary = df_summary[df_summary['Fouls'] != 0]
    return df_summary

def yc_stats(df: pd.DataFrame) -> pd.DataFrame:
    df_summary = df.groupby(['playerid', 'Player_FN', 'team']).agg(
        Yellow=('yellow_cards', 'sum') 
    ).reset_index()
    df_summary = df_summary.sort_values(by='Yellow', ascending=False)
    df_summary = df_summary[['Player_FN', 'team', 'Yellow']].rename(
        columns={'Player_FN': 'Name', 'Yellow': 'Yellow Cards'})
    df_summary['Name'] = df_summary['Name'].str.title()
    df_summary = df_summary.reset_index(drop=True)
    df_summary = df_summary[df_summary['Yellow Cards'] != 0]
    return df_summary

def rc_stats(df: pd.DataFrame) -> pd.DataFrame:
    df_summary = df.groupby(['playerid', 'Player_FN', 'team']).agg( 
        Red=('red_cards', 'sum') 
    ).reset_index()
    df_summary = df_summary.sort_values(by='Red', ascending=False)
    df_summary = df_summary[['Player_FN', 'team', 'Red']].rename(
        columns={'Player_FN': 'Name', 'Red': 'Red Cards'})
    df_summary['Name'] = df_summary['Name'].str.title()
    df_summary = df_summary.reset_index(drop=True)
    df_summary = df_summary[df_summary['Red Cards'] != 0]
    return df_summary

def offsides_stats(df: pd.DataFrame) -> pd.DataFrame:
    df_summary = df.groupby(['playerid', 'Player_FN', 'team']).agg(
        Offside=('offsides', 'sum') 
    ).reset_index()
    df_summary = df_summary.sort_values(by='Offside', ascending=False)
    df_summary = df_summary[['Player_FN', 'team', 'Offside']].rename(columns={'Player_FN': 'Name'})
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
    df_summary = df_summary[['Player_FN', 'team', 'Tackles_per90']].rename(
        columns={'Player_FN': 'Name', 'Tackles_per90': 'Tackles Per Match'})
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
    df_summary = df_summary[['Player_FN', 'team', 'Tackles_per90']].rename(
        columns={'Player_FN': 'Name', 'Tackles_per90': 'Interceptions Per Match'})
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
    df_summary = df_summary[['Player_FN', 'team', 'Tackles_per90']].rename(
        columns={'Player_FN': 'Name', 'Tackles_per90': 'Blocks Per Match'})
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
    df_summary = df_summary[['Player_FN', 'team', 'Tackles']].rename(
        columns={'Player_FN': 'Name', 'Tackles': 'Saves'})
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
    df_summary = df_summary[['Player_FN', 'team', 'Tackles']].rename(
        columns={'Player_FN': 'Name', 'Tackles': 'Clean Sheets'})
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
    df_summary = df_summary[['Player_FN', 'team', 'Saves', 'save%']].rename(
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
    
    # Sidebar for inputs
    st.sidebar.header("Data Source Configuration")
    
    # GitHub repository URL input
    github_repo = st.sidebar.text_input(
        "GitHub Repository URL",
        placeholder="https://github.com/username/repo"
    )
    
    # Load data button
    load_data = st.sidebar.button("Load Data")
    
    # Initialize session state for dataframe if not exists
    if 'df' not in st.session_state:
        st.session_state.df = None
    
    # Process data when load button is clicked
    if load_data and github_repo:
        with st.spinner("Loading data from GitHub..."):
            # Fetch and merge CSV files from csvfiles directory
            merged_df = fetch_csv_from_github(github_repo)
            
            if not merged_df.empty:
                st.session_state.df = merged_df
                
                # Process data similar to original script
                st.session_state.df['Player_FN'] = st.session_state.df['Player_FN'].fillna(st.session_state.df.get('player', ''))
                
                # Drop 'team' column if it exists
                if 'team' in st.session_state.df.columns:
                    st.session_state.df = st.session_state.df.drop(columns=['team'])
                
                # Fetch and merge team mapping
                team_mapping = fetch_team_mapping(github_repo)
                if not team_mapping.empty:
                    st.session_state.df = st.session_state.df.merge(
                        team_mapping, left_on='teamid', right_on='ID', how='left'
                    )
                    st.session_state.df['team'] = st.session_state.df['TeamName']
                    
                    # Drop unnecessary columns
                    columns_to_drop = ['ID', 'TeamName']
                    st.session_state.df = st.session_state.df.drop(
                        columns=[col for col in columns_to_drop if col in st.session_state.df.columns]
                    )
                
                st.success(f"Successfully loaded {len(merged_df)} rows of data!")
            else:
                st.error("Failed to load data. Please check the repository structure and try again.")
    elif load_data and not github_repo:
        st.error("Please provide a GitHub repository URL.")
    
    # Main content area
    if st.session_state.df is not None:
        # Display data overview
        st.header("Data Overview")
        st.write(f"Total records: {len(st.session_state.df)}")
        
        # Show sample of the data
        with st.expander("Preview Data"):
            st.dataframe(st.session_state.df.head())
        
        # Statistics selection
        st.header("Football Statistics")
        
        # Select statistic to display
        selected_stat = st.selectbox(
            "Select Stat to Display",
            options=list(STAT_FUNCTIONS.keys()),
            format_func=lambda x: f"{x} - {STAT_FUNCTIONS[x]['desc']}"
        )
        
        # Calculate and display selected statistic
        if selected_stat:
            with st.spinner(f"Calculating {selected_stat}..."):
                try:
                    stat_function = STAT_FUNCTIONS[selected_stat]["func"]
                    result_df = stat_function(st.session_state.df)
                    
                    if not result_df.empty:
                        st.subheader(f"{selected_stat} Statistics")
                        st.dataframe(result_df, use_container_width=True)
                        
                        # Download button for the results
                        csv = result_df.to_csv(index=False)
                        st.download_button(
                            label=f"Download {selected_stat} Data",
                            data=csv,
                            file_name=f"{selected_stat.lower().replace(' ', '_')}_stats.csv",
                            mime="text/csv"
                        )
                    else:
                        st.info(f"No data available for {selected_stat}.")
                except Exception as e:
                    st.error(f"Error calculating {selected_stat}: {str(e)}")
    else:
        # Display instructions when no data is loaded
        st.info("Please enter your GitHub repository URL and click 'Load Data' to begin.")
        
        # Example instructions
        with st.expander("How to use this app"):
            st.markdown("""
            ### Instructions:
            
            1. **Provide GitHub Repository URL**: Enter the URL to your GitHub repository.
               - Example: `https://github.com/username/repository`
            
            2. **Repository Structure**: Your repository should have:
               - A `csvfiles` directory containing all your CSV data files
               - An `impfiles` directory containing your Team IDs Excel file
            
            3. **Click 'Load Data'**: The app will fetch and process the data.
            
            4. **Select Statistics**: Choose which football statistics you want to view from the dropdown menu.
            
            5. **Download Results**: You can download any displayed statistics as CSV files.
            
            ### Deploying to Streamlit Cloud:
            
            1. Push this app to your GitHub repository
            2. Go to [Streamlit Cloud](https://streamlit.io/cloud)
            3. Connect your GitHub account
            4. Deploy the app by selecting your repository and this file
            """)

if __name__ == "__main__":
    main()
