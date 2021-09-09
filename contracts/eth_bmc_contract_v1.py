// SPDX-License-Identifier: GPL-3.0

pragma solidity >=0.7.0 <0.9.0;

/** 
 * @title BMC (Buy Me Crypto)
 * @dev implements open and transparent pateron for those who wanna earn living by what they love to do.
 */
contract BuyMeCrypto {
    
     // Instantiate a variable to hold the account address of the contract administrator
    address public owner;
    uint256 public creator_count = 0;
    uint256 public support_count = 0;
    
    struct Creator {
        uint id;   // index of the creator account
        string name;   // short name (up to 32 bytes)
        uint256 balance; // creator's account balanc
        address payable creator_address; // creator's wallet address
        
    }
    
    struct Support {
        uint creator_id;
        uint256 balance;
        address supporter_address;
        
    }
  
    mapping (uint256 => Creator) public creators;
    mapping (uint256 => Support) public supports_hub;
    
    // Events allow clients to react to specific
    // contract changes you declare
    event Sent(address from, address to, uint amount);


    

    

    
    
    function create_creator_account(string memory _creatorNames) public {
        creators[creator_count].id = creator_count;
        creators[creator_count].name = _creatorNames;
        creators[creator_count].balance = 0;
        creators[creator_count].creator_address = payable(msg.sender);

        // increase creator_count by 1
        creator_count += 1;
    }
    
    function get_creator_info(uint _creator_id) public view returns (uint, string memory, uint, address){
        return (creators[_creator_id].id, creators[_creator_id].name, msg.sender.balance, creators[_creator_id].creator_address);
    }
    
    
    // entrypoint for sending coins to creator_address 
    function support_creator(uint creator_id) public payable {
        address payable _to = creators[creator_id].creator_address;
        (bool sent, bytes memory data) = _to.call{value: msg.value}("");
        require(sent, "Failed to send Ether");
    }
    
       
}
