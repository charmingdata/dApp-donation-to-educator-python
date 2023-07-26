import { ethers } from "https://cdn-cors.ethers.io/lib/ethers-5.7.2.esm.min.js";

const CONTRACT_ADDRESS = "0x98544219dd60eCc071302dAfBfce22F74334f244";

const CONTRACT_ABI = [
  {
    inputs: [],
    stateMutability: "payable",
    type: "constructor",
  },
  {
    anonymous: false,
    inputs: [
      {
        indexed: true,
        internalType: "uint256",
        name: "amount",
        type: "uint256",
      },
      {
        indexed: false,
        internalType: "string",
        name: "reason",
        type: "string",
      },
      {
        indexed: false,
        internalType: "address",
        name: "donatorAddress",
        type: "address",
      },
      {
        indexed: false,
        internalType: "uint256",
        name: "timestamp",
        type: "uint256",
      },
    ],
    name: "LogData",
    type: "event",
  },
  {
    inputs: [
      {
        internalType: "string",
        name: "donationReason",
        type: "string",
      },
    ],
    name: "offerDonation",
    outputs: [],
    stateMutability: "payable",
    type: "function",
  },
  {
    inputs: [],
    name: "onlineEducator",
    outputs: [
      {
        internalType: "address payable",
        name: "",
        type: "address",
      },
    ],
    stateMutability: "view",
    type: "function",
  },
];

// targets zkEVM chain
const targetNetworkId = "0x5a2";

// checks if current chain matches with the one we need
const checkNetwork = async () => {
  if (window.ethereum) {
    const currentChainId = await window.ethereum.request({
      method: "eth_chainId",
    });

    // return true if network id is the same
    if (currentChainId == targetNetworkId) {
      console.log("true");
      return true;
    }
    // return false if network id is different and switch network
    console.log("false");

    await window.ethereum.request({
      method: "wallet_switchEthereumChain",
      params: [{ chainId: targetNetworkId }],
    });
    window.location.reload();
  }
};
window.checkNetwork = checkNetwork;

const provider = new ethers.providers.Web3Provider(window.ethereum);
await provider.send("eth_requestAccounts", []);
const signer = provider.getSigner();
const contract = new ethers.Contract(CONTRACT_ADDRESS, CONTRACT_ABI, signer);

async function sendTransaction(reason, amount) {
  // create transaction
  const unsignedTrx = await contract.populateTransaction.offerDonation(reason, {
    value: amount,
  });
  console.log("Transaction created");

  // send transaction via signer so it's automatically signed
  const txResponse = await signer.sendTransaction(unsignedTrx);

  console.log(`Transaction signed and sent: ${txResponse.hash}`);
  // wait for block
  await txResponse.wait(1);
  console.log(
    `Transaction has been mined. You can view it here: https://testnet-zkevm.polygonscan.com/tx/${txResponse.hash}`
  );
}
// expose the transaction to the clientside callback
window.sendTransaction = sendTransaction;
