# Curl to delete pdf chat collection
```
curl --location --request DELETE 'http://localhost:6333/collections/pdf-chat'
```

# Curl to delete image search chat collection
```
curl --location --request DELETE 'http://localhost:6333/collections/image-search'
```

# Curl to delete
```
curl --location 'http://localhost:6333/collections/pdf-chat/points/delete' \
--header 'Content-Type: application/json' \
--data '{
    "filter": {
        "must": [
            {
                "key": "pdf_name",
                "match": {
                    "value": "Apoorva_Boppana.pdf"
                }
            }
        ]
    }
}'
```

# Curl to prettify qdrant's vectors pdf response
```
curl --location 'https://api.openai.com/v1/chat/completions' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer xyz' \
--data '{
    "model": "gpt-3.5-turbo",
    "messages": [
      {
        "role": "system",
        "content": "You are a helpful assistant."
      },
      {
        "role": "user",
        "content": "Who is himatesh cirikonda"
      }
    ]
  }'
```

# Curl to get images
```
curl --location 'http://localhost:5000/images?image_name=7dbe6660-9471-4ac9-b738-3970f2704c87.png&image_type=text-based'
```