-------------------------------- MODULE Shop --------------------------------
\* A customer shopping through the API, as the client sees it.
VARIABLES screen

vars == <<screen>>

Init == screen = "browsing"

AddItem == screen \in {"browsing", "cart"} /\ screen' = "cart"
BadQuantity == screen \in {"browsing", "cart"} /\ screen' = screen
PlaceOrder == screen = "cart" /\ screen' = "placing"
Placed == screen = "placing" /\ screen' = "ordered"
OutOfStock == screen = "placing" /\ screen' = "cart"
EmptyCart == screen = "cart" /\ screen' = "browsing"

Next == AddItem \/ BadQuantity \/ PlaceOrder \/ Placed \/ OutOfStock \/ EmptyCart
        \/ (screen = "ordered" /\ UNCHANGED vars)

Spec == Init /\ [][Next]_vars

Known == screen \in {"browsing", "cart", "placing", "ordered"}
=============================================================================
