# Local AI and TTS snapshot

This directory and the sibling `TTS/` directory are a snapshot of the local
AI dialogue and GPT-SoVITS code. The existing `voice-service/` remains a
separate integration and has not been replaced by this snapshot.

- Install Git LFS before cloning to download the three checkpoint files.
- User memory, generated audio, Python caches and the downloadable NLTK data
  are not included. Follow the GPT-SoVITS setup instructions to obtain its
  dependencies and pretrained models.
- Set `TAVILY_API_KEY` in the environment to enable authenticated search.
- The dialogue service defaults to `TransformerAItalk/TTS`; when using the
  sibling directory, set `TTS_ROOT` to its absolute path.
- The dialogue README refers to `api.server`; the available API entry point
  in this snapshot is `api.server_with_intent`.

The snapshot has not been deployed or integration-tested with the existing
repository backend or voice service.
