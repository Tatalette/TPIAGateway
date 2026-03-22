from ai.code_indexer import CodeOptimizationIndexer

indexer = CodeOptimizationIndexer(sample_size=5000, rebuild=False)  # changez rebuild=True pour forcer la reconstruction

# Exemple de code (tri à bulles)
test_code = """def sort_list(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr
"""

suggestions = indexer.suggest_optimization(test_code)
for i, s in enumerate(suggestions):
    print(f"\n--- Suggestion {i+1} (similarité: {s['similarity']:.2f}) ---")
    print("Code inefficace trouvé :")
    print(s['inefficient'])
    print("\nCode efficace associé :")
    print(s['efficient'])