class DataPipeline:
    """Pipeline de données principal (placeholder pour implémentation future)."""

    def __init__(self):
        self.processors = []

    async def process(self, payload):
        """Traitement générique d'un payload."""
        for processor in self.processors:
            payload = await processor(payload)
        return payload
