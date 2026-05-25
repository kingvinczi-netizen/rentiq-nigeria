import streamlit as st
import pandas as pd
import numpy as np
import pickle
import os
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="RentIQ Nigeria",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Tier-to-image mapping (Unsplash free-use, no attribution required)
TIER_BACKGROUNDS = {
    'island':           'https://images.unsplash.com/photo-1668010023661-89c9bea88ade?w=1920&q=80',
    'gra':              'https://images.unsplash.com/photo-1580500550469-4f0baa4a2da3?w=1920&q=80',
    'upscale-mainland': 'https://images.unsplash.com/photo-1580500550469-4f0baa4a2da3?w=1920&q=80',
    'mainland':         'https://images.unsplash.com/photo-1606298855672-3efb63017be8?w=1920&q=80',
    'suburb':           'https://images.unsplash.com/photo-1606298855672-3efb63017be8?w=1920&q=80',
    'outskirt':         'https://images.unsplash.com/photo-1568395216634-3acdca9eaf30?w=1920&q=80',
    'unknown':          'https://images.unsplash.com/photo-1606298855672-3efb63017be8?w=1920&q=80',
}


def render_background(tier_key):
    img_url = TIER_BACKGROUNDS.get(tier_key, TIER_BACKGROUNDS['mainland'])
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;600;700&family=Space+Mono:wght@400;700&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Sora', sans-serif;
    }}

    .stApp {{
        background-image:
            linear-gradient(rgba(10, 10, 10, 0.92), rgba(10, 10, 10, 0.96)),
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
        background: rgba(20, 20, 20, 0.7);
        border-left: 3px solid #c8f564;
        padding: 14px 18px;
        margin-top: 12px;
        border-radius: 4px;
        font-size: 0.88rem;
        color: #bbb;
        line-height: 1.55;
    }}

    .driver-explain strong {{ color: #c8f564; }}

    .stNumberInput label {{ font-size: 0.85rem; color: #aaa !important; }}
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

PLAIN_LABELS = {
    'neighbourhood_median_rent': 'What the area normally costs',
    'area_median_rent':          'Average rent in the area',
    'bedrooms_encoded':          'Number of bedrooms',
    'bathrooms':                 'Number of bathrooms',
    'tier_median_rent':          'Where this area ranks',
    'tier_encoded':              'Where this area ranks',
    'tier_target_enc':           'Where this area ranks',
    'electricity_hours':         'Electricity supply',
    'dist_to_vi_km':             'Distance to Victoria Island',
    'dist_to_ikeja_km':          'Distance to Ikeja',
    'type_house':                'Type of property',
    'longitude':                 'Location on the map',
    'latitude':                  'Location on the map',
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
    drive_path = '/content/drive/MyDrive/RentIQ Nigeria/data/processed/rentiq_master.csv'
    local_paths = [
        os.path.join(os.path.dirname(__file__), 'data', 'rentiq_master.csv'),
        os.path.join(os.path.dirname(__file__), 'rentiq_master.csv'),
    ]
    if os.path.exists(drive_path):
        return pd.read_csv(drive_path)
    for lp in local_paths:
        if os.path.exists(lp):
            return pd.read_csv(lp)
    return None


@st.cache_data(show_spinner=False)
def load_shap():
    path = get_artifacts_path()
    shap_path = f'{path}/shap_importance_advanced.csv'
    if os.path.exists(shap_path):
        return pd.read_csv(shap_path)
    return None


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


# Apply tier background
render_background(st.session_state.current_tier_key)


# Sidebar
with st.sidebar:
    st.markdown("## RentIQ Nigeria")
    st.markdown("<p style='color:#666; font-size:0.78rem; font-family:Space Mono; margin-top:-10px;'>Rental price intelligence</p>", unsafe_allow_html=True)
    st.markdown("---")

    if not lookup.empty:
        area_options = sorted(lookup['area_scraped'].str.replace('-', ' ').str.title().tolist())
        area_display = st.selectbox("Area", area_options)
        area_key = area_display.lower().replace(' ', '-')

        # Update tier key for background as soon as area changes
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

    bathrooms = st.number_input("Bathrooms", min_value=1, max_value=8, value=2, step=1)

    elec_hours = st.slider("Hours of electricity per day", min_value=0, max_value=24, value=16, step=1)
    st.caption(electricity_label(elec_hours))

    st.markdown("---")
    predict_clicked = st.button("Predict rent", use_container_width=True)


# Main panel header
st.markdown("<h1 style='font-family:Space Mono; font-size:1.6rem; color:#c8f564; margin-bottom:2px;'>RentIQ Nigeria</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#777; font-size:0.82rem; margin-top:0; margin-bottom:24px;'>Annual rental price estimates for Lagos residential property</p>", unsafe_allow_html=True)

if not models_loaded:
    st.error(f"Could not load model files. Check that all pkl files are in the artifacts folder.\n\n{load_error}")
    st.stop()


# Run prediction when button is clicked, save results to session_state
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


# Placeholder if nothing predicted yet
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

    quoted = st.number_input(
        "Enter the rent you are being quoted (₦)",
        min_value=0,
        value=0,
        step=100_000,
        format="%d",
        key="quoted_input"
    )

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
                You were quoted: {format_naira(quoted)}
            </span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


st.markdown("<br>", unsafe_allow_html=True)


# Tabs
tab1, tab2 = st.tabs(["What's pushing this price", "Similar listings"])

with tab1:
    if shap_df is not None:
        # Pick top 5 unique features after collapsing tier-* family
        seen_groups = set()
        rows_to_show = []
        for _, r in shap_df.iterrows():
            feat = r.iloc[0]
            label = PLAIN_LABELS.get(feat, feat)
            if label == 'Where this area ranks' and label in seen_groups:
                continue
            if label == 'Location on the map' and label in seen_groups:
                continue
            seen_groups.add(label)
            rows_to_show.append((label, r.iloc[1]))
            if len(rows_to_show) == 5:
                break

        labels = [r[0] for r in rows_to_show]
        values = [r[1] for r in rows_to_show]

        fig, ax = plt.subplots(figsize=(7.5, 3.4))
        fig.patch.set_facecolor('none')
        ax.set_facecolor('none')

        colors = ['#c8f564' if v == max(values) else '#4a5e28' for v in values]
        ax.barh(labels[::-1], values[::-1], color=colors[::-1], height=0.55)

        ax.set_xticks([])
        ax.tick_params(colors='#bbb', labelsize=10, length=0)
        for spine in ['top', 'right', 'bottom', 'left']:
            ax.spines[spine].set_visible(False)

        plt.tight_layout()
        st.pyplot(fig, use_container_width=True)
        plt.close()

        elec_band = electricity_label(st.session_state.elec_hours)

        st.markdown(f"""
        <div class='driver-explain'>
            The biggest factor in your estimate is <strong>what rent typically looks like in {st.session_state.area_display}</strong>.
            After that, bedroom and bathroom count make the next biggest difference. Power supply (this area is {elec_band})
            is part of the calculation too, since Lagos rents quietly track electricity bands. Location plays a role as well:
            how close the area sits to Victoria Island and Ikeja both feed into the final number.
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

            st.dataframe(
                comp_display,
                use_container_width=True,
                hide_index=True,
            )
            st.markdown(f"<p style='font-size:0.72rem; color:#555; margin-top:6px;'>Real listings pulled from the project dataset (NigeriaPropertyCentre and PropertyPro, 2025-2026).</p>", unsafe_allow_html=True)
        else:
            st.info(f"No similar listings in the dataset for {st.session_state.area_display}.")
    else:
        st.info("Master dataset not loaded. Comparable listings unavailable.")


# Footer
st.markdown("<br><hr>", unsafe_allow_html=True)
st.markdown("""
<p style='font-size:0.72rem; color:#444; font-family:Space Mono; line-height:1.6;'>
Built as part of Victory Ezeala's MSc Data Science dissertation at Pan-Atlantic University.
The model was trained on roughly 11,000 Lagos rental listings. These are estimates, not appraisals.
</p>
""", unsafe_allow_html=True)
