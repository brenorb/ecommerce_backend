---
name: verify-checkout-stock
description: Check that placing orders never takes stock for an order that fails and never drives stock below zero, even when customers check out at the same time. Use when changing place_order, add_to_cart or delete_cart in routes/cart.py, the product stock updates in routes/products.py, or the database layer in models.py.
---

# Verify checkout stock

**Properties.** `SoldOnlyByOrders`: a refused order leaves every product's stock as it was. `StockNeverNegative`: no product's stock goes below zero.

**Harm if broken.** Products disappear from the shelf with no order to show for them, or are sold twice.

## Run

```sh
export TLA2TOOLS=/absolute/path/to/tla2tools.jar   # TLC 1.7.4 release
export JAVA=/path/to/java                          # Java 11 or later
bash scripts/verification/check-model.sh .claude/skills/verify-checkout-stock/model/Checkout.tla
bash scripts/verification/check-model.sh .claude/skills/verify-checkout-stock/model/Checkout.tla --mutant
```

Then run `tests/test_order_rules.py` from a scratch directory that contains a copy of `data/sample_products.json`, with the repository on `PYTHONPATH`. The app keeps `data/ecommerce.db` relative to the working directory, so running from the repository writes a database there.

The model must pass (9 distinct states). The `--mutant` run replays the per-item code before commit 2ad169f and must report a violation. With one rule per config, Alice's two-item order takes product `a` and is then refused on `b` (`SoldOnlyByOrders`), and two orders both pass the check for `b` (`StockNeverNegative`). Read every TLC result with the pstack `/statechart` skill.

## Coverage

Synced with the code at commit `fb8d9d4`. Move this forward only after you confirm that the model still describes the code at the new commit.

| Model step | Code (`routes/cart.py`) |
| --- | --- |
| `TakeAll` | `place_order`: `with db.conn:` and the conditional `UPDATE ... AND stock >= ?` |
| `Record` | `db.t.orders.insert`, `delete_cart` |
| `Check`, `Take`, `Advance` | the old per-item loop, used only when `Broken = TRUE` |

Quantities are one unit. `add_to_cart` refuses zero and negative quantities, which the model does not represent.

## Not covered

Authentication of cart and order routes: they take `user_id` from the URL or body, so anyone can act on any cart. Also not covered: product updates during checkout and multiple app processes.
