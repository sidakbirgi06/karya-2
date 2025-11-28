// static/js/notebook.js

document.addEventListener('DOMContentLoaded', function() {
    
    // --- 1. SETUP AXIOS ---
    const api = axios.create();
    api.interceptors.response.use(
        response => response,
        error => {
            if (error.response && error.response.status === 401) {
                window.location.href = '/login';
            }
            return Promise.reject(error);
        }
    );

    // --- 2. ELEMENTS ---
    const grid = document.getElementById('bookshelfGrid');
    const modal = document.getElementById('notebookModal');
    const createBtn = document.getElementById('createNotebookBtn');
    const closeBtn = document.querySelector('.close-button');
    const form = document.getElementById('notebookForm');
    const logoutButton = document.getElementById('logoutButton');

    // --- 3. LOAD NOTEBOOKS ---
    loadNotebooks();

    function loadNotebooks() {
        api.get('/api/notebooks')
            .then(res => {
                const notebooks = res.data;
                renderNotebooks(notebooks);
            })
            .catch(err => {
                console.error(err);
                grid.innerHTML = '<p>Error loading notebooks.</p>';
            });
    }

    function renderNotebooks(list) {
        if (list.length === 0) {
            grid.innerHTML = '<p>No notebooks yet. Create one!</p>';
            return;
        }
        grid.innerHTML = ''; // Clear loading text
        
        list.forEach(nb => {
            const div = document.createElement('div');
            // Add the dynamic color class (e.g., "notebook-blue")
            div.className = `notebook-item notebook-${nb.cover}`;
            div.innerHTML = `<div class="notebook-title">${nb.name}</div>`;
            
            // Make it clickable
            div.onclick = function() {
                // UNCOMMENT THIS NOW:
                window.location.href = `/notebooks/${nb.id}`; 
            };
            
            grid.appendChild(div);
        });
    }

    // --- 4. CREATE NOTEBOOK LOGIC ---
    
    // Color Picker Logic
    const colorCircles = document.querySelectorAll('.color-circle');
    const colorInput = document.getElementById('notebookCover');
    
    colorCircles.forEach(circle => {
        circle.onclick = function() {
            // Remove 'selected' from all
            colorCircles.forEach(c => c.classList.remove('selected'));
            // Add 'selected' to clicked
            this.classList.add('selected');
            // Update hidden input
            colorInput.value = this.dataset.color;
        }
    });
    // Select the first one by default
    if(colorCircles.length > 0) colorCircles[0].click();

    // Form Submit
    form.onsubmit = function(e) {
        e.preventDefault();
        const data = {
            name: document.getElementById('notebookName').value,
            cover: colorInput.value
        };
        
        api.post('/api/notebooks', data)
            .then(() => {
                modal.style.display = 'none';
                form.reset();
                loadNotebooks(); // Reload grid
            })
            .catch(err => alert("Error creating notebook"));
    }

    // --- 5. MODAL & LOGOUT UTILS ---
    createBtn.onclick = () => modal.style.display = 'block';
    closeBtn.onclick = () => modal.style.display = 'none';
    window.onclick = (e) => { if(e.target == modal) modal.style.display = 'none'; }
    
    if (logoutButton) {
        logoutButton.onclick = function() {
            api.post('/logout').then(() => window.location.href = '/login');
        }
    }
});