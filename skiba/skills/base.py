class Skill:
    """Base class for skills/plugins."""

    name: str = "base"
    description: str = "Base skill"

    def run(self, prompt: str, context: str) -> str:
        raise NotImplementedError
