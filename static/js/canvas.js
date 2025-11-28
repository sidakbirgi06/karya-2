// static/js/canvas.js

document.addEventListener('DOMContentLoaded', function() {
    
    let editingNoteId = null;
    let isEditMode = false;


    // 1. SETUP
    const api = axios.create();
    api.interceptors.response.use(
        response => response,
        error => { if (error.response?.status === 401) window.location.href = '/login'; return Promise.reject(error); }
    );

    const notebookId = document.getElementById('notebookId').value;
    const grid = document.getElementById('masonryGrid');
    const titleEl = document.getElementById('notebookTitle');

    // Modals
    const textModal = document.getElementById('textModal');
    const listModal = document.getElementById('listModal');
    
    // 2. INITIAL LOAD
    loadNotebookDetails();
    loadNotes();

    function loadNotebookDetails() {
        api.get(`/api/notebooks/${notebookId}`)
            .then(res => {
                titleEl.textContent = res.data.name;
            })
            .catch(err => titleEl.textContent = "Notebook not found");
    }

    function loadNotes() {
        api.get(`/api/notebooks/${notebookId}/notes`)
            .then(res => {
                renderNotes(res.data);
            });
    }

    // 3. RENDER LOGIC
    function renderNotes(notes) {
        grid.innerHTML = '';
        notes.forEach(note => {
            const card = document.createElement('div');
            card.className = 'note-card';

            card.onclick = (e) => {
                // Ignore clicks on the delete button
                if (e.target.classList.contains('delete-note-btn')) return;
                openEditModal(note);
            };
            
            // --- NEW: Delete Button ---
            // We put it at the top-right
            let html = `
                <div class="note-header">
                    <span class="delete-note-btn" onclick="deleteNote(${note.id})">&times;</span>
                </div>
            `;
            // --------------------------

            if (note.title) html += `<div class="note-title">${note.title}</div>`;
            
            // (The rest of your Body/Checklist logic stays the same...)
            if (note.type === 'checklist') {
                // ... existing checklist code ...
                try {
                    const items = JSON.parse(note.content);
                    html += `<div class="checklist-container">`;
                    items.forEach(item => {
                        const checked = item.done ? 'checked' : '';
                        html += `
                            <div class="checklist-item ${checked}">
                                <input type="checkbox" ${checked} disabled> 
                                <span>${item.text}</span>
                            </div>`;
                    });
                    html += `</div>`;
                } catch(e) { html += '<p class="error">Error loading list</p>'; }
            } else {
                html += `<div class="note-body">${note.content || ''}</div>`;
            }

            card.innerHTML = html;
            grid.appendChild(card);
        });
    }

    // 4. CREATE LOGIC
    
    // Open Modals
    document.getElementById('addTextBtn').onclick = () => textModal.style.display = 'block';
    document.getElementById('addChecklistBtn').onclick = () => listModal.style.display = 'block';

    // Close Modals
    document.querySelectorAll('.close-button').forEach(btn => {
        btn.onclick = () => { textModal.style.display = 'none'; listModal.style.display = 'none'; };
    });

    // Submit Text Note
    document.getElementById('textForm').onsubmit = function(e) {
        e.preventDefault();
        saveNote({
            title: document.getElementById('textTitle').value,
            content: document.getElementById('textContent').value,
            type: 'text'
        }, textModal);
    };

    // Submit Checklist
    document.getElementById('listForm').onsubmit = function(e) {
        e.preventDefault();
        // Convert textarea lines into JSON
        const rawText = document.getElementById('listContent').value;
        const lines = rawText.split('\n').filter(line => line.trim() !== '');
        const jsonItems = lines.map(line => ({ text: line, done: false }));
        
        saveNote({
            title: document.getElementById('listTitle').value,
            content: JSON.stringify(jsonItems), // Save as JSON string
            type: 'checklist'
        }, listModal);
    };

    function saveNote(payload, activeModal) {
        let promise;

        // CHECK: Are we editing an old note or making a new one?
        if (editingNoteId) {
            // UPDATE existing (PUT)
            promise = api.put(`/api/notebooks/notes/${editingNoteId}`, payload);
        } else {
            // CREATE new (POST)
            promise = api.post(`/api/notebooks/${notebookId}/notes`, payload);
        }

        promise
            .then(() => {
                activeModal.style.display = 'none';
                activeModal.querySelector('form').reset();
                editingNoteId = null; // Clear the ID so next time we create new
                loadNotes(); // Refresh the grid
            })
            .catch(err => alert("Error saving note"));
    }


    function openEditModal(note) {
        editingNoteId = note.id;
        
        // 1. TEXT NOTE
        if (note.type === 'text') {
            const titleInput = document.getElementById('textTitle');
            const contentInput = document.getElementById('textContent');
            const saveBtn = document.getElementById('saveTextBtn');
            const editBtn = document.getElementById('editTextBtn');

            // Fill Data
            titleInput.value = note.title || '';
            contentInput.value = note.content || '';

            // Set to View Mode (Disable inputs, Hide Save, Show Edit)
            setEditMode(false, [titleInput, contentInput], saveBtn, editBtn);

            textModal.style.display = 'block';
        } 
        // 2. CHECKLIST
        else if (note.type === 'checklist') {
            const titleInput = document.getElementById('listTitle');
            const contentInput = document.getElementById('listContent');
            const saveBtn = document.getElementById('saveListBtn');
            const editBtn = document.getElementById('editListBtn');
            const hint = document.getElementById('listHint');

            titleInput.value = note.title || '';
            
            // Convert JSON to text for the textarea
            try {
                const items = JSON.parse(note.content);
                contentInput.value = items.map(i => i.text).join('\n');
            } catch(e) { contentInput.value = ''; }

            // Set to View Mode
            setEditMode(false, [titleInput, contentInput], saveBtn, editBtn);
            hint.classList.add('hidden'); // Always hide hint in view mode

            listModal.style.display = 'block';
        }
    }

    // Helper to toggle between View and Edit
    function setEditMode(isEditing, inputs, saveBtn, editBtn) {
        inputs.forEach(input => input.disabled = !isEditing);
        
        if (isEditing) {
            saveBtn.classList.remove('hidden'); // Show Save
            editBtn.classList.add('hidden');    // Hide Pencil
            // Show hint only if it's the checklist
            if(inputs[0].id === 'listTitle') document.getElementById('listHint').classList.remove('hidden');
        } else {
            saveBtn.classList.add('hidden');    // Hide Save
            editBtn.classList.remove('hidden'); // Show Pencil
        }
    }


    // --- EDIT BUTTON LOGIC (Step 4) ---
    document.getElementById('editTextBtn').onclick = function() {
        const title = document.getElementById('textTitle');
        const content = document.getElementById('textContent');
        const save = document.getElementById('saveTextBtn');
        setEditMode(true, [title, content], save, this);
        title.focus();
    };

    document.getElementById('editListBtn').onclick = function() {
        const title = document.getElementById('listTitle');
        const content = document.getElementById('listContent');
        const save = document.getElementById('saveListBtn');
        setEditMode(true, [title, content], save, this);
        title.focus();
    };

    // --- CREATE NEW LOGIC (Step 5 - Force Edit Mode) ---
    document.getElementById('addTextBtn').onclick = () => {
        editingNoteId = null;
        document.getElementById('textForm').reset();
        
        const title = document.getElementById('textTitle');
        const content = document.getElementById('textContent');
        const save = document.getElementById('saveTextBtn');
        const edit = document.getElementById('editTextBtn');
        
        setEditMode(true, [title, content], save, edit);
        textModal.style.display = 'block';
    };
    
    document.getElementById('addChecklistBtn').onclick = () => {
        editingNoteId = null;
        document.getElementById('listForm').reset();
        
        const title = document.getElementById('listTitle');
        const content = document.getElementById('listContent');
        const save = document.getElementById('saveListBtn');
        const edit = document.getElementById('editListBtn');
        
        setEditMode(true, [title, content], save, edit);
        listModal.style.display = 'block';
    };
});


// Add this OUTSIDE the DOMContentLoaded block
window.deleteNote = function(noteId) {
    if(!confirm("Are you sure you want to delete this note?")) return;

    // We need axios (it's loaded globally via CDN so this works)
    axios.delete(`/api/notebooks/notes/${noteId}`)
        .then(() => {
            // Reload the notes to show it's gone
            // We need to trigger the loadNotes function inside the scope.
            // A cleaner way is to just reload the page for MVP, 
            // OR we can make loadNotes global. 
            // Let's just reload the list by finding the grid and removing the item visually 
            // strictly speaking, but reloading is safer for sync.
            location.reload(); 
        })
        .catch(err => alert("Error deleting note"));
}