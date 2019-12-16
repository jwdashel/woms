from whatsonms.dynamodb import metadb


def playlist_history_preview(stream):
    metadata = metadb.get_metadata(stream)['Item']['metadata']
    php = metadata['playlist_hist_preview'] if 'playlist_hist_preview' in metadata else []
    return php


def next_playlist_history_preview(stream):
    metadata = metadb.get_metadata(stream)['Item']['metadata']
    php = playlist_history_preview(stream)
    if 'playlist_hist_preview' in metadata:
        del metadata['playlist_hist_preview']
    new_php = [metadata] + php[:2]
    return new_php
