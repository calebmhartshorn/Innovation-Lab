// Define the initial data
let data = {
  "inventory": [
    {
        "name": "Beans",
        "unique": [
            {
                "expirationDT": "2024-03-12T13:37:27+00:00",
                "uniqueDescription": "Pinto Beans",
                "quantity": {
                    "amount": 4,
                    "unit": "Tin (400g)"
                }
            },
            {
                "expirationDT": "2024-03-12T13:37:27+00:00",
                "uniqueDescription": "Black Beans",
                "quantity": {
                    "amount": 2,
                    "unit": "Tin (400g)"
                }
            },
            {
                "expirationDT": "2025-03-12T13:37:27+00:00",
                "uniqueDescription": "Black Beans",
                "quantity": {
                    "amount": 1,
                    "unit": "Tin (400g)"
                }
            }
        ]
    },
    {
        "name": "Potatoes",
        "unique": [
            {
                "expirationDT": "2023-05-12T13:37:27+00:00",
                "uniqueDescription": "Russet Potatoes",
                "quantity": {
                    "amount": 1000,
                    "unit": "Grams"
                }
            }
        ]
    },
    {
        "name": "Butter",
        "unique": [
            {
                "expirationDT": "2023-04-12T13:37:27+00:00",
                "uniqueDescription": "Salted Butter",
                "quantity": {
                    "amount": 250,
                    "unit": "Grams"
                }
            }
        ]
    } 
]
 };
 
 // Function to render the table
 function renderTable() {
  const container = document.getElementById('dataContainer');
  container.innerHTML = '';
 
  // Loop through each item in the inventory
  data.inventory.forEach((item, index) => {
  // Create a div for the item
  const itemDiv = document.createElement('div');
  itemDiv.className = 'item';
  itemDiv.classList.add('collapsed');
  container.appendChild(itemDiv);
 
  // Create a toggle button for the item
  const toggleButton = document.createElement('button');
  toggleButton.textContent = 'v';
  toggleButton.addEventListener('click', () => {
    itemDiv.classList.toggle('collapsed');
  });
  itemDiv.appendChild(toggleButton);
 
  // Create an input for the item name
  const nameInput = document.createElement('input');
  nameInput.value = item.name;
  nameInput.addEventListener('input', () => {
    // Update the item name in the data object
    data.inventory[index].name = nameInput.value;
   });
  itemDiv.appendChild(nameInput);
 
  // Create a button to delete the section
  const deleteButton = document.createElement('button');
  deleteButton.textContent = '-';
  deleteButton.addEventListener('click', () => {
    // Remove the section from the data object
    data.inventory.splice(index, 1);
    // Re-render the table
    renderTable();
  });
  itemDiv.appendChild(deleteButton);
 
  // Create a button to add a new item
  const addButton = document.createElement('button');
  addButton.textContent = '+';
  addButton.addEventListener('click', () => {
    addUniqueItem(item.name);
  });
  itemDiv.appendChild(addButton);
 
  // Create a div for the item's unique items
  const uniqueItemsDiv = document.createElement('div');
  uniqueItemsDiv.className = 'unique-items';
  itemDiv.appendChild(uniqueItemsDiv);
 
  // Loop through each unique item in the item
  item.unique.forEach((uniqueItem, uniqueIndex) => {
    // Create a div for the unique item
    const uniqueItemDiv = document.createElement('div');
    uniqueItemsDiv.appendChild(uniqueItemDiv);
 
    // Create input fields for the unique item's properties
    const descriptionField = document.createElement('input');
    descriptionField.value = uniqueItem.uniqueDescription;
    descriptionField.addEventListener('input', () => {
      // Update the unique description in the data object
      data.inventory[index].unique[uniqueIndex].uniqueDescription = descriptionField.value;
    });
    uniqueItemDiv.appendChild(descriptionField);
 
    const expirationDateField = document.createElement('input');
    expirationDateField.value = uniqueItem.expirationDT;
    expirationDateField.addEventListener('input', () => {
      // Update the expiration date in the data object
      data.inventory[index].unique[uniqueIndex].expirationDT = expirationDateField.value;
    });
    uniqueItemDiv.appendChild(expirationDateField);
 
    const quantityAmountField = document.createElement('input');
    quantityAmountField.value = uniqueItem.quantity.amount;
    quantityAmountField.addEventListener('input', () => {
      // Update the quantity amount in the data object
      data.inventory[index].unique[uniqueIndex].quantity.amount = parseInt(quantityAmountField.value);
    });
    uniqueItemDiv.appendChild(quantityAmountField);
 
    const quantityUnitField = document.createElement('input');
    quantityUnitField.value = uniqueItem.quantity.unit;
    quantityUnitField.addEventListener('input', () => {
      // Update the quantity unit in the data object
      data.inventory[index].unique[uniqueIndex].quantity.unit = quantityUnitField.value;
    });
    uniqueItemDiv.appendChild(quantityUnitField);
 
    // Create a button to delete the unique item
    const deleteButton = document.createElement('button');
    deleteButton.textContent = '-';
    deleteButton.addEventListener('click', () => {
      // Remove the unique item from the data object
      data.inventory[index].unique.splice(uniqueIndex, 1);
      // Re-render the table
      renderTable();
    });
    uniqueItemDiv.appendChild(deleteButton);
  });
  });
 }
 
 // Function to add a new section
 function addSection() {
  // Add the new section to the data object
  data.inventory.unshift({
  name: '',
  unique: []
  });
  // Re-render the table
  renderTable();
 }
 
 // Function to add a new unique item
 function addUniqueItem(categoryName) {
  // Find the category in the data object
  const category = data.inventory.find(item => item.name === categoryName);
  // Add the new unique item to the category
  category.unique.push({
  expirationDT: "",
  uniqueDescription: "",
  quantity: {
    amount: 0,
    unit: ""
  }
  });
  // Re-render the table
  renderTable();
 }
 
 // Function to export the data
 function exportData() {
  // Convert the table data to JSON
  const jsonData = convertTableToJson();
 
  // Output the JSON data
  document.getElementById('jsonOutput').value = JSON.stringify(jsonData, null, 2);
 }
 
// Function to convert the table data to JSON
function convertTableToJson() {
  // Initialize the JSON data
  const jsonData = {
  inventory: []
  };
 
  // Loop through each item div
  document.querySelectorAll('.item').forEach(itemDiv => {
  // Initialize the item data
  const itemData = {
   name: itemDiv.querySelector('input').value,
   unique: []
  };
 
  // Loop through each unique item div
  itemDiv.querySelectorAll('.unique-items div').forEach(uniqueItemDiv => {
   // Initialize the unique item data
   const uniqueItemData = {
     uniqueDescription: uniqueItemDiv.querySelector('input').value,
     expirationDT: uniqueItemDiv.querySelector('input:nth-child(2)').value,
     quantity: {
       amount: parseInt(uniqueItemDiv.querySelector('input:nth-child(3)').value),
       unit: uniqueItemDiv.querySelector('input:nth-child(4)').value
     }
   };
 
   // Add the unique item data to the item data
   itemData.unique.push(uniqueItemData);
  });
 
  // Add the item data to the JSON data
  jsonData.inventory.push(itemData);
  });
 
  return jsonData;
 }
 
 // Render the table with the initial data
 renderTable();
 
 // Add an event listener to the export button
 document.getElementById('exportButton').addEventListener('click', exportData);
 // Add an event listener to the add section button
 document.getElementById('addSectionButton').addEventListener('click', addSection);
 
