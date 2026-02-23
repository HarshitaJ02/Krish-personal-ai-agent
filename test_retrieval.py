from rag.retriever import retrieve_context

query1 = "what database am I using for vectors?"
results1 = retrieve_context(query1, top_k=3)

print("Query:", query1)
print("Results:")
print(results1)
print("\n" + "="*50 + "\n")

query2 = "weather"
results2 = retrieve_context(query2, top_k=3)

print("Query:", query2)
print("Results:")
print(results2)