let map;
        let markers = {}; // To hold markers with IMEI as key
        let routePath = [];
        let selectedImei = null;
        let routeHistory = JSON.parse(localStorage.getItem('routeHistory')) || [];
        let previousStates = {}; 
        let infoWindow; // Declare the infoWindow globally
        let isSearching = false; // Flag to track if we are in search mode
        const searchKey = 'searchImei'; // Key to store search input in localStorage
        let highlightedMarker = null;
        let data = [];  // Global variable to hold fetched data
let currentPage = 1;
let rowsPerPage = 10;
let totalPages = 0;

        
        let countdownTime = 30; // Set the initial countdown time in seconds
    const countdownElement = document.getElementById('countdown');
    
    function highlightMarker(marker) {
    if (highlightedMarker) {
        // Reset the previously highlighted marker to its original state
        highlightedMarker.setIcon({
            url: 'http://64.227.135.38/car1.png',
            scaledSize: new google.maps.Size(38, 38),
        });
        highlightedMarker.setAnimation(null); // Stop any existing animations
        // Remove the blink effect from the previously highlighted marker
        highlightedMarker.setOptions({ icon: highlightedMarker.getIcon(), zIndex: 1 });
    }

    // Highlight the new marker with the blink effect and larger icon
    marker.setIcon({
        url: 'http://64.227.135.38/car1.png', // Use the same image or a different one
        scaledSize: new google.maps.Size(50, 50), // Make the icon larger
    });

    // Apply blink effect by adding the class
    marker.setOptions({
        zIndex: 9999, // Ensure this marker is drawn above other markers
        icon: {
            url: 'http://64.227.135.38/car1.png',
            scaledSize: new google.maps.Size(50, 50),
            className: 'blink' // Add blink effect
        }
    });

    // Update the highlighted marker reference
    highlightedMarker = marker;
}


    function startCountdown() {
        setInterval(() => {
            countdownTime--;
            countdownElement.textContent = countdownTime;
            if (countdownTime === 0) {
                window.location.reload(); // Refresh the page when countdown reaches 0
            }
        }, 1000); // Update countdown every second
    }


    function initializeMap(lat = 0, lon = 0) {
    console.log("Initializing map at:", lat, lon);

    if (!map) {
        map = new google.maps.Map(document.getElementById('map'), {
            center: { lat: lat, lng: lon },
            zoom: 17
        });
        console.log("Map object:", map); // Log the map object

        routePath = new google.maps.Polyline({
            path: [],
            geodesic: true,
            strokeColor: '#FF0000',
            strokeOpacity: 1.0,
            strokeWeight: 2,
            icons: [{
                icon: {
                    path: google.maps.SymbolPath.FORWARD_CLOSED_ARROW,
                    scale: 3,
                    strokeColor: '#0000FF'
                },
                offset: '100%'
            }]
        });
        routePath.setMap(map);

        infoWindow = new google.maps.InfoWindow();
        mapInitialized = true;
    } else {
        map.setCenter({ lat: lat, lng: lon });
        map.setZoom(17);
    }
}

// Ensure map initialization in modal
$('#mapModal').on('shown.bs.modal', () => {
    let lastLat = parseFloat(localStorage.getItem('lastLat')) || 0;
    let lastLon = parseFloat(localStorage.getItem('lastLon')) || 0;
    
        initializeMap(lastLat, lastLon); // Initialize map with default or last known coordinates

    if (selectedImei && lastLat && lastLon) {
        updateMarker(selectedImei, lastLat, lastLon, null, null);  // Use last coordinates to update marker
    }
});



        // smooth marker/icom movement
function interpolatePosition(startLat, startLng, endLat, endLng, fraction) {
    const lat = (endLat - startLat) * fraction + startLat;
    const lng = (endLng - startLng) * fraction + startLng;
    return new google.maps.LatLng(lat, lng);
}


function animateMarker(marker, startLat, startLng, endLat, endLng, duration) {
    const startTime = performance.now();

    function animateStep(time) {
        const elapsed = time - startTime;
        const fraction = Math.min(elapsed / duration, 1);
        const newPosition = interpolatePosition(startLat, startLng, endLat, endLng, fraction);

        marker.setPosition(newPosition);
        if (fraction < 1) {
            requestAnimationFrame(animateStep);
        }
    }
    requestAnimationFrame(animateStep);
}


