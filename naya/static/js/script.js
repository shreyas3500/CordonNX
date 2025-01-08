document.addEventListener('DOMContentLoaded', function () {
    // Button click handlers for navigation
    document.getElementById('dashboard-btn').addEventListener('click', function() {
        console.log('Dashboard clicked');
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
  