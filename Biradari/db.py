import pymongo

#client = pymongo.MongoClient("mongodb://localhost",27017)

client = pymongo.MongoClient("mongodb+srv://test:12345@cluster0.4luf0.mongodb.net/test?retryWrites=true&w=majority")
db = client['test']

user_collection = db['users']
request_collection = db['requests']
post_collection = db['posts']
