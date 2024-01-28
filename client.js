
function postTable () {
    const jsonInput = document.getElementById('jsonOutput');
   
    try {
      const jsonData = JSON.parse(jsonInput.value);
   
      fetch('/update', {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json',
          },
          body: JSON.stringify(jsonData),
      })
      .then(response => response.text())
      .then(message => {
          document.getElementById('statusMessage').innerText = message;
          return fetch('/read'); // Fetch the updated data
      })
      .then(response => response.json())
      .catch(error => {
          // Handle the error
          document.getElementById('statusMessage').innerText = 'An error occurred: ' + error;
      });
    } catch (error) {
      // Handle the error
      document.getElementById('statusMessage').innerText = 'Invalid JSON: ' + error;
    }
}

   
fetch('/read')
.then(response => response.json())
.then(response1 => {
    // Convert the JSON data to a string and insert it into the dataContainer div
    data = response1
    inventoryManager.data = data;
    inventoryManager.renderTable();
});
   