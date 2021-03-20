python3 -m venv bankenv && \
source bankenv/bin/activate && \
python -m pip install -r requirements.txt && \
python -m uvicorn bank_app.main:app
