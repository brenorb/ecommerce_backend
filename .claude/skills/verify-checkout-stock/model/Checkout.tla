------------------------------ MODULE Checkout ------------------------------
\* Two customers placing orders at once (routes/cart.py place_order) on two
\* products with one unit each. Alice's cart has one of each product; Bob's
\* has one of product "b". Each step is one statement of place_order:
\*   Check(c, p)  -> SELECT stock (the old per-item check)
\*   Take(c, p)   -> UPDATE products SET stock = stock - q
\*   TakeAll(c)   -> the fixed transaction: conditional UPDATEs, roll back
\*                   if any item is short
\*   Record(c)    -> insert the order and clear the cart
\* Broken = TRUE is the code before the fix: per-item check, then update,
\* and a short item returned 400 after earlier items were taken.
EXTENDS Naturals, Integers

CONSTANT Broken

Products == {"a", "b"}
Customers == {"alice", "bob"}
Cart == [c \in Customers |-> IF c = "alice" THEN {"a", "b"} ELSE {"b"}]
Order == <<"a", "b">>   \* place_order walks the cart in this order

VARIABLES stock, pc, step, taken, ordered

vars == <<stock, pc, step, taken, ordered>>

Init ==
  /\ stock = [p \in Products |-> 1]
  /\ pc = [c \in Customers |-> "start"]
  /\ step = [c \in Customers |-> 1]
  /\ taken = [c \in Customers |-> {}]
  /\ ordered = {}


\* Old code: check one item, then update it, moving down the cart.
Check(c) ==
  /\ Broken /\ pc[c] \in {"start", "next"} /\ step[c] <= 2
  /\ LET p == Order[step[c]] IN
       IF p \notin Cart[c] THEN /\ step' = [step EXCEPT ![c] = @ + 1] /\ UNCHANGED <<pc, stock, taken, ordered>>
       ELSE IF stock[p] >= 1 THEN /\ pc' = [pc EXCEPT ![c] = "checked"] /\ UNCHANGED <<step, stock, taken, ordered>>
       ELSE /\ pc' = [pc EXCEPT ![c] = "refused"] /\ UNCHANGED <<step, stock, taken, ordered>>

Take(c) ==
  /\ Broken /\ pc[c] = "checked"
  /\ LET p == Order[step[c]] IN
       /\ stock' = [stock EXCEPT ![p] = @ - 1]
       /\ taken' = [taken EXCEPT ![c] = @ \cup {p}]
  /\ step' = [step EXCEPT ![c] = @ + 1]
  /\ pc' = [pc EXCEPT ![c] = IF step[c] = 2 THEN "paid" ELSE "next"]
  /\ UNCHANGED ordered

Advance(c) ==
  /\ Broken /\ pc[c] = "next" /\ step[c] > 2
  /\ pc' = [pc EXCEPT ![c] = "paid"]
  /\ UNCHANGED <<stock, step, taken, ordered>>

TakeAll(c) ==
  /\ ~Broken /\ pc[c] = "start"
  /\ IF \A p \in Cart[c] : stock[p] >= 1
     THEN /\ stock' = [p \in Products |-> IF p \in Cart[c] THEN stock[p] - 1 ELSE stock[p]]
          /\ taken' = [taken EXCEPT ![c] = Cart[c]]
          /\ pc' = [pc EXCEPT ![c] = "paid"]
     ELSE /\ pc' = [pc EXCEPT ![c] = "refused"] /\ UNCHANGED <<stock, taken>>
  /\ UNCHANGED <<step, ordered>>

Record(c) ==
  /\ pc[c] = "paid"
  /\ ordered' = ordered \cup {c} /\ pc' = [pc EXCEPT ![c] = "done"]
  /\ UNCHANGED <<stock, step, taken>>

Stop == (\A c \in Customers : pc[c] \in {"done", "refused"}) /\ UNCHANGED vars

Next == Stop \/ \E c \in Customers : Check(c) \/ Take(c) \/ Advance(c) \/ TakeAll(c) \/ Record(c)

Spec == Init /\ [][Next]_vars

\* Stock leaves the shelf only for orders that are placed.
SoldOnlyByOrders ==
  \A c \in Customers : pc[c] = "refused" => taken[c] = {}

\* Stock never goes below zero.
StockNeverNegative == \A p \in Products : stock[p] >= 0
=============================================================================
