#!/usr/bin/env bash


./setup-data.py

# To skip openning browser, add --server.headless true
streamlit run app.py 
