from pier.agents.base import BaseAgent
from pier.models.agent.network import NetworkAllowlist
from bub_common import setup, run
import json
import pier.environments.docker.docker as docker_environment


_original_proxy_compose = docker_environment.write_docker_proxy_compose


def _offline_proxy_compose(*args, **kwargs):
    path = _original_proxy_compose(*args, **kwargs)
    compose = json.loads(path.read_text())
    proxy = compose["services"]["pier-egress-proxy"]
    proxy.pop("build", None)
    proxy["image"] = "fh-pier-egress-proxy:v1"
    proxy["pull_policy"] = "never"
    path.write_text(json.dumps(compose, indent=2))
    return path


docker_environment.write_docker_proxy_compose = _offline_proxy_compose


class BubAgent(BaseAgent):
    @staticmethod
    def name():
        return "bub"

    def version(self):
        return "0.4.4.dev14+g6f7d2b604"

    def network_allowlist(self):
        return NetworkAllowlist(domains=["api.kimi.com"])

    async def setup(self, environment):
        await setup(environment)

    async def run(self, instruction, environment, context):
        await run(self, instruction, environment, context)
