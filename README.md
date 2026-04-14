# 🗳️ ONPE Real-Time Election Tracker

A comprehensive Streamlit dashboard for tracking Peruvian election results in real-time with statistical projections and confidence intervals.

## Features

✅ **Auto-refresh every 45 seconds** - Automatic data updates with countdown timer
✅ **Top 5 candidates display** - Current and projected results side-by-side
✅ **Projection tracking** - Line charts showing how projections change over time
✅ **Regional breakdown** - Lima vs provinces comparison with processing status
✅ **Confidence intervals** - 95% confidence intervals for all projections
✅ **Visual progress bars** - Color-coded candidate results
✅ **Countdown timer** - Shows time until next refresh
✅ **Manual refresh button** - Force immediate data update
✅ **Error handling** - Graceful error messages with auto-recovery
✅ **Color-coded candidates** - Unique colors for easy identification
✅ **Change indicators** - Shows if projections are trending up or down

## Installation

1. Install required packages:
```bash
pip install -r requirements.txt
```

## Running the Dashboard

```bash
streamlit run app.py
```

The dashboard will open in your browser at `http://localhost:8501`

## Dashboard Components

### Header Section
- Real-time countdown timer
- Key metrics: Votes Processed, Total Votes, Leading Candidate, Projection Confidence

### Top 5 Candidates
- Candidate name and ranking
- Current vs Projected percentages
- Change indicators (📈/📉/➡️)
- 95% Confidence intervals
- Dual progress bars (current and projected)

### Analysis Tabs

**Projection Trends**
- Line chart showing projection changes over last 2 hours
- Confidence interval bands for each candidate
- Interactive hover tooltips

**Regional Breakdown**
- Bar chart of processing status by region
- Regional statistics (Lima, Arequipa, Cusco, Provinces)
- Total votes per region

**Confidence Intervals**
- Horizontal error bars showing projection uncertainty
- Visual representation of statistical confidence
- Sorted by projected vote share

### Lima vs Provinces
- Side-by-side comparison
- Processing status metrics
- Total vote counts
- Progress bars

### Sidebar Controls
- 🔄 Manual refresh button
- Auto-refresh toggle (45s interval)
- Update statistics
- Last update timestamp
- Information messages

## Data Classes

### ONPEDataExtractor
Extracts and processes election data from ONPE website (currently uses mock data for demonstration).

**Methods:**
- `fetch_election_data()` - Returns current election results with regional breakdown

### StatisticalProjectionEngine
Generates statistical projections with confidence intervals.

**Methods:**
- `calculate_projection(current_data)` - Projects final results based on current data
- `get_projection_history(candidate, hours)` - Returns historical projections for trend analysis

## Customization

### Adjust Refresh Interval
Change the refresh interval in the code (default: 45 seconds):
```python
if seconds_since_update >= 45 and st.session_state.auto_refresh:  # Change 45 to your value
```

### Modify Candidate Colors
Edit the color assignments in `ONPEDataExtractor.fetch_election_data()`:
```python
candidates = [
    {"name": "Candidate Name", "party": "Party", "color": "#HEX_COLOR"},
    ...
]
```

### Change Confidence Level
Adjust confidence interval calculation in `StatisticalProjectionEngine.calculate_projection()`:
```python
margin = uncertainty * 2.5  # Adjust multiplier for wider/narrower intervals
```

## Technical Details

- **Framework:** Streamlit 1.31.0
- **Visualization:** Plotly 5.18.0
- **Data Processing:** Pandas 2.2.0, NumPy 1.26.3
- **Web Scraping:** BeautifulSoup4 4.12.3 (for future ONPE integration)

## Production Deployment

For production use with real ONPE data:

1. Implement actual web scraping in `ONPEDataExtractor.fetch_election_data()`
2. Add error handling for network failures
3. Implement data caching to reduce server load
4. Add authentication if required by ONPE
5. Deploy to cloud platform (Streamlit Cloud, AWS, Heroku, etc.)

## Notes

- Current implementation uses mock data for demonstration
- Projections are statistical estimates and include uncertainty margins
- Confidence intervals narrow as more votes are processed
- Auto-refresh can be toggled on/off via sidebar
- All timestamps are in local system time

## License

MIT License - Feel free to modify and use for your projects!
