async function updateContribution(participantId, productId, bill_id, isChecked, csrfToken) {
    try {
        // Envoyer une requête AJAX vers votre vue Django
        const response = await fetch(`/bill/${bill_id}/participant/${participantId}/update-contribution/`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken  // Assurez-vous d'avoir le jeton CSRF dans votre template
            },
            body: JSON.stringify({
                product_id: productId,
                contribution: isChecked
            })
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const data = await response.json();

        const pricePerPersonElement = document.getElementById(`price-per-person-${productId}`);
        pricePerPersonElement.textContent = data.new_price.replace(/\./g, ',');  // Supposons que vous recevez le nouveau prix par personne depuis la vue Django
    } catch (error) {
        console.error('There was an error!', error);
    }
}

async function updateParticipantsTotalCost(bill_id, participantId, csrfToken) {
    try {
        // Envoyer une requête AJAX vers votre vue Django
        const response = await fetch(`/bill/${bill_id}/participants/total/`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken  // Assurez-vous d'avoir le jeton CSRF dans votre template
            }
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const data = await response.json();
        Object.keys(data).forEach((participant) => {
            const participantsTotalCost = document.getElementById(`participant-total-cost-${participant}`);
            participantsTotalCost.textContent = data[participant].replace(/\./g, ',');  // Supposons que vous recevez le nouveau prix par personne depuis la vue Django
        })
    } catch (error) {
        console.error('There was an error!', error);
    }
}

async function updateCostsAndPrices(participantId, productId, bill_id, isChecked) {
    try {
        await updateContribution(participantId, productId, bill_id, isChecked)
        updateParticipantsTotalCost(bill_id, participantId)
    } catch (error) {
        console.log(error)
    }
}

