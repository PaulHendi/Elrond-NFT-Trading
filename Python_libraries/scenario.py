import time


def scenario_lock_unlock_simple(contract_deployed, order) : 

    contract_deployed.lock_token(order)


    time.sleep(30)
    tx_id = contract_deployed.get_tx_id(order["user"])
        

    time.sleep(5) 
    contract_deployed.get_all_infos(tx_id, order["alter_user"])


    time.sleep(5)
    contract_deployed.unlock_token(order["user"])
 

    return tx_id


def scenario_lock_swap(contract_deployed, order) : 

    contract_deployed.lock_token(order)


    time.sleep(30)
    tx_id = contract_deployed.get_tx_id(order["user"])
        

    time.sleep(5) 
    contract_deployed.get_all_infos(tx_id, order["alter_user"])


    time.sleep(5)
    contract_deployed.swap_tokens(order["alter_user"], tx_id)
 

    return tx_id


def scenario_unlock_before_swap_simple(contract_deployed, order) :

    tx_id = scenario_lock_unlock_simple(contract_deployed, order)
    time.sleep(30)

    contract_deployed.swap_tokens(order["alter_user"], tx_id)    


