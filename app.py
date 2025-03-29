import streamlit as st
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="Wine List",
    page_icon="🍷",
    layout="wide"
)

# Custom CSS to match the design in the screenshot
st.markdown("""
<style>
    .main {
        background-color: #2b4055;
        color: white;
    }
    .block-container {
        padding-top: 1rem;
        padding-bottom: 0rem;
        max-width: 1200px;
    }
    h1, h2, h3 {
        color: white;
    }
    .big-format {
        font-size: 2.5rem;
        font-weight: 500;
        margin-bottom: 2rem;
        color: white;
    }
    .country-header {
        font-size: 2rem;
        font-style: italic;
        margin-top: 2rem;
        margin-bottom: 1rem;
        color: white;
    }
    .region-header {
        font-size: 1.5rem;
        font-weight: 500;
        margin-top: 1.5rem;
        margin-bottom: 0.5rem;
        text-decoration: underline;
        color: white;
    }
    .producer {
        font-size: 1.2rem;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
        color: white;
    }
    .wine-entry {
        margin-left: 1rem;
        margin-bottom: 0.5rem;
        color: white;
        display: flex;
        justify-content: space-between;
    }
    .wine-info {
        flex-grow: 1;
    }
    .wine-price {
        min-width: 60px;
        text-align: right;
    }
    .grape-variety {
        font-style: italic;
        color: white;
    }
    .wine-divider {
        border-bottom: 1px dotted rgba(255, 255, 255, 0.3);
        flex-grow: 1;
        margin: 0 10px;
        position: relative;
        top: -5px;
    }
    .sidebar .css-1d391kg {
        background-color: #1e2e42;
    }
    .sidebar .stCheckbox label {
        color: white;
    }
    .sidebar .stSelectbox label {
        color: white;
    }
    .sidebar .stMultiselect label {
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Function to load data from Google Sheets
@st.cache_data(ttl=600)
def load_data(sheet_url):
    csv_url = sheet_url.replace('/edit#gid=', '/export?format=csv&gid=')
    return pd.read_csv(csv_url)

# URL of your Google Sheet
sheet_url = "https://docs.google.com/spreadsheets/d/1hEqvhRM6qnflV_fkqHq5jf2fDXHuDFDZCv53HYPBQeI/edit#gid=0"

# Load data
try:
    df = load_data(sheet_url)
    # Ensure numeric price
    df['Salgspris'] = pd.to_numeric(df['Salgspris'], errors='coerce')
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# Sidebar for filters
with st.sidebar:
    st.markdown("# Filters")
    
    # Countries filter
    countries = sorted(df['Land'].unique())
    selected_countries = st.multiselect(
        "COUNTRIES",
        countries,
        default=[]
    )
    
    # Regions filter (dependent on country selection)
    if selected_countries:
        regions = sorted(df[df['Land'].isin(selected_countries)]['Region'].unique())
    else:
        regions = sorted(df['Region'].unique())
    
    selected_regions = st.multiselect(
        "REGIONS",
        regions,
        default=[]
    )
    
    # Producers filter (dependent on region selection)
    if selected_regions:
        producers = sorted(df[df['Region'].isin(selected_regions)]['Producent'].unique())
    elif selected_countries:
        producers = sorted(df[df['Land'].isin(selected_countries)]['Producent'].unique())
    else:
        producers = sorted(df['Producent'].unique())
    
    selected_producers = st.multiselect(
        "PRODUCERS",
        producers,
        default=[]
    )
    
    # Year filter
    years = sorted(df['Årgang'].unique(), reverse=True)
    selected_years = st.multiselect(
        "YEAR",
        years,
        default=[]
    )
    
    # Price range filter
    st.markdown("### PRICE")
    price_ranges = ["< 600:-", "600 - 799:-", "800 - 999:-", "> 1000:-"]
    selected_price_ranges = []
    
    col1, col2 = st.columns(2)
    with col1:
        if st.checkbox("< 600:-"):
            selected_price_ranges.append("< 600:-")
        if st.checkbox("800 - 999:-"):
            selected_price_ranges.append("800 - 999:-")
    
    with col2:
        if st.checkbox("600 - 799:-"):
            selected_price_ranges.append("600 - 799:-")
        if st.checkbox("> 1000:-"):
            selected_price_ranges.append("> 1000:-")
    
    # Grapes filter
    all_grapes = []
    for grapes in df['Drue(r)'].dropna().unique():
        if isinstance(grapes, str):
            grape_list = [g.strip() for g in grapes.split(',')]
            all_grapes.extend(grape_list)
    
    unique_grapes = sorted(list(set(all_grapes)))
    
    selected_grapes = st.multiselect(
        "GRAPES",
        unique_grapes,
        default=[]
    )
    
    # Size filter (for Magnums)
    sizes = sorted(df['Størrelse'].unique())
    selected_sizes = st.multiselect(
        "SIZE",
        sizes,
        default=[]
    )
    
    # Wine type filter
    wine_types = sorted(df['Type'].unique())
    selected_types = st.multiselect(
        "TYPE",
        wine_types,
        default=[]
    )

# Apply filters to dataframe
filtered_df = df.copy()

if selected_countries:
    filtered_df = filtered_df[filtered_df['Land'].isin(selected_countries)]

if selected_regions:
    filtered_df = filtered_df[filtered_df['Region'].isin(selected_regions)]

if selected_producers:
    filtered_df = filtered_df[filtered_df['Producent'].isin(selected_producers)]

if selected_years:
    filtered_df = filtered_df[filtered_df['Årgang'].isin(selected_years)]

if selected_grapes:
    filtered_df = filtered_df[filtered_df['Drue(r)'].apply(
        lambda x: any(grape in str(x).split(',') for grape in selected_grapes) if pd.notna(x) else False
    )]

if selected_sizes:
    filtered_df = filtered_df[filtered_df['Størrelse'].isin(selected_sizes)]

if selected_types:
    filtered_df = filtered_df[filtered_df['Type'].isin(selected_types)]

# Price filtering logic
if selected_price_ranges:
    price_filter = pd.Series(False, index=filtered_df.index)
    for price_range in selected_price_ranges:
        if price_range == "< 600:-":
            price_filter = price_filter | (filtered_df['Salgspris'] < 600)
        elif price_range == "600 - 799:-":
            price_filter = price_filter | ((filtered_df['Salgspris'] >= 600) & (filtered_df['Salgspris'] <= 799))
        elif price_range == "800 - 999:-":
            price_filter = price_filter | ((filtered_df['Salgspris'] >= 800) & (filtered_df['Salgspris'] <= 999))
        elif price_range == "> 1000:-":
            price_filter = price_filter | (filtered_df['Salgspris'] > 1000)
    
    filtered_df = filtered_df[price_filter]

# Main display area
st.markdown('<div class="big-format">Big Format</div>', unsafe_allow_html=True)

# Group by Country, Region, Producer
countries = filtered_df['Land'].unique()

if len(filtered_df) == 0:
    st.info("No wines match your selected filters. Try adjusting your criteria.")

for country in countries:
    st.markdown(f'<div class="country-header">{country}</div>', unsafe_allow_html=True)
    
    country_df = filtered_df[filtered_df['Land'] == country]
    regions = country_df['Region'].unique()
    
    for region in regions:
        st.markdown(f'<div class="region-header">{region}</div>', unsafe_allow_html=True)
        
        region_df = country_df[country_df['Region'] == region]
        producers = region_df['Producent'].unique()
        
        for producer in producers:
            st.markdown(f'<div class="producer">{producer}</div>', unsafe_allow_html=True)
            
            producer_df = region_df[region_df['Producent'] == producer]
            
            for _, wine in producer_df.iterrows():
                wine_name = wine['Navn']
                year = wine['Årgang'] if pd.notna(wine['Årgang']) else ""
                grapes = wine['Drue(r)'] if pd.notna(wine['Drue(r)']) else ""
                price = int(wine['Salgspris']) if pd.notna(wine['Salgspris']) else ""
                size = wine['Størrelse'] if pd.notna(wine['Størrelse']) else "MGM"  # Default to MGM if empty
                
                wine_html = f"""
                <div class="wine-entry">
                    <div class="wine-info">
                        {year}, {wine_name}, <span class="grape-variety">{grapes}</span>, {size}
                    </div>
                    <span class="wine-divider"></span>
                    <div class="wine-price">{price}</div>
                </div>
                """
                st.markdown(wine_html, unsafe_allow_html=True)
            
            # Add some space after each producer
            st.markdown("<br>", unsafe_allow_html=True)
