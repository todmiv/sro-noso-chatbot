"""Top-level package for SRO NOSO Chatbot."""
from asyncio import set_event_loop_policy, WindowsSelectorEventLoopPolicy
import sys

# Windows-совместимость для asyncio <3.12
if sys.platform.startswith("win"):
    set_event_loop_policy(WindowsSelectorEventLoopPolicy())
