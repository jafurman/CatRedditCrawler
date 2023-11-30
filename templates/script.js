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
                    <td> Descrrription :3 </td>
                    <td>${randomCat.CatDescription}</td>
                </tr>
                <tr>
                    <td> Subscribpurrs </td>
                    <td>${randomCat.subscribers}</td>
                </tr>
                <tr>
                    <td> Cat-Related Words </td>
                    <td>${randomCat['cat-like_words']}</td>
                </tr>
            `;
        } else {
            console.error('RandomCat is undefined.');
        }
    } else {
        console.error('Data array is empty.');
    }
}

setInterval(fetchData, 5 * 1000);
//setInterval(fetchData, 24 * 60 * 60 * 1000);
fetchData();