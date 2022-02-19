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


    # Note : For this current version, this function is fine. However for futur releases it will need to be updated
    def tx_infos_parser(self, tx_infos) : 


        number_of_field = 3
        sizes = re.findall('0{6}[0-9a-f][1-9a-f]', tx_infos)
        lock_token_number = int(sizes[0])
        desired_token_number = int(sizes[lock_token_number*number_of_field+1])
        
        infos = re.split('0{6}[0-9a-f][1-9a-f]', tx_infos)
        addr_buyer = infos[0]
        locked_tokens = []
        start_index = 2
        for i in range(lock_token_number) : 

            token = {"amount" : self.hex_to_num(infos[start_index+i*number_of_field]), 
                    "id" : self.hex_to_text(infos[start_index+1+i*number_of_field]), 
                    "nonce" : self.hex_to_num(infos[start_index+2+i*number_of_field])}        
            
            locked_tokens.append(token)
        
        desired_tokens = []
        start_index = lock_token_number*number_of_field+3
        for j in range(desired_token_number) : 
            
            token = {"amount" : self.hex_to_num(infos[start_index+j*number_of_field]), 
                    "id" : self.hex_to_text(infos[start_index+1+j*number_of_field]), 
                    "nonce" : self.hex_to_num(infos[start_index+2+j*number_of_field])}
            
            desired_tokens.append(token)
            

        infos_parsed = {"address_buyer" : addr_buyer, "locked_tokens": locked_tokens, "desired_tokens" : desired_tokens}
        
    
        return infos_parsed        


    def swap_info_input(self, tokens) : 

        output = ""
        for token in tokens : 
            for token_info in ["amount", "id", "nonce"]: 
                nb_bytes = hex(int(len(token[token_info])/2)).split("x")[1]
                output+=("0"*7 + str(nb_bytes) + token[token_info])

        return output


if Test : 

    formatter = Formatter()
    print(formatter.hex_to_num("056bc75e2d63100000")) # Should return 100000000000000000000 (100*1e18)
    print(formatter.hex_to_text("474e472d386437653035")) # Should return GNG-8d7e05 (GNG fake collection ID)
    print(formatter.text_to_hex("MEX")) # Should return 4d4558
    print(formatter.int_to_BigInt(100, 1000000000000000000)) # Should return 10000000000000000
    print(formatter.num_to_hex(1)) # Should return 01 (the function handles cases when the hex is odd)
