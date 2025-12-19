import requests
import json

def test_debug():
    # Pega aquí tu llave de ResRobot v2.1
    API_KEY = "de2ff1aa-161b-42d6-9566-1df608b4210c" 
    
    # Vamos a preguntar por Hallonbergen
    url = f"https://api.resrobot.se/v2.1/location.name?input=Hallonbergen&format=json&accessId={API_KEY}"
    
    print(f"📡 Llamando a: {url}")
    
    try:
        response = requests.get(url)
        data = response.json()
        
        print("\n--- 🕵️‍♂️ LO QUE RESPONDIÓ LA API (CRUDO) ---")
        # Esto imprime el JSON bonito para que lo podamos leer
        print(json.dumps(data, indent=4)) 
        
    except Exception as e:
        print(f"💥 Error técnico: {e}")

if __name__ == "__main__":
    test_debug()