function updateMarker(imei, lat, lon, dir1, dir2, speed) {
    if (!map) {
        console.error("Map is not initialized. Unable to update marker.");
        return;
    }

    console.log(`Updating marker for IMEI: ${imei}, Speed: ${speed}`); // Log the speed value here

    const heading = calculateHeading(dir1, dir2);
    const latitude = parseFloat(lat);
    const longitude = parseFloat(lon);

    if (!isNaN(latitude) && !isNaN(longitude)) {
        const latLng = new google.maps.LatLng(latitude, longitude);

        if (markers[imei]) {
            const oldPosition = markers[imei].getPosition();
            animateMarker(
                markers[imei],
                oldPosition.lat(), oldPosition.lng(),
                latitude, longitude,
                10000 // Animation duration
            );

            // Check if speed is valid and update marker accordingly
            if (speed && !isNaN(speed)) {
                markers[imei].setIcon({
                    url: 'http://64.227.135.38/car1.png',
                    scaledSize: new google.maps.Size(38, 38),
                    rotation: heading
                });
            }

            markers[imei].setPosition(latLng);
        } else {
            markers[imei] = new google.maps.Marker({
                position: latLng,
                map: map,    
                icon: {
                    url: 'http://64.227.135.38/car1.png',
                    scaledSize: new google.maps.Size(38, 38),
                    rotation: heading
                },
                title: imei,
            });

            addMarkerClickListener(markers[imei], latLng, { imei, date: new Date(), time: new Date() }, { lat: latitude, lon: longitude }, speed);
        }

        highlightMarker(markers[imei]);

        map.panTo(latLng); // Center the map
        updateRoute(latitude, longitude);
    } else {
        console.error("Invalid latitude or longitude values:", lat, lon);
    }
}





function updateRoute(lat, lon) {
    // Get the current timestamp
    const now = new Date().getTime();
    // Add the new point with its timestamp to the route history
    routeHistory.push({ position: new google.maps.LatLng(lat, lon), timestamp: now });
    // Remove points older than 30 minutes
    const thirtyMinutesAgo = now - 30 * 60 * 1000;
    routeHistory = routeHistory.filter(point => point.timestamp >= thirtyMinutesAgo);

    localStorage.setItem('routeHistory', JSON.stringify(routeHistory));
    // Update the routePath with the latest points
    const path = routeHistory.map(point => point.position);
    routePath.setPath(path);
}

        function calculateHeading(dir1, dir2) {
            const direction = '${dir1}${dir2}';
            switch (direction) {
                case 'nn': return 0;   // North
                case 'ne': return 45;  // Northeast
                case 'ee': return 90;  // East
                case 'se': return 135; // Southeast
                case 'ss': return 180; // South
                case 'sw': return 225; // Southwest
                case 'ww': return 270; // West
                case 'nw': return 315; // Northwest
                default: return 0;     // Default
            }
        }
        
        function clearMarkers() {
            Object.values(markers).forEach(marker => marker.setMap(null));
            markers = {};
        }
        
        function parseCoordinates(lat, lon) {
            // Convert to 13.024585 and 77.370977
            const parsedLat = parseFloat(lat.slice(0, 2)) + parseFloat(lat.slice(2)) / 60;
            const parsedLon = parseFloat(lon.slice(0, 3)) + parseFloat(lon.slice(3)) / 60;
            return { lat: parsedLat, lon: parsedLon };
        }

        function updateMapIfModalOpen(lat, lon, imei, dir1, dir2) {
if ($('#mapModal').hasClass('show') && selectedImei === imei) {
    updateMarker(imei, lat, lon, dir1, dir2); // Update the marker's position
}
}


function addMarkerClickListener(marker, latLng, device, coords, speed) {
    marker.addListener('click', function() {
        console.log(`Marker clicked for IMEI: ${device.imei}, Speed: ${speed}`);

        const content = `
            <div class="info-window">
                <strong>IMEI:</strong> ${device.imei}<br>
                <strong>Lat:</strong> ${coords.lat.toFixed(6)}<br>
                <strong>Lon:</strong> ${coords.lon.toFixed(6)}<br>
                <strong>Last Update:</strong> ${formatDateTime(device.date, device.time).formattedDate} ${formatDateTime(device.date, device.time).formattedTime}<br>
                <strong>Speed:</strong> ${speed ? speed + ' km/h' : 'N/A'}<br>
            </div>`;

        infoWindow.setContent(content);
        infoWindow.setPosition(latLng);
        infoWindow.open(map, marker);
    });
}






