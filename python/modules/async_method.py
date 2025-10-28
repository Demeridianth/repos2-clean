import time
import asyncio


def cook():
    time.sleep(2)
    return 'done'

def main():
    print(cook())
    print(cook())
    


async def cook():
    await asyncio.sleep(2)
    return 'done'

async def main_async():
    task1 = asyncio.create_task(cook())
    task2 = asyncio.create_task(cook())
    print(await task1)
    print(await task2)

# main()
asyncio.run(main_async())