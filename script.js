function showRegister() {
    document.getElementById('registerForm').style.display = 'block';
    document.getElementById('loginForm').style.display = 'none';
    // Hide login button
    document.querySelector('button[onclick="showLogin()"]').style.display = 'none';
    // Hide register button to prevent multiple clicks
    document.querySelector('button[onclick="showRegister()"]').style.display = 'none';
}

function showLogin() {
    document.getElementById('loginForm').style.display = 'block';
    document.getElementById('registerForm').style.display = 'none';
    // Hide register button
    document.querySelector('button[onclick="showRegister()"]').style.display = 'none';
    // Hide login button to prevent multiple clicks
    document.querySelector('button[onclick="showLogin()"]').style.display = 'none';
}

async function register() {
    const username = document.getElementById('registerUsername').value;
    const email = document.getElementById('registerEmail').value;
    const password = document.getElementById('registerPassword').value;
    if (username && email && password) {
        try {
            const response = await fetch('http://localhost:5000/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ username, email, password })
            });
            const data = await response.json();
            if (response.ok) {
                alert(data.message);
                document.getElementById('registerUsername').value = '';
                document.getElementById('registerEmail').value = '';
                document.getElementById('registerPassword').value = '';
                const authSection = document.getElementById('auth-section');
                authSection.innerHTML = '<h2>Welcome, ' + username + '! You are logged in.</h2>';
            } else {
                alert(data.error || 'Registration failed');
            }
        } catch (error) {
            alert('Error connecting to server');
        }
    } else {
        alert('Please enter username, email, and password to register.');
    }
}

async function login() {
    const username = document.getElementById('loginUsername').value;
    const password = document.getElementById('loginPassword').value;
    if (username && password) {
        try {
            const response = await fetch('http://localhost:5000/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ username, password })
            });
            const data = await response.json();
            if (response.ok) {
                alert(data.message);
                document.getElementById('loginUsername').value = '';
                document.getElementById('loginPassword').value = '';
                // Check if user has previous reports
                const hasReportsResponse = await fetch(`http://localhost:5000/user/${encodeURIComponent(username)}/has_reports`);
                const hasReportsData = await hasReportsResponse.json();
                if (hasReportsData.has_reports) {
                    // Prompt user to choose between new report or check status
                    const choice = confirm("Press OK to issue a new report, or Cancel to check the status of a previous report.");
                    if (choice) {
                        window.location.href = '/report';
                    } else {
                        window.location.href = '/checkreport';
                    }
                } else {
                    // No previous reports, redirect to new report page
                    window.location.href = '/report';
                }
            } else {
                alert(data.error || 'Login failed');
            }
        } catch (error) {
            alert('Error connecting to server');
        }
    } else {
        alert('Please enter both username and password to login.');
    }
}

async function showUsers() {
    try {
        const response = await fetch('http://localhost:5000/users');
        if (response.ok) {
            const users = await response.json();
            const usersUl = document.getElementById('usersUl');
            usersUl.innerHTML = '';
            users.forEach(user => {
                const li = document.createElement('li');
                li.textContent = `Username: ${user.username}, Email: ${user.email}`;
                usersUl.appendChild(li);
            });
            document.getElementById('usersList').style.display = 'block';
        } else {
            alert('Failed to fetch users');
        }
    } catch (error) {
        alert('Error connecting to server');
    }
}
