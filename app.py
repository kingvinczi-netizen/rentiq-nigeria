import streamlit as st
import pandas as pd
import numpy as np
import pickle
import os
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

st.set_page_config(
    page_title="RentIQ Nigeria",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;600;700&family=Space+Mono:wght@400;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Sora', sans-serif;
}

.stApp {
    background-color: #0d0d0d;
    color: #f0ede6;
}

section[data-testid="stSidebar"] {
    background-color: #141414;
    border-right: 1px solid #2a2a2a;
}

section[data-testid="stSidebar"] * {
    color: #f0ede6 !important;
}

.rent-display {
    font-family: 'Space Mono', monospace;
    font-size: 3.2rem;
    font-weight: 700;
    color: #c8f564;
    letter-spacing: -1px;
    line-height: 1.1;
}

.rent-range {
    font-family: 'Space Mono', monospace;
    font-size: 1.05rem;
    color: #888;
    margin-top: 6px;
}

.tier-badge {
    display: inline-block;
    padding: 4px 14px;
    border-radius: 4px;
    font-family: 'Space Mono', monospace;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-top: 10px;
}

.tier-budget    { background: #1a2e1a; color: #6fcf6f; border: 1px solid #3a5e3a; }
.tier-midrange  { background: #2e2a14; color: #f0c040; border: 1px solid #5e521a; }
.tier-premium   { background: #2a1e14; color: #f09060; border: 1px solid #5e3a20; }
.tier-luxury    { background: #1e1430; color: #b090f0; border: 1px solid #3a2060; }

.location-pill {
    display: inline-block;
    padding: 3px 12px;
    border-radius: 20px;
    font-size: 0.72rem;
    font-family: 'Space Mono', monospace;
    letter-spacing: 0.5px;
    background: #1e1e1e;
    border: 1px solid #333;
    color: #aaa;
    margin-left: 10px;
    vertical-align: middle;
}

.verdict-fair    { color: #6fcf6f; font-weight: 700; font-size: 1.3rem; }
.verdict-above   { color: #f09060; font-weight: 700; font-size: 1.3rem; }
.verdict-below   { color: #b090f0; font-weight: 700; font-size: 1.3rem; }

.metric-card {
    background: #1a1a1a;
    border: 1px solid #2a2a2a;
    border-radius: 8px;
    padding: 18px 22px;
    margin-bottom: 12px;
}

.section-label {
    font-size: 0.68rem;
    font-family: 'Space Mono', monospace;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #555;
    margin-bottom: 14px;
}

.comp-table th {
    background: #1a1a1a;
    color: #888;
    font-size: 0.72rem;
    font-family: 'Space Mono', monospace;
    letter-spacing: 1px;
    text-transform: uppercase;
    padding: 8px 12px;
    border-bottom: 1px solid #2a2a2a;
}

.comp-table td {
    padding: 8px 12px;
    font-size: 0.85rem;
    border-bottom: 1px solid #1e1e1e;
    color: #ccc;
}

.comp-table tr:last-child td { border-bottom: none; }

div[data-testid="stTabs"] button {
    font-family: 'Space Mono', monospace;
    font-size: 0.75rem;
    letter-spacing: 1px;
}

.stSlider > div > div > div { background: #c8f564 !important; }

hr { border-color: #2a2a2a; }

.stButton > button {
    background: #c8f564;
    color: #0d0d0d;
    font-family: 'Space Mono', monospace;
    font-weight: 700;
    font-size: 0.8rem;
    letter-spacing: 1px;
    border: none;
    border-radius: 4px;
    padding: 10px 24px;
}

.stButton > button:hover {
    background: #d4f97a;
    color: #0d0d0d;
}

.warning-box {
    background: #1e1a10;
    border: 1px solid #4a3a10;
    border-radius: 6px;
    padding: 12px 16px;
    font-size: 0.82rem;
    color: #c8a840;
    margin-top: 12px;
}

h1, h2, h3 { color: #f0ede6; }
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

SHAP_LABELS = {
    'neighbourhood_median_rent': 'Area price level',
    'bedrooms_encoded':          'Bedroom count',
    'area_median_rent':          'Area median rent',
    'bathrooms':                 'Bathroom count',
    'dist_to_vi_km':             'Distance to VI',
    'type_house':                'Property type',
    'longitude':                 'Location (East-West)',
    'latitude':                  'Location (North-South)',
    'tier_encoded':              'Location tier',
    'tier_target_enc':           'Tier rent level',
    'electricity_hours':         'Electricity supply',
    'dist_to_ikeja_km':          'Distance to Ikeja',
    'tier_median_rent':          'Tier median rent',
}


def get_artifacts_path():
    """Try Drive path first, fall back to local ./artifacts/"""
    drive_path = '/content/drive/MyDrive/RentIQ Nigeria/model/artifacts'
    if os.path.exists(drive_path):
        return drive_path
    local_path = os.path.join(os.path.dirname(__file__), 'artifacts')
    return local_path


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
    local_path = os.path.join(os.path.dirname(__file__), 'data', 'rentiq_master.csv')
    if os.path.exists(drive_path):
        return pd.read_csv(drive_path)
    elif os.path.exists(local_path):
        return pd.read_csv(local_path)
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


# --- Load everything ---
try:
    ensemble, p10_model, p90_model = load_models()
    lookup = load_lookup()
    master = load_master()
    shap_df = load_shap()
    models_loaded = True
except Exception as e:
    models_loaded = False
    load_error = str(e)


# --- Sidebar ---
with st.sidebar:
    st.markdown("## RentIQ Nigeria")
    st.markdown("<p style='color:#555; font-size:0.8rem; font-family:Space Mono; margin-top:-10px;'>Rental price intelligence</p>", unsafe_allow_html=True)
    st.markdown("---")

    area_options = sorted(lookup['area_scraped'].str.replace('-', ' ').str.title().tolist())
    area_display = st.selectbox("Area", area_options)
    area_key = area_display.lower().replace(' ', '-')

    prop_type = st.radio("Property type", ["Flat / Apartment", "House / Duplex"], horizontal=True)
    type_house = 1 if "House" in prop_type else 0

    bedroom_label = st.selectbox("Bedrooms", list(BEDROOM_LABELS.keys()))
    bedrooms_encoded = BEDROOM_LABELS[bedroom_label]

    bathrooms = st.number_input("Bathrooms", min_value=1, max_value=8, value=2, step=1)

    elec_hours = st.slider("Hours of electricity per day", min_value=0, max_value=24, value=16, step=1)
    st.caption(electricity_label(elec_hours))

    st.markdown("---")
    predict_clicked = st.button("Predict rent", use_container_width=True)


# --- Main panel ---
st.markdown("<h1 style='font-family:Space Mono; font-size:1.6rem; color:#c8f564; margin-bottom:2px;'>RentIQ Nigeria</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#555; font-size:0.82rem; margin-top:0; margin-bottom:24px;'>Annual rental price intelligence for Lagos residential property</p>", unsafe_allow_html=True)

if not models_loaded:
    st.error(f"Could not load model files. Check that all pkl files are in the artifacts folder.\n\n{load_error}")
    st.stop()

if not predict_clicked:
    st.markdown("""
    <div style='margin-top:60px; text-align:center; color:#333;'>
        <p style='font-family:Space Mono; font-size:0.9rem;'>Select your property details in the sidebar and click <strong style='color:#c8f564;'>Predict rent</strong></p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()


# --- Inference ---
row = lookup[lookup['area_scraped'] == area_key]

if row.empty:
    st.error(f"Area '{area_display}' not found in lookup table. Check the area_scraped values match exactly.")
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
price_tier = classify_price_tier(predicted)
location_tier_display = str(row['location_tier']).replace('-', ' ').title()


# --- Result block ---
col_result, col_gap, col_fair = st.columns([5, 1, 4])

with col_result:
    st.markdown("<div class='section-label'>Predicted Annual Rent</div>", unsafe_allow_html=True)

    p10_safe = min(p10, predicted * 0.98)
    p90_safe = max(p90, predicted * 1.02)

    st.markdown(f"""
    <div class='metric-card'>
        <div class='rent-display'>{format_naira(predicted)}</div>
        <div class='rent-range'>Range: {format_naira(p10_safe)} — {format_naira(p90_safe)} &nbsp; <span style='font-size:0.7rem; color:#444;'>(80% confidence)</span></div>
        <div>
            <span class='tier-badge {TIER_CSS[price_tier]}'>{price_tier}</span>
            <span class='location-pill'>{location_tier_display}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class='warning-box'>
        NPC listings skew toward asking prices. Actual transacted rents in Lagos are typically
        10-20% lower after negotiation. Adjust accordingly.
    </div>
    """, unsafe_allow_html=True)

with col_fair:
    st.markdown("<div class='section-label'>Is this rent fair?</div>", unsafe_allow_html=True)
    st.markdown("<div class='metric-card'>", unsafe_allow_html=True)

    quoted = st.number_input(
        "Quoted annual rent (₦)",
        min_value=0,
        value=0,
        step=100_000,
        format="%d",
        help="Enter the rent you are being asked to pay"
    )

    if quoted > 0:
        delta_pct = ((quoted - predicted) / predicted) * 100
        if abs(delta_pct) <= 10:
            verdict_class = "verdict-fair"
            verdict_text = "Fair"
            verdict_detail = f"{abs(delta_pct):.1f}% within market estimate"
        elif delta_pct > 10:
            verdict_class = "verdict-above"
            verdict_text = "Above market"
            verdict_detail = f"{delta_pct:.1f}% above model estimate"
        else:
            verdict_class = "verdict-below"
            verdict_text = "Below market"
            verdict_detail = f"{abs(delta_pct):.1f}% below model estimate — good deal"

        st.markdown(f"""
        <div style='margin-top:8px;'>
            <span class='{verdict_class}'>{verdict_text}</span><br>
            <span style='color:#666; font-size:0.82rem;'>{verdict_detail}</span><br>
            <span style='color:#444; font-size:0.78rem; margin-top:6px; display:block;'>
                Model estimate: {format_naira(predicted)}<br>
                Quoted: {format_naira(quoted)}
            </span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("<p style='color:#444; font-size:0.82rem;'>Enter the rent you are being quoted above</p>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


st.markdown("<br>", unsafe_allow_html=True)


# --- Tabs ---
tab1, tab2 = st.tabs(["What's driving this price", "Comparable listings"])

with tab1:
    st.markdown("<div class='section-label'>Feature attribution</div>", unsafe_allow_html=True)

    if shap_df is not None:
        top_features = shap_df.head(6).copy()
        top_features['label'] = top_features.iloc[:, 0].map(SHAP_LABELS).fillna(top_features.iloc[:, 0])
        shap_values = top_features.iloc[:, 1].values

        fig, ax = plt.subplots(figsize=(7, 3.2))
        fig.patch.set_facecolor('#1a1a1a')
        ax.set_facecolor('#1a1a1a')

        colors = ['#c8f564' if v == max(shap_values) else '#3a4a20' for v in shap_values]
        bars = ax.barh(top_features['label'][::-1], shap_values[::-1], color=colors[::-1], height=0.55)

        ax.set_xlabel('Mean |SHAP value|', color='#555', fontsize=8)
        ax.tick_params(colors='#888', labelsize=8)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_color('#2a2a2a')
        ax.spines['left'].set_color('#2a2a2a')
        ax.xaxis.label.set_color('#555')

        plt.tight_layout()
        st.pyplot(fig, use_container_width=True)
        plt.close()

        st.markdown(f"""
        <p style='font-size:0.78rem; color:#555; margin-top:8px;'>
        <strong style='color:#888;'>Area price level</strong> is the dominant driver of rent in Lagos —
        neighbourhood location accounts for the largest share of model variance.
        Electricity supply ({electricity_label(elec_hours)}) is included as a pricing factor,
        reflecting NERC band classifications across Lagos areas.
        </p>
        """, unsafe_allow_html=True)
    else:
        st.info("SHAP importance file not found in artifacts folder. Add shap_importance_advanced.csv to model/artifacts/.")


with tab2:
    st.markdown("<div class='section-label'>Similar listings in dataset</div>", unsafe_allow_html=True)

    if master is not None:
        bed_col = 'bedrooms_encoded' if 'bedrooms_encoded' in master.columns else 'bedrooms_enc'

        comps = master[
            (master['area_scraped'] == area_key) &
            (master[bed_col] == bedrooms_encoded)
        ].copy()

        if len(comps) == 0:
            comps = master[master['area_scraped'] == area_key].copy()

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
            comp_display['Area'] = comp_display['Area'].str.replace('-', ' ').str.title()

            st.dataframe(
                comp_display,
                use_container_width=True,
                hide_index=True,
            )
            st.markdown(f"<p style='font-size:0.72rem; color:#444; margin-top:4px;'>Showing {len(comp_display)} listings from the RentIQ Nigeria dataset — NigeriaPropertyCentre & PropertyPro, scraped 2025-2026.</p>", unsafe_allow_html=True)
        else:
            st.info("No comparable listings found for this area and bedroom combination.")
    else:
        st.info("rentiq_master.csv not found. Comparable listings unavailable in this deployment.")


# --- Footer ---
st.markdown("---")
st.markdown("""
<p style='font-size:0.7rem; color:#333; font-family:Space Mono;'>
RentIQ Nigeria — MSc Data Science dissertation project, Pan-Atlantic University.
Model trained on 10,999 Lagos rental listings. Predictions are estimates only.
</p>
""", unsafe_allow_html=True)
