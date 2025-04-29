from openai import OpenAI
import json
from config import config
import asyncio

def ai_get_songs(song):
    content = "I like to listen "+song+".What two songs I am likely to love?"
    client = OpenAI(api_key = config.OPENAI_API_KEY)
    response = client.responses.create(
    model="gpt-4.1",
    input=[{"role": "user", "content": content}],
    text={
            "format": {
                "type": "json_schema",
                "name": "songs",
                "schema": {
                    "type": "object",
                    "properties": {
                        "songs": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string"},
                                    "artist": {"type": "string"}
                                },
                                "required": ["title", "artist"],
                                "additionalProperties": False
                            }
                        },
                    },
                    "required": ["songs"],
                    "additionalProperties": False
                },
                "strict": True
            }
        }
    )
    songs_list = json.loads(response.output_text)['songs']
    return songs_list

