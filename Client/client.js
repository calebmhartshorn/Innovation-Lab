// Function to fetch inventory data
async function fetchInventoryData() {
    try {
        // Perform fetch request to '/inventory'
        const response = await fetch('/inventory');
        if (!response.ok) {
            throw new Error('Failed to fetch inventory data');
        }
        const data = await response.json();
        return data;
    } catch (error) {
        throw new Error('Error fetching inventory data: ' + error.message);
    }
}

// Function to fetch recipes based on ingredients
async function fetchRecipes(ingredients) {
    try {
        // Construct URL for fetching recipes
        const url = `/recipe?ingredients=${ingredients.toString()}&must=${ingredients[0]}`;
        // Perform fetch request to URL
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error('Failed to fetch recipes');
        }
        const data = await response.json();
        return data.results;
    } catch (error) {
        throw new Error('Error fetching recipes: ' + error.message);
    }
}

// Function to update inventory
async function updateInventory(jsonData) {
    try {
        // Perform fetch request to '/update-inventory'
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
        return message;
    } catch (error) {
        throw new Error('Error updating inventory: ' + error.message);
    }
}