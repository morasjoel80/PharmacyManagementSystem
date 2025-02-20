document.getElementById('viewMedicines').addEventListener('click', () => {
    fetch('/medicines')
        .then(response => response.json())
        .then(data => {
            const table = document.getElementById('medicineTable');
            const tbody = table.querySelector('tbody');
            tbody.innerHTML = '';
            data.forEach(medicine => {
                const row = `<tr>
                    <td>${medicine.Medicine_ID}</td>
                    <td>${medicine.M_name}</td>
                    <td>${medicine.Price}</td>
                    <td>${medicine.Quantity_in_stock}</td>
                    <td>${medicine.Expiry_date}</td>
                    <td>${medicine.Supplier_ID}</td>
                    <td>${medicine.Category}</td>
                </tr>`;
                tbody.innerHTML += row;
            });
            table.style.display = 'table';
        })
        .catch(error => {
            console.error('Error fetching medicines:', error);
        });
});