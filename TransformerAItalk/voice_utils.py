import io
import wave


def pcm16_wav(sample_rate, pcm):
    if not isinstance(sample_rate, int) or sample_rate <= 0 or not pcm or len(pcm) % 2:
        raise ValueError("invalid PCM audio")
    stream = io.BytesIO()
    with wave.open(stream, "wb") as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(sample_rate)
        output.writeframes(pcm)
    return stream.getvalue()
