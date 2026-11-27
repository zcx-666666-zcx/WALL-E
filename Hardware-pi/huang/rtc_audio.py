class RtcAudio:
    def __init__(self, player_factory, recorder_factory):
        self.player_factory = player_factory
        self.recorder_factory = recorder_factory
        self.player = None
        self.recorder = None
        self.closed = False

    def add_microphone(self, peer, device):
        player = self.player_factory(device, format='alsa', options={'sample_rate': '48000', 'channels': '1'})
        if player.audio is None:
            raise RuntimeError('microphone has no audio stream')
        self.player = player
        peer.addTrack(player.audio)

    async def play_incoming(self, track, device):
        if self.closed:
            return
        recorder = self.recorder_factory(device, format='alsa')
        recorder.addTrack(track)
        self.recorder = recorder
        await recorder.start()

    async def close(self):
        self.closed = True
        if self.recorder is not None:
            await self.recorder.stop()
            self.recorder = None
        if self.player is not None:
            if self.player.audio:
                self.player.audio.stop()
            self.player = None
