# NBA Statistical Analysis Dashboard

An interactive dashboard that visualizes NBA team statistics and the evolution of 3-point shooting from 1990-91 to 2024-25 seasons.

## Features

- Historical team statistics visualization
- Interactive season selection
- Three distinct visualizations:
  - Team Points Per Game
  - Team Three-Pointers Made Per Game
  - League-wide 3-Point Attempt Trends
- Data export functionality
- Caching system for improved performance

## Requirements

- Python 3.8+
- Required packages:
  - dash
  - pandas
  - plotly
  - nba_api
  - diskcache

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/nba-dashboard.git
cd nba-dashboard
```

2. Create and activate a virtual environment:
```bash
python -m venv data_viz_env
data_viz_env\Scripts\activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the dashboard:
```bash
python dash_nba_style_evolution.py
```

2. Open your web browser and navigate to:
```
http://localhost:8051
```

3. Use the season dropdown to select different NBA seasons
4. Export data using the "Export Data" button

## Project Structure

```
nba-dashboard/
│
├── dash_nba_style_evolution.py  # Main application file
├── requirements.txt             # Package dependencies
├── README.md                   # Project documentation
├── assets/                     # Static assets
│   └── styles.css             # Custom styling
└── cache/                      # Data cache directory
```

## Data Sources

- Data is fetched from the official NBA API using the `nba_api` package
- Statistics include regular season team data from 1990-91 to 2024-25

## License

MIT License - Feel free to use and modify as needed.