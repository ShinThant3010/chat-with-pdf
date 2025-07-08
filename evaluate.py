import requests
import json

# Load golden Q&A pairs
with open("golden_qa.json") as f:
    goldens = json.load(f)

url = "http://localhost:8000/ask"
session_id = "eval"

for qa in goldens:
    q = qa["question"]
    expected = qa["expected"]

    resp = requests.post(url, json={"session_id": session_id, "question": q})
    data = resp.json()

    answer = data.get("answer", "")
    agent = data.get("agent", "")

    print(f"Q: {q}")
    print(f"Expected: {expected}")
    print(f"Got (agent): {agent}")
    print(f"Got (answer): {answer}\n")

    # Simple match: does agent or answer contain expected?
    if (expected.lower() in agent.lower()) or (expected.lower() in answer.lower()):
        print("✅ Passed\n")
    else:
        print("❌ Failed\n")