// Function to perform reverse geocoding
function geocodeLatLng(latlng, callback) {
    const geocoder = new google.maps.Geocoder();
    geocoder.geocode({ location: latlng }, function(results, status) {
        if (status === 'OK' && results[0]) {
            callback(results[0].formatted_address);  // Return the formatted address
        } else {
            callback('Location not available');  // If geocoding fails, return a default message
        }
    });
}

// Function to format date and time
function formatDateTime(date, time) {
    const formattedDate = new Date(date).toLocaleDateString();
    const formattedTime = new Date(time).toLocaleTimeString();
    return { formattedDate, formattedTime };
}







async function fetchData(imei = '') {
    try {
        const url = `http://64.227.135.38:8001/api/data`;
        console.log("Fetching data from URL:", url);

        const response = await fetch(url);
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const data = await response.json();
        console.log("Received data:", data);

        // Store the fetched data globally
        data = await response.json();
        console.log("Received data:", data);

        // Calculate total pages based on the data length
        totalPages = Math.ceil(data.length / rowsPerPage);

        // Display the first page of data
        displayTable(data, currentPage);

        const tableBody = document.getElementById('data-table-body');
        const errorMessage = document.getElementById('error-message');
        const notification = document.getElementById('notification');
        const alertSound = document.getElementById('alert-sound');

        if (!data || data.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="99">No data available</td></tr>';
            return;
        }

        const fieldsToDisplay = [
            'imei', 'header', 'time', 'gps', 'latitude', 'dir1', 'longitude',
            'dir2', 'speed', 'course', 'date', 'checksum', 'ignition',
            'door', 'sos', 'r1', 'r2', 'ac', 'r3', 'main_power', 'harsh_speed', 'arm',
            'sleep', 'accelerometer', 'adc', 'one_wire', 'i_btn', 'odometer', 'temp', 'internal_bat',
            'gsm_sig', 'mcc', 'mnc', 'cellid'
        ];

        // Generate table headers if not already present
        const tableHeaderRow = document.getElementById('header-row');
        if (tableHeaderRow.children.length === 0) {
            const emptyTh = document.createElement('th');
            tableHeaderRow.appendChild(emptyTh);

            fieldsToDisplay.forEach(field => {
                const th = document.createElement('th');
                th.textContent = field.toUpperCase();
                tableHeaderRow.appendChild(th);
            });

            const locationHeader = document.createElement('th');
            locationHeader.textContent = 'LOCATION';
            tableHeaderRow.appendChild(locationHeader);

            const alertHeader = document.createElement('th');
            alertHeader.textContent = 'ALERT';
            tableHeaderRow.appendChild(alertHeader);
        }

        tableBody.innerHTML = '';

        let alertTriggered = false;
        let dataFound = false;

        data.forEach((item, index) => {
            // Parse numeric IMEI
            const numericImei = item.imei.replace(/[^\d]/g, '');
            const sos = item.sos || '0';  // Default to '0' if undefined
            if (imei === '' || numericImei.includes(imei)) {
                dataFound = true;

                const { lat, lon } = parseCoordinates(item.latitude, item.longitude);
                const row = tableBody.insertRow();
                const rowNumCell = row.insertCell();
                rowNumCell.textContent = index + 1;

                let speedInKilometers = null; // To store converted speed
                
                fieldsToDisplay.forEach(field => {
                    const cell = row.insertCell();
                    
                    // Convert speed from miles to kilometers and display it
                    if (field === 'speed' && item[field]) {
                        const speedInMiles = parseFloat(item[field]);
                        speedInKilometers = (speedInMiles * 1.60934).toFixed(2); // Convert to km/h
                        cell.textContent = `${speedInKilometers} km/h`;

                        // Log the converted speed
                        console.log(`Converted Speed for IMEI: ${item.imei}: ${speedInKilometers} km/h`);
                    } else {
                        cell.textContent = item[field] || '';
                    }
                });

                // Log the final speed value before updating marker
                console.log(`Final Speed Value before updating marker for IMEI: ${item.imei}: ${speedInKilometers}`);

                // Outline the row in red if speed > 60 km/h
                if (speedInKilometers !== null && parseFloat(speedInKilometers) > 60) {
                    row.style.outline = '3px solid red'; // Add red outline
                }

                // Location link
                const locationCell = row.insertCell();
                const locationLink = document.createElement('a');
                locationLink.href = '#';
                locationLink.textContent = 'View Location';

                locationLink.onclick = () => {
                    selectedImei = item.imei;
                    $('#mapModal').modal('show');

                    // Ensure the map is initialized after the modal is fully visible
                    $('#mapModal').on('shown.bs.modal', () => {
                        if (!map) {
                            const lat = parseFloat(localStorage.getItem('lastLat')) || 0; 
                            const lon = parseFloat(localStorage.getItem('lastLon')) || 0; 
                            initializeMap(lat, lon); 
                        }
                    });

                    clearMarkers();
                    routeHistory = [];
                    routePath.setPath([]);

                    if (!map) {
                        initializeMap(lat, lon);
                    }

                    // Log the speed value before passing to the updateMarker function
                    console.log(`Passing Speed Value to updateMarker for IMEI: ${item.imei}: ${speedInKilometers}`);

                    // Pass the speedInKilometers value to the updateMarker function
                    updateMarker(item.imei, lat, lon, item.dir1, item.dir2, speedInKilometers);

                    // Debugging log to check the state of previousStates[item.imei]
                    console.log("Previous state for IMEI:", item.imei, previousStates[item.imei]);

                    // Ensure previousStates[item.imei] is initialized as an object
                    if (!previousStates[item.imei]) {
                        previousStates[item.imei] = {}; // Initialize as an empty object
                        console.log("Initialized previousStates for IMEI:", item.imei);
                    }

                    // Remove the red background when the location is viewed
                    row.style.backgroundColor = ''; // Reset background color
                    previousStates[item.imei].sosAcknowledged = true; // Mark SOS as acknowledged

                    // Log the updated state to verify assignment
                    console.log("Updated previousStates for IMEI:", item.imei, previousStates[item.imei]);
                };
                locationCell.appendChild(locationLink);

                // Alert icon handling
                const alertCell = row.insertCell();
                const alertIcon = document.createElement('i');
                alertIcon.classList.add('fas', 'fa-exclamation-triangle');
                
                // Handle SOS and row highlighting
                if (item.sos === '1') {
                    alertIcon.style.color = 'red';
                    alertTriggered = true;
                    
                    // Check if this SOS has not been acknowledged by viewing the location
                    const previousState = previousStates[item.imei] || { sos: '0', sosAcknowledged: false };
                    
                    // If SOS is triggered and not acknowledged, mark the row as red
                    if (!previousState.sosAcknowledged) {
                        row.style.backgroundColor = 'red';  // Highlight row in red
                    }

                    // Update the SOS state in previousStates
                    previousStates[item.imei] = { sos: item.sos, sosAcknowledged: previousState.sosAcknowledged };
                } else {
                    alertIcon.style.color = 'gray';
                }
                alertCell.appendChild(alertIcon);

                updateMapIfModalOpen(lat, lon, item.imei, item.dir1, item.dir2);
            }
        });

        if (!dataFound) {
            tableBody.innerHTML = '<tr><td colspan="99">No matching data found</td></tr>';
        }

        if (alertTriggered) {
            notification.textContent = "SOS alert triggered!";
            notification.style.display = 'block';
            triggerSOSAlert(notification, alertSound);
            alertSound.play().catch(error => {
                console.error("Audio playback failed:", error);
            });
        } else {
            notification.style.display = 'none';
        }

        errorMessage.style.display = 'none';
    } catch (error) {
        console.error('Error fetching data:', error);
        document.getElementById('error-message').style.display = 'block';
    }
}


