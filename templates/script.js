async function fetchData() {
    const response = await fetch('/api/data');
    const data = await response.json();

    if (data.length > 0) {
        const randomCat = data[Math.floor(Math.random() * data.length)];

        if (randomCat) {
            const dataTable = document.getElementById('data-table');
            dataTable.innerHTML = `
                <tr>
                    <th colspan="2"> r/${randomCat.display_name} </th>
                </tr>
                <tr>
                    <td> Description </td>
                    <td>${randomCat.CatDescription}</td>
                </tr>
                <tr>
                    <td> Subscribers </td>
                    <td>${randomCat.subscribers}</td>
                </tr>
                <tr>
                    <td> Cat-Related Words </td>
                    <td>${randomCat['cat-like_words']}</td>
                </tr>
                <tr>
                    <td> Total Cat Bonus </td>
                    <td>${randomCat['Total CatBonus']}</td>
                </tr>
                <tr>
                    <td> Cat Document Score </td>
                    <td>${randomCat['Cat Document Score']}</td>
                </tr>
            `;
        } else {
            console.error('RandomCat is undefined.');
        }
    } else {
        console.error('Data array is empty.');
    }
}

function toggleTopCatBonus() {
    const toggleDataContainer = document.getElementById('toggleDataContainer');

    // Toggle visibility
    if (toggleDataContainer.style.display === 'none' || !toggleDataContainer.style.display) {
        toggleDataContainer.style.display = 'block';
        showTopCatBonus();
    } else {
        toggleDataContainer.style.display = 'none';
    }
}

async function showTopCatBonus() {
    const response = await fetch('/api/data');
    const data = await response.json();

    if (data.length > 0) {
        const topCatBonusList = document.getElementById('topCatBonusList');
        const topCatBonusData = data[data.length - 1]; // assuming addData is the last element

        // Clear previous data
        topCatBonusList.innerHTML = '';

        for (const entry of topCatBonusData) {
            const listItem = document.createElement('li');
            listItem.textContent = `${entry[1]}: ${entry[0]}`;
            topCatBonusList.appendChild(listItem);
        }
    } else {
        console.error('Data array is empty.');
    }
}

setInterval(fetchData, 5 * 1000);
// Uncomment the line below if you want to fetch data once every 24 hours
// setInterval(fetchData, 24 * 60 * 60 * 1000);
fetchData();