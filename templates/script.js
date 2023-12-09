async function fetchData() {
    const response = await fetch('/api/data');
    const data = await response.json();

    if (data.length > 0) {
        const randomCat = data[Math.floor(Math.random() * data.length)];

        if (randomCat) {
            const dataTable = document.getElementById('data-table');
            const timerElement = document.getElementById('timer');

            // Display data in the table
            dataTable.innerHTML = `
                <tr>
                    <th colspan="2"> r/${randomCat.display_name} </th>
                </tr>
                <tr>
                    <td> Descrritpion </td>
                    <td>${randomCat.CatDescription}</td>
                </tr>
                <tr>
                    <td> Subscrib(purr)ers </td>
                    <td>${randomCat.subscribers}</td>
                </tr>
                <tr>
                    <td> Cat-Like Words Found </td>
                    <td>${randomCat['cat-like_words']}</td>
                </tr>
                <tr>
                    <td> Images </td>
                    <td>${randomCat['images']}</td>
                </tr>
                <tr>
                    <td> Total Cat Bonus </td>
                    <td>${randomCat['Total CatBonus']}</td>
                </tr>
                <tr>
                    <td> Cat Relevance Score </td>
                    <td>${randomCat['Cat Document Score']}</td>
                </tr>
                <tr>
                    <td> New Subreddit in </td>
                    <td id="countdown">Next update in 60 seconds</td>
                </tr>
            `;

            // Update timer every second
            let secondsRemaining = 60;
            const timerInterval = setInterval(() => {
                secondsRemaining--;

                if (secondsRemaining > 0) {
                    document.getElementById('countdown').textContent = `${secondsRemaining} seconds`;
                } else {
                    clearInterval(timerInterval);
                    document.getElementById('countdown').textContent = 'Updating...';
                    fetchData(); // Fetch data immediately after the timer reaches zero
                }
            }, 1000);
        } else {
            console.error('RandomCat is undefined.');
        }
    } else {
        console.error('Data array is empty.');
    }
}

async function toggleTopCatBonus() {
  const toggleDataContainer = document.getElementById('toggleDataContainer');
  const allData = await fetchAllData();
  const sortedData = allData.sort((a, b) => b['Cat Document Score'] - a['Cat Document Score']);
  toggleDataContainer.innerHTML = sortedData.map(item => `<p>${item['Cat Document Score']}: ${item.display_name}</p>`).join('');
  toggleDataContainer.style.display = toggleDataContainer.style.display === 'none' ? 'block' : 'none';
}

async function fetchAllData() {
  const response = await fetch('/api/data');
  const data = await response.json();
  return data;
}



// Uncomment the line below to fetch data once every 24 hours
// setInterval(fetchData, 24 * 60 * 60 * 1000);

fetchData(); // Fetch data immediately when the page loads
