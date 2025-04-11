# components/sidebar.py
import streamlit as st
import streamlit.components.v1 as components

def render_sidebar(game_name_mapping=None):
    # All calls explicitly use st.sidebar.
    st.sidebar.image("logo.png", use_container_width=True)
    
    selected_game = None
    if game_name_mapping:
        selected_game = st.sidebar.selectbox("Select a game", list(game_name_mapping.keys()))
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("🎯 **Support The Model**")
    st.sidebar.markdown("💖 [Become a Patron](https://www.patreon.com/The_Model)")
    st.sidebar.markdown("☕️ [Buy me a coffee](https://www.buymeacoffee.com/aflmodel)")
    st.sidebar.markdown("---")
    st.sidebar.markdown("📬 **Stay in touch**")
    st.sidebar.caption("Join the mailing list to get notified when each round goes live.")
    components.iframe(
        "https://tally.so/embed/3E6VNo?alignLeft=1&hideTitle=1&hideDescription=1&transparentBackground=1&dynamicHeight=1",
        height=130,
        scrolling=False
    )
    
    # Spacer to push the navigation element toward the bottom.
    st.sidebar.markdown("<br><br><br>", unsafe_allow_html=True)
    
    # Instead of a markdown link, use a button to change pages.
    if st.sidebar.button("🧮 EV Calculator"):
        # Set the query parameter for page navigation and rerun.
        st.experimental_set_query_params(page="EV_Calculator")
        st.experimental_rerun()
    
    return selected_game
