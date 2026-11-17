# Checkout verification

| Skill | What it checks | Tool |
| --- | --- | --- |
| [verify-checkout-stock](../../.claude/skills/verify-checkout-stock/SKILL.md) | Refused orders take no stock; stock never goes negative | TLA+ / TLC, 9 states, plus `tests/test_order_rules.py` |

Fixed along the way:

1. The app could not start: `<str:username>` is not a Flask converter (e53c0bb).
2. Deletes and checkout crashed under the current fastlite, which has no `cursor.rowcount` and returns inserted rows as dicts (7cdfc86, 9cdc3e1).
3. A refused order kept the stock of the items before the short one, and concurrent orders could oversell (2ad169f).
4. Zero and negative cart quantities were accepted and added stock back at checkout (f1f138e).
5. Anyone could register as an admin with `is_admin` (fb8d9d4).

`test_auth.py::test_login`, `test_auth.py::test_logout` and `test_cart.py::test_add_to_cart` still fail. They log in as a user they never register and expect 200 where the route returns 201.

## Order from the shop

Generated with pstack `/statechart` from [Shop.tla](flows/checkout/Shop.tla) ([TLC report](flows/checkout/report.md)).

```mermaid
---
title: "Order from the shop"
---
stateDiagram-v2
  state "Legend" as legend {
    lg0: done
    lg1: shopping
  }
  class lg0 teal
  class lg1 blue
  s0: Browsing products
  s1: Items in the cart
  s2: Order being placed
  s3: Order placed, cart cleared
  [*] --> s0
  s0 --> s1: you add an item
  s1 --> s0: you empty the cart
  s1 --> s2: you place the order
  s2 --> s1: an item is short, nothing is taken
  s2 --> s3: every item is in stock
  class s0 blue
  class s1 blue
  class s2 blue
  class s3 teal
```
