#![no_std]

elrond_wasm::imports!();
elrond_wasm::derive_imports!();

use elrond_wasm::elrond_codec::TopEncode;





#[derive(TypeAbi, TopEncode, TopDecode, Clone)]
pub struct IdGenerator<M: ManagedTypeApi> {
    pub timestamp: u64,
    pub caller_address: ManagedAddress<M>,
}


#[derive(TypeAbi, TopEncode, TopDecode, Clone)]
pub struct TxInfos<M: ManagedTypeApi> {
    pub address_buyer: ManagedAddress<M>,
    pub locked_tokens: Vec<EsdtTokenPayment<M>>,
    pub desired_tokens: Vec<EsdtTokenPayment<M>>,
}







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
    fn locked_tokens(&self, address: &ManagedAddress) -> SingleValueMapper<Vec<EsdtTokenPayment<Self::Api>>>;

    // 4) Record every authorized tradable tokens
    #[view(getAuthorizedTokens)]
    #[storage_mapper("authorized_tokens")]
	fn authorized_tokens(&self) -> SetMapper<TokenIdentifier>;	




    // ******************* INIT FUNCTION **********************************
    #[init]
    fn init(&self) {
        self.add_authorized_token(TokenIdentifier::from("GNG-8d7e05".as_bytes()));
        self.add_authorized_token(TokenIdentifier::from("MEX-4183e7".as_bytes()));
        self.add_authorized_token(TokenIdentifier::from("WATER-104d38".as_bytes()));
        self.add_authorized_token(TokenIdentifier::from("WEGLD-02bdfa".as_bytes()));
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
                    desired_tokens: Vec<EsdtTokenPayment<Self::Api>>)-> SCResult<()>{



        // Check if there is a payment                
        require!(!payments.is_empty(), "No tokens to be locked");

        let caller = self.blockchain().get_caller();

        // Check if the Buyer didn't already locked tokens
        require!(self.locked_tokens(&caller).is_empty(), "User has already locked tokens");



    	// Generate a random transaction ID with a hash of the block timestamp and the caller address
        let tx_id = self.generate_tx_id(&caller).unwrap();

        // Use as_managed_buffer() // TODO : check if it works
        let caller_hex = caller.as_managed_buffer();        
    	self.tx_id(&caller_hex).set(&tx_id);


        // Check if the desired tokens are authorized
        for token in &desired_tokens { 
            require!(self.authorized_tokens().contains(&token.token_identifier), "Desired token not authorized");
        }

        // Check if the locked tokens are authorized  
        for token in &payments { 
            require!(self.authorized_tokens().contains(&token.token_identifier), "Locked token not authorized");
        }


        let tokens_to_lock = payments.into_vec();

        // Save all information for this transaction id.
        self.locked_tokens(&caller).set(&tokens_to_lock);
        self.tx_infos(&tx_id).set(&TxInfos {
            address_buyer: caller.clone(),
            locked_tokens: tokens_to_lock,
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
            self.send().direct(&seller_address, &token.token_identifier, token.token_nonce, &token.amount , &[]);                     
        }
        // For future releases : Need to check if payment coincides with desired tokens
        // For now this works, cause the SC won't be able to send the desired tokens if it didn't receive them first
        // However if the Seller sends more, the rest will be kept in the SC
        for token in tokens_desired {
            self.send().direct(&buyer_address, &token.token_identifier, token.token_nonce, &token.amount , &[]);                     
        }              

        


        // Clear memory for this transaction, the swap has been made
        self.tx_infos(&tx_id).clear();
        self.locked_tokens(&buyer_address).clear();

        // We need the address of the buyer in hexa to clear the tx id
        let buyer_address_hex = buyer_address.as_managed_buffer();        
        self.tx_id(&buyer_address_hex).clear();
        
        Ok(())//royalties_payment.royalties_needed)
    
    }    


  
    // Unlock function : to be called by any "Buyer" that has locked tokens and wishes to unlock them
    #[endpoint(unlock)]
    fn unlock(&self) -> SCResult<()>{

        let caller = self.blockchain().get_caller();
        let token_data = self.locked_tokens(&caller).get();

        // Check if the caller has tokens locked
        require!(!token_data.is_empty(), "Caller has no tokens locked");         

        // Send the locked tokens back to the Buyer
        for token in token_data {
            self.send().direct(&caller, &token.token_identifier, token.token_nonce, &token.amount , &[]);                     
        }

        // We need the address of the caller in hexa to get the tx id
        let caller_hex = caller.as_managed_buffer();
		let tx_id = self.tx_id(&caller_hex).get(); 

    	// Clear memory for this transaction, the swap has been made
        self.tx_infos(&tx_id).clear();  
        self.locked_tokens(&caller).clear();         
        self.tx_id(&caller_hex).clear();


        Ok(())

    }     


    // ******************* HELPER FUNCTION ***************************


    // Note : this function has to return either Option or SCResult in order to use ? with the top encode function
    // Option doesn't natively do ManageBuffer, so SCResult was used, even though it should be used for endpoints only
    fn generate_tx_id(&self, caller_address: &ManagedAddress) -> SCResult<ManagedBuffer> {
        
        let id_generator = IdGenerator {
            timestamp: self.blockchain().get_block_timestamp(),
            caller_address: caller_address.clone(),
        };
    	
    	let mut serialized_tx_id = Vec::new();
        id_generator.top_encode(&mut serialized_tx_id)?;  

        let tx_id_hash = self.crypto().sha256_legacy(&serialized_tx_id);
        
        Ok(ManagedBuffer::from(tx_id_hash.as_bytes()))
        
    }
    
}
       

