from erdpy.accounts import Account

  
# Users
def get_users() : 
    devWallet_dir = "../Wallets/DevWallets/"
    user = {}
    user["owner"] = Account(pem_file=devWallet_dir + "wallet_owner.pem")
    user["bob"] = Account(pem_file= devWallet_dir + "wallet_Bob.pem")
    user["alice"] = Account(pem_file=devWallet_dir + "wallet_Alice.pem")
    user["jack"] = Account(pem_file=devWallet_dir + "wallet_Jack.pem")
    user["lucette"] = Account(pem_file=devWallet_dir + "wallet_Lucette.pem")

    return user


def get_user_address(user) : 
    return user.address.bech32()