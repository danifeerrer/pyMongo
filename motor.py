import pymongo
import sys

if len(sys.argv) != 2:
    print("You must type <python> <program> <parameter_id>")
    exit()

try:
    integer_param = int(sys.argv[1])
except ValueError:
    print("Error: The provided parameter is not an integer.")
    sys.exit(1)

mongo_uri = "mongodb://localhost:27017" 
db_name = "hetionet"  

disease_id = f"Disease::DOID:{sys.argv[1]}"   

# Connect to MongoDB
client = pymongo.MongoClient(mongo_uri)
db = client[db_name]
collection_nodes = db["nodes"]
collection_relationships = db["relationships"]

# Query the database to retrieve the disease name
result_name = collection_nodes.find_one({"id": disease_id})

if result_name:
    disease_name = result_name.get("name", "Disease Name Not Found")
    print("Disease Name:", disease_name, '\n')
else:
    print("Disease with ID", disease_id, "not found in the database.")
    exit()

"""
GENES 
"""
result_genes = collection_relationships.find({"$and": [{"source": disease_id, "metaedge": "DaG"}]})
genes_list = []
output_genes = "This disease is associated with genes "

for item in result_genes:
    genes_list.append(item["target"])

for gene in genes_list:
    result_name_gene = collection_nodes.find_one({"id": gene})

    if result_name_gene:
        gene_name = result_name_gene.get("name", "Gene Name Not Found")
        output_genes += gene_name + ", "

"""
ANATOMIES
"""

result_anatomies = collection_relationships.find({"$and": [{"source": disease_id, "metaedge": "DlA"}]})
anatomies_list = []
output_anatomies = "This disease occurs in "

for item in result_anatomies:
    anatomies_list.append(item["target"])

for anatomy in anatomies_list:
    result_name_anatomy = collection_nodes.find_one({"id": anatomy})

    if result_name_anatomy:
        anatomy_name = result_name_anatomy.get("name", "Anatomy Name Not Found")
        output_anatomies += anatomy_name + ", "

"""
COMPOUNDS
"""
compounds_list = []

result_compounds = collection_relationships.find({
    "$and": [
        {"target": disease_id, "metaedge": "CtD"}
    ]
})

for compound in result_compounds:
    compounds_list.append(compound["source"])

"""
VALID DRUGS
"""
valid_drugs = []

for compound_id in compounds_list:
    # Find relationships with CuG between compound and gene
    cuG_relationships = collection_relationships.find({
        "source": compound_id,
        "metaedge": "CuG"
    })

    for cuG_relationship in cuG_relationships:
        gene_id = cuG_relationship["target"]
        if gene_id in genes_list:
            # Find relationships with AdU between gene and anatomy
            adU_relationships = collection_relationships.find({
                "target": gene_id,
                "metaedge": "AdG"
            })

            for adU_relationship in adU_relationships:
                anatomy_id = adU_relationship["source"]
                if anatomy_id in anatomies_list:
                    valid_drugs.append(compound_id)

valid_drugs_output = "Drugs that can treat this disease are "

for drug in valid_drugs:
    result_drug = collection_nodes.find_one({"id": drug})
    if result_drug:
        drug_name = result_drug.get("name")
        valid_drugs_output += drug_name + ", "

print(valid_drugs_output[:-2], '\n')

print(output_anatomies, '\n')

print(output_genes, '\n')
