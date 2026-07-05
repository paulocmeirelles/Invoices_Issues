source venv/bin/activate && pkill -f 'streamlit run app.py' || true && streamlit run app.py --server.headless true --server.port 8501
