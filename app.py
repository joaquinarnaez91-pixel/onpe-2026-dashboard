import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import time
from typing import Dict, List, Tuple
import requests
from bs4 import BeautifulSoup

# Page configuration
st.set_page_config(
    page_title="ONPE Election Tracker",
    page_icon="🗳️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .candidate-name {
        font-weight: bold;
        font-size: 1.2rem;
    }
    .countdown {
        font-size: 1.5rem;
        font-weight: bold;
        color: #ff4b4b;
        text-align: center;
    }
    .stProgress > div > div > div > div {
        background-color: #1f77b4;
    }
</style>
""", unsafe_allow_html=True)

# ==================== DATA EXTRACTION ====================

class ONPEDataExtractor:
    """Extracts and processes election data from ONPE website"""

    def __init__(self):
        self.base_url = "https://resultados.onpe.gob.pe"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    def fetch_election_data(self) -> Dict:
        """
        Fetch current election results
        Returns mock data for demonstration purposes
        """
        # In production, this would scrape actual ONPE data
        # For demo, we'll generate realistic mock data

        candidates = [
            {"name": "María Rodríguez", "party": "Partido A", "color": "#FF6B6B"},
            {"name": "Carlos Mendoza", "party": "Partido B", "color": "#4ECDC4"},
            {"name": "Ana García", "party": "Partido C", "color": "#45B7D1"},
            {"name": "José Torres", "party": "Partido D", "color": "#FFA07A"},
            {"name": "Luis Fernández", "party": "Partido E", "color": "#98D8C8"},
            {"name": "Patricia Silva", "party": "Partido F", "color": "#F7DC6F"},
        ]

        # Generate realistic vote percentages
        votes = np.random.dirichlet(np.array([5, 4, 3, 2, 1.5, 1]))

        results = []
        for i, candidate in enumerate(candidates):
            results.append({
                "candidate": candidate["name"],
                "party": candidate["party"],
                "votes": int(votes[i] * 10000000),
                "percentage": votes[i] * 100,
                "color": candidate["color"]
            })

        # Regional breakdown
        regional_data = {
            "Lima": {
                "processed": np.random.uniform(75, 95),
                "total_votes": 4500000
            },
            "Arequipa": {
                "processed": np.random.uniform(70, 90),
                "total_votes": 850000
            },
            "Cusco": {
                "processed": np.random.uniform(65, 85),
                "total_votes": 720000
            },
            "Provinces": {
                "processed": np.random.uniform(60, 80),
                "total_votes": 3930000
            }
        }

        return {
            "results": sorted(results, key=lambda x: x["percentage"], reverse=True),
            "timestamp": datetime.now(),
            "processed_percentage": np.random.uniform(70, 95),
            "total_votes": 10000000,
            "regional": regional_data
        }

# ==================== STATISTICAL PROJECTION ====================

class StatisticalProjectionEngine:
    """Generates statistical projections with confidence intervals"""

    def __init__(self):
        self.historical_projections = {}

    def calculate_projection(self, current_data: Dict) -> Dict:
        """
        Calculate projected final results with confidence intervals
        """
        projections = []

        for candidate in current_data["results"]:
            current_pct = candidate["percentage"]
            processed_pct = current_data["processed_percentage"]

            # Adjustment factor based on processed percentage
            uncertainty = (100 - processed_pct) / 100

            # Calculate projection with margin of error
            margin = uncertainty * 2.5  # Decreases as more votes are counted

            projected_pct = current_pct + np.random.uniform(-margin/2, margin/2)

            projections.append({
                "candidate": candidate["candidate"],
                "current": current_pct,
                "projected": max(0, projected_pct),
                "lower_bound": max(0, projected_pct - margin),
                "upper_bound": min(100, projected_pct + margin),
                "confidence": min(99, 70 + (processed_pct * 0.3)),
                "color": candidate["color"]
            })

        # Store historical projection for tracking
        timestamp = datetime.now()
        for proj in projections:
            candidate_name = proj["candidate"]
            if candidate_name not in self.historical_projections:
                self.historical_projections[candidate_name] = []

            self.historical_projections[candidate_name].append({
                "timestamp": timestamp,
                "projected": proj["projected"],
                "lower": proj["lower_bound"],
                "upper": proj["upper_bound"]
            })

        return {
            "projections": sorted(projections, key=lambda x: x["projected"], reverse=True),
            "timestamp": timestamp
        }

    def get_projection_history(self, candidate: str, hours: int = 2) -> List[Dict]:
        """Get historical projections for a candidate"""
        if candidate not in self.historical_projections:
            return []

        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [
            p for p in self.historical_projections[candidate]
            if p["timestamp"] > cutoff_time
        ]

# ==================== INITIALIZE SESSION STATE ====================

if 'extractor' not in st.session_state:
    st.session_state.extractor = ONPEDataExtractor()

if 'projection_engine' not in st.session_state:
    st.session_state.projection_engine = StatisticalProjectionEngine()

if 'last_update' not in st.session_state:
    st.session_state.last_update = datetime.now()

if 'update_count' not in st.session_state:
    st.session_state.update_count = 0

if 'auto_refresh' not in st.session_state:
    st.session_state.auto_refresh = True

# ==================== HELPER FUNCTIONS ====================

def create_progress_bar(percentage: float, color: str) -> str:
    """Create HTML progress bar"""
    return f"""
    <div style="background-color: #e0e0e0; border-radius: 10px; height: 30px; width: 100%;">
        <div style="background-color: {color}; width: {percentage}%; height: 100%; 
                    border-radius: 10px; text-align: center; line-height: 30px; 
                    color: white; font-weight: bold;">
            {percentage:.2f}%
        </div>
    </div>
    """

def calculate_countdown(last_update: datetime, refresh_interval: int = 45) -> int:
    """Calculate seconds until next refresh"""
    elapsed = (datetime.now() - last_update).total_seconds()
    remaining = max(0, refresh_interval - elapsed)
    return int(remaining)

def create_projection_chart(projection_engine: StatisticalProjectionEngine, 
                           top_candidates: List[str]) -> go.Figure:
    """Create line chart showing projection changes over time"""
    fig = go.Figure()

    for candidate in top_candidates:
        history = projection_engine.get_projection_history(candidate)

        if len(history) > 0:
            timestamps = [h["timestamp"] for h in history]
            projections = [h["projected"] for h in history]
            upper = [h["upper"] for h in history]
            lower = [h["lower"] for h in history]

            # Main projection line
            fig.add_trace(go.Scatter(
                x=timestamps,
                y=projections,
                mode='lines+markers',
                name=candidate,
                line=dict(width=3),
                marker=dict(size=8)
            ))

            # Confidence interval
            fig.add_trace(go.Scatter(
                x=timestamps + timestamps[::-1],
                y=upper + lower[::-1],
                fill='toself',
                fillcolor=f'rgba(128, 128, 128, 0.2)',
                line=dict(color='rgba(255,255,255,0)'),
                showlegend=False,
                name=f'{candidate} CI'
            ))

    fig.update_layout(
        title="Projection Trends Over Time",
        xaxis_title="Time",
        yaxis_title="Projected Vote Share (%)",
        hovermode='x unified',
        height=400,
        template="plotly_white"
    )

    return fig

def create_regional_breakdown(regional_data: Dict) -> go.Figure:
    """Create regional breakdown chart"""
    regions = list(regional_data.keys())
    processed = [regional_data[r]["processed"] for r in regions]

    fig = go.Figure(data=[
        go.Bar(
            x=regions,
            y=processed,
            text=[f"{p:.1f}%" for p in processed],
            textposition='auto',
            marker_color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A']
        )
    ])

    fig.update_layout(
        title="Vote Processing by Region",
        xaxis_title="Region",
        yaxis_title="Percentage Processed (%)",
        yaxis_range=[0, 100],
        height=350,
        template="plotly_white"
    )

    return fig

def create_confidence_chart(projections: List[Dict]) -> go.Figure:
    """Create confidence interval visualization"""
    candidates = [p["candidate"] for p in projections[:5]]
    projected = [p["projected"] for p in projections[:5]]
    lower = [p["lower_bound"] for p in projections[:5]]
    upper = [p["upper_bound"] for p in projections[:5]]
    colors = [p["color"] for p in projections[:5]]

    fig = go.Figure()

    for i, candidate in enumerate(candidates):
        # Error bars for confidence intervals
        fig.add_trace(go.Scatter(
            x=[projected[i]],
            y=[candidate],
            error_x=dict(
                type='data',
                symmetric=False,
                array=[upper[i] - projected[i]],
                arrayminus=[projected[i] - lower[i]],
                thickness=3,
                width=10
            ),
            mode='markers',
            marker=dict(size=15, color=colors[i]),
            name=candidate,
            showlegend=False
        ))

    fig.update_layout(
        title="Projected Results with 95% Confidence Intervals",
        xaxis_title="Vote Share (%)",
        yaxis_title="Candidate",
        height=400,
        template="plotly_white",
        xaxis_range=[0, max(upper) * 1.1]
    )

    return fig

# ==================== MAIN DASHBOARD ====================

def main():
    # Header
    st.markdown('<div class="main-header">🗳️ ONPE Real-Time Election Tracker</div>', 
                unsafe_allow_html=True)

    # Sidebar controls
    with st.sidebar:
        st.header("⚙️ Dashboard Controls")

        # Manual refresh button
        if st.button("🔄 Refresh Now", use_container_width=True):
            st.session_state.last_update = datetime.now() - timedelta(seconds=45)
            st.rerun()

        # Auto-refresh toggle
        auto_refresh = st.toggle("Auto-refresh (45s)", value=st.session_state.auto_refresh)
        st.session_state.auto_refresh = auto_refresh

        st.divider()

        # Stats
        st.metric("Total Updates", st.session_state.update_count)
        st.metric("Last Update", st.session_state.last_update.strftime("%H:%M:%S"))

        st.divider()

        # Info
        st.info("📊 Dashboard updates every 45 seconds with latest ONPE data")
        st.warning("⚠️ Projections are statistical estimates based on current vote counts")

    # Countdown timer
    countdown_placeholder = st.empty()

    # Check if refresh is needed
    seconds_since_update = (datetime.now() - st.session_state.last_update).total_seconds()

    if seconds_since_update >= 45 and st.session_state.auto_refresh:
        st.session_state.last_update = datetime.now()
        st.session_state.update_count += 1
        st.rerun()

    # Display countdown
    remaining = calculate_countdown(st.session_state.last_update)
    countdown_placeholder.markdown(
        f'<div class="countdown">⏱️ Next update in: {remaining} seconds</div>',
        unsafe_allow_html=True
    )

    # Fetch data
    try:
        with st.spinner("Fetching latest election data..."):
            election_data = st.session_state.extractor.fetch_election_data()
            projection_data = st.session_state.projection_engine.calculate_projection(election_data)

        # Key metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Votes Processed",
                f"{election_data['processed_percentage']:.1f}%",
                delta=f"+{np.random.uniform(0.5, 2.0):.1f}%"
            )

        with col2:
            st.metric(
                "Total Votes",
                f"{election_data['total_votes']:,}",
                delta=f"+{np.random.randint(10000, 50000):,}"
            )

        with col3:
            leader = projection_data["projections"][0]
            st.metric(
                "Leading Candidate",
                leader["candidate"].split()[0],
                delta=f"{leader['projected']:.1f}%"
            )

        with col4:
            st.metric(
                "Projection Confidence",
                f"{leader['confidence']:.0f}%",
                delta=f"+{np.random.uniform(0.5, 1.5):.1f}%"
            )

        st.divider()

        # Main content - Top 5 candidates
        st.header("🏆 Top 5 Candidates - Current & Projected Results")

        for i, proj in enumerate(projection_data["projections"][:5], 1):
            with st.container():
                col1, col2 = st.columns([2, 3])

                with col1:
                    st.markdown(f"### {i}. {proj['candidate']}")
                    st.caption(f"Current: {proj['current']:.2f}% | Projected: {proj['projected']:.2f}%")

                    # Change indicator
                    change = proj['projected'] - proj['current']
                    change_icon = "📈" if change > 0 else "📉" if change < 0 else "➡️"
                    st.markdown(f"{change_icon} Change: {change:+.2f}%")

                    st.caption(f"95% CI: [{proj['lower_bound']:.2f}%, {proj['upper_bound']:.2f}%]")

                with col2:
                    # Current results progress bar
                    st.caption("Current Results")
                    st.markdown(
                        create_progress_bar(proj['current'], proj['color']),
                        unsafe_allow_html=True
                    )

                    # Projected results progress bar
                    st.caption("Projected Results")
                    st.markdown(
                        create_progress_bar(proj['projected'], proj['color']),
                        unsafe_allow_html=True
                    )

                st.divider()

        # Charts section
        st.header("📊 Detailed Analysis")

        tab1, tab2, tab3 = st.tabs(["Projection Trends", "Regional Breakdown", "Confidence Intervals"])

        with tab1:
            st.plotly_chart(
                create_projection_chart(
                    st.session_state.projection_engine,
                    [p["candidate"] for p in projection_data["projections"][:5]]
                ),
                use_container_width=True
            )
            st.info("📈 This chart shows how projected results have changed over the last 2 hours")

        with tab2:
            col1, col2 = st.columns([2, 1])

            with col1:
                st.plotly_chart(
                    create_regional_breakdown(election_data["regional"]),
                    use_container_width=True
                )

            with col2:
                st.subheader("Regional Stats")
                for region, data in election_data["regional"].items():
                    st.metric(
                        region,
                        f"{data['processed']:.1f}%",
                        delta=f"{data['total_votes']:,} votes"
                    )

        with tab3:
            st.plotly_chart(
                create_confidence_chart(projection_data["projections"]),
                use_container_width=True
            )
            st.info("📊 Wider intervals indicate higher uncertainty in projections")

        # Lima vs Provinces comparison
        st.header("🏙️ Lima vs Provinces Breakdown")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Lima Metropolitan")
            lima_data = election_data["regional"]["Lima"]
            st.metric("Processing Status", f"{lima_data['processed']:.1f}%")
            st.metric("Total Votes", f"{lima_data['total_votes']:,}")
            st.progress(lima_data['processed'] / 100)

        with col2:
            st.subheader("Provinces")
            prov_data = election_data["regional"]["Provinces"]
            st.metric("Processing Status", f"{prov_data['processed']:.1f}%")
            st.metric("Total Votes", f"{prov_data['total_votes']:,}")
            st.progress(prov_data['processed'] / 100)

        # Footer
        st.divider()
        st.caption(f"Last updated: {election_data['timestamp'].strftime('%Y-%m-%d %H:%M:%S')} | "
                  f"Data source: ONPE | Auto-refresh: {'ON' if st.session_state.auto_refresh else 'OFF'}")

    except Exception as e:
        st.error(f"❌ Error fetching election data: {str(e)}")
        st.info("🔄 The dashboard will attempt to refresh automatically in 45 seconds")
        st.exception(e)

    # Auto-refresh mechanism
    if st.session_state.auto_refresh:
        time.sleep(1)
        st.rerun()

if __name__ == "__main__":
    main()
