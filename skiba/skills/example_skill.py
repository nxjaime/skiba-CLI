from .base import Skill


class SummarizeSkill(Skill):
    name = "summarize"
    description = "Summarizes long texts into a concise bullet list."

    def run(self, prompt: str, context: str) -> str:
        # Very small example: if user asks to summarize, do a quick summarize
        text = context + "\n" + prompt
        if len(text) > 200:
            return "Summary: " + context[:200] + "..."
        return text


def register() -> dict:
    return {SummarizeSkill.name: SummarizeSkill()}
