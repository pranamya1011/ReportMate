const issueTypeSelect = document.getElementById('issue_type');
const customIssueInput = document.getElementById('custom_issue');

issueTypeSelect.addEventListener('change', () => {
    if (issueTypeSelect.value === 'Other') {
        customIssueInput.style.display = 'block';
        customIssueInput.focus();
    } else {
        customIssueInput.style.display = 'none';
        customIssueInput.value = '';
    }
});

document.getElementById('reportForm').addEventListener('submit', async function(event) {
    event.preventDefault();

    const form = event.target;

    // If "Other" is selected, replace issue_type value with custom input value
    if (issueTypeSelect.value === 'Other') {
        if (customIssueInput.value.trim() === '') {
            alert('Please specify the issue.');
            return;
        }
        // Temporarily set the select value to custom issue for submission
        issueTypeSelect.value = customIssueInput.value.trim();
    }

    const formData = new FormData(form);

    try {
const response = await fetch('http://127.0.0.1:5000/report', {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            const responseData = await response.json();
            // Assuming the backend returns the inserted report ID in response
            const reportId = responseData.id;
                if (reportId) {
                    // Redirect to checkreport route with reportId as query param
                    window.location.href = `/checkreport?reportId=${reportId}`;
                } else {
                    alert('Report submitted successfully!');
                    form.reset();
                    // Hide custom issue input after reset
                    customIssueInput.style.display = 'none';
                }
        } else {
            const errorData = await response.json();
            alert('Error: ' + (errorData.error || 'Failed to submit report'));
        }
    } catch (error) {
        alert('Error connecting to server');
    }
});

async function loadWorkers(location) {
    try {
        let url = 'http://127.0.0.1:5000/workers';
        if (location) {
            url += '?location=' + encodeURIComponent(location);
        }
        const response = await fetch(url);
        if (response.ok) {
            const workers = await response.json();
            const workersList = document.getElementById('workersList');
            workersList.innerHTML = '';
workers.forEach(worker => {
    const li = document.createElement('li');
    li.innerHTML = `<strong>${worker.name}</strong> - Skills: ${worker.skills}`;
    workersList.appendChild(li);
});
        } else {
            alert('Failed to fetch workers');
        }
    } catch (error) {
        alert('Error connecting to server');
    }
}

// Clear workers list on page load (no workers shown initially)
window.onload = () => {
    const workersList = document.getElementById('workersList');
    workersList.innerHTML = '';
};

document.getElementById('checkWorkersBtn').addEventListener('click', () => {
    const locationInput = document.getElementById('location');
    const issueTypeInput = document.getElementById('issue_type');
    const location = locationInput.value.trim();
    const issueType = issueTypeInput.value.trim();
    const workerAvailabilityMessage = document.getElementById('workerAvailabilityMessage');
    if (location) {
        // Hide the availability message
        workerAvailabilityMessage.style.display = 'none';

        // Load and show the workers list
        loadWorkers(location, issueType);
        const workersContainer = document.getElementById('workersContainer');
        workersContainer.style.display = 'block';
    } else {
        alert('Please enter your location to check nearby workers.');
        workerAvailabilityMessage.style.display = 'none';
    }
});

async function loadWorkers(location, issueType) {
    try {
        let url = 'http://127.0.0.1:5000/workers';
        const params = [];
        if (location) {
            params.push('location=' + encodeURIComponent(location));
        }
        if (issueType) {
            params.push('issue_type=' + encodeURIComponent(issueType));
        }
        if (params.length > 0) {
            url += '?' + params.join('&');
        }
        console.log('Fetching workers from URL:', url);
        const response = await fetch(url);
        if (response.ok) {
            const workers = await response.json();
            console.log('Workers received:', workers);
            const workersList = document.getElementById('workersList');
            workersList.innerHTML = '';
                if (workers.length === 0) {
                    const li = document.createElement('li');
                    li.textContent = 'No workers found for the selected location and issue type.';
                    workersList.appendChild(li);
                } else {
                    workers.forEach(worker => {
                        const li = document.createElement('li');
                        li.innerHTML = `<label><input type="radio" name="workerSelect" value="${worker.id}"> <strong>${worker.name}</strong></label>`;
                        workersList.appendChild(li);
                    });

                    // Add event listener for worker selection
                    const workerRadios = document.getElementsByName('workerSelect');
                    workerRadios.forEach(radio => {
                        radio.addEventListener('change', () => {
                            const selectedWorkerId = radio.value;
                            const selectedWorkerName = radio.parentElement.textContent.trim();

                            // Hide workers list and container
                            const workersContainer = document.getElementById('workersContainer');
                            workersContainer.style.display = 'none';

                            // Show selected worker message
                            const selectedWorkerContainer = document.getElementById('selectedWorkerContainer');
                            selectedWorkerContainer.textContent = `This worker has been selected: ${selectedWorkerName}`;
                            selectedWorkerContainer.style.display = 'block';

                            // Optionally, store selected worker id for form submission or further processing
                            // For example, add a hidden input to the form
                            let hiddenInput = document.getElementById('selectedWorkerId');
                            if (!hiddenInput) {
                                hiddenInput = document.createElement('input');
                                hiddenInput.type = 'hidden';
                                hiddenInput.id = 'selectedWorkerId';
                                hiddenInput.name = 'selectedWorkerId';
                                document.getElementById('reportForm').appendChild(hiddenInput);
                            }
                            hiddenInput.value = selectedWorkerId;
                        });
                    });
                }
        } else {
            alert('Failed to fetch workers');
        }
    } catch (error) {
        alert('Error connecting to server');
        console.error('Error fetching workers:', error);
    }
}
