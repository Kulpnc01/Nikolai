import asyncio
import sys
import logging

logger = logging.getLogger(__name__)

class AsyncRespondLoop:
    """
    Non-blocking user input reader.
    Replaces the synchronous generator to allow the async event loop to breathe
    while waiting for stdin.
    """
    def __init__(self, core_runtime):
        self.core = core_runtime

    async def run(self):
        """
        Continuously read from stdin without blocking the asyncio loop.
        """
        logger.info("AsyncRespondLoop active. Ready for user input.")
        
        loop = asyncio.get_running_loop()
        
        while self.core.is_running:
            # Run the blocking input() call in a separate thread
            try:
                user_input = await loop.run_in_executor(None, sys.stdin.readline)
            except Exception as e:
                logger.error(f"Stdin read error: {e}")
                break

            if not user_input:
                break # EOF

            text = user_input.strip()
            if text:
                response = await self.core.process_user_input(text)
                if response:
                    print(f"\n{response}\n> ", end="", flush=True)
                else:
                    print("> ", end="", flush=True)
            else:
                 print("> ", end="", flush=True)
