"""MailGuard ML - Streamlit entry point.

Run locally:  streamlit run app.py
"""

from __future__ import annotations

import streamlit as st

st.set_page_config(page_title="MailGuard ML Mahesh-Scandan ", page_icon=":material/shield:", layout="wide")

from src.app_resources import get_model_bundle, get_service  # noqa: E402
from src.theme import inject_theme   # with your other imports, after st.set_page_config

inject_theme()                        # once, before st.navigation(pages).run()

pages = [
    st.Page("views/analyzer.py", title="Email Analyzer", icon=":material/mail:", default=True),
    st.Page("views/evaluation.py", title="Model Evaluation", icon=":material/analytics:"),
    st.Page("views/monitoring.py", title="Monitoring", icon=":material/monitor_heart:"),
    st.Page("views/model_info.py", title="Model Information", icon=":material/info:"),
]

get_service()  # warm up model + metrics store once per process
model, model_error = get_model_bundle()

with st.sidebar:
    st.markdown("### :material/local_fire_department: MailGuard ML-Mahesh-Scandan")
    if model is not None:
        st.success(f"Model ready: {model.display_name} v{model.version}", icon=":material/check_circle:")
    else:
        st.error("Model unavailable - see Model Information.", icon=":material/error:")
    st.caption(
        "Educational spam-detection demo trained on the public SpamAssassin corpus. "
        "Emails you analyse are processed in memory and are not stored or logged."
        " Mahesh-CSE"
        " Scandan-CSE"
    )

st.navigation(pages).run()