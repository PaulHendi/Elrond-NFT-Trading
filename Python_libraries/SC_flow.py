from Python_libraries.SC_Interactions import SC_interactions
from Python_libraries.const import *
from erdpy.accounts import Address


class SC_flow(SC_interactions) :

    def __init__(self) : 

        SC_interactions.__init__(self)


    def deploy_SC(self) :

        print("\nDeploying the SC..")

        self.environment.run_flow(self.deploy)
        self.users["owner"].nonce += 1


    def prepare_data(self,tokens) :


        for token in tokens :
            if (token["type"]!="NonFungible") and (token["type"]!="SemiFungible") : 
                token["amount"] = self.formatter.int_to_BigInt(float(token["amount"]), DECIMALS[token["id"]])

            token["id"] = self.formatter.text_to_hex(token["id"])
            token["nonce"] = self.formatter.num_to_hex(int(token["nonce"]))
            token["amount"] = self.formatter.num_to_hex(token["amount"])
            token["type"] = TOKEN_TYPE_U8[token["type"]]

        return tokens


    def lock_token(self, order) :


        user_that_lock = order["user"]
        print(f"\n{user_that_lock} locks:")
        for token in order["lock"] : 
            amount, token_id, nonce = token['amount'], token['id'], token['nonce']
            print(f"    _ {amount} of {token_id} and nonce {nonce}")
        print("And wishes to swap it for:")
        for token in order["swap"] : 
            amount, token_id, nonce = token['amount'], token['id'], token['nonce']
            print(f"    _ {amount} of {token_id} and nonce {nonce}")        
        


        
        # Prepare data before calling the SC function
        order["lock"] = self.prepare_data(order["lock"])
        order["swap"] = self.prepare_data(order["swap"])
        

        user = self.users[order["user"]]
        self.lock(user, order)
        user.nonce += 1 


        

    def get_tx_id(self, user_that_locks) : 

        user = self.users[user_that_locks]

        print(f"\n{user_that_locks} : get tx_id and send it to the Seller")
        tx_id = self.environment.run_flow(lambda: self.query_tx_id(user))
        print(f"Tx id: {tx_id[0].hex}")  


        return tx_id


    def get_all_infos(self, tx_id, user) : 

        print(f"\n\n{user} : get all information for this tx_id\n")
        infos_parsed = self.query_tx_infos(tx_id)

        print(infos_parsed)

        addr_buyer = Address(infos_parsed["address_buyer"]).bech32()
        print(f"Buyer with address {addr_buyer} locked : ")
        for token in infos_parsed["locked_tokens"] : 
            amount, token_id, nonce = token['amount'], token['id'], token['nonce']
            if TOKEN_TYPE[token['id']]!="NFT" : amount /= DECIMALS[token['id']]
            print(f"    _ {amount} of {token_id} and nonce {nonce}")
        print("And wishes to swap it for:")
        for token in infos_parsed["desired_tokens"] : 
            amount, token_id, nonce = token['amount'], token['id'], token['nonce']
            if TOKEN_TYPE[token['id']]!="NFT" :  amount /= DECIMALS[token['id']] 
            print(f"    _ {amount} of {token_id} and nonce {nonce}") 
        print("\nDo you agree with this swap ?")     


    def unlock_token(self, user_that_unlock) : 

        print(f"\n{user_that_unlock} unlocks his tokens")
        
        user = self.users[user_that_unlock]
        self.unlock(user)
        user.nonce += 1  


    def swap_tokens(self, user_that_swap, tx_id) : 

        print(f"\n{user_that_swap} agrees and enable the swap")
        
        user = self.users[user_that_swap]
        self.swap(user, tx_id)
        user.nonce += 1     
     
