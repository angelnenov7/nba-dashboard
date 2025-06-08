import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
from nba_api.stats.endpoints import LeagueDashTeamStats
import time

# Add caching to prevent unnecessary API calls
import diskcache
cache = diskcache.Cache("./cache")

@cache.memoize(expire=3600)  # Cache for 1 hour
def fetch_nba_team_stats(season):
    """
    Fetch NBA team stats for a given season.
    
    Args:
        season (str): The NBA season in the format 'YYYY-YY'.
        
    Returns:
        pd.DataFrame: DataFrame containing team stats.
    """
    try:
        # Fetch data from the NBA API
        response = LeagueDashTeamStats(season=season)
        data = response.get_data_frames()[0]
        
        # Convert to DataFrame
        df = pd.DataFrame(data)
        
        # Rename columns for consistency
        df.columns = [col.lower() for col in df.columns]
        
        return df
    
    except Exception as e:
        print(f"Error fetching data for season {season}: {e}")
        return pd.DataFrame()
    
def main():
    global combined_df  # Declare global

    # Generate seasons list from 2024 to 1990
    seasons = []
    for year in range(2024, 1989, -1):  # Stop at 1989 to get '1990-91' as earliest season
        season = f"{year}-{str(year+1)[2:]}"  # Format: '2024-25', '2023-24', etc.
        seasons.append(season)

    print(f"Fetching data for {len(seasons)} seasons from {seasons[0]} to {seasons[-1]}")

    all_team_stats = []

    for season in seasons:
        print(f"Fetching data for season: {season}")
        team_stats = fetch_nba_team_stats(season)
        if not team_stats.empty:
            team_stats['season'] = season
            all_team_stats.append(team_stats)
        time.sleep(2)  # Increase to 2 seconds between requests

    # Combine all seasons into a single DataFrame
    if all_team_stats:
        global combined_df  # Need to declare again when assigning
        combined_df = pd.concat(all_team_stats, ignore_index=True)
        print(f"Successfully fetched data for {len(all_team_stats)} seasons")
        print(combined_df.head())
    else:
        print("No data fetched.")

