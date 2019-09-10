We are using mongodb

tentative db structure:

one database

collections: messages and users

messages schema: 

```json
{
    "_id": ObjectId,
    "userId": ObjectId,
    "message": String,
    "timestamp": Date
} 
```

users schema:

```json
{
    "_id": ObjectId,
    "name": String,
    "displayName": String,
    "password": String
} 
```