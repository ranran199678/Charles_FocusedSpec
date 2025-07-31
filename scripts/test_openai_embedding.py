import openai

openai.api_key = "sk-proj-BJhpB2Ex6iNWgFWmhYstBh4zj1IqxzuRN7przSc3jzdnv4CmYkLS-gVc-CPhiLxBUQYsXtZCMZT3BlbkkFJrI-piVn5PWCdq71KiXkgVL6xcP-kUsAjMLHiQgyLikhEIJEGeTjJ22w5wiczzW6GvjyH5w-DgA"

try:
    response = openai.embeddings.create(
        model="text-embedding-3-small",
        input=["שלום עולם"]
    )
    print("✅ הצלחה:", response.data[0].embedding[:10])
except Exception as e:
    print("❌ שגיאה:", str(e)) 