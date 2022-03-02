import time
from Python_libraries.SC_flow import SC_flow
from Python_libraries.scenario import *


# Deploying the contract
smart_contract = SC_flow()
#smart_contract.deploy_SC()

deployed_SC_address = "erd1qqqqqqqqqqqqqpgqeululg646np3tkc74wek2mymcsys6w7kkewq2pfz0j"
smart_contract.use_deployed_SC(deployed_SC_address)
time.sleep(2)

token_1 = {"id" : "WARMY-cc922b", "amount" : 1, "nonce" : 1, "type" : "SemiFungible"}
token_2 = {"id" : "GNG-8d7e05", "amount" : 1, "nonce" : 0, "type" : "Fungible"}
token_3 = {"id" : "COLORS-14cff1", "amount" : 1, "nonce" : 4, "type" : "NonFungible"}
token_4 = {"id" : "WATER-104d38", "amount" : 100, "nonce" : 0, "type" : "Fungible"}
token_5 = {"id" : "MEX-4183e7", "amount" : 100, "nonce" : 0, "type" : "Fungible"}


# Note : To swap the exact same token, we need to use .copy() in order to make the token independant
token_lock = [token_2]
token_swap = [token_5]



order = {"user" : "alice", "alter_user" : "bob",  "lock" : token_lock, "swap" : token_swap}


# smart_contract.unlock_token("alice")
# time.sleep(30)

smart_contract.authorized_token("COLORS-14cff1") # Royalties 10%
time.sleep(30)

smart_contract.lock_token(order)

time.sleep(30)
tx_id = smart_contract.get_tx_id(order["user"])
    

time.sleep(5) 
smart_contract.get_all_infos(tx_id, order["alter_user"])


time.sleep(5)
smart_contract.swap_tokens(order["alter_user"], tx_id)

#scenario_lock_unlock_simple(smart_contract, order)
#scenario_unlock_before_swap_simple(smart_contract, order)
#scenario_lock_swap(smart_contract, order)

