#!/usr/bin/env bash


./setup-data.py

streamlit run app.py --server.headless true
