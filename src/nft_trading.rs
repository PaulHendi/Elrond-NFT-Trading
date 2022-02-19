#![no_std]

elrond_wasm::imports!();
elrond_wasm::derive_imports!();

use elrond_wasm::elrond_codec::TopEncode;


#[derive(TypeAbi, TopEncode, TopDecode, Clone)]
pub struct IdGenerator<M: ManagedTypeApi> {
    pub timestamp: u64,
    pub caller_address: ManagedAddress<M>,
}

#[derive(TypeAbi, TopEncode, TopDecode, NestedEncode, NestedDecode, Clone)]
pub struct Token<M: ManagedTypeApi> {
    pub amount:  BigUint<M>,
    pub identifier: TokenIdentifier<M>,
    pub nonce: BigUint<M>,
}

#[derive(TypeAbi, TopEncode, TopDecode, Clone)]
pub struct TxInfos<M: ManagedTypeApi> {
    pub address_buyer: ManagedAddress<M>,
    pub locked_tokens: Vec<Token<M>>,
    pub desired_tokens: Vec<Token<M>>,
}

const ARTIFICIAL_NONCE: u64 = 42069;


#[elrond_wasm::derive::contract]
pub trait NftTrading {
  	    

    // ********************  STORAGE MAPPERS ********************************
    // 1) Store the tx id, indexed by "Buyer" addresses 
    #[view(getTxId)]
    #[storage_mapper("txId")]
    fn tx_id(&self, address: &ManagedBuffer) -> SingleValueMapper<ManagedBuffer>;
        

	// 2) For each transaction Id we get a bunch of informations 
    #[view(getTxInfos)]
    #[storage_mapper("tx_infos")]
    fn tx_infos(&self, tx_id: &ManagedBuffer) -> SingleValueMapper<TxInfos<Self::Api>>;


	// 3) Useful to record tokens that was locked and need to be unlock
    #[view(getLockedTokens)]
    #[storage_mapper("locked_tokens")]
    fn locked_tokens(&self, address: &ManagedAddress) -> SingleValueMapper<Vec<Token<Self::Api>>>;

    // 4) Record every authorized tradable tokens
    #[view(getAuthorizedTokens)]
    #[storage_mapper("authorized_tokens")]
	fn authorized_tokens(&self) -> SetMapper<TokenIdentifier>;	



    // ******************* INIT FUNCTION **********************************
    #[init]
    fn init(&self) {
		self.authorized_tokens().insert(TokenIdentifier::from("GNG-8d7e05".as_bytes()));
		self.authorized_tokens().insert(TokenIdentifier::from("MEX-4183e7".as_bytes()));
        self.authorized_tokens().insert(TokenIdentifier::from("WATER-104d38".as_bytes()));
    }

    #[only_owner]
    #[endpoint(addAuthorizedToken)]
    fn add_authorized_token(&self, token_id: TokenIdentifier) {
        self.authorized_tokens().insert(token_id);
    }



    // ******************* ENDPOINTS FUNCTION *****************************

    // Lock function : callable by any buyer, needs to send the tokens to be
    // locked and the desired tokens he wishes to have in exchange
    #[payable("*")]
    #[endpoint(lock)]
    fn lock(&self, #[payment_multi] payments: ManagedVec<EsdtTokenPayment<Self::Api>>,
                    desired_tokens: Vec<Token<Self::Api>>)-> SCResult<()>{



        // Check if there is a payment                
        require!(!payments.is_empty(), "No tokens to be locked");


        let caller = self.blockchain().get_caller();
        let caller_hex = ManagedBuffer::from(&caller.to_byte_array());

        // Check if the Buyer didn't already locked tokens
        require!(self.locked_tokens(&caller).is_empty(), "User has already locked tokens");



    	// Generate a random transaction ID with a hash of the block timestamp and the caller address
    	let id_generator = IdGenerator {
            timestamp: self.blockchain().get_block_timestamp(),
            caller_address: caller.clone(),
        };
    	
    	let mut serialized_tx_id = Vec::new();
        id_generator.top_encode(&mut serialized_tx_id)?;

        let tx_id_hash = self.crypto().sha256_legacy(&serialized_tx_id);
        let tx_id = ManagedBuffer::from(tx_id_hash.as_bytes());        

    	self.tx_id(&caller_hex).set(&tx_id);

        // Save the tokens information to be locked
        let mut token_to_lock = Vec::new();
        for token in &payments {

    	    // Check if the token sent is an authorized token 
            require!(self.authorized_tokens().contains(&token.token_identifier), "Token to lock not authorized");

            // Give an artificial nonce to Esdt tokens (0 doesn't get recorded on the blockchain)
            let custom_nonce = if token.token_type == EsdtTokenType::Fungible {
                ARTIFICIAL_NONCE
            }
            else {
                token.token_nonce
            };

            // Note : Nonces are stored as BigUint as they are more difficult to parse if U64
            // Even though this is a temporary fix, it can be left as is since the storage used doesn't increase
            // the format is stil 000000x[0-9a-f] with x being the number of bytes the nonce requires.            
            token_to_lock.push(Token{
                amount: token.amount,
                identifier: token.token_identifier,
                nonce: BigUint::from(custom_nonce),
            });
        }

        // Check if the desired token is an authorized token 
        for token in &desired_tokens { 
            require!(self.authorized_tokens().contains(&token.identifier), "Desired token not authorized");
        }

        // Save all information for this transaction id.
        self.locked_tokens(&caller).set(&token_to_lock);
        self.tx_infos(&tx_id).set(&TxInfos {
            address_buyer: caller.clone(),
            locked_tokens: token_to_lock,
            desired_tokens: desired_tokens,
        });
        

        Ok(())
    }


