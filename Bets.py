import pandas as pd

# Define files
goals_file = 'Export.xlsx'
disposals_file = 'ExportDisposals.xlsx'

# Define market rows and columns
goal_markets = {
    'AGS': (3, 8, 'AGS Odds'),
    '2+': (10, 15, '2+ Odds'),
    '3+': (17, 22, '3+ Odds')
}

disposal_markets = {
    '15+': (3, 8, '15+ Odds'),
    '20+': (10, 15, '20+ Odds'),
    '25+': (17, 22, '25+ Odds')
}

# Load sheet names
goals_xls = pd.ExcelFile(goals_file)
disposals_xls = pd.ExcelFile(disposals_file)

# Collect results
output = []

for sheet in goals_xls.sheet_names:
    row = {'Game': sheet}
    df_goal = pd.read_excel(goals_xls, sheet_name=sheet, header=None)

    # Process goal markets
    for market, (start, end, colname) in goal_markets.items():
        home_df = df_goal.iloc[start:end, 1:5].copy()
        away_df = df_goal.iloc[start:end, 8:12].copy()
        home_df.columns = away_df.columns = ['Player', 'Edge', colname, 'VS']
        combined = pd.concat([home_df, away_df])
        combined = combined.dropna(subset=['Edge', colname])
        combined[colname] = pd.to_numeric(combined[colname], errors='coerce')
        combined = combined[combined[colname] < 3]
        if not combined.empty:
            top_idx = combined['Edge'].idxmax()
            top_player = combined.loc[[top_idx], 'Player'].values[0]
            top_edge = combined.loc[[top_idx], 'Edge'].values[0]
            top_odds = combined.loc[[top_idx], colname].values[0]

            row[f'{market}_Player'] = str(top_player)
            row[f'{market}_Edge'] = round(float(top_edge), 3)
            row[f'{market}_Odds'] = round(float(top_odds), 2)
        else:
            row[f'{market}_Player'] = None
            row[f'{market}_Edge'] = None
            row[f'{market}_Odds'] = None

    # Process disposal markets
    if sheet in disposals_xls.sheet_names:
        df_disp = pd.read_excel(disposals_xls, sheet_name=sheet, header=None)
        for market, (start, end, colname) in disposal_markets.items():
            home_df = df_disp.iloc[start:end, 1:5].copy()
            away_df = df_disp.iloc[start:end, 8:12].copy()
            home_df.columns = away_df.columns = ['Player', 'Edge', colname, 'VS']
            combined = pd.concat([home_df, away_df])
            combined = combined.dropna(subset=['Edge', colname])
            combined[colname] = pd.to_numeric(combined[colname], errors='coerce')
            combined = combined[combined[colname] < 3]
            if not combined.empty:
                top_idx = combined['Edge'].idxmax()
                top_player = combined.loc[[top_idx], 'Player'].values[0]
                top_edge = combined.loc[[top_idx], 'Edge'].values[0]
                top_odds = combined.loc[[top_idx], colname].values[0]

                row[f'{market}_Player'] = str(top_player)
                row[f'{market}_Edge'] = round(float(top_edge), 3)
                row[f'{market}_Odds'] = round(float(top_odds), 2)
            else:
                row[f'{market}_Player'] = None
                row[f'{market}_Edge'] = None
                row[f'{market}_Odds'] = None
    else:
        for market in disposal_markets.keys():
            row[f'{market}_Player'] = None
            row[f'{market}_Edge'] = None
            row[f'{market}_Odds'] = None

    output.append(row)

# Save output
output_df = pd.DataFrame(output)
output_df.to_csv('top_edges_per_game.csv', index=False)

print("✅ Top edges saved to 'top_edges_per_game.csv'")
