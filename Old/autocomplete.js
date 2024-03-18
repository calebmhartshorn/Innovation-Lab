document.addEventListener('DOMContentLoaded', function() {
    let ingredients = [];
    const inputField = document.getElementById('ingredientInput');

    if (!inputField) {
        console.error("Input field with ID 'ingredientInput' not found.");
        return;
    }

    const suggestionsPanel = document.createElement('div');
    inputField.parentNode.insertBefore(suggestionsPanel, inputField.nextSibling);

    fetch('/ingredients')
        .then(response => response.json())
        .then(data => {
            ingredients = data;
        }).catch(error => {
            console.error("Error loading ingredients:", error);
        });

    inputField.addEventListener('input', function() {
        const input = inputField.value.toLowerCase();
        suggestionsPanel.innerHTML = '';
        
        if (input) {
            const filteredIngredients = ingredients.filter(ingredient => ingredient.toLowerCase().startsWith(input));

            filteredIngredients.forEach(function(ingredient) {
                const div = document.createElement('div');
                div.innerHTML = ingredient;
                div.className = 'autocomplete-suggestion';
                div.addEventListener('click', function () {
                    inputField.value = '';
                    suggestionsPanel.innerHTML = '';
                    inventoryManager.addItem(ingredient);
                });
                suggestionsPanel.appendChild(div);
            });
        }
    });
});