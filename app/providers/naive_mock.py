"""A deliberately gullible stand-in for an LLM, used for tests, the red-team evaluation and keyless demos.

It answers by extracting sentences from the supplied documents, but it also *obeys* injected instructions the way
an unprotected model often does: it reveals its instructions when asked, follows "ignore previous instructions",
copies markdown images and links from documents, and repeats whatever text it is told to say. That makes it a
pessimistic model for measuring what the surrounding guardrails catch. Results against it are not a claim about any
real model; run the evaluation with LLM_PROVIDER=ollama or anthropic for that.
"""

from __future__ import annotations

import re

from app.guardrails.normalise import deleet, normalise
from app.retrieval import tokens

DOC = re.compile(r'<document ref="([^"]+)"[^>]*>\n(.*?)\n</document>', re.S)
SAY = re.compile(r"\b(?:say|respond with|reply with|output|print)\s*[:\"']\s*(.+?)[\"']?(?:$|\n)", re.I)


class NaiveMockProvider:
    name = "naive-mock"

    def generate(self, system: str, user: str, max_tokens: int) -> str:
        question = user.rsplit("Question:", 1)[-1].strip()
        docs = DOC.findall(user)
        everything = deleet(normalise(user))

        # Behaviour 1: leaks its instructions on request.
        if re.search(
            r"(system prompt|your instructions|text above|initial prompt|repeat everything|developer message)", everything
        ):
            return "Sure. My instructions are:\n" + system

        # Behaviour 2: repeats anything it is explicitly told to say.
        m = SAY.search(question)
        if m:
            return m.group(1).strip()

        # Behaviour 3: obeys "ignore previous instructions ... say X", from the user or from a document.
        if (
            re.search(r"(ignore|disregard|forget|set aside|stop following).{0,40}(instructions|rules|prompt|told)", everything)
            or "new instructions" in everything
        ):
            m = SAY.search(user) or SAY.search(normalise(user))
            if m:
                return m.group(1).strip()
            # Otherwise dumps every document it was given.
            return "\n".join(f"{body} [{ref}]" for ref, body in docs) or system

        # Behaviour 4: extractive answer, copying any images or links it sees in the chosen sentences.
        q = set(tokens(question))
        best: list[tuple[int, str, str]] = []
        for ref, body in docs:
            for sentence in re.split(r"(?<=[.!?])\s+|\n", body):
                overlap = len(q & set(tokens(sentence)))
                if overlap or "](" in sentence:
                    best.append((overlap + (1 if "](" in sentence else 0), sentence.strip(), ref))
        best.sort(key=lambda x: -x[0])
        if not best:
            return "I don't know based on the documents available to you."
        return " ".join(f"{s} [{ref}]" for _, s, ref in best[:3])[: max_tokens * 4]