function nextPage() {
    if (currentPage < totalPages) {
        currentPage++;
        displayTable(data, currentPage); // Display the next page
    }
}

function prevPage() {
    if (currentPage > 1) {
        currentPage--;
        displayTable(data, currentPage); // Display the previous page
    }
}

function displayTable(data, page) {
    const tableBody = document.getElementById('data-table-body');
    tableBody.innerHTML = ''; // Clear previous rows

    // Calculate the start and end index for the current page
    const start = (page - 1) * rowsPerPage;
    const end = start + rowsPerPage;

    const paginatedItems = data.slice(start, end);
    paginatedItems.forEach((item, index) => {
        const row = tableBody.insertRow();
        const rowNumCell = row.insertCell();
        rowNumCell.textContent = start + index + 1; // Display row number

        Object.values(item).forEach(value => {
            const cell = row.insertCell();
            cell.textContent = value || ''; // Fill cells with data
        });
    });

    // Update page info
    document.getElementById('page-info').textContent = `Page ${page} of ${totalPages}`;
    document.getElementById('prev-btn').disabled = page === 1;
    document.getElementById('next-btn').disabled = page === totalPages;
}



// Handle the back button click to reset the search
document.getElementById('back-button').addEventListener('click', function () {
            document.getElementById('search-input').value = '';
            isSearching = false;
            this.style.display = 'none';
            localStorage.removeItem(searchKey);
            fetchData();
        });
        // Store and restore the search IMEI in localStorage
        function storeSearchImei(imei) {
            localStorage.setItem(searchKey, imei);
        }
        function restoreSearchImei() {
            const storedImei = localStorage.getItem(searchKey);
            if (storedImei) {
                document.getElementById('search-input').value = storedImei;
                $('#back-button').show();
                isSearching = true;
                fetchData(storedImei);
            } else {
                fetchData();
            }
        }
