    // Import the functions you need from the SDKs you need
    import { initializeApp } from "https://www.gstatic.com/firebasejs/11.6.0/firebase-app.js";
    import { getDatabase, ref, push, set, serverTimestamp } from "https://www.gstatic.com/firebasejs/11.6.0/firebase-database.js";


    const firebaseConfig = {
        apiKey: "AIzaSyAFFdYvQ7JqHgMTlulOlBHdrL6x8gZPPZY",
        authDomain: "contact1-a0fd2.firebaseapp.com",
        projectId: "contact1-a0fd2",
        storageBucket: "contact1-a0fd2.firebasestorage.app",
        messagingSenderId: "484459908005",
        appId: "1:484459908005:web:bca4250e40128ea1abb64c"
    };

        
    // Initialize Firebase
    const app = initializeApp(firebaseConfig);
    console.log("Firebase initialized!", app);

    // Initialize Realtime Database
    const db = getDatabase(app);
    console.log("Database ready!", db);

    // ✅ Example: write some test data
    set(ref(db, 'test/path'), {
    message: "Hello from Firebase v11!"
    })
    .then(() => console.log("Data written successfully!"))
    .catch((error) => console.error("Write failed:", error));

    // Reference to your database
  const contactRef = ref(db, 'infos');
  
  // Handle form submission
  document.querySelector('form').addEventListener('submit', submitForm);
  
  function submitForm(e) {
    e.preventDefault();
    
    // Get form values
    const name = document.querySelector('input[type="text"]').value.trim();
    const email = document.querySelector('input[type="email"]').value.trim();
    const phone = document.querySelector('input[type="tel"]').value.trim();
    const message = document.querySelector('textarea').value.trim();
  
    // Validation check
    if (!name || !email || !phone || !message) {
      showAlert("Something went wrong. Please fill out all fields.", "error");
      return; // Stop further execution
    }
  
    // Save to Firebase
    saveContactInfo(name, email, phone, message);
  
    // Reset form and show success message
    e.target.reset();
    showAlert('Thank you! Your message has been sent.', 'success');
  }
    
  function saveContactInfo(name, email, phone, message) {
    const newContactRef = push(contactRef); // 🔄 push in modular SDK
  
    set(newContactRef, {
      name: name,
      email: email,
      phone: phone,
      message: message,
      timestamp: serverTimestamp() // ✅ Modular SDK replacement
    })
    .then(() => console.log('Data saved successfully'))
    .catch(error => {
      console.error('Error saving data:', error);
      showAlert('There was an error sending your message. Please try again.', 'error');
    });
  }
  
  
  // Show alert message
  function showAlert(message, type) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert ${type}`;
    alertDiv.textContent = message;
    
    const main = document.querySelector('main');
    main.insertBefore(alertDiv, main.firstChild);
    
    // Remove alert after 5 seconds
    setTimeout(() => {
      alertDiv.remove();
    }, 5000);
  }
       // FAQ functionality
    const faqItems = document.querySelectorAll('.faq-item');
        
    faqItems.forEach(item => {
        const question = item.querySelector('.faq-question');
           
        question.addEventListener('click', () => {
            item.classList.toggle('active');
               
            const icon = question.querySelector('i');
            if (item.classList.contains('active')) {
                icon.classList.remove('fa-chevron-down');
                icon.classList.add('fa-chevron-up');
            } else {
                icon.classList.remove('fa-chevron-up');
                icon.classList.add('fa-chevron-down');
            }
        });
    });
  // Add this CSS for alerts in your styles.css
  /*
  .alert {
    padding: 1rem;
    margin: 1rem 0;
    border-radius: 4px;
    font-weight: 500;
  }
  .alert.success {
    background: #d4edda;
    color: #155724;
    border: 1px solid #c3e6cb;
  }
  .alert.error {
    background: #f8d7da;
    color: #721c24;
    border: 1px solid #f5c6cb;
  }
  */
        // Function to show popup
        function showLoginPopup() {
          document.getElementById('loginPopup').style.display = 'flex';
      }
  
      // Function to close popup
      function closePopup() {
          document.getElementById('loginPopup').style.display = 'none';
      }
  
      // Add click event listeners to protected links
      document.addEventListener('DOMContentLoaded', function() {
          const protectedLinks = document.querySelectorAll('a[href="models.html"], a[href="contact.html"], a[href="design.html"]');
          
          protectedLinks.forEach(link => {
              link.addEventListener('click', function(e) {
                  e.preventDefault();
                  showLoginPopup();
              });
          });
      });
  
  // Check login status and update UI
function updateAuthUI() {
  const authSection = document.getElementById('auth-section');
  if (!authSection) return;

  // Check if user is logged in (in a real app, you'd check Firebase auth)
  const isLoggedIn = localStorage.getItem('isLoggedIn') === 'true';
  const userName = localStorage.getItem('userName') || 'User';


  if (isLoggedIn) {
      authSection.innerHTML = `
          <div class="user-profile">
              <img src="https://ui-avatars.com/api/?name=${encodeURIComponent(userName)}&background=random" class="user-avatar" alt="User">
              <div class="user-dropdown">
                  <a href="dashboard.html">Dashboard</a>
                  <a href="#" id="logout-btn">Logout</a>
              </div>
          </div>
      `;

      // Add logout functionality
      const logoutBtn = document.getElementById('logout-btn');
      if (logoutBtn) {
          logoutBtn.addEventListener('click', function(e) {
              e.preventDefault();
              localStorage.removeItem('isLoggedIn');
              localStorage.removeItem('userName');
              window.location.href = 'index.html';
          });
      }
  } else {
      authSection.innerHTML = '<a href="login.html" class="login-btn">Login</a>';
  }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
  updateAuthUI();
  
  // For protected pages, redirect to login if not authenticated
  const protectedPages = ['models.html', 'design.html', 'dashboard.html'];
  const currentPage = window.location.pathname.split('/').pop();
  
  if (protectedPages.includes(currentPage) && localStorage.getItem('isLoggedIn') !== 'true') {
      window.location.href = 'login.html';
  }
});
        // Popup functions
        function showPopup() {
            document.getElementById('loginPopup').style.display = 'flex';
        }
        function hidePopup() {
            document.getElementById('loginPopup').style.display = 'none';
        }
        
        // Wait for page to fully load
        document.addEventListener('DOMContentLoaded', function() {
            // Add click handlers to specific navigation links
            const navLinks = document.querySelectorAll('nav a');
            
            navLinks.forEach(link => {
                const href = link.getAttribute('href');
                
                // Check if link is one of our protected pages
                if (href && (href.includes('models.html') || 
                             href.includes('design.html') || 
                             href.includes('contact.html'))) {
                    
                    link.addEventListener('click', function(e) {
                        // For testing - you can remove this later
                        console.log('Link clicked:', href);
                        
                        e.preventDefault();
                        showPopup();
                    });
                }
            });
                    // Utility to check login status
                function isLoggedIn() {
                    return localStorage.getItem("loggedInUserId") !== null;
                }
                            
        });
        
