import streamlit as st
import pandas as pd
import numpy as np
import pickle
import os
import datetime
import matplotlib.pyplot as plt
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(
    page_title="RentIQ Nigeria",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Verified Lagos background images (Unsplash, free-use, no attribution)
TIER_BACKGROUNDS = {
    'island':           'https://images.unsplash.com/photo-1580500550469-4f0baa4a2da3?w=1920&q=80',
    'gra':              'https://images.unsplash.com/photo-1714329797174-67e6cbe05920?w=1920&q=80',
    'upscale-mainland': 'https://images.unsplash.com/photo-1714329797174-67e6cbe05920?w=1920&q=80',
    'mainland':         'https://images.unsplash.com/photo-1572931089825-cf67ec0c2e7b?w=1920&q=80',
    'suburb':           'https://images.unsplash.com/photo-1572931089825-cf67ec0c2e7b?w=1920&q=80',
    'outskirt':         'https://images.unsplash.com/photo-1572931089825-cf67ec0c2e7b?w=1920&q=80',
}

DEFAULT_BG = 'https://images.unsplash.com/photo-1580500550469-4f0baa4a2da3?w=1920&q=80'


def render_background(tier_key):
    img_url = TIER_BACKGROUNDS.get(tier_key, DEFAULT_BG)
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;600;700&family=Space+Mono:wght@400;700&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Sora', sans-serif;
    }}

    .stApp {{
        background-image:
            linear-gradient(rgba(10, 10, 10, 0.93), rgba(10, 10, 10, 0.97)),
            url('{img_url}');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        color: #f0ede6;
    }}

    section[data-testid="stSidebar"] {{
        background-color: rgba(15, 15, 15, 0.95);
        backdrop-filter: blur(10px);
        border-right: 1px solid #2a2a2a;
    }}

    section[data-testid="stSidebar"] * {{
        color: #f0ede6 !important;
    }}

    .rent-display {{
        font-family: 'Space Mono', monospace;
        font-size: 3.2rem;
        font-weight: 700;
        color: #c8f564;
        letter-spacing: -1px;
        line-height: 1.1;
    }}

    .rent-range {{
        font-family: 'Space Mono', monospace;
        font-size: 1.05rem;
        color: #888;
        margin-top: 6px;
    }}

    .tier-badge {{
        display: inline-block;
        padding: 4px 14px;
        border-radius: 4px;
        font-family: 'Space Mono', monospace;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 1px;
        text-transform: uppercase;
        margin-top: 10px;
    }}

    .tier-budget    {{ background: #1a2e1a; color: #6fcf6f; border: 1px solid #3a5e3a; }}
    .tier-midrange  {{ background: #2e2a14; color: #f0c040; border: 1px solid #5e521a; }}
    .tier-premium   {{ background: #2a1e14; color: #f09060; border: 1px solid #5e3a20; }}
    .tier-luxury    {{ background: #1e1430; color: #b090f0; border: 1px solid #3a2060; }}

    .location-pill {{
        display: inline-block;
        padding: 3px 12px;
        border-radius: 20px;
        font-size: 0.72rem;
        font-family: 'Space Mono', monospace;
        letter-spacing: 0.5px;
        background: rgba(30, 30, 30, 0.8);
        border: 1px solid #333;
        color: #aaa;
        margin-left: 10px;
        vertical-align: middle;
    }}

    .verdict-fair    {{ color: #6fcf6f; font-weight: 700; font-size: 1.3rem; }}
    .verdict-above   {{ color: #f09060; font-weight: 700; font-size: 1.3rem; }}
    .verdict-below   {{ color: #b090f0; font-weight: 700; font-size: 1.3rem; }}

    .metric-card {{
        background: rgba(20, 20, 20, 0.85);
        backdrop-filter: blur(8px);
        border: 1px solid rgba(60, 60, 60, 0.5);
        border-radius: 10px;
        padding: 20px 24px;
        margin-bottom: 12px;
    }}

    .section-label {{
        font-size: 0.68rem;
        font-family: 'Space Mono', monospace;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: #666;
        margin-bottom: 14px;
    }}

    div[data-testid="stTabs"] button {{
        font-family: 'Space Mono', monospace;
        font-size: 0.75rem;
        letter-spacing: 1px;
    }}

    .stSlider > div > div > div {{ background: #c8f564 !important; }}

    hr {{ border-color: #2a2a2a; }}

    .stButton > button {{
        background: #c8f564;
        color: #0d0d0d;
        font-family: 'Space Mono', monospace;
        font-weight: 700;
        font-size: 0.8rem;
        letter-spacing: 1px;
        border: none;
        border-radius: 4px;
        padding: 10px 24px;
    }}

    .stButton > button:hover {{
        background: #d4f97a;
        color: #0d0d0d;
    }}

    .warning-box {{
        background: rgba(30, 26, 16, 0.85);
        border: 1px solid #4a3a10;
        border-radius: 6px;
        padding: 12px 16px;
        font-size: 0.82rem;
        color: #c8a840;
        margin-top: 12px;
    }}

    h1, h2, h3 {{ color: #f0ede6; }}

    .driver-explain {{
        background: rgba(20, 20, 20, 0.75);
        padding: 16px 20px;
        margin-top: 14px;
        border-radius: 6px;
        font-size: 0.88rem;
        color: #bbb;
        line-height: 1.6;
    }}

    .driver-explain strong {{ color: #c8f564; }}

    .submission-counter {{
        text-align: right;
        font-family: 'Space Mono', monospace;
        font-size: 0.72rem;
        color: #555;
        margin-bottom: 12px;
    }}

    .submission-counter strong {{
        color: #c8f564;
        font-size: 0.85rem;
    }}

    .stNumberInput label, .stTextInput label {{
        font-size: 0.85rem;
        color: #aaa !important;
    }}

    .submit-success {{
        background: rgba(20, 50, 20, 0.85);
        border: 1px solid #4a8a4a;
        border-radius: 6px;
        padding: 14px 18px;
        color: #8af08a;
        font-size: 0.9rem;
        margin-top: 12px;
    }}

    .submit-error {{
        background: rgba(50, 20, 20, 0.85);
        border: 1px solid #8a4a4a;
        border-radius: 6px;
        padding: 14px 18px;
        color: #f08a8a;
        font-size: 0.9rem;
        margin-top: 12px;
    }}
    </style>
    """, unsafe_allow_html=True)


FEATURES_V2 = [
    'bedrooms_encoded', 'bathrooms', 'type_house', 'tier_encoded',
    'neighbourhood_median_rent', 'area_median_rent', 'tier_median_rent',
    'electricity_hours', 'latitude', 'longitude',
    'dist_to_vi_km', 'dist_to_ikeja_km', 'tier_target_enc',
]

BEDROOM_LABELS = {
    'Mini-flat': 1,
    '1 Bedroom': 2,
    '2 Bedrooms': 3,
    '3 Bedrooms': 4,
    '4+ Bedrooms': 5,
}

PRICE_TIERS = {
    'Budget':    (0,        700_000),
    'Mid-range': (700_000,  2_500_000),
    'Premium':   (2_500_000, 7_000_000),
    'Luxury':    (7_000_000, float('inf')),
}

TIER_CSS = {
    'Budget':    'tier-budget',
    'Mid-range': 'tier-midrange',
    'Premium':   'tier-premium',
    'Luxury':    'tier-luxury',
}

# Plain-English SHAP labels mapped from actual feature names
PLAIN_LABELS = {
    'neighbourhood_median_rent': 'What rent normally looks like in this area',
    'area_median_rent':          'Local average rent',
    'bedrooms_encoded':          'Number of bedrooms',
    'bathrooms':                 'Number of bathrooms',
    'tier_median_rent':          'Where this area ranks in Lagos',
    'tier_encoded':              'Where this area ranks in Lagos',
    'tier_target_enc':           'Where this area ranks in Lagos',
    'electricity_hours':         'Electricity supply',
    'dist_to_vi_km':             'Distance to Victoria Island',
    'dist_to_ikeja_km':          'Distance to Ikeja',
    'type_house':                'Flat vs House',
    'longitude':                 'Location on the Lagos map',
    'latitude':                  'Location on the Lagos map',
}


def get_artifacts_path():
    drive_path = '/content/drive/MyDrive/RentIQ Nigeria/model/artifacts'
    if os.path.exists(drive_path):
        return drive_path
    return os.path.join(os.path.dirname(__file__), 'artifacts')


@st.cache_resource(show_spinner=False)
def load_models():
    path = get_artifacts_path()
    with open(f'{path}/stacked_ensemble.pkl', 'rb') as f:
        ensemble = pickle.load(f)
    with open(f'{path}/lgb_p10.pkl', 'rb') as f:
        p10 = pickle.load(f)
    with open(f'{path}/lgb_p90.pkl', 'rb') as f:
        p90 = pickle.load(f)
    return ensemble, p10, p90


@st.cache_data(show_spinner=False)
def load_lookup():
    path = get_artifacts_path()
    return pd.read_csv(f'{path}/area_lookup.csv')


@st.cache_data(show_spinner=False)
def load_master():
    candidates = [
        '/content/drive/MyDrive/RentIQ Nigeria/data/processed/rentiq_master.csv',
        os.path.join(os.path.dirname(__file__), 'data', 'rentiq_master.csv'),
        os.path.join(os.path.dirname(__file__), 'rentiq_master.csv'),
    ]
    for p in candidates:
        if os.path.exists(p):
            return pd.read_csv(p)
    return None


@st.cache_data(show_spinner=False)
def load_shap():
    path = get_artifacts_path()
    shap_path = f'{path}/shap_importance_advanced.csv'
    if os.path.exists(shap_path):
        return pd.read_csv(shap_path)
    return None


@st.cache_resource(show_spinner=False)
def get_gsheet_client():
    """Connect to Google Sheets. Returns the worksheet or None if credentials missing."""
    scopes = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]

    # Try Streamlit secrets first (production)
    try:
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    except (KeyError, FileNotFoundError):
        # Fall back to local key file (Colab/dev)
        key_path = '/content/drive/MyDrive/RentIQ Nigeria/rentiq_sheets_key.json'
        if os.path.exists(key_path):
            creds = Credentials.from_service_account_file(key_path, scopes=scopes)
        else:
            return None

    try:
        gc = gspread.authorize(creds)
        sh = gc.open("RentIQ Ground Truth")
        return sh.sheet1
    except Exception:
        return None


def get_submission_count():
    """Count rows in the Google Sheet (excluding header)."""
    try:
        ws = get_gsheet_client()
        if ws is None:
            return 0
        all_values = ws.get_all_values()
        return max(0, len(all_values) - 1)
    except Exception:
        return 0


def classify_price_tier(rent):
    for tier, (low, high) in PRICE_TIERS.items():
        if low <= rent < high:
            return tier
    return 'Luxury'


def predict_rent(ensemble, p10_model, p90_model, features_dict):
    X = pd.DataFrame([features_dict], columns=FEATURES_V2)
    xgb_pred = ensemble['xgb'].predict(X)[0]
    lgb_pred = ensemble['lgb'].predict(X)[0]
    cat_pred = ensemble['cat'].predict(X)[0]
    stack_in = np.array([[xgb_pred, lgb_pred, cat_pred]])
    point = float(np.expm1(ensemble['meta'].predict(stack_in)[0]))
    p10 = float(np.expm1(p10_model.predict(X)[0]))
    p90 = float(np.expm1(p90_model.predict(X)[0]))
    return point, p10, p90


def format_naira(amount):
    if amount >= 1_000_000:
        return f"₦{amount/1_000_000:.1f}m"
    elif amount >= 1_000:
        return f"₦{amount/1_000:.0f}k"
    return f"₦{amount:,.0f}"


def format_with_commas(num_str):
    """Take a raw digit string and return it formatted with commas."""
    digits = ''.join(c for c in num_str if c.isdigit())
    if not digits:
        return ''
    return f"{int(digits):,}"


def parse_naira_input(formatted_str):
    """Parse a comma-formatted string back to an integer."""
    digits = ''.join(c for c in formatted_str if c.isdigit())
    return int(digits) if digits else 0


def electricity_label(hours):
    if hours >= 20:
        return "Band A (20hrs+)"
    elif hours >= 16:
        return "Band B (~16hrs)"
    elif hours >= 12:
        return "Band C (~12hrs)"
    elif hours >= 8:
        return "Band D (~8hrs)"
    else:
        return "Band E (~4hrs)"


def auto_bathrooms(bedrooms_encoded):
    """Sensible default for bathrooms based on bedroom count."""
    mapping = {0: 1, 1: 1, 2: 1, 3: 2, 4: 3, 5: 4}
    return mapping.get(bedrooms_encoded, 2)


# Initialise session state
defaults = {
    'prediction_done': False,
    'predicted': None,
    'p10': None,
    'p90': None,
    'price_tier_name': None,
    'location_tier_display': None,
    'area_display': None,
    'area_key': None,
    'bedrooms_encoded': None,
    'elec_hours': None,
    'current_tier_key': 'mainland',
    'submitted_areas': set(),
    'last_features': None,
    'last_prop_type': None,
    'last_bedrooms_label': None,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# Load everything
try:
    ensemble, p10_model, p90_model = load_models()
    lookup = load_lookup()
    master = load_master()
    shap_df = load_shap()
    models_loaded = True
    load_error = None
except Exception as e:
    models_loaded = False
    load_error = str(e)
    lookup = pd.DataFrame()


# Build display name → key map directly from lookup
if not lookup.empty:
    DISPLAY_TO_KEY = {
        area_key.replace('-', ' ').title(): area_key
        for area_key in lookup['area_scraped'].tolist()
    }
    AREA_OPTIONS = sorted(DISPLAY_TO_KEY.keys())
else:
    DISPLAY_TO_KEY = {}
    AREA_OPTIONS = []


# Apply tier background
render_background(st.session_state.current_tier_key)


# Sidebar
with st.sidebar:
    st.markdown("## RentIQ Nigeria")
    st.markdown("<p style='color:#666; font-size:0.78rem; font-family:Space Mono; margin-top:-10px;'>Rental price intelligence</p>", unsafe_allow_html=True)
    st.markdown("---")

    if AREA_OPTIONS:
        area_display = st.selectbox("Area", AREA_OPTIONS)
        area_key = DISPLAY_TO_KEY[area_display]

        matched = lookup[lookup['area_scraped'] == area_key]
        if not matched.empty:
            new_tier = str(matched.iloc[0]['location_tier']).lower().strip()
            if new_tier != st.session_state.current_tier_key:
                st.session_state.current_tier_key = new_tier
                st.rerun()
    else:
        area_display = ""
        area_key = ""

    prop_type = st.radio("Property type", ["Flat / Apartment", "House / Duplex"], horizontal=True)
    type_house = 1 if "House" in prop_type else 0

    bedroom_label = st.selectbox("Bedrooms", list(BEDROOM_LABELS.keys()))
    bedrooms_encoded = BEDROOM_LABELS[bedroom_label]

    suggested_bathrooms = auto_bathrooms(bedrooms_encoded)
    bathrooms = st.number_input("Bathrooms", min_value=1, max_value=8, value=suggested_bathrooms, step=1)

    elec_hours = st.slider("Hours of electricity per day", min_value=0, max_value=24, value=16, step=1)
    st.caption(electricity_label(elec_hours))

    st.markdown("---")
    predict_clicked = st.button("Predict rent", use_container_width=True)


# Header with submission counter
header_col, counter_col = st.columns([3, 2])

with header_col:
    st.markdown("<h1 style='font-family:Space Mono; font-size:1.6rem; color:#c8f564; margin-bottom:2px;'>RentIQ Nigeria</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#777; font-size:0.82rem; margin-top:0;'>Annual rental price estimates for Lagos residential property</p>", unsafe_allow_html=True)

with counter_col:
    submission_count = get_submission_count()
    if submission_count > 0:
        st.markdown(f"""
        <div class='submission-counter'>
            <strong>{submission_count}</strong> real rents submitted by users
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


if not models_loaded:
    st.error(f"Could not load model files.\n\n{load_error}")
    st.stop()


# Run prediction
if predict_clicked:
    row = lookup[lookup['area_scraped'] == area_key]

    if row.empty:
        st.error(f"Area '{area_display}' not found in lookup table.")
        st.stop()

    row = row.iloc[0]

    features_dict = {
        'bedrooms_encoded':          bedrooms_encoded,
        'bathrooms':                 int(bathrooms),
        'type_house':                type_house,
        'tier_encoded':              float(row['tier_encoded']),
        'neighbourhood_median_rent': float(row['neighbourhood_median_rent']),
        'area_median_rent':          float(row['area_median_rent']),
        'tier_median_rent':          float(row['tier_median_rent']),
        'electricity_hours':         float(elec_hours),
        'latitude':                  float(row['latitude']),
        'longitude':                 float(row['longitude']),
        'dist_to_vi_km':             float(row['dist_to_vi_km']),
        'dist_to_ikeja_km':          float(row['dist_to_ikeja_km']),
        'tier_target_enc':           float(row['tier_target_enc']),
    }

    with st.spinner('Calculating...'):
        predicted, p10, p90 = predict_rent(ensemble, p10_model, p90_model, features_dict)

    st.session_state.prediction_done = True
    st.session_state.predicted = predicted
    st.session_state.p10 = p10
    st.session_state.p90 = p90
    st.session_state.price_tier_name = classify_price_tier(predicted)
    st.session_state.location_tier_display = str(row['location_tier']).replace('-', ' ').title()
    st.session_state.area_display = area_display
    st.session_state.area_key = area_key
    st.session_state.bedrooms_encoded = bedrooms_encoded
    st.session_state.elec_hours = elec_hours
    st.session_state.last_features = features_dict
    st.session_state.last_prop_type = prop_type
    st.session_state.last_bedrooms_label = bedroom_label
    st.session_state.last_bathrooms = int(bathrooms)


if not st.session_state.prediction_done:
    st.markdown("""
    <div style='margin-top:80px; text-align:center; color:#444;'>
        <p style='font-family:Space Mono; font-size:0.9rem;'>Select your property details in the sidebar and click <strong style='color:#c8f564;'>Predict rent</strong></p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()


# Result block
predicted = st.session_state.predicted
p10 = st.session_state.p10
p90 = st.session_state.p90
price_tier = st.session_state.price_tier_name

col_result, col_gap, col_fair = st.columns([5, 1, 4])

with col_result:
    st.markdown("<div class='section-label'>Predicted Annual Rent</div>", unsafe_allow_html=True)

    p10_safe = min(p10, predicted * 0.98)
    p90_safe = max(p90, predicted * 1.02)

    st.markdown(f"""
    <div class='metric-card'>
        <div class='rent-display'>{format_naira(predicted)}</div>
        <div class='rent-range'>Range: {format_naira(p10_safe)} to {format_naira(p90_safe)} &nbsp; <span style='font-size:0.7rem; color:#444;'>(80% confidence)</span></div>
        <div>
            <span class='tier-badge {TIER_CSS[price_tier]}'>{price_tier}</span>
            <span class='location-pill'>{st.session_state.location_tier_display}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class='warning-box'>
        Listings on the major Nigerian property sites usually show asking prices.
        Real Lagos rents come in 10 to 20 percent lower after negotiation, so adjust the number above accordingly.
    </div>
    """, unsafe_allow_html=True)

with col_fair:
    st.markdown("<div class='section-label'>Is this rent fair?</div>", unsafe_allow_html=True)

    st.markdown("<div class='metric-card'>", unsafe_allow_html=True)

    quoted_str = st.text_input(
        "Enter the rent you are being quoted (₦)",
        value="",
        key="quoted_input_str",
        placeholder="e.g. 2,500,000"
    )

    if quoted_str:
        formatted = format_with_commas(quoted_str)
        if formatted != quoted_str:
            st.markdown(f"<p style='font-size:0.78rem; color:#888; margin-top:-8px;'>Reading as: ₦{formatted}</p>", unsafe_allow_html=True)

    quoted = parse_naira_input(quoted_str)

    if quoted > 0:
        delta_pct = ((quoted - predicted) / predicted) * 100
        if abs(delta_pct) <= 10:
            verdict_class = "verdict-fair"
            verdict_text = "Fair"
            verdict_detail = f"Within {abs(delta_pct):.1f}% of our estimate"
        elif delta_pct > 10:
            verdict_class = "verdict-above"
            verdict_text = "Above market"
            verdict_detail = f"{delta_pct:.1f}% above our estimate. Negotiate."
        else:
            verdict_class = "verdict-below"
            verdict_text = "Below market"
            verdict_detail = f"{abs(delta_pct):.1f}% below our estimate. Good deal."

        st.markdown(f"""
        <div style='margin-top:10px;'>
            <span class='{verdict_class}'>{verdict_text}</span><br>
            <span style='color:#888; font-size:0.85rem;'>{verdict_detail}</span><br>
            <span style='color:#555; font-size:0.78rem; margin-top:8px; display:block; line-height:1.6;'>
                Our estimate: {format_naira(predicted)}<br>
                You were quoted: ₦{quoted:,}
            </span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


st.markdown("<br>", unsafe_allow_html=True)


# Tabs
tab1, tab2, tab3 = st.tabs(["What's pushing this price", "Similar listings", "Submit your real rent"])

with tab1:
    if shap_df is not None:
        # Use the actual top features in ranked order, collapsing tier-family
        seen_groups = set()
        rows_to_show = []
        sorted_shap = shap_df.sort_values('mean_abs_shap', ascending=False)

        for _, r in sorted_shap.iterrows():
            feat = r['feature']
            label = PLAIN_LABELS.get(feat, feat)
            if label in seen_groups:
                continue
            seen_groups.add(label)
            rows_to_show.append((label, r['mean_abs_shap']))
            if len(rows_to_show) == 6:
                break

        labels = [r[0] for r in rows_to_show]
        values = [r[1] for r in rows_to_show]
        total = sum(values)
        percentages = [v / total * 100 for v in values]

        fig, ax = plt.subplots(figsize=(8, 3.6))
        fig.patch.set_facecolor('none')
        ax.set_facecolor('none')

        colors = ['#c8f564' if v == max(values) else '#5a6e38' for v in values]
        bars = ax.barh(labels[::-1], values[::-1], color=colors[::-1], height=0.55)

        for i, (bar, pct) in enumerate(zip(bars, percentages[::-1])):
            width = bar.get_width()
            ax.text(width + max(values) * 0.02, bar.get_y() + bar.get_height()/2,
                    f'{pct:.0f}% of decision',
                    va='center', fontsize=9, color='#aaa', family='monospace')

        ax.set_xticks([])
        ax.tick_params(colors='#ccc', labelsize=10, length=0)
        for spine in ['top', 'right', 'bottom', 'left']:
            ax.spines[spine].set_visible(False)

        ax.set_xlim(0, max(values) * 1.25)

        plt.tight_layout()
        st.pyplot(fig, use_container_width=True)
        plt.close()

        elec_band = electricity_label(st.session_state.elec_hours)

        st.markdown(f"""
        <div class='driver-explain'>
            The biggest factor in your estimate is <strong>what rent typically looks like in {st.session_state.area_display}</strong>.
            After that, bedroom and bathroom count make the next biggest difference. Power supply matters too (this area is {elec_band}),
            since rents in Lagos quietly track electricity bands. Location plays a role as well, especially how close the area sits to Victoria Island.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("SHAP importance file not found.")


with tab2:
    if master is not None:
        bed_col = 'bedrooms_encoded' if 'bedrooms_encoded' in master.columns else 'bedrooms_enc'

        comps = master[
            (master['area_scraped'] == st.session_state.area_key) &
            (master[bed_col] == st.session_state.bedrooms_encoded)
        ].copy()

        if len(comps) == 0:
            comps = master[master['area_scraped'] == st.session_state.area_key].copy()

        comps = comps.sort_values('annual_rent_naira').head(8)

        if len(comps) > 0:
            display_cols = ['area_scraped', 'bedrooms', 'location_tier', 'annual_rent_naira']
            available = [c for c in display_cols if c in comps.columns]
            comp_display = comps[available].copy()

            if 'annual_rent_naira' in comp_display.columns:
                comp_display['annual_rent_naira'] = comp_display['annual_rent_naira'].apply(format_naira)

            rename_map = {
                'area_scraped': 'Area',
                'bedrooms': 'Bedrooms',
                'location_tier': 'Tier',
                'annual_rent_naira': 'Annual Rent',
            }
            comp_display = comp_display.rename(columns=rename_map)
            if 'Area' in comp_display.columns:
                comp_display['Area'] = comp_display['Area'].str.replace('-', ' ').str.title()
            if 'Tier' in comp_display.columns:
                comp_display['Tier'] = comp_display['Tier'].str.replace('-', ' ').str.title()

            st.dataframe(comp_display, use_container_width=True, hide_index=True)
            st.markdown(f"<p style='font-size:0.72rem; color:#555; margin-top:6px;'>Real listings pulled from the project dataset (NigeriaPropertyCentre and PropertyPro, 2025-2026).</p>", unsafe_allow_html=True)
        else:
            st.info(f"No similar listings in the dataset for {st.session_state.area_display}.")
    else:
        st.info("Master dataset not loaded. Comparable listings unavailable.")


with tab3:
    st.markdown("<div class='section-label'>Help improve the model</div>", unsafe_allow_html=True)

    st.markdown("""
    <p style='color:#aaa; font-size:0.9rem; line-height:1.6;'>
    If you actually live in <strong style='color:#c8f564;'>""" + st.session_state.area_display + """</strong> or you've recently rented somewhere in Lagos, share what you actually paid.
    Your submission is anonymous and helps the model learn from real transactions, not just listing asking prices.
    </p>
    """, unsafe_allow_html=True)

    with st.form("ground_truth_form", clear_on_submit=True):
        col_a, col_b = st.columns(2)

        with col_a:
            submit_area = st.selectbox(
                "Area",
                AREA_OPTIONS,
                index=AREA_OPTIONS.index(st.session_state.area_display) if st.session_state.area_display in AREA_OPTIONS else 0,
                key="submit_area"
            )
            submit_bedrooms = st.selectbox(
                "Bedrooms",
                list(BEDROOM_LABELS.keys()),
                index=list(BEDROOM_LABELS.keys()).index(st.session_state.last_bedrooms_label) if st.session_state.last_bedrooms_label else 2,
                key="submit_bedrooms"
            )
            submit_bathrooms = st.number_input(
                "Bathrooms", min_value=1, max_value=8,
                value=st.session_state.last_bathrooms if st.session_state.last_bathrooms else 2,
                key="submit_bathrooms"
            )

        with col_b:
            submit_prop_type = st.radio(
                "Property type",
                ["Flat / Apartment", "House / Duplex"],
                index=0 if st.session_state.last_prop_type == "Flat / Apartment" else 1,
                horizontal=True,
                key="submit_prop_type"
            )
            submit_elec = st.slider(
                "Hours of electricity per day",
                min_value=0, max_value=24,
                value=st.session_state.elec_hours if st.session_state.elec_hours else 16,
                key="submit_elec"
            )
            submit_year = st.number_input(
                "Year you paid this rent",
                min_value=2020, max_value=2026, value=2026,
                key="submit_year"
            )

        submit_rent_str = st.text_input(
            "What you actually paid (annual rent, ₦)",
            value="",
            placeholder="e.g. 1,500,000",
            key="submit_rent_str"
        )

        if submit_rent_str:
            formatted_submit = format_with_commas(submit_rent_str)
            if formatted_submit != submit_rent_str:
                st.markdown(f"<p style='font-size:0.78rem; color:#888; margin-top:-12px;'>Reading as: ₦{formatted_submit}</p>", unsafe_allow_html=True)

        submit_note = st.text_input(
            "Anything we should know? (optional)",
            value="",
            placeholder="e.g. fully furnished, security included, etc.",
            key="submit_note"
        )

        form_submit = st.form_submit_button("Submit anonymously")

        if form_submit:
            submit_rent_value = parse_naira_input(submit_rent_str)

            # Validation
            if submit_rent_value < 100_000:
                st.markdown("<div class='submit-error'>Rent below ₦100,000 looks like a typo. Please check and try again.</div>", unsafe_allow_html=True)
            elif submit_rent_value > 300_000_000:
                st.markdown("<div class='submit-error'>Rent above ₦300m looks unusual. Please check and try again.</div>", unsafe_allow_html=True)
            elif submit_area in st.session_state.submitted_areas:
                st.markdown("<div class='submit-error'>You've already submitted for this area in this session. Thank you for your contribution.</div>", unsafe_allow_html=True)
            else:
                try:
                    ws = get_gsheet_client()
                    if ws is None:
                        st.markdown("<div class='submit-error'>Submission service is not configured. Please try again later.</div>", unsafe_allow_html=True)
                    else:
                        submit_area_key = DISPLAY_TO_KEY.get(submit_area, submit_area.lower().replace(' ', '-'))
                        ws.append_row([
                            datetime.datetime.now().isoformat(),
                            submit_area_key,
                            str(BEDROOM_LABELS[submit_bedrooms]),
                            str(submit_bathrooms),
                            'house' if 'House' in submit_prop_type else 'flat',
                            str(submit_elec),
                            str(submit_rent_value),
                            str(submit_year),
                            submit_note,
                        ])
                        st.session_state.submitted_areas.add(submit_area)
                        # Bust the count cache
                        get_submission_count.clear() if hasattr(get_submission_count, 'clear') else None
                        st.markdown(f"<div class='submit-success'>Submitted. Thank you for contributing real rent data from {submit_area}.</div>", unsafe_allow_html=True)
                except Exception as e:
                    st.markdown(f"<div class='submit-error'>Could not submit: {str(e)[:100]}</div>", unsafe_allow_html=True)


# Footer
st.markdown("<br><hr>", unsafe_allow_html=True)
st.markdown("""
<p style='font-size:0.72rem; color:#444; font-family:Space Mono; line-height:1.6;'>
Built as part of Victory Ezeala's MSc Data Science dissertation at Pan-Atlantic University.
The model was trained on roughly 11,000 Lagos rental listings. These are estimates, not appraisals.
</p>
""", unsafe_allow_html=True)
