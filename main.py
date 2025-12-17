#!/usr/bin/env python3
"""CLI runner for testing the Creative Fortune Teller chatbot"""

from langchain_core.messages import HumanMessage
from src.graph import graph
from src.state import UserData

def main():
    print("🔮 Selamat datang di peramal masa depan kamu di dunia industri kreatif 🔮")
    print("=" * 70)
    print("Ketik 'keluar' untuk berhenti\n")
    
    state = {
        "messages": [],
        "user_data": {
            "name": None,
            "location": None,
            "dob": None,
            "job_field": None,
            "email": None
        },
        "next_step": "name"
    }
    
    # Initial greeting
    state["messages"].append(HumanMessage(content="Halo"))
    result = graph.invoke(state)
    print(f"🔮 Peramal: {result['messages'][-1].content}\n")
    state = result
    
    while True:
        user_input = input("Anda: ").strip()
        
        if user_input.lower() in ['keluar', 'exit', 'quit', 'q']:
            print("\n✨ Sang peramal menghilang ke alam semesta... Sampai jumpa! ✨")
            break
        
        if not user_input:
            continue
        
        state["messages"].append(HumanMessage(content=user_input))
        result = graph.invoke(state)
        
        print(f"\n🔮 Peramal: {result['messages'][-1].content}\n")
        
        # Show collected data (for debugging)
        collected = {k: v for k, v in result['user_data'].items() if v}
        if collected:
            print(f"[Data terkumpul: {collected}]\n")
        
        if result["next_step"] == "complete":
            print("\n✨ Takdir Anda telah terungkap! ✨")
            break
        
        state = result

if __name__ == "__main__":
    main()
