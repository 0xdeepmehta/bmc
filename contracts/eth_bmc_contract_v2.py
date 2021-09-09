// SPDX-License-Identifier: GPL-3.0

pragma solidity >=0.7.0 <0.9.0;

/** 
 * @title BMC (Buy Me Crypto)
 * @dev implements open and transparent pateron for those who wanna earn living by what they love to do.
 */
contract BuyMeCrypto {

    address payable[] public creators;
    
    // get specific creator's address
    function get(uint i) public view returns (address) {
        return creators[i];
    }

    // get all creator's address
    function getArr() public view returns (address payable[] memory) {
        return creators;
    }
    
    // create creator's account
    function create_creator_account() public {
        creators.push(payable(msg.sender));
    }
    
    // entrypoint for sending coins to creator's address 
    function support_creator(address payable _creator_address) public payable {
        (bool sent, bytes memory data) = _creator_address.call{value: msg.value}("");
        require(sent, "Failed to send Ether");
    }
    
       
}
