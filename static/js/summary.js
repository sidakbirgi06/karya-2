// Finance_app/static/summary.js

document.addEventListener('DOMContentLoaded', function() {
    
    // 1. Get Dates from URL
    const params = new URLSearchParams(window.location.search);
    const startDate = params.get('start');
    const endDate = params.get('end');
    
    if (!startDate || !endDate) {
        alert("No dates selected!");
        window.location.href = '/finance';
        return;
    }

    // Display friendly dates
    document.getElementById('dateRangeDisplay').textContent = 
        `${new Date(startDate).toLocaleDateString()} - ${new Date(endDate).toLocaleDateString()}`;

    // 2. Fetch Data
    const token = localStorage.getItem('access_token');
    const api = axios.create({ headers: { 'Authorization': 'Bearer ' + token } });

    api.get(`/api/finance/summary?start_date=${startDate}&end_date=${endDate}`)
        .then(res => {
            const data = res.data;
            
            // A. Update Big Numbers
            document.getElementById('sumIncome').textContent = formatMoney(data.total_income);
            document.getElementById('sumExpense').textContent = formatMoney(data.total_expense);
            document.getElementById('sumBalance').textContent = formatMoney(data.balance);

            // B. Draw Chart (Expense Breakdown)
            renderExpenseChart(data.expense_by_category);

            // C. Fill Category List
            renderCategoryList(data.expense_by_category);
        })
        .catch(err => {
            console.error(err);
            alert("Error loading report.");
        });

    // --- HELPER: Draw Chart ---
    function renderExpenseChart(categories) {
        const ctx = document.getElementById('expenseChart').getContext('2d');
        
        if (categories.length === 0) {
            // Handle empty data
            document.querySelector('.chart-box').innerHTML += "<p class='text-center'>No expenses in this period.</p>";
            return;
        }

        // Prepare data for Chart.js
        const labels = categories.map(c => c.category);
        const values = categories.map(c => c.total);
        const colors = ['#ff6384', '#36a2eb', '#ffce56', '#4bc0c0', '#9966ff', '#ff9f40'];

        new Chart(ctx, {
            type: 'doughnut', // or 'pie'
            data: {
                labels: labels,
                datasets: [{
                    data: values,
                    backgroundColor: colors
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { position: 'bottom' }
                }
            }
        });
    }

    // --- HELPER: Render List ---
    function renderCategoryList(categories) {
        const list = document.getElementById('categoryList');
        
        if (categories.length === 0) {
            list.innerHTML = "<li>No expenses recorded.</li>";
            return;
        }

        // Sort largest expenses first
        categories.sort((a,b) => b.total - a.total);

        categories.forEach(c => {
            const li = document.createElement('li');
            li.innerHTML = `
                <span class="cat-name">${c.category}</span>
                <span class="cat-total">${formatMoney(c.total)}</span>
            `;
            list.appendChild(li);
        });
    }

    function formatMoney(amount) {
        return '₹' + parseFloat(amount).toFixed(2);
    }
});