document.addEventListener("DOMContentLoaded", function () {
  // уведомления
  const showAlert = (message, type = "info") => {
    const alertContainer = document.getElementById("alert-container");
    if (!alertContainer) return;

    const alertDiv = document.createElement("div");
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.role = "alert";
    alertDiv.innerHTML = `${message}<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>`;

    alertContainer.prepend(alertDiv);
    setTimeout(() => alertDiv.remove(), 5000);
  };

  // страница аутентификации - login.html и register.html
  const loginForm = document.getElementById("login-form");
  const registerForm = document.getElementById("register-form");

  if (registerForm) {
    registerForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const username = registerForm.querySelector("#username").value;
      const password = registerForm.querySelector("#password").value;
      const errorMessageDiv = registerForm.querySelector("#error-message");

      const response = await fetch("/api/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });

      const data = await response.json();
      if (response.ok && data.status === "success") {
        showAlert(
          "Регистрация завершена, теперь вы можете войти в систему",
          "success",
        );
        setTimeout(() => {
          window.location.href = "/login";
        }, 1000);
      } else {
        errorMessageDiv.textContent = data.message || "Неизвестная ошибка";
        errorMessageDiv.style.display = "block";
      }
    });
  }

  if (loginForm) {
    loginForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const username = loginForm.querySelector("#username").value;
      const password = loginForm.querySelector("#password").value;
      const errorMessageDiv = loginForm.querySelector("#error-message");

      const response = await fetch("/api/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });

      if (response.ok) {
        window.location.href = "/";
      } else {
        const data = await response.json();
        errorMessageDiv.textContent = data.message || "Неизвестная ошибка";
        errorMessageDiv.style.display = "block";
      }
    });
  }

  // основная страница приложения - index.html

  const mainAppPage = document.getElementById("welcome-message");
  if (mainAppPage) {
    const logoutBtn = document.getElementById("logout-btn");
    const productSearchInput = document.getElementById("product-search");
    const searchResultsContainer = document.getElementById("search-results");
    const addItemForm = document.getElementById("add-item-form");
    const selectedProductIdInput = document.getElementById(
      "selected-product-id",
    );
    const selectedProductNameInput = document.getElementById(
      "selected-product-name",
    );
    const productWeightInput = document.getElementById("product-weight");
    const rationItemsTable = document.getElementById("ration-items-table");
    const rationTotalsTable = document.getElementById("ration-totals-table");
    const evaluateRationBtn = document.getElementById("evaluate-ration-btn");
    const evaluationResult = document.getElementById("evaluation-result");
    let debounceTimer;

    // принимает данные о рационе и отрисовывает таблицы
    const renderRation = (data) => {
      rationItemsTable.innerHTML = "";
      data.items.forEach((item) => {
        const row = `<tr>
                    <td>${item.name}</td>
                    <td>${item.weight}</td>
                    <td>${item.calories}</td>
                    <td>${item.proteins}</td>
                    <td>${item.fats}</td>
                    <td>${item.carbs}</td>
                    <td>
                        <button class="btn btn-danger btn-sm delete-item-btn" data-item-id="${item.id}">
                            &times;
                        </button>
                    </td>
                </tr>`;
        rationItemsTable.innerHTML += row;
      });

      rationTotalsTable.innerHTML = `<tr>
                <td><b>ИТОГО:</b></td>
                <td></td>
                <td><b>${data.totals.calories}</b></td>
                <td><b>${data.totals.proteins}</b></td>
                <td><b>${data.totals.fats}</b></td>
                <td><b>${data.totals.carbs}</b></td>
                <td></td>
            </tr>`;
    };

    // загружает рацион при первоначальной загрузке страницы
    const loadInitialRation = async () => {
      const today = new Date().toISOString().split("T")[0];
      const response = await fetch(`/api/rations/${today}`, {
        credentials: "same-origin",
      });

      if (!response.ok) {
        if (response.status === 401) window.location.href = "/login";
        return;
      }
      const data = await response.json();
      renderRation(data);
    };

    // кнопка выхода
    logoutBtn.addEventListener("click", async () => {
      await fetch("/api/logout", { credentials: "same-origin" });
      window.location.href = "/login";
    });

    // поиск продуктов
    productSearchInput.addEventListener("input", (e) => {
      clearTimeout(debounceTimer);
      const query = e.target.value;
      if (query.length < 2) {
        searchResultsContainer.innerHTML = "";
        return;
      }
      debounceTimer = setTimeout(async () => {
        const response = await fetch(`/api/products?q=${query}`, {
          credentials: "same-origin",
        });
        const products = await response.json();
        searchResultsContainer.innerHTML = "";
        products.forEach((product) => {
          const item = document.createElement("a");
          item.href = "#";
          item.className = "list-group-item list-group-item-action";
          item.textContent = product.name;
          item.addEventListener("click", (ev) => {
            ev.preventDefault();
            selectedProductIdInput.value = product.id;
            selectedProductNameInput.value = product.name;
            searchResultsContainer.innerHTML = "";
            productSearchInput.value = "";
          });
          searchResultsContainer.appendChild(item);
        });
      }, 300);
    });

    // добавление продукта
    addItemForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const productId = selectedProductIdInput.value;
      const weight = productWeightInput.value;
      const today = new Date().toISOString().split("T")[0]; // фикс на случай рассинхрона часовых поясов для UTC -> MSK

      if (!productId || !weight) {
        showAlert("Выберите продукт и укажите его вес (в граммах)", "warning");
        return;
      }

      const response = await fetch("/api/rations/items", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          product_id: productId,
          weight: weight,
          date: today,
        }),
        credentials: "same-origin",
      });

      const data = await response.json();
      if (response.ok) {
        showAlert("Продукт добавлен", "success");
        addItemForm.reset();
        selectedProductNameInput.value = "";
        renderRation(data);
      } else {
        showAlert(data.message || "Ошибка добавления продукта", "danger");
      }
    });

    // оценка рациона
    evaluateRationBtn.addEventListener("click", async () => {
      evaluationResult.textContent = "Идет оценка ...";
      const today = new Date().toISOString().split("T")[0];

      const response = await fetch("/api/rations/evaluate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ date: today }),
        credentials: "same-origin",
      });

      const data = await response.json();
      if (response.ok) {
        evaluationResult.textContent = `Оценка: ${data.evaluation}`;
        if (data.evaluation.includes("Дефицит")) {
          evaluationResult.className = "mt-2 fw-bold text-primary";
        } else if (data.evaluation.includes("Сбалансированный")) {
          evaluationResult.className = "mt-2 fw-bold text-success";
        } else {
          evaluationResult.className = "mt-2 fw-bold text-danger";
        }
      } else {
        evaluationResult.textContent = `Ошибка: ${data.message || "Не удалось получить оценку"}`;
        evaluationResult.className = "mt-2 fw-bold text-warning";
      }
    });

    loadInitialRation();

    // удаление продукта из рациона
    rationItemsTable.addEventListener("click", async (e) => {
      if (e.target && e.target.classList.contains("delete-item-btn")) {
        const itemId = e.target.dataset.itemId;

        const response = await fetch(`/api/rations/items/${itemId}`, {
          method: "DELETE",
          credentials: "same-origin",
        });

        const data = await response.json();
        if (response.ok) {
          showAlert("Продукт удален из рациона", "info");
          renderRation(data);
        } else {
          showAlert(data.message || "Ошибка удаления продукта", "danger");
        }
      }
    });
  }
});
