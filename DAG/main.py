import time
import pprint
import json
import tkinter as tk
from hashlib import sha256


class Transaction:
    def __init__(self, data, lenght):
        # lenght - в эту переменную будет передаваться массив транзакций
        self.index = len(lenght)
        self.data = data
        self.w = 1
        self.sum_w = 1

    def compute_hash(self):
        """
        Функция, возвращающая хэш-сумму
        """
        block_string = json.dumps(self.__dict__, sort_keys=True)
        return sha256(block_string.encode()).hexdigest()


class DAG:
    def __init__(self):
        self.transactions = []
        self.edges = []

    def create_genesis_transaction(self):

        genesis_transaction = Transaction(
            data="initial block", lenght=self.transactions)

        genesis_transaction.connections = None

        self.transactions.append([genesis_transaction.__dict__])

    @property
    def last_transactions(self):
        if(len(self.transactions) == 1):
            return self.transactions[-1:]
        else:
            return self.transactions[-2:]

    def add_new_transaction(self, data):

        new_transaction = Transaction(data=data, lenght=self.transactions)
        new_transaction.index = len(self.transactions)

        connections = [x[0]["index"] for x in self.last_transactions]

        new_transaction.connections = connections
        self.transactions.append([new_transaction.__dict__])

        graph = {x[0]["index"]: x[0]["connections"]
                 for x in self.transactions}

        genesis_weight = 0
        for el in self.transactions:
            genesis_weight += el[0]["w"]

        self.transactions[0][0]["sum_w"] = genesis_weight


net = DAG()
net.create_genesis_transaction()


window = tk.Tk()
window.geometry("600x400")
e1 = tk.Entry(width=23, font=("Helvetica", 24))
lbl = tk.Label(height=22, font=("Montserrat", 10))
lbl.grid(row=1)


def add_tr():
    data = e1.get()
    net.add_new_transaction(data=data)

    text = ""
    for x in net.transactions:
        text = text + str(x[0]) + "\n"
    print(text)
    lbl.configure(text=text)


button = tk.Button(
    text="Отправить",
    width=25,
    height=2,
    command=add_tr
)

button.grid(column=1, row=0)
e1.grid(column=0, row=0)


window.mainloop()
