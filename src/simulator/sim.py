import asyncio
import os
import time


async def main():
    declare_wallets = os.environ["DECLARE_WALLETS"]
    print('wallet loaded')
    if declare_wallets == 'yes':
        print('declare wallet')
    await simulate()

async def simulate(batch = 10):
    while True:
        tasks = [asyncio.create_task(send_tx()) for i in range(batch)]

        print(f"started at {time.strftime('%X')}")

        time.sleep(2)
        # Wait until both tasks are completed (should take
        # around 2 seconds.)
        for i in range(batch):
            await tasks[i]

async def send_tx():
    print('send a tx')

if __name__ == "__main__":
    asyncio.run(main())
    