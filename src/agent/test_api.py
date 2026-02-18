import asyncio
import httpx
import json

async def test_accounts():
    async with httpx.AsyncClient() as client:
        r = await client.get('http://localhost:5091/api/accounts')
        data = r.json()
        print("=== ACCOUNTS ===")
        print("Type:", type(data))
        print("Keys:", list(data.keys()) if isinstance(data, dict) else "List")
        
async def test_transactions():
    async with httpx.AsyncClient() as client:
        r = await client.get('http://localhost:5091/api/transactions')
        data = r.json()
        print("\n=== TRANSACTIONS ===")
        print("Type:", type(data))
        if isinstance(data, dict):
            print("Keys:", list(data.keys()))
            print("transactions count:", len(data.get('transactions', [])) if 'transactions' in data else 'N/A')
        else:
            print("List length:", len(data))

asyncio.run(test_accounts())
asyncio.run(test_transactions())
