import asyncio
import queue
import time

# Create the event queue
event_queue = queue.Queue()

async def process_event_queue():
    while True:
        try:
            while not event_queue.empty():
                func = event_queue.get_nowait()
                func()
        except queue.Empty:
            pass  # No items in the queue
        await asyncio.sleep(0.1)  # Sleep briefly to prevent blocking

async def add_to_event_queue(fn):
    # Add functions to the event queue
    event_queue.put(fn)

def main():
    loop = asyncio.get_event_loop()
    # Schedule the event queue processor
    loop.create_task(process_event_queue())
    # Schedule the addition of functions to the event queue
    loop.create_task(add_to_event_queue(lambda: print("Hello")))
    loop.create_task(add_to_event_queue(lambda: print("World")))
    loop.create_task(add_to_event_queue(lambda: print("Goodbye")))
    loop.create_task(add_to_event_queue(lambda: print("End")))
    # Run the event loop indefinitely
    loop.run_forever()

if __name__ == "__main__":
    # Run main on the main thread
    main()