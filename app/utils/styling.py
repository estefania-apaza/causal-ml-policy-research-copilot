import streamlit as st

def apply_custom_styling():
    """
    Applies a professional white background aesthetic with soft pink accents.
    """
    custom_css = """
    <style>
        /* Main background color - Pure White */
        .stApp {
            background-color: #FFFFFF;
        }
        
        /* Headers */
        h1, h2, h3, h4, h5, h6 {
            color: #d1495b !important;
            font-family: 'Inter', 'Helvetica Neue', sans-serif;
            font-weight: 600;
        }

        /* Sidebar styling - Light Gray/Pink tint */
        [data-testid="stSidebar"] {
            background-color: #FAFAFA;
            border-right: 1px solid #F0F0F0;
        }
        
        [data-testid="stSidebar"] * {
            color: #444444 !important;
        }
        
        /* Buttons - Keeping the pink look but slightly more refined */
        .stButton > button {
            background-color: #ffb6c1 !important; /* Light Pink */
            color: #FFFFFF !important;
            border-radius: 8px;
            border: none;
            padding: 0.5rem 1rem;
            transition: all 0.2s ease;
            font-weight: 600;
        }
        
        .stButton > button:hover {
            background-color: #ff8fa3 !important; /* Slightly darker pink */
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        
        /* Chat Input */
        .stChatInputContainer {
            background-color: #FFFFFF;
            border-radius: 12px;
            border: 1px solid #E0E0E0 !important;
        }

        /* Expander/Cards */
        .streamlit-expanderHeader {
            background-color: #fdf2f4;
            border-radius: 8px;
            color: #5c3c43;
            border: 1px solid #fee2e6;
        }
        
        /* Metrics */
        [data-testid="stMetricValue"] {
            color: #d1495b !important;
            font-weight: 700;
        }
        
        /* Dataframes */
        .stDataFrame {
            border-radius: 8px;
            overflow: hidden;
        }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)
