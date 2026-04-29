import streamlit as st

def render_sidebar():

    if "session" not in st.session_state:

        with st.sidebar:

            st.info("No session loaded")

        return False
    
    session = st.session_state["session"]
    drivers = session.laps["Driver"].unique()

    with st.sidebar:
        
        st.subheader("Current Session")

        st.write(f"**Season:- **{st.session_state["year"]}")
        st.write(f"**Grand Prix:- **{st.session_state["gp"]}")
        st.write(f"**Session:- **{st.session_state["session_type"]}")

        st.divider()

        st.subheader("Driver Comparsion")

        if "driver_ref" not in st.session_state:
            st.session_state.driver_ref = drivers[0]

        if "driver_comp" not in st.session_state:
            st.session_state.driver_comp = drivers[1] if len(drivers) > 1 else drivers[0]

        st.selectbox("Reference Driver",drivers,key="driver_ref")
        st.selectbox("Comparison Driver",drivers,index=1 if len(drivers) > 1 else 0,key="driver_comp")

    return True