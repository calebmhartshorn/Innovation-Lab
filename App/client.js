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
  const use_in_0_days = document.getElementById('use-in-0-days')
  const use_in_1_days = document.getElementById('use-in-1-days')
  const use_in_3_days = document.getElementById('use-in-3-days')
  const use_in_7_days = document.getElementById('use-in-7-days')

  use_in_0_days.innerHTML = '';
  use_in_1_days.innerHTML = '';
  use_in_3_days.innerHTML = '';
  use_in_7_days.innerHTML = '';

  // Convert the object into an array of items
  const items = Object.values(inventoryData);

  items.forEach((element, i, arr)=>{
    console.log(element.name)
    element.scans.forEach((scan, i, arr)=>{
      daysLeft = calculateDaysLeft(scan, element.shelf_life)
      console.log(daysLeft)
      
      let productNameDiv = document.createElement('div');
      productNameDiv.classList.add('product-name');
      productNameDiv.textContent = element.name;
  
      let productQuantityDiv = document.createElement('div');
      productQuantityDiv.classList.add('product-quantity');
      productQuantityDiv.textContent = `${element.size} ${element.size_units}`;
      
      let div = use_in_0_days;

      if (daysLeft >= 7) {
        div = use_in_7_days;
      } else if (daysLeft >= 3) {
        div = use_in_3_days;
      } else if (daysLeft >= 1) {
        div = use_in_1_days;
      }

      div.appendChild(productNameDiv);
      div.appendChild(productQuantityDiv);
    });
  })

  // Hide unused sections
  if (!use_in_0_days.hasChildNodes()) {
    use_in_0_days.style.display = 'none';
  }
  if (!use_in_1_days.hasChildNodes()) {
    use_in_1_days.style.display = 'none';
  }
  if (!use_in_3_days.hasChildNodes()) {
    use_in_3_days.style.display = 'none';
  }
  if (!use_in_7_days.hasChildNodes()) {
    use_in_7_days.style.display = 'none';
  }
}

function calculateDaysLeft(dateString, shelfLife) {
  // Parse the given date string into a Date object
  const startDate = new Date(dateString);
  
  // Calculate the expiration date by adding the shelf life to the start date
  const expirationDate = new Date(startDate);
  expirationDate.setDate(startDate.getDate() + shelfLife);

  // Get the current date
  const currentDate = new Date();

  // Calculate the difference in milliseconds between the expiration date and the current date
  const differenceMs = expirationDate - currentDate;

  // Convert milliseconds to days (1 day = 24 * 60 * 60 * 1000 milliseconds)
  const daysLeft = Math.ceil(differenceMs / (1000 * 60 * 60 * 24));

  return daysLeft;
}

// Call the fetchInventoryData function
fetchInventoryData();
