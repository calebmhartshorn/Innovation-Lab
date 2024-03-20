async function fetchInventoryData() {
    try {
        console.log('Fetching inventory data...');
        const response = await fetch('/inventory');

        if (!response.ok) {
            throw new Error(`Failed to fetch inventory data: ${response.status}`);
        }

        const data = await response.json();
        console.log('Inventory data fetched:', data);

        // Call the displayInventory function with the fetched data
        displayInventory(data);

        return data;
    } catch (error) {
        console.error('Error fetching inventory data:', error);
        throw error;
    }
}

async function fetchRecipes(ingredients) {
    try {
        const url = `/recipe?ingredients=${ingredients.toString()}&must=${ingredients[0]}`;
        console.log('Fetching recipes with URL:', url);

        const response = await fetch(url);
        if (!response.ok) {
            throw new Error('Failed to fetch recipes');
        }

        const data = await response.json();
        return data.results;
    } catch (error) {
        console.error('Error fetching recipes:', error);
        throw error;
    }
}

async function updateInventory(jsonData) {
    try {
        const response = await fetch('/update-inventory', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(jsonData),
        });

        if (!response.ok) {
            throw new Error('Failed to update inventory');
        }

        const message = await response.text();
        console.log('Inventory updated:', message);
        return message;
    } catch (error) {
        console.error('Error updating inventory:', error);
        throw error;
    }
}

function displayInventory(inventoryData) {
  const inventorySectionDiv = document.getElementById('inventory-section').querySelector('div');
  inventorySectionDiv.innerHTML = '';

  // Sort items based on expiration_days in ascending order
  const sortedItems = inventoryData.sort((a, b) => {
    if (a.expiration_days === -1 && b.expiration_days === -1) {
      // If both are non-expirable, it sorts them alphabetically
      return a.name.localeCompare(b.name);
    } else if (a.expiration_days === -1) {
      // If a is non-expirable, it places it after expirable items
      return 1;
    } else if (b.expiration_days === -1) {
      // If b is non-expirable, it places it after expirable items
      return -1;
    } else {
      // Sorts expirable items based on expiration_days
      return a.expiration_days - b.expiration_days;
    }
  });

  sortedItems.forEach(item => {
    const productNameDiv = document.createElement('div');
    productNameDiv.classList.add('product-name');
    productNameDiv.textContent = item.name;

    const productQuantityDiv = document.createElement('div');
    productQuantityDiv.classList.add('product-quantity');
    productQuantityDiv.textContent = `${item.quantity_amount} ${item.quantity_unit}`;

    const productExpirationDiv = document.createElement('div');
    productExpirationDiv.classList.add('product-expiration');
    if (item.expiration_days === -1) {
      productExpirationDiv.textContent = 'Non-expirable';
    } else {
      productExpirationDiv.textContent = `Expires in ${item.expiration_days} days`;
    }

    inventorySectionDiv.appendChild(productNameDiv);
    inventorySectionDiv.appendChild(productQuantityDiv);
    //inventorySectionDiv.appendChild(productExpirationDiv);
  });
}

// Call the fetchInventoryData function
fetchInventoryData();
