// Finance_app/static/finance.js

document.addEventListener('DOMContentLoaded', function() {
    // --- 1. AUTH CHECK ---
    const token = localStorage.getItem('access_token');
    if (!token) {
        window.location.href = '/login';
        return;
    }

    // Setup Axios with the token
    const api = axios.create({
        headers: { 'Authorization': 'Bearer ' + token }
    });

    // --- SET CURRENT DATE HEADER ---
    const dateOptions = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
    // Example output: "Tuesday, November 18, 2025"
    document.getElementById('todaysDate').textContent = new Date().toLocaleDateString('en-US', dateOptions);

    // --- 2. ELEMENTS ---
    const dashboardContainer = document.getElementById('dashboardContainer');
    const totalIncomeEl = document.getElementById('totalIncome');
    const totalExpenseEl = document.getElementById('totalExpense');
    const totalBalanceEl = document.getElementById('totalBalance');
    const addIncomeBtn = document.getElementById('addIncomeBtn');
    const addExpenseBtn = document.getElementById('addExpenseBtn');
    const transactionListEl = document.getElementById('transactionList');
    
    // Modal Elements
    const modal = document.getElementById('transactionModal');
    const closeModal = modal.querySelector('.close-button');
    const modalTitle = document.getElementById('modalTitle');
    const transactionForm = document.getElementById('transactionForm');
    const submitBtn = transactionForm.querySelector('button[type="submit"]');
    const transTypeInput = document.getElementById('transType');
    const transCategorySelect = document.getElementById('transCategory');

    // --- 3. LOAD DATA ---
    loadDashboard();
    loadTransactions();

    function loadDashboard() {
        api.get('/api/finance/dashboard')
            .then(res => {
                const data = res.data;
                totalIncomeEl.textContent = formatMoney(data.total_income);
                totalExpenseEl.textContent = formatMoney(data.total_expense);
                totalBalanceEl.textContent = formatMoney(data.balance);
            })
            .catch(err => {
                // If 403 Forbidden, it means user is an Employee
                if (err.response && err.response.status === 403) {
                    // Hide the dashboard and the Add Income button
                    dashboardContainer.style.display = 'none';
                    addIncomeBtn.style.display = 'none';
                } else {
                    console.error(err);
                }
            });
    }

    // --- NEW GLOBAL VARIABLE ---
    let allTransactions = []; // Stores the raw data from the server

    function loadTransactions() {
        api.get('/api/finance/transactions')
            .then(res => {
                allTransactions = res.data; // 1. Save the data
                renderList('all');          // 2. Show everything by default
            })
            .catch(err => console.error(err));
    }

    // --- NEW RENDER FUNCTION (Handles Filtering) ---
    // We attach this to the 'window' object so the HTML buttons can find it
    window.filterTransactions = function(type) {
        renderList(type);
        updateActiveButton(type);
    }

    function renderList(filterType) {
        transactionListEl.innerHTML = ''; // Clear list

        // 1. Filter the data locally
        let filteredList = allTransactions;
        if (filterType !== 'all') {
            filteredList = allTransactions.filter(t => t.type === filterType);
        }

        if (filteredList.length === 0) {
            transactionListEl.innerHTML = '<p class="no-data">No transactions found.</p>';
            return;
        }

        let lastDate = '';

        // 2. Loop through the FILTERED list
        filteredList.forEach(t => {
            const dateObj = new Date(t.date);
            const dateString = dateObj.toLocaleDateString(); 
            
            if (dateString !== lastDate) {
                const header = document.createElement('div');
                header.className = 'date-header';
                header.textContent = getFriendlyDate(dateObj);
                transactionListEl.appendChild(header);
                lastDate = dateString;
            }

            const div = document.createElement('div');
            div.className = 'transaction-item';
            const sign = t.type === 'income' ? '+' : '-';
            const colorClass = t.type === 'income' ? 'income' : 'expense';
            
            div.innerHTML = `
                <div class="t-info">
                    <h4>${t.category} <small>(${t.notes || ''})</small></h4>
                </div>
                <div class="t-amount ${colorClass}">
                    ${sign}₹${parseFloat(t.amount).toFixed(2)}
                </div>
            `;
            transactionListEl.appendChild(div);
        });
    }

    function updateActiveButton(type) {
        // Reset all buttons
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        // Activate the clicked one
        // (We find the button by its text content or onclick attribute)
        const buttons = document.querySelectorAll('.filter-btn');
        if(type === 'all') buttons[0].classList.add('active');
        if(type === 'income') buttons[1].classList.add('active');
        if(type === 'expense') buttons[2].classList.add('active');
    }

    // --- NEW HELPER FUNCTION ---
    // Make the dates look human (Today, Yesterday, or Nov 18)
    function getFriendlyDate(dateObj) {
        const today = new Date();
        const yesterday = new Date();
        yesterday.setDate(today.getDate() - 1);

        if (dateObj.toDateString() === today.toDateString()) {
            return 'Today';
        } else if (dateObj.toDateString() === yesterday.toDateString()) {
            return 'Yesterday';
        } else {
            // Returns "Nov 18, 2025"
            return dateObj.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' });
        }
    }

    // --- 4. INTERACTION ---
    
    // Helper to open modal
    function openModal(type) {
        modal.style.display = 'block';
        transTypeInput.value = type;
        modalTitle.textContent = type === 'income' ? 'Add Income' : 'Add Expense';
        
        // --- NEW: Change Button Color & Text ---
        submitBtn.className = ''; // Clear old classes
        if (type === 'income') {
            submitBtn.classList.add('btn-save-income');
            submitBtn.textContent = 'Save Income';
        } else {
            submitBtn.classList.add('btn-save-expense');
            submitBtn.textContent = 'Save Expense';
        }

        // Populate Categories based on type
        transCategorySelect.innerHTML = '';
        const categories = type === 'income' 
            ? ['Salary', 'Freelance', 'Business', 'Other'] 
            : ['Food', 'Transport', 'Supplies', 'Bills', 'Entertainment', 'Other'];
        
        categories.forEach(c => {
            const opt = document.createElement('option');
            opt.value = c;
            opt.textContent = c;
            transCategorySelect.appendChild(opt);
        });
    }

    addIncomeBtn.onclick = () => openModal('income');
    addExpenseBtn.onclick = () => openModal('expense');
    
    closeModal.onclick = () => modal.style.display = 'none';
    window.onclick = (e) => { if(e.target == modal) modal.style.display = 'none'; }

    // Submit Form
    transactionForm.onsubmit = function(e) {
        e.preventDefault();
        const data = {
            amount: document.getElementById('transAmount').value,
            type: transTypeInput.value,
            category: transCategorySelect.value,
            date: document.getElementById('transDate').value,
            notes: document.getElementById('transNotes').value
        };

        api.post('/api/finance/transactions', data)
            .then(() => {
                modal.style.display = 'none';
                transactionForm.reset();
                loadDashboard(); // Refresh numbers
                loadTransactions(); // Refresh list
            })
            .catch(err => {
                alert("Error: " + (err.response?.data?.detail || "Unknown error"));
            });
    }

    function formatMoney(amount) {
        return '₹' + parseFloat(amount).toFixed(2);
    }



    // --- 5. LOGOUT LOGIC ---
    const logoutButton = document.getElementById('logoutButton');
    if (logoutButton) {
        logoutButton.onclick = function() {
            // 1. Remove the key
            localStorage.removeItem('access_token');
            // 2. Kick them out
            window.location.href = '/login';
        };
    }


    // --- 6. SUMMARY LOGIC ---
    const summaryModal = document.getElementById('summaryModal');
    const viewSummaryBtn = document.getElementById('viewSummaryBtn');
    const closeSummaryModal = document.getElementById('closeSummaryModal');
    const summaryForm = document.getElementById('summaryForm');

    // Open Modal
    viewSummaryBtn.onclick = function() {
        summaryModal.style.display = 'block';
        // Default to current month?
        const today = new Date();
        const firstDay = new Date(today.getFullYear(), today.getMonth(), 1);
        
        // Helper to format YYYY-MM-DD for the input
        const toISODate = (d) => d.toISOString().split('T')[0];
        
        document.getElementById('startDate').value = toISODate(firstDay);
        document.getElementById('endDate').value = toISODate(today);
    }

    // Close Modal
    closeSummaryModal.onclick = function() {
        summaryModal.style.display = 'none';
    }

    // Handle Form Submit -> Redirect to new page
    summaryForm.onsubmit = function(e) {
        e.preventDefault();
        const start = document.getElementById('startDate').value;
        const end = document.getElementById('endDate').value;
        
        // Redirect to the summary page with dates in the URL
        window.location.href = `/finance/summary?start=${start}&end=${end}`;
    }
    
    // Close modal when clicking outside
    window.onclick = function(e) {
        if (e.target == document.getElementById('transactionModal')) {
             document.getElementById('transactionModal').style.display = 'none';
        }
        if (e.target == summaryModal) {
             summaryModal.style.display = 'none';
        }
    }
});