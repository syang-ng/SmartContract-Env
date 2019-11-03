pragma solidity ^0.4.24;

contract base {
  address owner;
}

contract Challenge is base{
    event GetFlag(string b64email); 
    
    function payforflag(string b64email) public {
        emit GetFlag(b64email);
    }
}