async function addNewProduct(billId, csrfToken) {
    try {
        const labelInput = document.getElementById('new-product-label');
        const quantityInput = document.getElementById('new-product-quantity');
        const totalPriceInput = document.getElementById('new-product-total-price');

        // Valider les entrées utilisateur
        if (labelInput.value.trim() === '' || isNaN(parseInt(quantityInput.value)) || isNaN(parseFloat(totalPriceInput.value))) {
            alert('Veuillez remplir correctement tous les champs.');
            return;
        }

        // Envoyer les données à la vue Django via une requête HTTP
        const data = {
            product_label: labelInput.value.trim(),
            product_price: parseFloat(totalPriceInput.value),
            quantity: parseInt(quantityInput.value)
        };

        const response = await fetch('/bill/' + billId + '/product/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        // Récupérer le nouveau produit depuis la réponse JSON
        const newData = await response.json();
        const newProduct = newData.new_product;

        // Récupérer la dernière ligne du tableau des produits
        const productsTableBody = document.querySelector('tbody');
        const lastRow = productsTableBody.lastElementChild;
        const newRow = document.createElement('tr'); // Créez un nouvel élément tr
        newRow.setAttribute('id', `product-row-${newProduct.product_id}`); // Attribuez-lui l'attribut id
        productsTableBody.insertBefore(newRow, lastRow); // Insérez le nouvel élément avant la dernière ligne

        // Remplir les cellules de la nouvelle ligne avec les informations du nouveau produit
        newRow.innerHTML = `
            <td id="product-label-${newProduct.product_id}">${newProduct.product_label}</td>
            <td id="product-quantity-${newProduct.product_id}">${newProduct.product_quantity}</td>
            <td id="product-price-${newProduct.product_id}">${newProduct.product_price_per_unit.replace(/\./g, ',')}</td>
            <td id="product-total-price-${newProduct.product_id}">${newProduct.product_total_price.replace(/\./g, ',')}</td>
            <td class="price-per-person" id="price-per-person-${newProduct.product_id}">N/A</td>
            <td>
                <!-- Bouton Modifier pour chaque ligne produit -->
                <button onclick="editProduct(${newProduct.product_id})">Modifier</button>
                <button onclick="deleteProduct(${newProduct.product_id})">Supprimer</button>
                <div id="product-action-buttons-${newProduct.product_id}" style="display: none;">
                    <!-- Boutons Valider et Annuler pour chaque ligne produit -->
                    <button onclick="saveProductChanges(${newProduct.product_id}, ${billId}, ${csrfToken})">Valider</button>
                    <button onclick="cancelProductEdit()">Annuler</button>
                </div>
            </td>
        `;

        // Masquer la ligne de saisie du nouveau produit
        cancelNewProduct();
    } catch (error) {
        console.error('Error:', error);
    }
}

async function deleteProduct(productId, csrfToken) {
    try {

        const response = await fetch('/product/' + productId + '/delete/', {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            }
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const responseBody = await response.json()
        if (responseBody.success) {
            hideDeletedProduct(productId)
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

function hideDeletedProduct(productId) {
    // Masquer la ligne de saisie du nouveau produit
    const oldProductRow = document.getElementById(`product-row-${productId}`);
    oldProductRow.remove();

    // Supprimer les cellules correspondantes dans le deuxième tableau
    const checkboxes = document.querySelectorAll(`[id^="checkbox-"][id$="-${productId}"]`);
    checkboxes.forEach((checkbox) => {
        checkbox.parentNode.parentNode.remove(); // Supprimer la ligne entière
    });
    document.getElementById(`product-head-${productId}`).remove()
}


function cancelNewProduct() {
    // Masquer la ligne de saisie du nouveau produit
    const newProductRows = document.getElementsByClassName('new-product-row');
    // Parcourir chaque élément et inverser son état d'affichage
    for (let i = 0; i < newProductRows.length; i++) {
        const row = newProductRows[i];
        if (row.style.display === "table-cell") {
            row.style.display = "none";
        }
        row.value = ''
    }
}

function showNewProductRow() {
    // Récupérer tous les éléments avec la classe "new-product-row"
    const newProductRows = document.getElementsByClassName('new-product-row');

    // Parcourir chaque élément et inverser son état d'affichage
    for (let i = 0; i < newProductRows.length; i++) {
        const row = newProductRows[i];
        if (row.style.display === "none") {
            row.style.display = "table-cell";
        }
    }
}

function editProduct(productId) {
    // Afficher les champs d'entrée pour modifier les valeurs
    const totalPrice = document.getElementById(`product-total-price-${productId}`).innerHTML.replace(/,/g, '.')
    document.getElementById(`product-label-${productId}`).innerHTML = `<input type="text" id="edit-product-label-${productId}" value="${document.getElementById(`product-label-${productId}`).innerText}">`;
    document.getElementById(`product-quantity-${productId}`).innerHTML = `<input type="number" id="edit-product-quantity-${productId}" value="${document.getElementById(`product-quantity-${productId}`).innerText}">`;
    document.getElementById(`product-total-price-${productId}`).innerHTML = `<input type="number" id="edit-product-total-price-${productId}" value="${totalPrice}">`;

    // Masquer le bouton Modifier et afficher les boutons Valider et Annuler
    document.getElementById(`product-action-buttons-${productId}`).style.display = 'block';
    document.querySelector(`button[onclick="editProduct(${productId})"]`).style.display = 'none';
}

async function saveProductChanges(productId, billId, csrfToken) {
    // Récupérer les nouvelles valeurs depuis les champs d'entrée modifiés
    const newLabel = document.getElementById(`edit-product-label-${productId}`).value;
    const newQuantity = document.getElementById(`edit-product-quantity-${productId}`).value;
    const newTotalPrice = document.getElementById(`edit-product-total-price-${productId}`).value;

    const data = {
        product_label: newLabel.trim(),
        product_price: parseFloat(newTotalPrice),
        quantity: parseInt(newQuantity)
    };
    console.log(data)
    const response = await fetch('/bill/' + billId + '/product/' + productId + '/update/', {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify(data)
    });

    if (!response.ok) {
        throw new Error('Network response was not ok');
    }

    // Récupérer le nouveau produit depuis la réponse JSON
    const newData = await response.json();
    console.log(newData)

    // Mettre à jour les valeurs dans la ligne produit
    document.getElementById(`product-label-${productId}`).innerText = newData.product_label;
    document.getElementById(`product-quantity-${productId}`).innerText = newData.product_quantity;
    document.getElementById(`product-price-${productId}`).innerText = newData.product_price_per_unit.replace(/\./g, ',');
    document.getElementById(`product-total-price-${productId}`).innerText = newData.product_total_price.replace(/\./g, ',');

    // Masquer les champs d'entrée et afficher le bouton Modifier
    document.getElementById(`product-action-buttons-${productId}`).style.display = 'none';
    document.querySelector(`button[onclick="editProduct(${productId})"]`).style.display = 'block';
}

function cancelProductEdit(productId) {
    // Restaurer les valeurs initiales dans la ligne produit
    document.getElementById(`product-label-${productId}`).innerHTML = document.getElementById(`edit-product-label-${productId}`).value;
    document.getElementById(`product-quantity-${productId}`).innerHTML = document.getElementById(`edit-product-quantity-${productId}`).value;
    document.getElementById(`product-total-price-${productId}`).innerHTML = document.getElementById(`edit-product-total-price-${productId}`).value.replace(/\./g, ',');

    // Masquer les champs d'entrée et afficher le bouton Modifier
    document.getElementById(`product-action-buttons-${productId}`).style.display = 'none';
    document.querySelector(`button[onclick="editProduct(${productId})"]`).style.display = 'block';
}

function showNewParticipantRow() {
    const newParticipantRows = document.getElementsByClassName('new-participant-row');

    // Parcourir chaque élément et inverser son état d'affichage
    for (let i = 0; i < newParticipantRows.length; i++) {
        const row = newParticipantRows[i];
        if (row.style.display === "none") {
            row.style.display = "table-cell";
        }
    }
}