# app.py - Streamlit app with scheduler that polls fetchers and scores items
import streamlit as st
from threading import Thread, Event
import time
from datetime import datetime
from fetchers import fetch_all
from scorer import compute_risk
from store import push_event, get_recent, increment_geo_topic, get_geo_topic_counts
from config import FETCH_INTERVAL_SECONDS, RISK_THRESHOLD, USE_HEAVY_MODELS

st.set_page_config(layout='wide', page_title='Misinfo EarlyAlert')

stop_event = Event()

def background_loop():
    # runs in separate thread
    while not stop_event.is_set():
        try:
            items = fetch_all()
            for item in items:
                res = compute_risk(item)
                item.update(res)
                item['scanned_at'] = datetime.utcnow().isoformat()
                # simple topic: first claim or title keywords
                topic = (res['claims'][0] if res.get('claims') else (item.get('title') or '')).split(':')[0][:80]
                location = "Unknown"
                push_event({**item, 'topic': topic, 'location': location})
                # update geo-topic counts (here loc unknown -> skip)
                increment_geo_topic(location, topic)
            # sleep
        except Exception as e:
            print("Background error:", e)
        for _ in range(int(FETCH_INTERVAL_SECONDS/2)):
            if stop_event.is_set():
                break
            time.sleep(2)

def start_bg():
    t = Thread(target=background_loop, daemon=True)
    t.start()
    return t

# Start background worker
if 'bg_started' not in st.session_state:
    st.session_state['bg_thread'] = start_bg()
    st.session_state['bg_started'] = True

st.title("⚡ Misinfo EarlyAlert — Live Dashboard")
st.markdown("**Realtime early-warning for suspicious viral content**")

col1, col2 = st.columns([2,1])
with col2:
    st.markdown("### Controls")
    st.write(f"Heavy models: {'ON' if USE_HEAVY_MODELS else 'OFF'}")
    st.write(f"Fetch interval: {FETCH_INTERVAL_SECONDS}s")
    if st.button("Force fetch now"):
        from fetchers import fetch_all
        items = fetch_all()
        st.write(f"Fetched {len(items)} items")

with col1:
    st.markdown("### Live Feed (most recent)")
    rows = get_recent(50)
    if not rows:
        st.info("No scanned items yet — open the app and wait ~1 minute or Force fetch.")
    for r in rows[:50]:
        risk = r.get('risk_score', 0)
        is_alert = risk >= RISK_THRESHOLD
        container = st.container()
        if is_alert:
            container.markdown(f"##### 🔥 [{risk:.2f}] {r.get('title')}")
            container.write(f"Source: {r.get('url')}")
            container.write(f"Topic: {r.get('topic')} — Scanned: {r.get('scanned_at')}")
            container.write("**Why flagged:**")
            container.json(r.get('components'))
            if st.button(f"Open: {r.get('url')}", key=r.get('id')):
                st.experimental_open_url(r.get('url'))
            st.audio(None)  # placeholder to allow adding a sound on alert if desired
        else:
            container.markdown(f"##### [{risk:.2f}] {r.get('title')}")
            container.write(f"{r.get('url')}")

st.sidebar.header("Alerts")
alerts = [r for r in get_recent(200) if r.get('risk_score',0) >= RISK_THRESHOLD]
st.sidebar.write(f"Active alerts: {len(alerts)}")
for a in alerts[:20]:
    st.sidebar.write(f"- [{a.get('topic')}] {a.get('title')[:80]} - {a.get('risk_score'):.2f}")

st.sidebar.header("Geo-topic counts (sample)")
st.sidebar.json(get_geo_topic_counts())

st.markdown("---")
st.caption("Built for hackathon demo. This is a minimal MVP — expand models, add geo extraction, and webhooks for production.")