// Function to trigger SOS alert
function triggerSOSAlert(notification, alertSound) {
    notification.textContent = "SOS alert triggered!";
    notification.style.display = 'block';
    alertSound.play().catch(error => {
        console.error("Audio playback failed:", error);
    });

    // Position notification at the top center of the page
    notification.style.position = 'fixed';
    notification.style.top = '20px';
    notification.style.left = '50%';
    notification.style.transform = 'translateX(-50%)';
    notification.style.zIndex = '1000';

    // Automatically hide the notification after a few seconds
    setTimeout(() => {
        notification.style.display = 'none';
    }, 4000);
}

// Handle the back button click to reset the search
document.getElementById('back-button').addEventListener('click', function () {
    document.getElementById('search-input').value = '';
    isSearching = false;
    this.style.display = 'none';
    localStorage.removeItem(searchKey);
    fetchData();
});



$(document).ready(() => {
    restoreSearchImei();  // Restore search state on page load
    startCountdown(); // Start the countdown on page load
    
// Check if the modal was open before reload
const modalOpen = localStorage.getItem('modalOpen');
const lastSelectedImei = localStorage.getItem('selectedImei');

if (modalOpen === 'true' && lastSelectedImei) {
    // Reopen the modal and restore the map with the last selected IMEI
    selectedImei = lastSelectedImei;
    $('#mapModal').modal('show');
    // Assuming last coordinates are stored
    const lastLat = parseFloat(localStorage.getItem('lastLat'));
    const lastLon = parseFloat(localStorage.getItem('lastLon'));

    if (!isNaN(lastLat) && !isNaN(lastLon)) {
        if (!map) {
            initializeMap(lastLat, lastLon);
        }
        updateMarker(selectedImei, lastLat, lastLon, null, null); // You can replace null with actual dir1, dir2 if needed
    }
}
fetchData(); // Initial fetch for table population

$('#mapModal').on('shown.bs.modal', () => {
    if (!map) {
        initializeMap(defaultLat, defaultLon); // Initialize map with default coordinates
    }
    // Save the state when modal is opened
    localStorage.setItem('modalOpen', 'true');
});

$('#mapModal').on('hidden.bs.modal', () => {
    selectedImei = null; // Reset selected IMEI when modal is closed
    clearMarkers(); // Clear markers when modal is closed
    // Clear modal state when modal is closed
    localStorage.setItem('modalOpen', 'false');
    localStorage.removeItem('selectedImei');
    localStorage.removeItem('lastLat');
    localStorage.removeItem('lastLon');
});

setInterval(() => {
    if (selectedImei) {
        fetchData(selectedImei); // Fetch and update data for the selected IMEI
    } else {
        fetchData(); // Regular fetch for the table
    }
}, 10000);

setInterval(() => {
    // Before reloading, save the modal state and the selected IMEI
    if ($('#mapModal').hasClass('show') && selectedImei) {
        localStorage.setItem('modalOpen', 'true');
        localStorage.setItem('selectedImei', selectedImei);

        // Store the last known coordinates
        const lastPoint = routeHistory[routeHistory.length - 1].position;
        localStorage.setItem('lastLat', lastPoint.lat());
        localStorage.setItem('lastLon', lastPoint.lng());
    } else {
        localStorage.setItem('modalOpen', 'false');
    }

    window.location.reload(); // Reload the entire page every 30 seconds
}, 30000);

setInterval(() => {
            const storedImei = localStorage.getItem(searchKey);
            fetchData(storedImei || '');  // Use stored IMEI or fetch full data
        }, 10000);  // Refresh every 10 seconds

        // Search input handling
        $('#search-input').on('input', function () {
            const searchValue = $(this).val().trim();
            if (searchValue !== '') {
                isSearching = true;
                $('#back-button').show();
                storeSearchImei(searchValue);  // Store search IMEI
                fetchData(searchValue);
            } else {
                isSearching = false;
                $('#back-button').hide();
                localStorage.removeItem(searchKey);  // Clear stored search IMEI
                fetchData();
            }
        });
        $('#mapModal').on('hidden.bs.modal', () => {
            selectedImei = null;  // Reset IMEI when the modal is closed
            map = null;  // Clear the map when modal is closed
        });
    });



