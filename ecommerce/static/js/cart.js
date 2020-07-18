let updateBtns = document.getElementsByClassName("update-cart");

for (i = 0; i < updateBtns.length; i++) {
  updateBtns[i].addEventListener("click", function () {
    var productId = this.dataset.product;
    var action = this.dataset.action;
    console.log("productId:", productId, "Action:", action);

    console.log("USER:", user);

    addCookieItem(productId, action);
    updateUserOrder(productId, action);
  });
}

function updateUserOrder(productId, action, additionalQt) {
  if (additionalQt && additionalQt != null) {
    additionalQt = parseInt(additionalQt);
  }

  var url = "/update_item/";

  fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrftoken,
    },
    body: JSON.stringify({
      productId: productId,
      action: action,
      additionalQt: additionalQt,
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      console.log("data:", data);
      // To see changes appear in our cart immediately once we render them:
      location.reload();
    });
}

function addCookieItem(productId, action, additionalQt = null) {
  if (additionalQt && additionalQt != null) {
    additionalQt = parseInt(additionalQt);
  }

  if (action == "add") {
    if (cart[productId] == undefined) {
      if (additionalQt != null) {
        cart[productId] = { "quantity": additionalQt };
      } else {
        cart[productId] = { "quantity": 1 };
      }
    } else {
      if (additionalQt != null) {
        cart[productId]["quantity"] += additionalQt;
      } else {
        cart[productId]["quantity"] += 1;
      }
    }
  }

  if (action == "remove") {
    cart[productId]["quantity"] -= 1;

    if (cart[productId]["quantity"] <= 0) {
      console.log("Item will be deleted.");
      delete cart[productId];
    }
  }

  console.log("CART:", cart);
  document.cookie = "cart=" + JSON.stringify(cart) + ";domain=;path=/";

  location.reload();
}
