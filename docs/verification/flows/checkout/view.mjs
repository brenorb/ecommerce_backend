export const title = "Order from the shop";
export const state = (v) => ({
  browsing: "Browsing products",
  cart: "Items in the cart",
  placing: "Order being placed",
  ordered: "Order placed, cart cleared",
}[v.screen]);
const steps = {
  AddItem: "you add an item",
  PlaceOrder: "you place the order",
  Placed: "every item is in stock",
  OutOfStock: "an item is short, nothing is taken",
  EmptyCart: "you empty the cart",
};
export const step = (action) => steps[action] ?? null;
export const group = (v) => (v.screen === "ordered" ? "done" : "shopping");
export const colors = { done: "teal", shopping: "blue" };
