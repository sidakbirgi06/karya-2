// static/script.js

document.addEventListener('DOMContentLoaded', function() {

    // --- 1. BOUNCER & ROLE CHECK ---
    let userRole = null;
    let employeeList = [];

    // --- MOVE THIS UP HERE (So 'api' exists before we use it) ---
    const api = axios.create();

    // Interceptor to kick us out if cookie is invalid
    api.interceptors.response.use(
        response => response,
        error => {
            if (error.response && error.response.status === 401) {
                window.location.href = '/login';
            }
            return Promise.reject(error);
        }
    );

    // NOW we can safely use 'api'
    api.get('/api/me')
        .then(res => {
            userRole = res.data.role;
            console.log("Logged in as:", userRole);
            
            // If we are an owner, fetch employees immediately
            if (userRole === 'owner') {
                fetchEmployees();
            }
        })
        .catch(err => {
            console.error("Not logged in or API error", err);
        });

    // --- 2. GLOBAL STATE ---
    let currentView = 'general'; // 'general' or 'personal'
    let currentModalView = 'event'; // 'event' or 'task'

    // --- 3. GET HTML ELEMENTS ---
    // Modals
    var createModal = document.getElementById('createModal'); // Renamed
    var createModalCloseButton = createModal.querySelector('.close-button');
    
    // Modal Toggles
    var navCreateEvent = document.getElementById('navCreateEvent');
    var navCreateTask = document.getElementById('navCreateTask');

    // Event Form
    var eventForm = document.getElementById('eventForm');
    var calendarTypeSelect = document.getElementById('calendarType');
    var eventStartInput = document.getElementById('eventStart');
    
    // Task Form
    var taskForm = document.getElementById('taskForm');
    var taskAssigneeSelect = document.getElementById('taskAssignee');
    var taskDueDateInput = document.getElementById('taskDueDate');

    // Details Modal
    var detailsModal = document.getElementById('detailsModal');
    var detailsCloseButton = document.getElementById('detailsCloseButton');
    var detailsTitle = document.getElementById('detailsTitle');
    var detailsStart = document.getElementById('detailsStart');
    var detailsEnd = document.getElementById('detailsEnd');
    var detailsPlace = document.getElementById('detailsPlace');
    var detailsNotes = document.getElementById('detailsNotes');
    var deleteButton = document.getElementById('deleteButton');
    var currentEventId = null;

    // Header Navigation
    var navGeneral = document.getElementById('navGeneral');
    var navPersonal = document.getElementById('navPersonal');
    var logoutButton = document.getElementById('logoutButton');


    // --- 5. HELPER FUNCTIONS ---
    function fetchEmployees() {
        // Only owners can fetch employees
        if (userRole === 'owner') {
            api.get('/api/my-employees')
                .then(function(response) {
                    employeeList = response.data;
                    // Populate the dropdown
                    taskAssigneeSelect.innerHTML = ''; // Clear old options
                    employeeList.forEach(function(emp) {
                        var option = document.createElement('option');
                        option.value = emp.id;
                        option.textContent = emp.email;
                        taskAssigneeSelect.appendChild(option);
                    });
                })
                .catch(function(error) {
                    console.error('Error fetching employees:', error);
                });
        }
    }

    // --- 6. FULLCALENDAR SETUP ---
    var calendarEl = document.getElementById('calendar');
    var calendar = new FullCalendar.Calendar(calendarEl, {
        
        initialView: 'dayGridMonth',
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,dayGridWeek'
        },

        // --- NEW: Smarter Events Function ---
        events: function(fetchInfo, successCallback, failureCallback) {
            
            // We only care about the *currentView* to toggle permissions,
            // not to fetch data. This one endpoint gets everything.
            api.get('/calendar/feed') // <-- Our new "super" endpoint
                .then(function(response) {
                    
                    // 1. Get the two lists from the response
                    let events = response.data.events;
                    let tasks = response.data.tasks;

                    // 2. Translate Events (This code is the same as before)
                    let translatedEvents = events.map(function(event) {
                        // Only show events that match our current view
                        if (event.calendar_type === currentView) {
                            return {
                                start: event.start_time, 
                                end: event.end_time,     
                                title: event.title,
                                id: event.id,
                                color: (event.calendar_type === 'general') ? '#3788d8' : '#33a00e', // Blue/Green
                                extendedProps: {
                                    type: 'event', 
                                    place: event.place,
                                    notes: event.notes,
                                    calendar_type: event.calendar_type
                                }
                            };
                        }
                        return null; // Return null if it doesn't match the view
                    }).filter(Boolean); // .filter(Boolean) removes all the nulls
                    
                    // 3. Translate Tasks (This code is the same as before)
                    let translatedTasks = tasks.map(function(task) {
                        // Only show tasks if we are on the "general" view
                        if (currentView === 'general') {
                            return {
                                start: task.due_date, 
                                title: task.title,
                                id: task.id,
                                color: '#f0ad4e', // Yellow for tasks
                                extendedProps: {
                                    type: 'task',
                                    status: task.status,
                                    assignee_id: task.assignee_id
                                }
                            };
                        }
                        return null;
                    }).filter(Boolean); // Removes nulls
                    
                    // 4. Send all items to the calendar
                    successCallback(translatedEvents.concat(translatedTasks));
                })
                .catch(function(error) {
                    console.error('Error fetching calendar feed:', error);
                    if (error.response && error.response.status === 401) {
                        localStorage.removeItem('access_token');
                    }
                    failureCallback(error);
                });
        },
        
        // --- NEW: Upgraded Click Handlers ---
        dateClick: function(info) {
            let canCreate = false;
            if (currentView === 'personal') {
                canCreate = true; // Anyone can create personal events
            } else if (currentView === 'general' && userRole === 'owner') {
                canCreate = true; // Only owners can create general items
            }

            if (!canCreate) return; // Stop if they don't have permission

            // Set the modal to its default state ("Create Event")
            navCreateEvent.click(); 

            // Set the correct calendar type in the dropdown
            calendarTypeSelect.value = currentView;

            // Pre-fill the dates
            eventStartInput.value = info.dateStr + 'T10:00';
            taskDueDateInput.value = info.dateStr + 'T17:00';

            // Show/hide UI based on role and view
            if (currentView === 'personal') {
                // On personal calendar, hide the "General" option and the "Task" toggle
                calendarTypeSelect.querySelector('option[value="general"]').style.display = 'none';
                navCreateTask.style.display = 'none';
            } else if (currentView === 'general' && userRole === 'owner') {
                // On general calendar as owner, show everything
                calendarTypeSelect.querySelector('option[value="general"]').style.display = 'block';
                navCreateTask.style.display = 'block';
                // Go fetch the employee list for the dropdown
                fetchEmployees();
            }

            createModal.style.display = 'block';
        },

        eventClick: function(info) {
            var event = info.event;
            
            // Check permissions (read-only for employees on general view)
            if (currentView === 'general' && userRole === 'employee') {
                return; // Employees can't click general items
            }
            
            // --- We'll just show the *existing* details modal for now ---
            // (We will upgrade this later to show task-specific info)
            
            currentEventId = event.id;
            detailsTitle.textContent = event.title;
            
            if (event.extendedProps.type === 'task') {
                // This is a Task
                detailsStart.textContent = new Date(event.start).toLocaleString();
                detailsEnd.textContent = 'N/A';
                detailsPlace.textContent = 'N/A';
                detailsNotes.textContent = "Status: " + event.extendedProps.status;
                // We'll hide the delete button for tasks for now
                deleteButton.style.display = 'none';
            } else {
                // This is an Event
                detailsStart.textContent = new Date(event.start).toLocaleString();
                detailsEnd.textContent = new Date(event.end).toLocaleString();
                detailsPlace.textContent = event.extendedProps.place || 'N/A';
                detailsNotes.textContent = event.extendedProps.notes || 'N/A';
                deleteButton.style.display = 'block';
            }

            detailsModal.style.display = 'block';
        }
    });

    // 7. RENDER THE CALENDAR
    calendar.render();

    // --- 8. NAVIGATION CLICK HANDLERS ---
    
    // Header Nav
    navGeneral.onclick = function(e) { e.preventDefault(); currentView = 'general'; navGeneral.classList.add('active-nav'); navPersonal.classList.remove('active-nav'); calendar.refetchEvents(); }
    navPersonal.onclick = function(e) { e.preventDefault(); currentView = 'personal'; navPersonal.classList.add('active-nav'); navGeneral.classList.remove('active-nav'); calendar.refetchEvents(); }
    
    // Modal Nav
    navCreateEvent.onclick = function(e) {
        e.preventDefault();
        currentModalView = 'event';
        navCreateEvent.classList.add('active-nav');
        navCreateTask.classList.remove('active-nav');
        eventForm.classList.remove('hidden');
        taskForm.classList.add('hidden');
    }
    navCreateTask.onclick = function(e) {
        e.preventDefault();
        currentModalView = 'task';
        navCreateTask.classList.add('active-nav');
        navCreateEvent.classList.remove('active-nav');
        taskForm.classList.remove('hidden');
        eventForm.classList.add('hidden');
    }

    // --- 9. FORM & BUTTON LOGIC ---

    // Create Event Form
    eventForm.onsubmit = function(event) {
        event.preventDefault(); 
        var newEvent = {
            title: document.getElementById('eventTitle').value,
            start_time: eventStartInput.value,
            end_time: document.getElementById('eventEnd').value,
            place: document.getElementById('eventPlace').value,
            notes: document.getElementById('eventNotes').value,
            calendar_type: calendarTypeSelect.value // Use the dropdown's value
        };
        api.post('/calendar/general/events', newEvent)
            .then(function() { createModal.style.display = 'none'; calendar.refetchEvents(); })
            .catch(function(error) { console.error('Error creating event:', error); alert('Error: ' + error.response.data.detail); });
    }
    
    // NEW: Create Task Form
    taskForm.onsubmit = function(event) {
        event.preventDefault();
        var newTask = {
            title: document.getElementById('taskTitle').value,
            due_date: taskDueDateInput.value,
            status: document.getElementById('taskStatus').value,
            assignee_id: taskAssigneeSelect.value
        };
        api.post('/api/tasks', newTask)
            .then(function() { createModal.style.display = 'none'; calendar.refetchEvents(); })
            .catch(function(error) { console.error('Error creating task:', error); alert('Error: ' + error.response.data.detail); });
    }

    // Delete Button (for Events only right now)
    deleteButton.onclick = function() {
        if (currentEventId === null) return; 
        if (!confirm('Are you sure you want to delete this event?')) return;
        api.delete('/events/' + currentEventId)
            .then(function() { detailsModal.style.display = 'none'; calendar.refetchEvents(); currentEventId = null; })
            .catch(function(error) { console.error('Error deleting event:', error); alert('Error: ' + error.response.data.detail); });
    }

    // Logout Button
    logoutButton.onclick = function() { 
        api.post('/logout')
            .then(() => { window.location.href = '/login'; })
            .catch(() => { window.location.href = '/login'; });
    }

    // Modal Close Logic
    createModalCloseButton.onclick = function() { createModal.style.display = 'none'; }
    detailsCloseButton.onclick = function() { detailsModal.style.display = 'none'; }
    window.onclick = function(event) {
        if (event.target == createModal) createModal.style.display = 'none';
        if (event.target == detailsModal) detailsModal.style.display = 'none';
    }
});