# Elrond-NFT-Trading
Example of a Smart Contract (SC) coded in RUST, that can perform any swaps of tokens (NFT, SFT, ESDT, MetaESDT)

## The idea   

P2P swaps are very tempting, we sometimes want an NFT and we are willing to give 2 NFTs, or 1 NFT plus some tokens in exchange. If feels like trading pokemon cards.
However this is not safe as we never know if both parties are trustful. This is why having an escrow SC as an intermediary helps us feeling more safe with those special trades. To understand the logic of the code, here is the process : 

_ The transaction is initiated by a "Buyer". He sets the desired tokens/NFTs he'd like to have, and locks in the SC the amount of tokens/NFTs the "Seller" wants. Once the tokens are locked, he will receive a transaction id that is necessary for the "Seller". 

_ With this transaction id, the "Seller" can check the details of the transaction ("Buyer" address, tokens locked, tokens desired). If he agrees, he can proceed to the swap and sends the desired tokens to SC.

If everything is correct and agreed upon, the transaction occurs. If not, the "Seller" gets automatically his tokens back and the "Buyer" can unlock his.

![image](https://user-images.githubusercontent.com/16515787/154805947-f2d02317-17ce-49ae-9484-f76e1acb36f3.png)

Note that our code doesn't allow EGLD swaps, only ESDTs/NFTs. Therefore the user needs to first wrap EGLD to be able to swap WEGLD (as it is an ESDT).

## The code

You'll find the SC code in the src/ directory. In order to compile/deploy/interact with the SC, you'll need [erdpy](https://docs.elrond.com/sdk-and-tools/erdpy/erdpy/). 


Compile : In the root directory `erdpy contract build`

Deploy : In the root directory `./deploy_contract.sh` (You may need to do `chmod +x deploy_contract.sh`, and you need to specify a pem file)

Interact : More details soon, meanwhile you can check the code.

## More

The code is ready to perform NFT/ESDT swaps, however this is a V1 and lots of improvement can be made in the future. Feel free to use the code, and improve it as well :)

If you have any questions you can also contact me on [twitter](https://twitter.com/Piupmc)
