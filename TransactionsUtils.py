from web3 import Web3
from web3.exceptions import ContractLogicError

# Definizione dell'ABI del contratto USDT
USDT_ABI = [
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "_to",
                "type": "address"
            },
            {
                "internalType": "uint256",
                "name": "_value",
                "type": "uint256"
            }
        ],
        "name": "transfer",
        "outputs": [
            {
                "internalType": "bool",
                "name": "",
                "type": "bool"
            }
        ],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]







def WithdrawBalance(recipient_address, amount,SENDER_ADDRESS,PRIVATE_KEY):



    w3 = Web3(Web3.HTTPProvider("https://mainnet.infura.io/v3/82ef994a3a434182982d8d862117aaf4"))

    USDT_ADDRESS = w3.to_checksum_address('0xdac17f958d2ee523a2206206994597c13d831ec7')

    usdt_contract = w3.eth.contract(address=USDT_ADDRESS, abi=USDT_ABI)

    nonce = w3.eth.get_transaction_count(SENDER_ADDRESS)


    amount_wei = w3.to_wei(amount, 'ether')

    recipient_address=w3.to_checksum_address(recipient_address)



    # Crea la transazione
    tx = {
        'nonce': nonce,
        'to': USDT_ADDRESS,
        'value': 0,
        'gas': 2000000,
        'gasPrice': w3.to_wei('50', 'gwei'),
        'data': usdt_contract.encodeABI(fn_name='transfer', args=[recipient_address, amount_wei]),
        'chainId': 1  # Mainnet
    }

    # Firma la transazione con la chiave privata del wallet mittente
    signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)



    # Invia la transazione alla rete Ethereum
    try:
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    except ContractLogicError as e:
        return str(e)


    return tx_hash.hex()
