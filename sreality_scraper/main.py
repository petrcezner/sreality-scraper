import streamlit as st

from scraper import RealityScraper
from database import SrealityDatabase
from utils import init_logger

db = SrealityDatabase(database='sreality', user='sreality', password='sreality_postgres', host='database')
scraper = RealityScraper(db, max_advertising=500)

if 'scrape_page' not in st.session_state:
    logger = init_logger('__main__', True)
    st.session_state.scrape_page = False
if 'scrape_push' not in st.session_state:
    st.session_state.scrape_push = False

st.set_page_config(
    page_title="SReality Scraping App",
    layout="wide",
    initial_sidebar_state="auto",
)

st.markdown("<h1 style='text-align: center;'>SReality Scraping App</h1>", unsafe_allow_html=True)
values = st.sidebar.slider('Select Ads?', 0, 500, (0, 20))

def start_scraping():
    scraper()
    st.session_state.scrape_page = True


def write_to_col(col, advert):
    col.write(f'Property Price: **{advert.price}**')
    col.write(f'Living Area: **{advert.living_area}**')
    col.write(f'Deal type: **{advert.deal_type}**')
    col.write(f'Reality type: **{advert.reality_type}**')
    col.write(f'[Link]({advert.url}) to the Advertisement')


def show_db(data, offset):
    if st.sidebar.button('Close'):
        st.session_state.scrape_push = False
        st.session_state.scrape_page = False
        st.experimental_rerun()
    for i, ad in enumerate(data):
        cols = st.columns(4, gap='medium')
        cols[0].header(f'Property number: {offset + i}')
        if len(ad.images) == 2:
            cols[1].subheader(f'{ad.title}')
            cols[1].image(ad.images[0], use_column_width='auto')
            cols[2].subheader(f'{ad.location}')
            cols[2].image(ad.images[1], use_column_width='auto')
        elif len(ad.images) == 1:
            cols[1].subheader(f'{ad.title}')
            cols[1].image(ad.images[0], use_column_width='auto')
        else:
            cols[1].subheader(f'{ad.title}')
            cols[1].write(f'There are no images.')
        write_to_col(cols[3], ad)


st.sidebar.title("Setup")

if st.sidebar.button('Scrape Web') and not st.session_state.scrape_page:
    with st.spinner('Please wait till the web is scrape'):
        st.session_state.scrape_push = True
        start_scraping()
    st.success('Web scraped!')

if st.session_state.scrape_push and st.session_state.scrape_page:
    data = db.get_data(how_many=500)
    show_db(data[values[0]:values[1]], values[0])

if not st.session_state.scrape_push:
    if st.sidebar.button('Show Database'):
        data = db.get_data(how_many=500)
        show_db(data[values[0]:values[1]], values[0])
