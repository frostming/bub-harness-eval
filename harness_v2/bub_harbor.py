from harbor.agents.base import BaseAgent
from bub_common import setup, run


class BubAgent(BaseAgent):
    @staticmethod
    def name():
        return "bub"

    def version(self):
        return "0.4.4.dev14+g6f7d2b604"

    async def setup(self, environment):
        await setup(environment)

    async def run(self, instruction, environment, context):
        await run(self, instruction, environment, context)
