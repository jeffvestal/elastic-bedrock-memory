"""
Create Elasticsearch indices for the Memory-as-a-Service demo.
Uses semantic_text field type (ELSER) for semantic recall.
"""
import os
import sys
from elasticsearch import Elasticsearch
from dotenv import load_dotenv

load_dotenv()

ES_URL = os.environ["ELASTICSEARCH_URL"]
ES_API_KEY = os.environ["ELASTICSEARCH_API_KEY"]

es = Elasticsearch(ES_URL, api_key=ES_API_KEY)

INDICES = {
    "conversation-history": {
        "mappings": {
            "properties": {
                "session_id":       {"type": "keyword"},
                "timestamp":        {"type": "date"},
                "role":             {"type": "keyword"},
                "content":          {"type": "text"},
                "content_semantic": {"type": "semantic_text"},
                "topic_tags":       {"type": "keyword"},
                "project":          {"type": "keyword"},
            }
        }
    },
    "knowledge-facts": {
        "mappings": {
            "properties": {
                "session_id":    {"type": "keyword"},
                "timestamp":     {"type": "date"},
                "category":      {"type": "keyword"},
                "fact":          {"type": "text"},
                "fact_semantic": {"type": "semantic_text"},
                "project":       {"type": "keyword"},
                "importance":    {"type": "keyword"},
            }
        }
    },
    "session-metadata": {
        "mappings": {
            "properties": {
                "session_id":  {"type": "keyword"},
                "start_time":  {"type": "date"},
                "end_time":    {"type": "date"},
                "summary":     {"type": "text"},
                "project":     {"type": "keyword"},
                "topics":      {"type": "keyword"},
            }
        }
    },
}


def create_indices():
    for name, body in INDICES.items():
        if es.indices.exists(index=name):
            print(f"  {name}: already exists, skipping")
            continue
        es.indices.create(index=name, **body)
        print(f"  {name}: created")


if __name__ == "__main__":
    print("Creating indices...")
    create_indices()
    print("Done.")
