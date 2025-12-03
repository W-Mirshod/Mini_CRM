import asyncio
import httpx
import random

BASE_URL = "http://localhost:8000"

async def verify():
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        print("Checking API health...")
        resp = await client.get("/")
        print(resp.json())

        # 1. Create Operators
        print("\nCreating Operators...")
        op1 = (await client.post("/operators/", json={"name": "Alice", "workload_limit": 100})).json()
        op2 = (await client.post("/operators/", json={"name": "Bob", "workload_limit": 100})).json()
        print(f"Created: {op1['name']} (ID: {op1['id']}), {op2['name']} (ID: {op2['id']})")

        # 2. Create Source
        print("\nCreating Source...")
        source = (await client.post("/sources/", json={"name": "Bot_A"})).json()
        print(f"Created: {source['name']} (ID: {source['id']})")

        # 3. Set Weights (Alice=1, Bob=3 -> 25% / 75%)
        print("\nSetting Weights (Alice=1, Bob=3)...")
        await client.post(f"/sources/{source['id']}/weights", json=[
            {"operator_id": op1['id'], "weight": 1},
            {"operator_id": op2['id'], "weight": 3}
        ])

        # 4. Simulate Traffic
        print("\nSimulating 100 contacts...")
        for i in range(100):
            await client.post("/contacts/", json={
                "lead_identifier": f"user_{i}@example.com",
                "source_id": source['id']
            })
        
        # 5. Check Stats
        print("\nChecking Stats...")
        stats = (await client.get("/stats/")).json()
        print(stats)
        
        alice_count = stats['by_operator'].get('Alice', 0)
        bob_count = stats['by_operator'].get('Bob', 0)
        print(f"\nAlice: {alice_count}, Bob: {bob_count}")
        print(f"Ratio: {alice_count / (alice_count + bob_count):.2f} / {bob_count / (alice_count + bob_count):.2f}")
        
        # 6. Test Workload Limit
        print("\nTesting Workload Limit...")
        # Create Op with limit 1
        op3 = (await client.post("/operators/", json={"name": "Charlie", "workload_limit": 1})).json()
        # Set weights so Charlie gets all traffic
        await client.post(f"/sources/{source['id']}/weights", json=[
            {"operator_id": op3['id'], "weight": 100}
        ])
        
        # First contact -> Should go to Charlie
        c1 = (await client.post("/contacts/", json={"lead_identifier": "limit_test_1", "source_id": source['id']})).json()
        print(f"Contact 1 assigned to: {c1['operator_id']} (Expected: {op3['id']})")
        
        # Second contact -> Should NOT go to Charlie (limit reached)
        c2 = (await client.post("/contacts/", json={"lead_identifier": "limit_test_2", "source_id": source['id']})).json()
        print(f"Contact 2 assigned to: {c2['operator_id']} (Expected: None)")

if __name__ == "__main__":
    asyncio.run(verify())
