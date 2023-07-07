import aminofix
import json

with open("a.json", "r") as file:
    teste = json.load(file)


for conta in teste:
    email = conta["email"]
    senha = conta["password"]
    dev_id = conta["device"]
    amino = aminofix.Client(
        deviceId=dev_id,
        userAgent= "Apple iPhone12,1 iOS v15.5 Main/3.12.2",
        
    )
    link = "http://aminoapps.com/c/RogerioCena"
    ndcId = amino.get_from_code(link).comId
    amino.login(email, senha)
    amino.join_community(ndcId, link)

    print(email, "entrou")
