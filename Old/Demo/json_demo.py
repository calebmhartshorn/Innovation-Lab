import json

# Opening JSON file
file = open("example_inventory.json")

# returns JSON object as 
# a dictionary
data = json.load(file)

# Closing file
file.close()

# Iterating through the json
for ingredient in data["inventory"]:
     
    # Print ingredient name
    print(ingredient["name"])

    for unique in ingredient["unique"]:
        print("\t" + unique["expirationDT"])
        print("\t" + unique["uniqueDescription"])
        print("\t" + str(unique["quantity"]["amount"]) + " " + (unique["quantity"]["unit"]) + "\n")
