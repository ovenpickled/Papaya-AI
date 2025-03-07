import os
import json
import datetime
import uuid
from pathlib import Path

class TransactionProcessor:
    def __init__(self):
        self.transactions_file = os.path.join(os.path.expanduser("~"), "transactions.json")
        self.accounts = {
            "main": {"balance": 5000.00, "currency": "USD"},
            "savings": {"balance": 10000.00, "currency": "USD"},
            "checking": {"balance": 2500.00, "currency": "USD"}
        }
        self._load_transactions()
        
    def _load_transactions(self):
        """Load transaction history from file"""
        try:
            if os.path.exists(self.transactions_file):
                with open(self.transactions_file, 'r') as f:
                    data = json.load(f)
                    self.transactions = data.get("transactions", [])
                    # Update accounts if they exist in the file
                    if "accounts" in data:
                        self.accounts = data["accounts"]
            else:
                self.transactions = []
                self._save_transactions()  # Create the file
        except Exception as e:
            print(f"Error loading transactions: {e}")
            self.transactions = []
            
    def _save_transactions(self):
        """Save transactions and account balances to file"""
        try:
            data = {
                "transactions": self.transactions,
                "accounts": self.accounts,
                "last_updated": datetime.datetime.now().isoformat()
            }
            with open(self.transactions_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving transactions: {e}")
            
    def get_balance(self, account="main"):
        """Get the balance of a specific account"""
        account = account.lower()
        if account in self.accounts:
            return self.accounts[account]
        return None
        
    def send_payment(self, amount, recipient, source_account="main", description=""):
        """Send a payment to a recipient"""
        source_account = source_account.lower()
        
        # Validate the transaction
        if source_account not in self.accounts:
            return {"success": False, "message": f"Account '{source_account}' not found"}
            
        if amount <= 0:
            return {"success": False, "message": "Amount must be greater than zero"}
            
        if self.accounts[source_account]["balance"] < amount:
            return {"success": False, "message": "Insufficient funds"}
            
        # Create transaction record
        transaction_id = str(uuid.uuid4())
        timestamp = datetime.datetime.now().isoformat()
        
        transaction = {
            "id": transaction_id,
            "type": "payment",
            "amount": amount,
            "currency": self.accounts[source_account]["currency"],
            "source_account": source_account,
            "recipient": recipient,
            "description": description,
            "status": "completed",
            "timestamp": timestamp
        }
        
        # Update account balance
        self.accounts[source_account]["balance"] -= amount
        
        # Add to transaction history
        self.transactions.append(transaction)
        
        # Save changes
        self._save_transactions()
        
        return {
            "success": True,
            "message": f"Payment of {amount} {self.accounts[source_account]['currency']} sent to {recipient}",
            "transaction_id": transaction_id,
            "new_balance": self.accounts[source_account]["balance"]
        }
        
    def get_transaction_history(self, account=None, limit=5):
        """Get recent transaction history, optionally filtered by account"""
        filtered_transactions = self.transactions
        
        if account:
            account = account.lower()
            filtered_transactions = [t for t in self.transactions if t.get("source_account") == account]
            
        # Sort by timestamp (newest first) and limit the results
        sorted_transactions = sorted(
            filtered_transactions, 
            key=lambda x: x.get("timestamp", ""), 
            reverse=True
        )
        
        return sorted_transactions[:limit]
