import streamlit as st
import streamlit.components.v1 as components

def render_sidebar(game_name_mapping=None):
    st.image("logo.png", use_container_width=True)


    # If game dropdown is needed (on AFL Dashboard page)
    selected_game = None
    if game_name_mapping:
        selected_game = st.selectbox("Select a game", list(game_name_mapping.keys()))

    st.markdown("---")
    st.markdown("🎯 **Support The Model**")
    st.markdown("💖 [Become a Patron](https://www.patreon.com/The_Model)")
    st.markdown("☕️ [Buy me a coffee](https://www.buymeacoffee.com/aflmodel)")

    st.markdown("---")
    st.markdown("📬 **Stay in touch**")
    st.caption("Join the mailing list to get notified when each round goes live.")
    components.iframe(
        "https://tally.so/embed/3E6VNo?alignLeft=1&hideTitle=1&hideDescription=1&transparentBackground=1&dynamicHeight=1",
        height=130,
        scrolling=False
    )

    st.markdown("---")
    st.markdown("🧮 [EV Calculator](./EV_Calculator)")

    return selected_game  # Will return None in pages like EV Calculator
