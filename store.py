# store.py - simple in-memory store for events and counts
from collections import deque, defaultdict
from threading import Lock
from config import MAX_EVENTS_STORED

_lock = Lock()
events = deque(maxlen=MAX_EVENTS_STORED)   # most recent events
geo_topic_counts = defaultdict(lambda: defaultdict(int))

def push_event(evt: dict):
    with _lock:
        events.appendleft(evt)

def get_recent(n=50):
    with _lock:
        return list(events)[:n]

def increment_geo_topic(loc: str, topic: str):
    if not loc or not topic:
        return
    with _lock:
        geo_topic_counts[loc][topic] += 1

def get_geo_topic_counts():
    with _lock:
        return {loc: dict(topics) for loc, topics in geo_topic_counts.items()}
