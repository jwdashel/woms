from whatsonms.dynamodb import metadb
from typing import List


def playlist_history_preview(stream: str) -> List[dict]:
    metadata = metadb.get_metadata(stream)['Item']['metadata']
    php = metadata['playlist_hist_preview'] if 'playlist_hist_preview' in metadata else []
    return php


def next_playlist_history_preview(stream: str) -> List[dict]:
    metadata = metadb.get_metadata(stream)
    metadata = metadata['Item']['metadata']

    if 'playlist_hist_preview' in metadata:
        php = metadata['playlist_hist_preview']
        del metadata['playlist_hist_preview']
    else:
        php = []

    if "air_break" in metadata:
        return php

    new_php = [metadata] + php[:2]
    return new_php
