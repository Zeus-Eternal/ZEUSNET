# anomaly.py
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from backend.db import get_db
from backend.models import WiFiScan
from sqlalchemy.orm import Session

def detect_anomalies(db: Session):
    query = db.query(WiFiScan).order_by(WiFiScan.timestamp.desc()).limit(500).all()
    if not query:
        return []

    df = pd.DataFrame([s.to_dict() for s in query])
    if df.empty or 'rssi' not in df.columns:
        return []

    model = IsolationForest(n_estimators=100, contamination=0.1)
    df['score'] = model.fit_predict(df[['rssi']])
    anomalies = df[df['score'] == -1]
    return anomalies.to_dict(orient="records")
