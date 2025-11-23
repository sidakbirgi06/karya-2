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

    // --- NEW: Check if the login form exists on this page ---
    if (loginForm) {
        loginForm.onsubmit = function(event) {
            event.preventDefault(); // Stop the form from reloading the page

            // Get values from the form
            const email = document.getElementById('loginEmail').value;
            const password = document.getElementById('loginPassword').value;

            // CRITICAL: Our backend /login route expects "form data", not JSON.
            const formData = new URLSearchParams();
            formData.append('username', email); // It expects "username", which is our email
            formData.append('password', password);

            // Send the form data to our backend /login endpoint
            axios.post('/login', formData)
            .then(function(response) {
                // If successful, we get a token back
                const token = response.data.access_token;
                
                // 1. Save the token to the browser's "digital wallet"
                localStorage.setItem('access_token', token);

                // 2. Redirect the user to the main calendar page
                window.location.href = '/'; 
            })
            .catch(function(error) {
                // If login fails (wrong email/password)
                loginMessage.style.color = 'red';
                loginMessage.textContent = 'Incorrect email or password.';
            });
        };
    } // --- End of new "if" block ---

});