import streamlit as st
import pandas as pd
import os
from typing import List, Dict, Callable, Any

# Set page title and configuration
st.set_page_config(
    page_title="Porkkalam Season 3",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Local directory information
CSV_DIR = "csvfiles"  # Directory containing CSV files
EXCEL_DIR = "impfiles"  # Directory containing Excel files
TEAM_MAPPING_FILE = os.path.join(EXCEL_DIR, "Team IDs.xlsx")

# Function to fetch all CSV files from local directory
def fetch_csv_files_local() -> pd.DataFrame:
    """Fetch and merge all CSV files from the local csvfiles directory."""
    try:
        # Check if directory exists
        if not os.path.exists(CSV_DIR):
            st.error(f"Directory {CSV_DIR} not found.")
            return pd.DataFrame()
        
        # Get all CSV files in the directory
        csv_files = [f for f in os.listdir(CSV_DIR) if f.lower().endswith('.csv')]
        
        if not csv_files:
            st.error(f"No CSV files found in {CSV_DIR} directory.")
            return pd.DataFrame()
        
        # Fetch and merge all CSV files
        all_dfs = []
        for file_name in csv_files:
            with st.spinner(f"Loading {file_name}..."):
                file_path = os.path.join(CSV_DIR, file_name)
                
                # Read CSV file
                try:
                    df = pd.read_csv(file_path, encoding='ISO-8859-1')
                    all_dfs.append(df)
                    # st.success(f"Loaded {file_name}")
                except Exception as e:
                    st.warning(f"Error reading {file_name}: {str(e)}")
        
        if all_dfs:
            # Concatenate all DataFrames
            merged_df = pd.concat(all_dfs, ignore_index=True)
            return merged_df
        else:
            st.error("Failed to load any CSV files.")
            return pd.DataFrame()
            
    except Exception as e:
        st.error(f"Error accessing local directory: {str(e)}")
        return pd.DataFrame()

# Function to fetch team mapping from local file
def fetch_team_mapping_local() -> pd.DataFrame:
    """Fetch team mapping Excel file from local directory."""
    try:
        with st.spinner(f"Loading team mapping file..."):
            # Check if file exists
            if not os.path.exists(TEAM_MAPPING_FILE):
                st.error(f"Team mapping file not found at {TEAM_MAPPING_FILE}")
                return pd.DataFrame()
            
            # Read Excel file
            team_mapping = pd.read_excel(TEAM_MAPPING_FILE)
            # st.success("Team mapping loaded successfully")
            return team_mapping
            
    except Exception as e:
        st.error(f"Error fetching team mapping file: {str(e)}")
        return pd.DataFrame()

# Statistics functions - keeping all the same functions from your original code
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

def Goals_statst(df: pd.DataFrame) -> pd.DataFrame:
    df_summary = df.groupby(['team']).agg(
        Matches=('matchid', 'nunique'),
        Goals=('Goals', 'sum')
    ).reset_index()
    df_summary = df_summary.sort_values(by=['Goals', 'Matches'], ascending=[False, True])
    df_summary['Rank'] = df_summary['Goals'].rank(method='dense', ascending=False).astype(int)
    df_summary = df_summary[['Rank', 'team', 'Goals']].rename(columns={'team':'Team'})
    df_summary = df_summary.reset_index(drop=True)
    return df_summary

def Goalsd_stats(df: pd.DataFrame) -> pd.DataFrame:
    df_summary = df.groupby(['team', 'playerid', 'Player_FN']).agg(
        Matches=('matchid', 'nunique'),
        Goals=('Goals', 'sum'),
        Left=('left_goals', 'sum'),
        Right=('right_goals', 'sum'),
        Head=('head_goals', 'sum'),
        Penalty=('penalty_goals', 'sum')
    ).reset_index()
    df_summary = df_summary.sort_values(by=['Goals', 'Matches'], ascending=[False, True])
    df_summary['Rank'] = df_summary['Goals'].rank(method='dense', ascending=False).astype(int)
    df_summary = df_summary[['Rank', 'Player_FN', 'team','Left','Right','Head','Penalty', 'Goals']].rename(columns={'Player_FN': 'Name','team':'Team'})
    df_summary['Name'] = df_summary['Name'].str.title()
    df_summary = df_summary.reset_index(drop=True)
    df_summary = df_summary[df_summary['Goals'] != 0]
    return df_summary

def shotsd_stats(df: pd.DataFrame) -> pd.DataFrame:
    df_summary = df.groupby(['team', 'playerid', 'Player_FN']).agg(
        Matches=('matchid', 'nunique'),
        Goals=('Goals', 'sum'),
        Shots=('shots', 'sum'),
        ShotsOT=('shots_on_target', 'sum')
    ).reset_index()
    df_summary = df_summary[df_summary['Shots'] > 0]
    df_summary['Shots Per Match']=df_summary['Shots']/df_summary['Matches']
    df_summary['Shots Per Match']=df_summary['Shots Per Match'].round(1)
    df_summary['Shots On Target Per Match']=df_summary['ShotsOT']/df_summary['Matches']
    df_summary['Shots On Target Per Match']=df_summary['Shots On Target Per Match'].round(1)
    df_summary['Goals Per Match']=df_summary['Goals']/df_summary['Matches']
    df_summary['Goals Per Match']=df_summary['Goals Per Match'].round(1)
    df_summary = df_summary.sort_values(by=['Shots Per Match'], ascending=[False])
    df_summary = df_summary[['Player_FN', 'team','Shots Per Match','Shots On Target Per Match','Goals Per Match']].rename(columns={'Player_FN': 'Name','team':'Team'})
    df_summary['Name'] = df_summary['Name'].str.title()
    df_summary = df_summary.reset_index(drop=True)
    return df_summary

def shotsd_statst(df: pd.DataFrame) -> pd.DataFrame:
    df_summary = df.groupby(['team']).agg(
        Matches=('matchid', 'nunique'),
        Goals=('Goals', 'sum'),
        Shots=('shots', 'sum'),
        ShotsOT=('shots_on_target', 'sum')
    ).reset_index()
    df_summary['Shots Per Match']=df_summary['Shots']/df_summary['Matches']
    df_summary['Shots Per Match']=df_summary['Shots Per Match'].round(1)
    df_summary['Shots On Target Per Match']=df_summary['ShotsOT']/df_summary['Matches']
    df_summary['Shots On Target Per Match']=df_summary['Shots On Target Per Match'].round(1)
    df_summary['Goals Per Match']=df_summary['Goals']/df_summary['Matches']
    df_summary['Goals Per Match']=df_summary['Goals Per Match'].round(1)
    df_summary = df_summary.sort_values(by=['Shots Per Match'], ascending=[False])
    df_summary = df_summary[['team','Shots Per Match','Shots On Target Per Match','Goals Per Match']].rename(columns={'team':'Team'})
    df_summary = df_summary.reset_index(drop=True)
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
    df_summary=df_summary[df_summary['Shots']>=df_summary['Shots'].median()]
    df_summary = df_summary.sort_values(by='Shot_Accuracy', ascending=False)
    df_summary = df_summary[(df_summary['Matches'] > df_summary['Matches'].median()) & (df_summary['Shots'] != 0)]
    df_summary = df_summary[['Player_FN','team','Shots', 'Shot_Accuracy']].rename(columns={'Player_FN': 'Name','team':'Team'})
    df_summary['Name'] = df_summary['Name'].str.title()
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
    df_summary = df_summary[(df_summary['Tackles_per90'] != 0)] #&(df_summary['Matches'] > df_summary['Matches'].median()
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
    df_summary = df_summary[(df_summary['Tackles_per90'] != 0)]#&(df_summary['Matches'] > df_summary['Matches'].median())
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
    df_summary = df_summary[(df_summary['Tackles_per90'] != 0)]#&(df_summary['Matches'] > df_summary['Matches'].median())
    df_summary = df_summary[['Player_FN','team', 'Tackles_per90']].rename(
        columns={'Player_FN': 'Name', 'Tackles_per90': 'Blocks Per Match','team':'Team'})
    df_summary['Name'] = df_summary['Name'].str.title()
    df_summary = df_summary.reset_index(drop=True)
    return df_summary

def GK_Saves(df: pd.DataFrame) -> pd.DataFrame:
    df_summary = df.groupby(['playerid', 'Player_FN', 'team']).agg(
        Matches=('matchid', 'nunique'),  
        PSaves=('penalty_saves', 'sum'),
        Tackles=('saves', 'sum') 
    ).reset_index()
    df_summary = df_summary.sort_values(by='Tackles', ascending=False)
    df_summary = df_summary[df_summary['Tackles'] != 0]
    df_summary = df_summary[['Player_FN','team', 'PSaves','Tackles']].rename(
        columns={'Player_FN': 'Name', 'Tackles': 'Saves','team':'Team','PSaves':'Penalty Saves'})
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
    df_summary = df_summary[df_summary['Saves'] > df_summary['Saves'].median()]
    df_summary = df_summary[['Player_FN','team', 'Saves', 'save%']].rename(
        columns={'Player_FN': 'Name', 'save%': 'Save Percentage','team':'Team'})
    df_summary['Name'] = df_summary['Name'].str.title()
    df_summary = df_summary.reset_index(drop=True)
    return df_summary

def totalgoals(df: pd.DataFrame) -> pd.DataFrame:
    df_summary = df['Goals'].sum()
    df_summary=(int(df_summary))+1
    return df_summary

def tpp(df: pd.DataFrame) -> pd.DataFrame:
    df_summary = df['playerid'].nunique()
    return df_summary
    




# Dictionary mapping function names to functions and their descriptions
STAT_FUNCTIONS = {
    "Goals": {"func": Goals_stats, "desc": "Goal Scored By Players"},
    "Detailed Goals": {"func": Goalsd_stats, "desc": "Detailed Goal Statistics For Players"},
    "Detailed Shots Per Match": {"func": shotsd_stats, "desc": "Detailed Shots Statistics For Players"},
    "Shot Accuracy": {"func": shot_accuracy, "desc": "Shot Accuracy By Players"},
    "Assists": {"func": Assists_stats, "desc": "Assists By Players"},
    "Goals + Assists": {"func": GA, "desc": "Goals + Assists By Players"},
    "Chances Created": {"func": cc, "desc": "Chances Created By Players"},
    "Tackles Per Match": {"func": tackles_90, "desc": "Tackles Per Match By Players"},
    "Interceptions Per Match": {"func": inter_90, "desc": "Interceptions Per Match By Players"},
    "Blocks Per Match": {"func": blocks_90, "desc": "Blocks Per Match By Players"},
    "Goalkeeper Saves": {"func": GK_Saves, "desc": "Total Saves By Goalkeepers"},
    "Goalkeeper Clean Sheets": {"func": GK_cs, "desc": "Clean Sheets By Goalkeepers"},
    "Goalkeeper Save Percentage": {"func": savesp, "desc": "Save Percentage By Goalkeepers"},
    "Offsides": {"func": offsides_stats, "desc": "Offside Statistics By Players"},
    "Fouls": {"func": fouls_stats, "desc": "Fouls Committed By Players"},
    "Yellow Cards": {"func": yc_stats, "desc": "Yellow Cards Received By Players"},
    "Red Cards": {"func": rc_stats, "desc": "Red Cards Received By Players"}
    # "Goals By Teams": {"func": Goals_statst, "desc": "Goal Scored By Teams"},
    # "Shots Stats By Teams": {"func": shotsd_statst, "desc": "Shot Stats By Teams"}
}

# # Main app
def main():
    st.title("Porkkalam Season 3 Player Statistics")

    # Initialize session state for dataframe if not exists
    if 'df' not in st.session_state:
        st.session_state.df = None
        st.session_state.data_loaded = False
        st.session_state.selected_stat = None  # Store selected stat

    # Load data 
    if not st.session_state.data_loaded:
        with st.spinner("Loading data from local files..."):
            # Fetch and merge CSV files
            merged_df = fetch_csv_files_local()
            total_goals=totalgoals(merged_df)
            tp_p=tpp(merged_df)
            st.metric(label="Total Goals", value=total_goals)
            st.metric(label="Total Players Played", value=tp_p)
            
            if not merged_df.empty:
                st.session_state.df = merged_df
                
                # Process data similar to original script
                st.session_state.df['Player_FN'] = st.session_state.df['Player_FN'].fillna(st.session_state.df.get('player', ''))
                
                # Fetch team mapping
                team_mapping = fetch_team_mapping_local()
                
                if not team_mapping.empty:
                    # Perform the merge
                    st.session_state.df = st.session_state.df.merge(team_mapping, left_on='teamid', right_on='ID', how='left')
                    st.session_state.df['team'] = st.session_state.df['TeamName']
                    st.session_state.df = st.session_state.df.drop(columns=['ID', 'TeamName'])
                else:
                    st.error("Team mapping could not be loaded, using teamid instead.")
                
                st.session_state.data_loaded = True
            else:
                st.error("Data loading failed. Check your local directories and file paths.")

    # Sidebar for statistic selection (Using Buttons Instead of Dropdown)
    st.sidebar.header("Select Stat")
    
    for stat_name in STAT_FUNCTIONS.keys():
        if st.sidebar.button(stat_name):
            st.session_state.selected_stat = stat_name

    # Display selected statistic
    if st.session_state.data_loaded and st.session_state.selected_stat:
        selected_stat = st.session_state.selected_stat
        stat_function = STAT_FUNCTIONS[selected_stat]["func"]
        description = STAT_FUNCTIONS[selected_stat]["desc"]
        
        st.subheader(f"{selected_stat} Stats")
        st.write(description)
        
        # Apply the selected statistic function
        try:
            result_df = stat_function(st.session_state.df.copy())
        
            # Display dataframe
            st.dataframe(
                result_df,
                height=500,
                use_container_width=True,
                hide_index=True,
                column_config={col: st.column_config.Column(width="auto") for col in result_df.columns}
            )
        
        except Exception as e:
            st.error(f"Error calculating statistics: {str(e)}")
    else:
        st.info("Please Select a Stat.")
# Run the main function
if __name__ == "__main__":
    main()

