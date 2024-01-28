class InventoryManager {
  constructor(data) {
    this.data = data;
  }
 
  renderTable() {
    const container = document.getElementById('dataContainer');
    container.innerHTML = '';
 
    this.data.inventory.forEach((item, index) => {
      const itemDiv = document.createElement('div');
      itemDiv.className = 'item';
      itemDiv.classList.add('collapsed');
      container.appendChild(itemDiv);
 
      const toggleButton = document.createElement('button');
      toggleButton.textContent = 'v';
      toggleButton.addEventListener('click', () => {
        itemDiv.classList.toggle('collapsed');
        if (itemDiv.classList.contains('collapsed')) {
          toggleButton.textContent = 'v';

        } else {
          toggleButton.textContent = '>';

        }
      });
      itemDiv.appendChild(toggleButton);
 
      const nameInput = document.createElement('input');
      nameInput.value = item.name;
      nameInput.addEventListener('input', () => {
        this.data.inventory[index].name = nameInput.value;
      });
      itemDiv.appendChild(nameInput);
 
      const deleteButton = document.createElement('button');
      deleteButton.textContent = '-';
      deleteButton.addEventListener('click', () => {
        this.data.inventory.splice(index, 1);
        this.renderTable();
      });
      itemDiv.appendChild(deleteButton);
 
      const addButton = document.createElement('button');
      addButton.textContent = '+';
      addButton.addEventListener('click', () => {
        this.addUniqueItem(item.name);
      });
      itemDiv.appendChild(addButton);
 
      const uniqueItemsDiv = document.createElement('div');
      uniqueItemsDiv.className = 'unique-items';
      itemDiv.appendChild(uniqueItemsDiv);
 
      item.unique.forEach((uniqueItem, uniqueIndex) => {
        const uniqueItemDiv = document.createElement('div');
        uniqueItemsDiv.appendChild(uniqueItemDiv);
 
        const descriptionField = document.createElement('input');
        descriptionField.value = uniqueItem.uniqueDescription;
        descriptionField.addEventListener('input', () => {
          this.data.inventory[index].unique[uniqueIndex].uniqueDescription = descriptionField.value;
        });
        uniqueItemDiv.appendChild(descriptionField);
 
        const expirationDateField = document.createElement('input');
        expirationDateField.value = uniqueItem.expirationDT;
        expirationDateField.type = "date"
        expirationDateField.addEventListener('input', () => {
          this.data.inventory[index].unique[uniqueIndex].expirationDT = expirationDateField.value;
        });
        uniqueItemDiv.appendChild(expirationDateField);
 
        const quantityAmountField = document.createElement('input');
        quantityAmountField.value = uniqueItem.quantity.amount;
        quantityAmountField.addEventListener('input', () => {
          this.data.inventory[index].unique[uniqueIndex].quantity.amount = parseInt(quantityAmountField.value);
        });
        uniqueItemDiv.appendChild(quantityAmountField);
 
        const quantityUnitField = document.createElement('select');

        const units = ["Grams", "Units", "Pints"]; // Array of options
        units.forEach((unit) => {
          let option = document.createElement('option');
          option.value = unit;
          option.text = unit;
          quantityUnitField.appendChild(option);
        });
        
        // Set the value after the options have been appended
        quantityUnitField.value = uniqueItem.quantity.unit;
        
        quantityUnitField.addEventListener('change', () => {
          this.data.inventory[index].unique[uniqueIndex].quantity.unit = quantityUnitField.value;
        });
        
        uniqueItemDiv.appendChild(quantityUnitField);
        
 
        const deleteButton = document.createElement('button');
        deleteButton.textContent = '-';
        deleteButton.addEventListener('click', () => {
          this.data.inventory[index].unique.splice(uniqueIndex, 1);
          this.renderTable();
        });
        uniqueItemDiv.appendChild(deleteButton);
      });
    });
    document.querySelectorAll('input').forEach(input => {
      input.addEventListener('input', this.exportData.bind(this));
    })
    document.querySelectorAll('button').forEach(input => {
      input.addEventListener('click', this.exportData.bind(this));
    })
    document.querySelectorAll('select').forEach(input => {
      input.addEventListener('change', this.exportData.bind(this));
    })
  }
 
  addSection() {
    this.data.inventory.unshift({
      name: '',
      unique: []
    });
    this.renderTable();
    }
  addItem(name) {
     this.data.inventory.push({
            name: name,
            unique: []
        });
        this.renderTable();
    }
 
  addUniqueItem(categoryName) {
    const category = this.data.inventory.find(item => item.name === categoryName);
    category.unique.push({
      expirationDT: "",
      uniqueDescription: "",
      quantity: {
        amount: 0,
        unit: ""
      }
    });
    this.renderTable();
  }
 

  addUnique(name, uniqueObject) {
    var itemExists = this.data.inventory.some(function(item) {
       if(item.name === name) {
         item.unique.push(uniqueObject);
         return true;
       }
    });
   
    if(!itemExists) {
      this.data.inventory.push({
         name: name,
         unique: [uniqueObject]
       });
    }
    this.renderTable();
   }
 
  convertTableToJson() {
    const jsonData = {
      inventory: []
    };
 
    document.querySelectorAll('.item').forEach(itemDiv => {
      const itemData = {
        name: itemDiv.querySelector('input').value,
        unique: []
      };
 
      itemDiv.querySelectorAll('.unique-items div').forEach(uniqueItemDiv => {
        const uniqueItemData = {
          uniqueDescription: uniqueItemDiv.querySelector('input').value,
          expirationDT: uniqueItemDiv.querySelector('input:nth-child(2)').value,
          quantity: {
            amount: parseInt(uniqueItemDiv.querySelector('input:nth-child(3)').value),
            unit: uniqueItemDiv.querySelector('select').value
          }
        };
 
        itemData.unique.push(uniqueItemData);
      });
 
      jsonData.inventory.push(itemData);
    });
 
    return jsonData;
  }

  exportData() {
    let jsonData = this.convertTableToJson();
    document.getElementById('jsonOutput').value = JSON.stringify(jsonData, null, 2);
    postTable()
  }
 }
data = { "inventory": [] }


 inventoryManager = new InventoryManager(data);
 inventoryManager.renderTable();
document.getElementById('addSectionButton').addEventListener('click', () => inventoryManager.addSection());