async function updateContribution(participantId, productId, bill_id, isChecked, csrfToken) {
    try {
        // Envoyer une requête AJAX vers votre vue Django
        const response = await fetch(`/splitease/bill/${bill_id}/participant/${participantId}/update-contribution/`, {
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

async function updateParticipantsTotalCost(billId, csrfToken) {
    try {
        // Envoyer une requête AJAX vers votre vue Django
        const response = await fetch(`/splitease/bill/${billId}/participants/total/`, {
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
        console.log(data)
        Object.keys(data).forEach((participant) => {
            console.log(participant)
            console.log(document.getElementById(`participant-total-cost-${participant}`))
            const participantsTotalCost = document.getElementById(`participant-total-cost-${participant}`);
            participantsTotalCost.textContent = data[participant].replace(/\./g, ',');  // Supposons que vous recevez le nouveau prix par personne depuis la vue Django
        })
        refreshParticipantsTotal()
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

async function updatePricesPerPerson(billId, csrfToken) {
    const response = await fetch('/splitease/bill/' + billId + '/price-per-person/', {
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

    for (let product in data) {
        const pricePerPersonElement = document.getElementById(`price-per-person-${product}`);
        pricePerPersonElement.textContent = data[product].replace(/\./g, ',');
    }
    return data
}

function refreshParticipantsTotal() {
    let total = 0.0;
    const participantTotalCells = document.querySelectorAll('[id^="participant-total-cost-"]');

    participantTotalCells.forEach(cell => {
        // Remplacer les virgules par des points et convertir en flottant
        const value = parseFloat(cell.textContent.replace(',', '.')) || 0;
        total += value;
    });

    document.getElementById('participants-total').textContent = total.toFixed(2).replace('.', ',');
}

function refreshProductsTotal() {
    let total = 0.0;
    const productsTotalCells = document.querySelectorAll('[id^="product-total-price-"]');

    productsTotalCells.forEach(cell => {
        // Remplacer les virgules par des points et convertir en flottant
        const value = parseFloat(cell.textContent.replace(',', '.')) || 0;
        total += value;
    });

    document.getElementById('total-of-product-table').textContent = total.toFixed(2).replace('.', ',');
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

        const response = await fetch('/splitease/bill/' + billId + '/product/', {
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

        const participantResponse = await fetch('/splitease/bill/' + billId + '/participants/', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            }
        });

        if (!participantResponse.ok) {
            throw new Error('Network response was not ok');
        }

        // Récupérer le nouveau produit depuis la réponse JSON
        const newData = await response.json();
        const participants = await participantResponse.json()
        const newProduct = newData.new_product;

        addProductRow(newProduct, billId, csrfToken)
        addProductRowParticipantTable(newProduct, billId, participants, csrfToken)
        refreshProductsTotal()
        // Masquer la ligne de saisie du nouveau produit
        cancelNewProduct();
    } catch (error) {
        console.error('Error:', error);
    }
}

function addProductRow(newProduct, billId, csrfToken) {
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
                <button class="button-secondary" onclick="editProduct(${newProduct.product_id})">Modifier</button>
                <button class="button-danger" onclick="deleteProduct(${newProduct.product_id}, ${billId}, '${csrfToken}')">Supprimer</button>
                <div id="product-action-buttons-${newProduct.product_id}" style="display: none;">
                    <!-- Boutons Valider et Annuler pour chaque ligne produit -->
                    <button class="button-secondary" onclick="saveProductChanges(${newProduct.product_id}, ${billId}, '${csrfToken}')">Valider</button>
                    <button class="button-danger" onclick="cancelProductEdit()">Annuler</button>
                </div>
            </td>
        `;
}

function addProductRowParticipantTable(newProduct, billId, participants, csrfToken) {
    // Récupérer la dernière ligne du tableau des produits
    const participantsTableBody = document.getElementById("participant-table-body");
    const lastRow = participantsTableBody.lastElementChild;

    // Créez un nouvel élément tr
    const newRow = document.createElement('tr');
    newRow.setAttribute('id', `row-product-${newProduct.product_id}`); // Attribuez-lui l'attribut id
    participantsTableBody.insertBefore(newRow, lastRow); // Insérez le nouvel élément avant la dernière ligne

    // Ajouter le label du produit
    let rowContent = `<td>${newProduct.product_label}</td>`;

    // Ajouter une case à cocher pour chaque participant
    participants.forEach(participant => {
        rowContent += `
            <td>
                <label>
                    <input type="checkbox" id="checkbox-${participant.participant_id}-${newProduct.product_id}" onchange="updateCostsAndPrices(${participant.participant_id}, ${newProduct.product_id}, ${billId}, this.checked)">
                </label>
            </td>
        `;
    });

    // Assigner le contenu accumulé à innerHTML
    newRow.innerHTML = rowContent;
}


async function deleteProduct(productId, billId, csrfToken) {
    try {

        const response = await fetch('/splitease/product/' + productId + '/delete/', {
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
            console.log("coucou")
            console.log(billId)
            await updateParticipantsTotalCost(billId, csrfToken)
            refreshProductsTotal()
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
    document.getElementById(`row-product-${productId}`).remove()
}


function cancelNewProduct() {
    // Masquer la ligne de saisie du nouveau produit
    const newProductRows = document.getElementsByClassName('new-product-row');
    // Parcourir chaque élément et inverser son état d'affichage
    for (let i = 0; i < newProductRows.length; i++) {
        const row = newProductRows[i];
        if (row.style.display === "table-row") {
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
            row.style.display = "table-row";
        }
    }
}

function editProduct(productId) {
    // Stocker les valeurs initiales
    const initialLabel = document.getElementById(`product-label-${productId}`).innerText;
    const initialQuantity = document.getElementById(`product-quantity-${productId}`).innerText;
    const initialTotalPrice = document.getElementById(`product-total-price-${productId}`).innerHTML.replace(/,/g, '.');

    // Ajouter les valeurs initiales dans les attributs de données des éléments
    document.getElementById(`product-label-${productId}`).setAttribute('data-initial-value', initialLabel);
    document.getElementById(`product-quantity-${productId}`).setAttribute('data-initial-value', initialQuantity);
    document.getElementById(`product-total-price-${productId}`).setAttribute('data-initial-value', initialTotalPrice);

    // Afficher les champs d'entrée pour modifier les valeurs
    document.getElementById(`product-label-${productId}`).innerHTML = `<input type="text" id="edit-product-label-${productId}" value="${initialLabel}">`;
    document.getElementById(`product-quantity-${productId}`).innerHTML = `<input type="number" id="edit-product-quantity-${productId}" value="${initialQuantity}">`;
    document.getElementById(`product-total-price-${productId}`).innerHTML = `<input type="number" id="edit-product-total-price-${productId}" value="${initialTotalPrice}">`;

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
    const response = await fetch('/splitease/bill/' + billId + '/product/' + productId + '/update/', {
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
    // Restaurer les valeurs initiales depuis les attributs de données
    const initialLabel = document.getElementById(`product-label-${productId}`).getAttribute('data-initial-value');
    const initialQuantity = document.getElementById(`product-quantity-${productId}`).getAttribute('data-initial-value');
    const initialTotalPrice = document.getElementById(`product-total-price-${productId}`).getAttribute('data-initial-value').replace(/\./g, ',');

    // Restaurer les valeurs initiales dans la ligne produit
    document.getElementById(`product-label-${productId}`).innerHTML = initialLabel;
    document.getElementById(`product-quantity-${productId}`).innerHTML = initialQuantity;
    document.getElementById(`product-total-price-${productId}`).innerHTML = initialTotalPrice;

    // Masquer les champs d'entrée et afficher le bouton Modifier
    document.getElementById(`product-action-buttons-${productId}`).style.display = 'none';
    document.querySelector(`button[onclick="editProduct(${productId})"]`).style.display = 'block';
}

function editParticipant(participantId) {
    // Stocker les valeurs initiales
    const initialName = document.getElementById(`participant-name-${participantId}`).innerText;

    // Ajouter les valeurs initiales dans les attributs de données des éléments
    document.getElementById(`participant-name-${participantId}`).setAttribute('data-initial-value', initialName);

    // Afficher les champs d'entrée pour modifier les valeurs
    document.getElementById(`participant-name-${participantId}`).innerHTML = `<input type="text" 
                                        id="edit-participant-name-${participantId}" 
                                        value="${initialName}">`;

    // Masquer le bouton Modifier et afficher les boutons Valider et Annuler
    document.getElementById(`participant-action-buttons-${participantId}`).style.display = 'block';
    document.querySelector(`button[onclick="editParticipant(${participantId})"]`).style.display = 'none';
}

async function saveParticipantChanges(participantId, csrfToken) {
    // Récupérer les nouvelles valeurs depuis les champs d'entrée modifiés
    const newName = document.getElementById(`edit-participant-name-${participantId}`).value;

    const data = {
        participant_name: newName.trim()
    };
    const response = await fetch('/splitease/participant/' + participantId + '/', {
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

    // Récupérer le nouveau participant depuis la réponse JSON
    const newData = await response.json();
    console.log(newData)

    // Mettre à jour les valeurs dans la ligne participant
    document.getElementById(`participant-name-${participantId}`).innerText = newData.participant_name;

    // Masquer les champs d'entrée et afficher le bouton Modifier
    document.getElementById(`participant-action-buttons-${participantId}`).style.display = 'none';
    document.querySelector(`button[onclick="editParticipant(${participantId})"]`).style.display = 'block';
}

function cancelParticipantEdit(participantId) {
    // Restaurer les valeurs initiales depuis les attributs de données
    const initialName = document.getElementById(`participant-name-${participantId}`).getAttribute('data-initial-value');

    // Restaurer les valeurs initiales dans la ligne participant
    document.getElementById(`participant-name-${participantId}`).innerHTML = initialName;

    // Masquer les champs d'entrée et afficher le bouton Modifier
    document.getElementById(`participant-action-buttons-${participantId}`).style.display = 'none';
    document.querySelector(`button[onclick="editParticipant(${participantId})"]`).style.display = 'block';
}

function cancelNewParticipant() {
    // Masquer la ligne de saisie du nouveau produit
    const newParticipantCol = document.getElementById('new-participant-col');
    // Parcourir chaque élément et inverser son état d'affichage

    if (newParticipantCol.style.display === "table-cell") {
        newParticipantCol.style.display = "none";
    }
    newParticipantCol.value = ''
}

function showNewParticipantRow() {
    // Récupérer tous les éléments avec la classe "new-product-row"
    const newParticipant = document.getElementById('new-participant-col');

    if (newParticipant.style.display === "none") {
        newParticipant.style.display = "table-cell";
    }
}

async function addNewParticipant(billId, csrfToken) {
    try {
        const nameInput = document.getElementById('new-participant-name');

        // Envoyer les données à la vue Django via une requête HTTP
        const data = {
            name: nameInput.value.trim(),
            bill_id: billId
        };

        const response = await fetch('/splitease/participant/create/', {
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

        // Récupérer le nouveau participant depuis la réponse JSON
        const newParticipant = await response.json();

        addParticipantCol(newParticipant, billId, csrfToken);

        addParticipantOption(newParticipant.participant_id, newParticipant.participant_name)

        // Masquer la ligne de saisie du nouveau participant
        cancelNewParticipant();
    } catch (error) {
        console.error('Error:', error);
    }
}

function addParticipantCol(newParticipant, billId, csrfToken) {
    const participantsTable = document.getElementById('participant-table');
    const participantsTableHeadRow = participantsTable.querySelector('thead tr');
    const participantsTableBody = document.getElementById('participant-table-body');
    const productRows = participantsTableBody.querySelectorAll('tr[id^="row-product-"]');

    // Ajouter l'en-tête du nouveau participant
    const newHeaderCell = document.createElement('th');
    newHeaderCell.setAttribute('id', `participant-head-${newParticipant.participant_id}`);
    newHeaderCell.innerHTML = `
        <div id="participant-name-${newParticipant.participant_id}">${newParticipant.participant_name}</div>
        <button class="button-secondary" onclick="editParticipant(${newParticipant.participant_id})">Modifier</button>
        <button class="button-danger" onclick="deleteParticipant(${billId}, ${newParticipant.participant_id})">Supprimer</button>
        <div id="participant-action-buttons-${newParticipant.participant_id}" style="display: none;">
            <button class="button-secondary" onclick="saveParticipantChanges(${newParticipant.participant_id}, '${csrfToken}')">Valider</button>
            <button class="button-danger" onclick="cancelParticipantEdit(${newParticipant.participant_id})">Annuler</button>
        </div>
    `;
    participantsTableHeadRow.insertBefore(newHeaderCell, participantsTableHeadRow.lastElementChild);

    // Ajouter une cellule de case à cocher pour chaque produit
    productRows.forEach(row => {
        const productId = row.getAttribute('id').split('-')[2];
        const newCheckboxCell = document.createElement('td');
        newCheckboxCell.innerHTML = `
            <label>
                <input type="checkbox" id="checkbox-${newParticipant.participant_id}-${productId}" onchange="updateCostsAndPrices(${newParticipant.participant_id}, ${productId}, ${billId}, this.checked)">
            </label>
        `;
        row.appendChild(newCheckboxCell);
    });

    // Ajouter une cellule pour le total
    const totalRow = participantsTableBody.querySelector('tr:last-child');
    const newTotalCell = document.createElement('td');
    newTotalCell.setAttribute('id', `participant-total-cost-${newParticipant.participant_id}`);
    newTotalCell.textContent = '0,00'
    totalRow.appendChild(newTotalCell);
}

async function deleteParticipant(billId, participantId, csrfToken) {
    try {

        const response = await fetch('/splitease/participant/' + participantId +"/delete/", {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            }
        });

        if (response.status !== 200) {
            throw new Error('Network response was not ok');
        }

        await updateParticipantsTotalCost(billId, csrfToken)
        await updatePricesPerPerson(billId, csrfToken)
        removeParticipantCol(participantId);
        removeParticipantOption(participantId)
        refreshParticipantsTotal()

    } catch (error) {
        console.error('Error:', error);
    }
}

function removeParticipantCol(participantId) {
    const participantsTableBody = document.getElementById('participant-table-body');
    const productRows = participantsTableBody.querySelectorAll('tr[id^="row-product-"]');

    // Supprimer l'en-tête du participant
    const participantHeaderCell = document.getElementById(`participant-head-${participantId}`);
    if (participantHeaderCell) {
        participantHeaderCell.remove();
    }

    // Supprimer les cellules de case à cocher associées à chaque produit
    productRows.forEach(row => {
        const checkboxCell = row.querySelector(`td > label > input[id^="checkbox-${participantId}-"]`).parentElement.parentElement;
        if (checkboxCell) {
            checkboxCell.remove();
        }
    });

    // Supprimer la cellule du total associée
    const totalCell = document.getElementById(`participant-total-cost-${participantId}`);
    if (totalCell) {
        totalCell.remove();
    }
}

function addParticipantOption(participantId, participantName) {
    const selectElement = document.getElementById('select-payer');
    const newOption = document.createElement('option');
    newOption.value = participantId;
    newOption.textContent = participantName;
    selectElement.appendChild(newOption);
}

function removeParticipantOption(participantId) {
    const selectElement = document.getElementById('select-payer');
    const optionToRemove = selectElement.querySelector(`option[value="${participantId}"]`);
    if (optionToRemove) {
        selectElement.removeChild(optionToRemove);
    }
}

async function setPayer(participantId, billId, csrfToken) {
    try {
        const body = {
            participant_id: participantId
        }
        const response = await fetch('/splitease/bill/' + billId + '/set-payer/', {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify(body)
        });

        if (response.status !== 200) {
            throw new Error('Network response was not ok');
        }
    } catch (error) {
        console.error('Error:', error);
    }
}
