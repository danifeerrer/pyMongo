import pymongo

# MongoDB connection information
mongo_uri = "mongodb://localhost:27017"  # Replace with your MongoDB server URI
db_name = "hetionet"  # Replace with your database name
collection_name = "relationships"  # Replace with your collection name

# Connect to MongoDB
client = pymongo.MongoClient(mongo_uri)
db = client[db_name]
collection = db[collection_name]

# Path to your TSV file
tsv_file_path = "./edges_test.tsv"  # Replace with your file path

# Open the TSV file and insert its data into MongoDB
with open(tsv_file_path, "r") as tsv_file:
    for line in tsv_file:
        fields = line.strip().split("\t")
        if len(fields) < 3:
            continue
        data = {
            "source": fields[0],
            "metaedge": fields[1],
            "target": fields[2],
        }
        # Insert the data into MongoDB
        collection.insert_one(data)