    // Swap function : to be called by the "Seller", sending the desired tokens along with the Tx id
    #[payable("*")]
    #[endpoint(swap)]
    fn swap(&self, #[payment_multi] _payments: ManagedVec<EsdtTokenPayment<Self::Api>>,
    			   tx_id: ManagedBuffer) -> SCResult<()> {
    	

   	    // Check if the tx id is valid 
        require!(!self.tx_infos(&tx_id).is_empty(), "Transaction not valid : Buyer has unlocked his tokens or the swap has been made");         

        // Get the transaction infos
        let tx_data = self.tx_infos(&tx_id).get();
        let buyer_address = tx_data.address_buyer;
        let tokens_locked = tx_data.locked_tokens;
        let tokens_desired = tx_data.desired_tokens;
    	
        // Get the seller address
    	let seller_address = self.blockchain().get_caller();   
        
        // Send the tokens locked to the Seller
        for token in tokens_locked {

            let amount = token.amount;
            let identifier = token.identifier;
            let nonce = token.nonce.to_u64().unwrap();  
            
            // Convert back the nonce to 0 if it's an ESDT
            let correct_nonce = self.convert_nonce(nonce);


            self.send().direct(&seller_address, &identifier, correct_nonce, &amount , &[]);            
            
        }  
        
        // For future releases : Need to check if payment coincides with desired tokens
        // For now this works, cause the SC won't be able to send the desired tokens if it didn't receive them first
        // However if the Seller sends more, the rest will be kept in the SC
        for token in tokens_desired {

            let amount = token.amount;
            let identifier = token.identifier;
            let nonce = token.nonce.to_u64().unwrap();  

            // Convert back the nonce to 0 if it's an ESDT
            let correct_nonce = self.convert_nonce(nonce);

            self.send().direct(&buyer_address, &identifier, correct_nonce, &amount , &[]);            
            
        }             


    	// Clear memory for this transaction, the swap has been made
        self.tx_infos(&tx_id).clear();
        self.locked_tokens(&buyer_address).clear();

        // We need the address of the buyer in hexa to clear the tx id
        let buyer_address_hex = ManagedBuffer::from(&buyer_address.to_byte_array());        
        self.tx_id(&buyer_address_hex).clear();
    	
    	Ok(())
    }     

    // Unlock function : to be called by any "Buyer" that has locked tokens and wishes to unlock them
    #[endpoint(unlock)]
    fn unlock(&self) -> SCResult<()>{

        let caller = self.blockchain().get_caller();
        let token_data = self.locked_tokens(&caller).get();

        // Check if the caller has tokens locked
        require!(!token_data.is_empty(), "Caller has no tokens locked");         


        // Send back the tokens locked to the Buyer
        for token in token_data {

            let amount = token.amount;
            let identifier = token.identifier;
            let nonce = token.nonce.to_u64().unwrap();  
            

            let correct_nonce = self.convert_nonce(nonce);

            self.send().direct(&caller, &identifier, correct_nonce, &amount , &[]);            
            
        }

        // We need the address of the caller in hexa to get the tx id
        let caller_hex = ManagedBuffer::from(&caller.to_byte_array());
		let tx_id = self.tx_id(&caller_hex).get(); 

    	// Clear memory for this transaction, the swap has been made
        self.tx_infos(&tx_id).clear();  
        self.locked_tokens(&caller).clear();         
        self.tx_id(&caller_hex).clear();


        Ok(())

    }

    // ******************* HELPER FUNCTION ***************************
    fn convert_nonce(&self, nonce: u64) -> u64{
        if nonce==ARTIFICIAL_NONCE {
            0
        }else {
            nonce
        }
    }
}
