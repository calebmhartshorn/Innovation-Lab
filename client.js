document.getElementById('readButton').addEventListener('click', function() {
    fetch('/read')
        .then(response => response.json())
        .then(data => {
            // Convert the JSON data to a string and insert it into the dataContainer div
            document.getElementById('dataContainer').innerHTML = JSON.stringify(data);
        });
 });

 document.getElementById('updateButton').addEventListener('click', function() {
    const jsonInput = document.getElementById('jsonInput');
   
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
      .then(data => {
          // Update the dataContainer div with the new data
          document.getElementById('dataContainer').innerHTML = JSON.stringify(data);
      })
      .catch(error => {
          // Handle the error
          document.getElementById('statusMessage').innerText = 'An error occurred: ' + error;
      });
    } catch (error) {
      // Handle the error
      document.getElementById('statusMessage').innerText = 'Invalid JSON: ' + error;
    }
   });
   