# Run main() first to populate combined_df
if __name__ == "__main__":
    main()
    
    if combined_df is not None:
        app = dash.Dash(__name__)
        app.title = "NBA Team Stats Dashboard"

        app.layout = html.Div([
            html.Div([
                html.H1("NBA Team Stats Dashboard", 
                        className='dashboard-header')
            ]),
            
            html.Div([
                html.Label('Select Season:', 
                          style={'fontSize': '18px', 
                                'fontWeight': 'bold',
                                'marginRight': '10px'}),
                dcc.Dropdown(
                    id='season-dropdown',
                    options=[{'label': season, 'value': season} 
                            for season in combined_df['season'].unique()],
                    value=combined_df['season'].unique()[0],
                    clearable=False,
                    className='season-dropdown'
                )
            ], className='dropdown-container'),
            
            dcc.Loading(
                id="loading",
                type="circle",
                children=[
                    html.Div([
                        dcc.Graph(id='team-stats-graph'),
                        dcc.Graph(id='three-point-graph'),
                        dcc.Graph(id='three-point-trend-graph')
                    ], className='graph-container')
                ]
            ),
            
            html.Div([
                html.Button(
                    "Export Data", 
                    id="export-button",
                    className="export-button"
                ),
                dcc.Download(id="download-data")
            ])
        ], className='dashboard-container')

        # Update the callback functions to include consistent styling
        @app.callback(
            Output('team-stats-graph', 'figure'),
            Input('season-dropdown', 'value')
        )
        def update_points_graph(selected_season):
            """
            Updates the team points per game bar chart for the selected season.
            
            Args:
                selected_season (str): Selected NBA season in 'YYYY-YY' format
            
            Returns:
                plotly.graph_objs._figure.Figure: Bar chart of team points per game
            """
            filtered_df = combined_df[combined_df['season'] == selected_season].copy()
            
            # Use loc to set values
            filtered_df.loc[:, 'pts_per_g'] = filtered_df['pts'] / filtered_df['gp']
            
            fig = px.bar(filtered_df, 
                        x='team_name', 
                        y='pts_per_g', 
                        title=f'Team Points Per Game - {selected_season}')
            
            # Add consistent styling
            fig.update_layout(
                plot_bgcolor='white',
                paper_bgcolor='white',
                font_family='Arial, sans-serif',
                title_font_size=20,
                xaxis_tickangle=45
            )
            return fig

        @app.callback(
            Output('three-point-graph', 'figure'),
            Input('season-dropdown', 'value')
        )
        def update_threes_graph(selected_season):
            """
            Updates the team three-pointers made per game bar chart for the selected season.
            
            Args:
                selected_season (str): Selected NBA season in 'YYYY-YY' format
            
            Returns:
                plotly.graph_objs._figure.Figure: Bar chart of team three-pointers per game
            """
            # Create a copy of the filtered data
            filtered_df = combined_df[combined_df['season'] == selected_season].copy()
            
            # Use loc to set values
            filtered_df.loc[:, 'fg3_per_g'] = filtered_df['fg3m'] / filtered_df['gp']
            
            fig = px.bar(filtered_df,
                         x='team_name',
                         y='fg3_per_g',
                         title=f'Team Three Pointers Made Per Game - {selected_season}')
            
            # Add consistent styling
            fig.update_layout(
                plot_bgcolor='white',
                paper_bgcolor='white',
                font_family='Arial, sans-serif',
                title_font_size=20,
                xaxis_tickangle=45
            )
            return fig

        @app.callback(
            Output('three-point-trend-graph', 'figure'),
            Input('season-dropdown', 'value')
        )
        def update_threes_trend(selected_season):
            """Create scatter plot showing 3-point attempt trends across seasons."""
            # Calculate league average 3-point attempts per game for each season
            season_avg = combined_df.groupby('season', as_index=False).agg(
                fg3a_per_g=pd.NamedAgg(column='fg3a', aggfunc=lambda x: x.sum() / combined_df.loc[x.index, 'gp'].sum())
            ).sort_values('season')  # Sort by season for better visualization
            
            # Create scatter plot with improved styling
            fig = px.scatter(season_avg, 
                            x='season', 
                            y='fg3a_per_g',
                            title='Evolution of NBA 3-Point Attempts Per Game',
                            labels={'fg3a_per_g': '3-Point Attempts Per Game',
                                   'season': 'Season'},
                            template='plotly_white')
            
            # Add trendline with custom styling
            fig.add_traces(px.line(season_avg, 
                                  x='season', 
                                  y='fg3a_per_g',
                                  line_shape='spline').data)  # Smoothed line
            
            # Enhanced styling
            fig.update_layout(
                plot_bgcolor='white',
                paper_bgcolor='white',
                font_family='Arial, sans-serif',
                title_font_size=20,
                showlegend=False,
                hovermode='x unified',
                xaxis=dict(
                    tickangle=45,
                    tickfont=dict(size=12),
                    gridcolor='lightgray'
                ),
                yaxis=dict(
                    title_font=dict(size=14),
                    gridcolor='lightgray',
                    zeroline=True,
                    zerolinecolor='lightgray'
                )
            )
            
            # Add hover template and customize marker size
            fig.update_traces(
                marker=dict(size=8),
                hovertemplate="Season: %{x}<br>3PA per game: %{y:.2f}<extra></extra>"
            )
            
            return fig
            
        @app.callback(
            Output("download-data", "data"),
            Input("export-button", "n_clicks"),
            prevent_initial_call=True,
        )
        def export_data(n_clicks):
            """
            Exports the combined NBA statistics to a CSV file.
            
            Args:
                n_clicks (int): Number of times the export button has been clicked
            
            Returns:
                dict: Dictionary containing the data to be downloaded
            """
            if n_clicks:
                return dcc.send_data_frame(
                    combined_df.to_csv,
                    "nba_stats.csv",
                    index=False
                )
        
        app.run(debug=True, port=8051)  # Updated to use run() instead of run_server()
    else:
        print("No data available to create dashboard")

def calculate_trend_statistics():
    """Calculate additional statistics for trend analysis."""
    stats = combined_df.groupby('season').agg({
        'fg3a': ['mean', 'std'],
        'fg3_pct': 'mean',
        'pts': 'mean'
    }).round(2)
    return stats
