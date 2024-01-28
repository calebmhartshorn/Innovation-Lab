
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

    updateRecipes();

}

function updateRecipes () {

    let ingredients = []
    document.querySelectorAll("#dataContainer>div>input").forEach(element => {
        ingredients.push(element.value);
    })
    let url = `/recipe?ingredients=${ingredients.toString()}&must=${ingredients[0]}`

    fetch(url)
    .then(response => response.json())
    .then(data => {

            document.getElementById('recipes-container').innerText = ""
            data["results"].forEach(element => {
                listItem = document.createElement("li");
                link = document.createElement("a");
                
                link.href = element["recipeUrl"];
                link.innerText = element["recipeName"];
                document.getElementById('recipes-container').appendChild(listItem);
                listItem.appendChild(link);
            });

    })
    .catch(error => console.error('Error:', error));
}
   
fetch('/read')
.then(response => response.json())
.then(response1 => {
    // Convert the JSON data to a string and insert it into the dataContainer div
    data = response1
    inventoryManager.data = data;
    inventoryManager.renderTable();
    updateRecipes();
});

var allowedStrings = ["string1", "string2", "string3"];

$("#autocomplete").autocomplete({
    source: allowedStrings
}).on("autocompletechange", function(event, ui) {
    if (!allowedStrings.includes($(this).val())) {
        $(this).val('');
        $('#errorMessage').text("Invalid input. Please choose from the suggested options.");
    } else {
        $('#errorMessage').text("");
    }
});

document.getElementById("scan-checkbox").addEventListener("change", () => {
    let enabled = document.getElementById("scan-checkbox").checked;
    console.log(enabled);
    if (enabled) {
        fetch('/enablescan', {
            method: 'POST',
            body: '',
        })
    } else {
        fetch('/disablescan', {
            method: 'POST',
            body: '',
        }) 
    }
})

setInterval(() => {

    if (document.getElementById("scan-checkbox").checked) {
        fetch('/scanresults')
        .then(response => response.json())
        .then(response => {
            document.getElementById('scan-results').value = JSON.stringify(response);
        })
    }

}, 500);