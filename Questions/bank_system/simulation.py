"""
All your implementation code for the bank system simulation goes here.
"""
class Account:
    def __init__(self, timestamp: int, id: str):
        self.id = id
        self.__balance = 0
        self.created_at = timestamp
        return None

    def deposit(self, amount: int) -> None:
        self.__balance += amount
        return None

    def withdraw(self, amount: int) -> None:
            self.__balance -= amount
            return None

    def get_balance(self):
        return self.__balance


class Transaction:
    def __init__(self, timestamp: int, account_id: str, amount: int, type: str, direction: str, payment_id: str | None):
        self.timestamp = timestamp
        self.amount = amount
        self.type = type
        self.direction = direction
        self.account_id = account_id
        self.payment_id = payment_id
        return None


    def set_account_id(self, new_account_id: str) -> None:
        self.account_id = new_account_id
        return None

class Simulation:
    def __init__(self):
        self.accounts = {}
        self.transactions = []
        self.current_payment_id = 0

    def create_account(self, timestamp: int, account_id: str) -> bool | None:
        if not self.exists(account_id):
            self.accounts[account_id] = Account(timestamp=timestamp, id=account_id)
            return True
        return False

    def deposit(self, timestamp: int, account_id: str, amount: int) -> int | None:
        if self.exists(account_id):
            account = self.accounts[account_id]
            account.deposit(amount=amount)
            self.record_transaction(timestamp=timestamp, account_id=account_id, amount=amount, type="deposit", direction="incoming")
            return account.get_balance()
        return None

    def transfer(self, timestamp: int, source_account_id: str, target_account_id: str, amount: int) -> int | None:
        if not self.exists(source_account_id) or not self.exists(target_account_id):
            return None
        if source_account_id == target_account_id:
            return None
        
        source = self.accounts[source_account_id]
        source_balance = source.get_balance()
        if source_balance < amount:
            return None

        target = self.accounts[target_account_id]
        source.withdraw(amount)
        target.deposit(amount)

        self.record_transaction(timestamp=timestamp, account_id=source_account_id, amount=amount, type="transfer", direction="outgoing")
        self.record_transaction(timestamp=timestamp, account_id=target_account_id, amount=amount, type="transfer", direction="incoming")

        return source.get_balance()

    def top_spenders(self, timestamp: int, n: int) -> list[str] | None:
        sums_by_account_id = []
        for account_id, _ in self.accounts.items():
            account_sum = sum([transaction.amount for transaction in self.transactions if transaction.account_id == account_id and transaction.direction == "outgoing"])
            if account_sum > 0:
                record = {'sum': account_sum, 'account_id': account_id}
                sums_by_account_id.append(record)

        sorted_sums = sorted(sums_by_account_id, key=lambda record: record['sum'], reverse=True)
        first_n = sorted_sums[:n]

        string_list = []
        for record in first_n:
            string_list.append(f"{record['account_id']}({record['sum']})")

        return string_list

    def pay(self, timestamp: int, account_id: str, amount: int) -> str | None:
        if not self.exists(account_id):
            return None
        
        account = self.accounts[account_id]
        if account.get_balance() < amount: 
            return None

        account.withdraw(amount=amount)
        id_number = self.current_payment_id + 1
        new_payment_id = f"payment{id_number}"
        self.record_transaction(timestamp=timestamp, account_id=account_id, amount=amount, type="payment", direction="outgoing", payment_id=new_payment_id)
        self.current_payment_id = id_number

        return new_payment_id

    def get_payment_status(self, timestamp: int, account_id: str, payment: str) -> str | None:
        if not self.exists(account_id): 
            return None

        matching_payment = next((transaction for transaction in self.transactions if transaction.account_id == account_id and transaction.payment_id == payment), None)

        if matching_payment is None:
            return None

        process_deadline = matching_payment.timestamp + 86400000

        if timestamp < process_deadline:
            return "IN_PROGRESS"


        cashback = matching_payment.amount * .02
        self.deposit(timestamp=timestamp, account_id=account_id, amount=cashback)
        return "CASHBACK_RECEIVED"
        
    def merge_accounts(self, timestamp: int, account_id_1: str, account_id_2: str) -> bool | None:
        if account_id_1 == account_id_2: 
            return False

        if not self.exists(account_id_1):
            return False

        if not self.exists(account_id_2): 
            return False

        for transaction in self.transactions:
            if transaction.account_id == account_id_2:
                transaction.set_account_id(account_id_1)

        account_1 = self.accounts[account_id_1]
        account_2 = self.accounts[account_id_2]
        balance_2 = account_2.get_balance()
        account_1.deposit(balance_2)

        del account_2
        return True
        

    def get_balance(self, timestamp: int, account_id: str, time_at: int) -> int | None:
        if not self.exists(account_id):
            return None
        account = self.accounts[account_id]

        if account.created_at > time_at: 
            return None

        return account.get_balance()

    def exists(self, account_id: str) -> True | False:
        return account_id in self.accounts

    def record_transaction(self, timestamp: int, account_id: str, amount: int, type: str, direction: str, payment_id=None) -> True:
        new_transaction = Transaction(timestamp=timestamp, account_id=account_id, amount=amount, type=type, direction=direction, payment_id=payment_id)
        self.transactions.append(new_transaction)