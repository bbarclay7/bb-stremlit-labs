SHELL=/bin/bash

pips=streamlit numpy matplotlib scipy watchdog

include venv.mk
#MENU go: run streamlit app locally
go:
	local/venv/bin/streamlit run app.py

