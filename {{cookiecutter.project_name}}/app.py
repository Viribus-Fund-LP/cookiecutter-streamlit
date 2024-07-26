import os

import streamlit as st

### These need to specifically be here
st.set_page_config(layout="wide")
for k, v in st.session_state.items():
    st.session_state[k] = v

state_defaults = {"_sb_name_value": None, "_sb_ye_name_value": None}
for k, v in state_defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v
        if k[:1] == "_":
            st.session_state[k[1:]] = v
for k, v in st.session_state.items():
    st.session_state[k] = v
###

from streamlit.logger import get_logger  # noqa: E402

logger = get_logger(__name__)


def is_local():
    return os.environ.get("LOCAL", "false").lower() == "true"


def main():
    st.title("Hello world!")

    def test():
        from {{cookiecutter.package_name}}.sf import Snowflake

        conn = Snowflake()
        assert conn.query("select 1").iat[0, 0] == 1

    test()

    st.text("Snowflake connection test passed!")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(e, icon="🚨")
