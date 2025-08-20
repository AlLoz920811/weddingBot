import requests

### --------------- Embeddings Generator Function ------------------------------------------------------------
#
def search_query(client, query, search_api_key, search_service_endpoint, index_name, api_search_version):
    
    # Generate query embedding
    response = client.embeddings.create(
        input=query,
        model="text-embedding-ada-002"
    )
    embeddings=response.model_dump()
    query_embedding = embeddings['data'][0]['embedding']

    # Build hybrid query
    payload = {
      "search": query,
      "select": "title, subtitle, content, category", 
      "queryLanguage": "en-us",
      "vectorQueries": [
        {
          "kind": "vector",
          "vector": query_embedding,  
          "fields": "contentVector",
          "k": 3
        }
      ],
      "top": 10}

    headers = {
    "Content-Type": "application/json",
    "api-key": search_api_key}

    # Send query to Azure AI Search
    url = f"{search_service_endpoint}/indexes/{index_name}/docs/search?api-version={api_search_version}"
    response = requests.post(url, headers=headers, json=payload)

    results = response.json()['value']
    context = " ".join([doc["category"] + ", " + doc["title"] + ", " + doc["subtitle"]  + ", " + doc["content"] for doc in results])

    return context