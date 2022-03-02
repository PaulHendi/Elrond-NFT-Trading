import binascii
import re

Test = False

class Formatter:

    def hex_to_text(self, hex_string) : 

        bytes_object = bytes.fromhex(hex_string)
        ascii_string = bytes_object.decode("ASCII")

        return ascii_string


    # TODO : check that it's always an even number of hex
    def text_to_hex(self, text) :
        hexa = binascii.hexlify(text.encode()).decode()
        if len(hexa)%2==1 :  
            return "0" + hexa
        return hexa


    # Sometimes need to add a 0 (if it's even, to be sure that it's grouped by bytes)
    def num_to_hex(self, num) : 
        hexa = format(num, "x")
        if len(hexa)%2==1 :  
            return "0" + hexa
        return hexa     


    def hex_to_num(self, hex_string) :
        return int(hex_string, base=16)           


    # Note that for very high numbers, python loses in precision and the number is not correct anymore
    def int_to_BigInt(self, num, decimals) : 
        return int(f"{num*decimals:.1f}".split(".")[0])         


    def tx_infos_parser(self, tx_infos) : 


        addr_size = 64
        address_buyer = tx_infos[:addr_size]
        size_tokens_locked = self.hex_to_num(tx_infos[addr_size:addr_size+8])
        pointer = addr_size+8
        locked_tokens = []
        for token in range(size_tokens_locked) : 
            token_type = self.hex_to_num(tx_infos[pointer:pointer+2])
            pointer+=2
            token_identifier_size = self.hex_to_num(tx_infos[pointer:pointer+8])*2
            pointer+=8
            token_identifier = self.hex_to_text(tx_infos[pointer:pointer+token_identifier_size])
            pointer+=token_identifier_size
            token_nonce = self.hex_to_num(tx_infos[pointer:pointer+16])
            pointer+=16
            token_amount_size = self.hex_to_num(tx_infos[pointer:pointer+8])*2
            pointer+=8
            token_amount = self.hex_to_num(tx_infos[pointer:pointer+token_amount_size])
            pointer+=token_amount_size

            locked_tokens.append({"type" : token_type,
                "id" : token_identifier, 
                "nonce" : token_nonce, 
                "amount" : token_amount})            

        size_tokens_desired = self.hex_to_num(tx_infos[pointer:pointer+8])
        pointer +=8
        desired_tokens = []
        for token in range(size_tokens_desired) : 
            token_desired_type = self.hex_to_num(tx_infos[pointer:pointer+2])
            pointer+=2
            token_desired_identifier_size = self.hex_to_num(tx_infos[pointer:pointer+8])*2
            pointer+=8
            token_desired_identifier = self.hex_to_text(tx_infos[pointer:pointer+token_desired_identifier_size])
            pointer+=token_desired_identifier_size
            token_desired_nonce = self.hex_to_num(tx_infos[pointer:pointer+16])
            pointer+=16
            token_desired_amount_size = self.hex_to_num(tx_infos[pointer:pointer+8])*2
            pointer+=8
            token_desired_amount = self.hex_to_num(tx_infos[pointer:pointer+token_desired_amount_size])
            pointer+=token_desired_amount_size    

            desired_tokens.append({"type" : token_desired_type,
                "id" : token_desired_identifier, 
                "nonce" : token_desired_nonce, 
                "amount" : token_desired_amount})
                        

        infos_parsed = {"address_buyer" : address_buyer, "locked_tokens": locked_tokens, "desired_tokens" : desired_tokens}
        
    
        return infos_parsed        


    # token = [token_type["Fungible"], "4d45582d343138336537",num_to_hex(0),"0DE0B6B3A7640000"]


    def swap_info_input(self, tokens) : 
        
        u64_nb_hexa = 16
        output = ""
        for token in tokens : 
            output+=token["type"] # token_type (coded in u8)
            nb_bytes = hex(int(len(token["id"])/2)).split("x")[1]
            output+=("0"*7 + str(nb_bytes) + token["id"]) # token_identifier (with the size)
            size_hexa = len(token["nonce"])
            zeros_to_add = u64_nb_hexa - size_hexa
            output+= "0"*zeros_to_add + token["nonce"]   # Nonce (coded in u64)
            nb_bytes = hex(int(len(token["amount"])/2)).split("x")[1]
            output+=("0"*7 + str(nb_bytes) + token["amount"])    # amount (with the size)


        return output


if Test : 

    formatter = Formatter()
    print(formatter.hex_to_num("056bc75e2d63100000")) # Should return 100000000000000000000 (100*1e18)
    print(formatter.hex_to_text("474e472d386437653035")) # Should return GNG-8d7e05 (GNG fake collection ID)
    print(formatter.text_to_hex("MEX")) # Should return 4d4558
    print(formatter.int_to_BigInt(100, 1000000000000000000)) # Should return 10000000000000000
    print(formatter.num_to_hex(1)) # Should return 01 (the function handles cases when the hex is odd)
