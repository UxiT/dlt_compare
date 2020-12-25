import time
import random
import json
from hashlib import sha256
import tkinter as tk


class Transaction:
    def __init__(self, timestamp, transaction, prev_hash_1, prev_hash_2):
        self.timestamp = timestamp
        self.transaction = transaction
        self.prev_hash_1 = prev_hash_1
        self.prev_hash_2 = prev_hash_2


class Node:
    def __init__(self, node_id):
        self.node_id = node_id
        self.events = []


class Hashgrpah:
    def __init__(self, nodes):
        self.nodes = nodes

    def init_transaction(self, node, data):

        if(node.events):
            """
            Если в узле есть предущие события,
            то вычисляется их хэш-сумма. Иначе
            None
            """
            prev_event_string = json.dumps(node.events[-1].__dict__)
            prev_hash_own = sha256(prev_event_string.encode()).hexdigest()
        else:
            prev_hash_own = None

        new_transaction = Transaction(
            timestamp=time.time(),
            transaction=data,
            prev_hash_1=prev_hash_own,
            prev_hash_2=None
        )

        node.events.append(new_transaction)

    def send_transaction(self, outcome_node, income_node):
        data = outcome_node.events[-1].transaction
        prev_alien_string = json.dumps(outcome_node.events[-1].__dict__)
        prev_alien_hash = sha256(prev_alien_string.encode()).hexdigest()

        if(income_node.events):
            prev_own_str = json.dumps(income_node.events[-1].__dict__)
            prev_own_hash = sha256(prev_own_str.encode()).hexdigest()
        else:
            prev_own_hash = None

        income_transaction = Transaction(
            timestamp=time.time(),
            transaction=data,
            prev_hash_1=prev_own_hash,
            prev_hash_2=prev_alien_hash
        )

        income_node.events.append(income_transaction)


A = Node("A")
B = Node("B")
C = Node("C")
D = Node("D")


hg = Hashgrpah(nodes=[A, B, C, D])

nodes = hg.nodes
print(nodes)
node_d = [x.__dict__["node_id"] for x in hg.nodes]
print(node_d)


window = tk.Tk()
# window.geometry("600x400")
e1 = tk.Entry(width=18, font=("Helvetica", 24))
e2 = tk.Entry(width=5, font=("Helvetica", 24), text="1")
lbl1 = tk.Label(height=2, font=("Montserrat", 8), text="A", fg="#A50005")
lbl2 = tk.Label(height=2, font=("Montserrat", 8))
lbl3 = tk.Label(height=2, font=("Montserrat", 8))
lbl4 = tk.Label(height=2, font=("Montserrat", 8))

lbl5 = tk.Label(height=2, font=("Montserrat", 8), text="B", fg="#A50005")
lbl6 = tk.Label(height=2, font=("Montserrat", 8))
lbl7 = tk.Label(height=2, font=("Montserrat", 8))
lbl8 = tk.Label(height=2, font=("Montserrat", 8))

lbl9 = tk.Label(height=2, font=("Montserrat", 8), text="C", fg="#A50005")
lbl10 = tk.Label(height=2, font=("Montserrat", 8))
lbl11 = tk.Label(height=2, font=("Montserrat", 8))
lbl12 = tk.Label(height=2, font=("Montserrat", 8))

lbl13 = tk.Label(height=2, font=("Montserrat", 8), text="D", fg="#A50005")
lbl14 = tk.Label(height=2, font=("Montserrat", 8))
lbl15 = tk.Label(height=2, font=("Montserrat", 8))
lbl16 = tk.Label(height=2, font=("Montserrat", 8))

lbl1.grid(row=1, column=0)
lbl2.grid(row=2, column=0)
lbl3.grid(row=3, column=0)
lbl4.grid(row=4, column=0)

lbl5.grid(row=5, column=0)
lbl6.grid(row=6, column=0)
lbl7.grid(row=7, column=0)
lbl8.grid(row=8, column=0)

lbl9.grid(row=9, column=0)
lbl10.grid(row=10, column=0)
lbl11.grid(row=11, column=0)
lbl12.grid(row=12, column=0)

lbl13.grid(row=13, column=0)
lbl14.grid(row=14, column=0)
lbl15.grid(row=15, column=0)
lbl16.grid(row=16, column=0)


def add_transaction():
    data = e1.get()
    try:
        index = node_d.index(e2.get())
    except BaseException:
        pass

    node = hg.nodes[index]
    hg.init_transaction(node=node, data=data)

    temp_nodes = hg.nodes[:]
    temp_nodes.remove(node)
    while (temp_nodes):
        target = random.choice(temp_nodes)
        hg.send_transaction(outcome_node=node, income_node=target)
        temp_nodes.remove(target)

    text = []

    timestamps = []
    datas = []
    prev_hash1 = []
    prev_hash2 = []

    for i in range(4):
        timestamps.append([x.__dict__["timestamp"]
                           for x in hg.nodes[i].events])
        datas.append([x.__dict__["transaction"] for x in hg.nodes[i].events])
        prev_hash1.append([(x.__dict__["prev_hash_1"])
                           for x in hg.nodes[i].events])
        prev_hash2.append([x.__dict__["prev_hash_2"]
                           for x in hg.nodes[i].events])

    lbl1.configure(text=timestamps[0])
    lbl2.configure(text=datas[0])
    lbl3.configure(text=prev_hash1[0])
    lbl4.configure(text=prev_hash2[0])

    lbl5.configure(text=timestamps[1])
    lbl6.configure(text=datas[1])
    lbl7.configure(text=prev_hash1[1])
    lbl8.configure(text=prev_hash2[1])

    lbl9.configure(text=timestamps[2])
    lbl10.configure(text=datas[2])
    lbl11.configure(text=prev_hash1[2])
    lbl12.configure(text=prev_hash2[2])

    lbl13.configure(text=timestamps[3])
    lbl14.configure(text=datas[3])
    lbl15.configure(text=prev_hash1[3])
    lbl16.configure(text=prev_hash2[3])


button = tk.Button(
    text="Отправить",
    width=25,
    height=2,
    command=add_transaction
)

button.grid(column=4, row=0)
e1.grid(column=0, row=0)
e2.grid(column=1, row=0)


window.mainloop()
