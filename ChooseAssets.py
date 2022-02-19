from Python_libraries.SC_flow import SC_flow
import requests
from Python_libraries.const import *
from Python_libraries.Users import get_users, get_user_address

def scan_wallet(user_address) : 

    # api-endpoint
    URL = "https://devnet-api.elrond.com"

    # sending get request and saving the response as response object
    nfts_requests = requests.get(url = URL+"/accounts/"+user_address+"/nfts")
    tokens_requests = requests.get(url = URL+"/accounts/"+user_address+"/tokens")


    print("\n" + 20*"*" + "Tokens" + 20*"*" + "\n")
    for token in tokens_requests.json() : 
        if token["identifier"] in AUTHORIZED_TOKENS : 
            amount = int(float(token["balance"])/10**float(token["decimals"]))
            print(f"{amount} "+token["identifier"])
        
    print("\n" + 20*"*" + "NFTs" + 20*"*" + "\n")
    for nft in nfts_requests.json() : 
        id_collection = nft["collection"]
        if id_collection not in AUTHORIZED_TOKENS : 
            continue

        if nft["type"] == "SemiFungibleESDT" : 
            amount = nft["balance"]
            print(f"{amount} SFT of collection {id_collection} ")
        elif nft["type"] == "MetaESDT" : 
            amount = int(float(nft["balance"])/10**float(nft["decimals"]))           
            print(f"{amount} {id_collection} ")
        else:
            id_NFT = nft["nonce"]
            print(f"NFT n°{id_NFT} of collection {id_collection} ")



# Use the smart contract object
smart_contract = SC_flow()

 
print("\n Wallet buyer : ")
scan_wallet(get_user_address(get_users()["alice"]))

print("\nWallet seller : ")
scan_wallet(get_user_address(get_users()["bob"]))


