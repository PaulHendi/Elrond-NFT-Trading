import time
from Python_libraries.SC_flow import SC_flow
from Python_libraries.scenario import *


# Deploying the contract
smart_contract = SC_flow()
#smart_contract.deploy_SC()

deployed_SC_address = "erd1qqqqqqqqqqqqqpgqgndry9jum6asyejupwe9seln590qjgftkewqlvj0ll"
smart_contract.use_deployed_SC(deployed_SC_address)
time.sleep(2)

token_1 = {"id" : "WARMY-cc922b", "amount" : 1, "nonce" : 1}
token_2 = {"id" : "GNG-8d7e05", "amount" : 1000, "nonce" : 0}
token_3 = {"id" : "COLORS-14cff1", "amount" : 1, "nonce" : 4}
token_4 = {"id" : "WATER-104d38", "amount" : 100, "nonce" : 0}
token_5 = {"id" : "MEX-4183e7", "amount" : 500, "nonce" : 0}
token_6 = {"id" : "COLORS-14cff1", "amount" : 1, "nonce" : 3}


# Note : To swap the exact same token, we need to use .copy() in order to make the token independant
token_lock = [token_2,  token_5, token_6]
token_swap = [token_1, token_3]



order = {"user" : "alice", "alter_user" : "bob",  "lock" : token_lock, "swap" : token_swap}

#scenario_lock_unlock_simple(smart_contract, order)
#scenario_unlock_before_swap_simple(smart_contract, order)
scenario_lock_swap(smart_contract, order)

