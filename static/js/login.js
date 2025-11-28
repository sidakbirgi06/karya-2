// static/login.js

document.addEventListener('DOMContentLoaded', function() {

    // --- SIGNUP FORM LOGIC ---
    const signupForm = document.getElementById('signupForm');
    const signupMessage = document.getElementById('signupMessage');

    // --- NEW: Check if the signup form exists on this page ---
    if (signupForm) {

        // Get the new elements we just created
        const ownerFields = document.getElementById('ownerFields');
        const employeeFields = document.getElementById('employeeFields');
        const roleOwner = document.getElementById('roleOwner');
        const roleEmployee = document.getElementById('roleEmployee');

        // This function shows/hides the correct fields
        function toggleRoleFields() {
            if (roleOwner.checked) {
                // If "Owner" is checked, show Owner fields and hide Employee fields
                ownerFields.classList.remove('hidden');
                employeeFields.classList.add('hidden');
            } else {
                // If "Employee" is checked, hide Owner fields and show Employee fields
                ownerFields.classList.add('hidden');
                employeeFields.classList.remove('hidden');
            }
        }

        // Add "click" listeners to the radio buttons
        roleOwner.addEventListener('click', toggleRoleFields);
        roleEmployee.addEventListener('click', toggleRoleFields);
        
        // Run it once on page load to set the correct initial state (Owner)
        toggleRoleFields();


        signupForm.onsubmit = function(event) {
            event.preventDefault(); // Stop the form from reloading

            // Get all the values from the form
            const email = document.getElementById('signupEmail').value;
            const password = document.getElementById('signupPassword').value;
            const role = document.querySelector('input[name="role"]:checked').value;
            
            // Build the data payload
            let payload = {
                email: email,
                password: password,
                role: role,
                companyName: null, // Start with null
                companyCode: null  // Start with null
            };

            // Add the correct company field based on the selected role
            if (role === 'owner') {
                payload.companyName = document.getElementById('companyName').value;
            } else {
                payload.companyCode = document.getElementById('companyCode').value;
            }

            // Send the new payload to our backend /signup endpoint
            axios.post('/signup', payload)
            .then(function(response) {
                // If successful, show a success message
                signupMessage.style.color = 'green';
                signupMessage.textContent = 'Signup successful! You can now log in.';
                signupForm.reset(); // Clear the form
                toggleRoleFields(); // Reset the fields
            })
            .catch(function(error) {
                // If there's an error
                signupMessage.style.color = 'red';
                signupMessage.textContent = error.response.data.detail || 'Signup failed.';
            });
        };
    } 


    // --- LOGIN FORM LOGIC ---
    const loginForm = document.getElementById('loginForm');
    const loginMessage = document.getElementById('loginMessage');

    if (loginForm) {
        loginForm.onsubmit = function(event) {
            event.preventDefault(); 

            const email = document.getElementById('loginEmail').value;
            const password = document.getElementById('loginPassword').value;

            const formData = new URLSearchParams();
            formData.append('username', email); 
            formData.append('password', password);

            axios.post('/login', formData)
            .then(function(response) {
                // SUCCESS! 
                // We do NOT need to save the token. The browser has the cookie now.
                window.location.href = '/'; 
            })
            .catch(function(error) {
                loginMessage.style.color = 'red';
                loginMessage.textContent = 'Incorrect email or password.';
            });
        };
    }

});