////////////////////////////////////////////////////////////////////////////////////////////



document.addEventListener('DOMContentLoaded', function () {
// Button click handlers for navigation
document.getElementById('dashboard-btn').addEventListener('click', function() {
    console.log('Dashboard clicked');
    // Redirect logic goes here
});

document.getElementById('singleVehicle-btn').addEventListener('click', function() {
    console.log('Single Vehicle Live maps clicked');
    // Redirect logic goes here
});

document.getElementById('livemap-btn').addEventListener('click', function() {
    console.log('Live maps clicked');
    // Redirect logic goes here
});

document.getElementById('inventory-btn').addEventListener('click', function() {
    console.log('Device Inventory clicked');
    // Redirect logic goes here
});

document.getElementById('typography-btn').addEventListener('click', function() {
    console.log('Typography clicked');
    // Redirect logic goes here
});

document.getElementById('base-btn').addEventListener('click', function() {
    console.log('Base clicked');
    // Redirect logic goes here
});

document.getElementById('buttons-btn').addEventListener('click', function() {
    console.log('Buttons clicked');
    // Redirect logic goes here
});

document.getElementById('charts-btn').addEventListener('click', function() {
    console.log('Charts clicked');
    // Redirect logic goes here
});

document.getElementById('forms-btn').addEventListener('click', function() {
    console.log('Forms clicked');
    // Redirect logic goes here
});

document.getElementById('icons-btn').addEventListener('click', function() {
    console.log('Icons clicked');
    // Redirect logic goes here
});

// Timeframe buttons click handlers
document.getElementById('day-btn').addEventListener('click', function() {
    console.log('Day selected');
    // Logic for day view
});

document.getElementById('month-btn').addEventListener('click', function() {
    console.log('Month selected');
    // Logic for month view
});

document.getElementById('year-btn').addEventListener('click', function() {
    console.log('Year selected');
    // Logic for year view
});

// Initialize auto mode on page load
autoMode();

// Add event listener for the dark mode toggle switch
document.getElementById('dark-mode-toggle').addEventListener('click', function() {
    toggleDarkMode();
});
});

// Toggle Sidebar
function toggleSidebar() {
const sidebar = document.querySelector('.sidebar');
const mainContent = document.querySelector('.main-content');
sidebar.classList.toggle('collapsed');
mainContent.classList.toggle('expanded');
}
document.getElementById('dark-mode-toggle').addEventListener('change', function() {
if (this.checked) {
  document.body.classList.remove('dark-mode');
  document.body.classList.add('light-mode');
  localStorage.setItem('theme', 'light');
} else {
  document.body.classList.remove('light-mode');
  document.body.classList.add('dark-mode');
  localStorage.setItem('theme', 'dark');
}
});

// On page load, set the correct theme based on saved preference
document.addEventListener('DOMContentLoaded', function () {
const savedTheme = localStorage.getItem('theme');
const darkModeToggle = document.getElementById('dark-mode-toggle');

if (savedTheme === 'light') {
  document.body.classList.add('light-mode');
  darkModeToggle.checked = true; // Set checkbox to light mode
} else {
  document.body.classList.add('dark-mode'); // Default to dark mode
  darkModeToggle.checked = false;
}
});


let enableCopy = false;

      console.log("Starting enable_copy.js script");
console.log("enableCopy status:", enableCopy);

if (!enableCopy) {
  console.log("E.C.P is not enabled, returning");
  return;
}
