import os
import json
import secrets
from pathlib import Path
from datetime import datetime

from pydantic_ai.messages import ModelMessagesTypeAdapter


LOG_DIR = Path(os.getenv('LOGS_DIRECTORY', 'logs'))
LOG_DIR.mkdir(exist_ok=True)


def log_entry(agent, messages, source="user"):
   
    dict_messages = ModelMessagesTypeAdapter.dump_python(messages)

    return {
        "provider": agent.model.system,
        "model": agent.model.model_name,
        "messages": dict_messages,
        "source": source
    }


def serializer(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")


def log_interaction_to_file(agent, messages, source='user'):
    entry = log_entry(agent, messages, source)

    rand_hex = secrets.token_hex(3)

    filename = f"{agent.name}_{rand_hex}.json"
    filepath = LOG_DIR / filename

    with filepath.open("w", encoding="utf-8") as f_out:
        json.dump(entry, f_out, indent=2, default=serializer)

    return filepath
