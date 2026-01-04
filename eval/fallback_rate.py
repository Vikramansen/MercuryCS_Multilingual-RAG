import requests

API_URL = "http://localhost:8000/chat"

def evaluate_fallback_rate(queries: list[dict]):
    """
    queries: list of dicts with 'text' and 'expected_fallback' (bool)
    """
    total = len(queries)
    fallback_count = 0
    correct_handling = 0
    
    print(f"Evaluating fallback rate on {total} queries...")
    
    for item in queries:
        query = item['text']
        expected_fallback = item['expected_fallback']
        
        try:
            response = requests.post(API_URL, json={"query": query})
            data = response.json()
            
            intent = data['intent']
            # Check if it was handled as fallback/unsupported OR if the generator refused
            is_fallback = (intent in ["unsupported", "fallback"]) or \
                          ("cannot assist" in data['response']) or \
                          ("cannot answer" in data['response'])
            
            if is_fallback:
                fallback_count += 1
                
            if is_fallback == expected_fallback:
                correct_handling += 1
            else:
                print(f"Mismatch: '{query}' -> Fallback: {is_fallback}, Expected: {expected_fallback}")
                
        except Exception as e:
            print(f"Error processing '{query}': {e}")
            
    rate = (fallback_count / total) * 100
    accuracy = (correct_handling / total) * 100
    
    return {
        "fallback_rate": rate,
        "handling_accuracy": accuracy,
        "total_queries": total,
        "fallback_count": fallback_count
    }

if __name__ == "__main__":
    test_set = [
        {"text": "shipping time", "expected_fallback": False},
        {"text": "return policy", "expected_fallback": False},
        {"text": "battery life of headphones", "expected_fallback": False},
        {"text": "tell me a joke", "expected_fallback": True},
        {"text": "who is the president", "expected_fallback": True},
        {"text": "write python code", "expected_fallback": True},
        {"text": "my package is lost", "expected_fallback": False}
    ]
    
    try:
        results = evaluate_fallback_rate(test_set)
        print(f"\nFallback Rate: {results['fallback_rate']:.2f}%")
        print(f"Handling Accuracy: {results['handling_accuracy']:.2f}%")
    except requests.exceptions.ConnectionError:
        print("Error: API is not running. Please start the API with 'uvicorn api.main:app' first.")
