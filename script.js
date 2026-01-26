// Application State
let travelData = {
    name: '',
    age: '',
    destination: '',
    budget: '',
    duration: '',
    interests: [],
    foodPreferences: [],
    hotelPreference: '',
    nightlife: false
};

// DOM Elements
const steps = {
    form: document.getElementById('travel-form'),
    processing: document.getElementById('ai-processing'),
    itinerary: document.getElementById('itinerary-output'),
    confirmation: document.getElementById('booking-confirmation'),
    ticket: document.getElementById('travel-ticket')
};

// Initialize Application
document.addEventListener('DOMContentLoaded', function() {
    initializeEventListeners();
    showStep('form');
});

// Event Listeners
function initializeEventListeners() {
    // Form submission
    document.getElementById('travelPlanForm').addEventListener('submit', handleFormSubmit);
    
    // Interest pills
    document.querySelectorAll('#interests .pill-btn').forEach(btn => {
        btn.addEventListener('click', () => togglePill(btn, 'interests'));
    });
    
    // Food preference pills
    document.querySelectorAll('#foodPrefs .pill-btn').forEach(btn => {
        btn.addEventListener('click', () => togglePill(btn, 'foodPreferences'));
    });
    
    // Booking confirmation
    document.getElementById('confirm-booking').addEventListener('click', handleBookingConfirmation);
    
    // View ticket
    document.getElementById('view-ticket').addEventListener('click', () => showStep('ticket'));
    
    // Ticket actions
    document.getElementById('download-ticket').addEventListener('click', handleDownloadTicket);
    document.getElementById('share-trip').addEventListener('click', handleShareTrip);
    document.getElementById('new-trip').addEventListener('click', handleNewTrip);
}

// Step Navigation
function showStep(stepName) {
    // Hide all steps
    Object.values(steps).forEach(step => {
        step.classList.remove('active');
    });
    
    // Show current step
    steps[stepName].classList.add('active');
    
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Form Handling
function handleFormSubmit(e) {
    e.preventDefault();
    
    // Collect form data
    travelData.name = document.getElementById('userName').value;
    travelData.age = document.getElementById('userAge').value;
    travelData.destination = document.getElementById('destination').value;
    travelData.budget = document.getElementById('budget').value;
    travelData.duration = document.getElementById('duration').value;
    travelData.hotelPreference = document.getElementById('hotelPref').value;
    travelData.nightlife = document.getElementById('nightlife').checked;
    
    // Validate required selections
    if (travelData.interests.length === 0) {
        alert('Please select at least one interest!');
        return;
    }
    
    if (travelData.foodPreferences.length === 0) {
        alert('Please select at least one food preference!');
        return;
    }
    
    // Show processing step
    showStep('processing');
    
    // Simulate AI processing
    setTimeout(() => {
        generateItinerary();
        showStep('itinerary');
    }, 3000);
}

// Pill Toggle Functionality
function togglePill(btn, category) {
    const value = btn.dataset.interest || btn.dataset.food;
    
    btn.classList.toggle('selected');
    
    if (btn.classList.contains('selected')) {
        if (category === 'interests') {
            travelData.interests.push(value);
        } else {
            travelData.foodPreferences.push(value);
        }
    } else {
        if (category === 'interests') {
            travelData.interests = travelData.interests.filter(item => item !== value);
        } else {
            travelData.foodPreferences = travelData.foodPreferences.filter(item => item !== value);
        }
    }
}

// Itinerary Generation
function generateItinerary() {
    // Update summary
    document.getElementById('summary-destination').textContent = travelData.destination;
    document.getElementById('summary-budget').textContent = `₹${parseInt(travelData.budget).toLocaleString()}`;
    document.getElementById('summary-duration').textContent = `${travelData.duration} days`;
    
    // Display selected interests
    const interestsContainer = document.getElementById('summary-interests');
    interestsContainer.innerHTML = '';
    travelData.interests.forEach(interest => {
        const tag = document.createElement('span');
        tag.className = 'interest-tag';
        tag.textContent = interest.charAt(0).toUpperCase() + interest.slice(1);
        interestsContainer.appendChild(tag);
    });
    
    // Generate day-wise itinerary
    const daysContainer = document.getElementById('itinerary-days');
    daysContainer.innerHTML = '';
    
    const itineraryTemplates = generateItineraryTemplates();
    
    for (let day = 1; day <= parseInt(travelData.duration); day++) {
        const dayCard = createDayCard(day, itineraryTemplates[day - 1] || itineraryTemplates[0]);
        daysContainer.appendChild(dayCard);
    }
}

// Itinerary Templates
function generateItineraryTemplates() {
    const templates = [
        {
            title: "Arrival & Exploration",
            activities: [
                { icon: "fas fa-plane-arrival", text: "Airport pickup and hotel check-in" },
                { icon: "fas fa-utensils", text: "Welcome lunch at local restaurant" },
                { icon: "fas fa-map-marked-alt", text: "City orientation tour" },
                { icon: "fas fa-camera", text: "Sunset photography session" }
            ]
        },
        {
            title: "Adventure & Culture",
            activities: [
                { icon: "fas fa-hiking", text: "Morning adventure activity" },
                { icon: "fas fa-monument", text: "Cultural site visit" },
                { icon: "fas fa-shopping-bag", text: "Local market exploration" },
                { icon: "fas fa-cocktail", text: "Evening at rooftop bar" }
            ]
        },
        {
            title: "Relaxation & Departure",
            activities: [
                { icon: "fas fa-spa", text: "Spa and wellness session" },
                { icon: "fas fa-gift", text: "Souvenir shopping" },
                { icon: "fas fa-suitcase", text: "Hotel checkout" },
                { icon: "fas fa-plane-departure", text: "Airport transfer" }
            ]
        }
    ];
    
    // Customize based on interests
    if (travelData.interests.includes('beach')) {
        templates[1].activities[0] = { icon: "fas fa-umbrella-beach", text: "Beach activities and water sports" };
    }
    
    if (travelData.interests.includes('food')) {
        templates[0].activities[1] = { icon: "fas fa-utensils", text: "Food tour and cooking class" };
    }
    
    if (travelData.nightlife) {
        templates[1].activities[3] = { icon: "fas fa-music", text: "Nightlife and club experience" };
    }
    
    return templates;
}

// Create Day Card
function createDayCard(dayNumber, template) {
    const dayCard = document.createElement('div');
    dayCard.className = 'day-card';
    
    dayCard.innerHTML = `
        <div class="day-title">
            <i class="fas fa-calendar-day"></i>
            Day ${dayNumber}: ${template.title}
        </div>
        <div class="day-activities">
            ${template.activities.map(activity => `
                <div class="activity">
                    <i class="${activity.icon}"></i>
                    <span>${activity.text}</span>
                </div>
            `).join('')}
        </div>
    `;
    
    return dayCard;
}

// Booking Confirmation
function handleBookingConfirmation() {
    showStep('confirmation');
    
    // Auto-advance to ticket after animation
    setTimeout(() => {
        generateTicket();
    }, 2000);
}

// Ticket Generation
function generateTicket() {
    // Generate random booking details
    const bookingId = 'WL' + Math.random().toString(36).substr(2, 8).toUpperCase();
    const seatNumber = Math.floor(Math.random() * 30) + 1 + String.fromCharCode(65 + Math.floor(Math.random() * 6));
    
    // Populate ticket details
    document.getElementById('ticket-name').textContent = travelData.name;
    document.getElementById('ticket-destination').textContent = travelData.destination;
    document.getElementById('ticket-duration').textContent = `${travelData.duration} days`;
    document.getElementById('ticket-booking-id').textContent = bookingId;
    document.getElementById('ticket-seat').textContent = seatNumber;
}

// Ticket Actions
function handleDownloadTicket() {
    // Simulate download
    const link = document.createElement('a');
    link.download = `WanderLust-AI-Ticket-${travelData.name.replace(/\s+/g, '-')}.pdf`;
    link.href = 'data:text/plain;charset=utf-8,WanderLust AI Travel Ticket - ' + travelData.name;
    link.click();
    
    showNotification('Ticket downloaded successfully! 📄');
}

function handleShareTrip() {
    // Simulate sharing
    if (navigator.share) {
        navigator.share({
            title: 'My WanderLust AI Trip',
            text: `I'm going to ${travelData.destination} for ${travelData.duration} days! Planned with WanderLust AI.`,
            url: window.location.href
        });
    } else {
        // Fallback for browsers without Web Share API
        const shareText = `I'm going to ${travelData.destination} for ${travelData.duration} days! Planned with WanderLust AI.`;
        navigator.clipboard.writeText(shareText).then(() => {
            showNotification('Trip details copied to clipboard! 📋');
        });
    }
}

function handleNewTrip() {
    // Reset form and data
    travelData = {
        name: '',
        age: '',
        destination: '',
        budget: '',
        duration: '',
        interests: [],
        foodPreferences: [],
        hotelPreference: '',
        nightlife: false
    };
    
    // Reset form fields
    document.getElementById('travelPlanForm').reset();
    
    // Reset pill selections
    document.querySelectorAll('.pill-btn.selected').forEach(btn => {
        btn.classList.remove('selected');
    });
    
    // Reset toggle
    document.getElementById('nightlife').checked = false;
    
    // Show form
    showStep('form');
    
    showNotification('Ready to plan your next adventure! ✈️');
}

// Notification System
function showNotification(message) {
    // Create notification element
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 100px;
        right: 20px;
        background: rgba(255, 215, 0, 0.95);
        color: #0f4c3a;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        font-weight: 600;
        z-index: 10000;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(10px);
        animation: slideInRight 0.3s ease-out;
    `;
    notification.textContent = message;
    
    // Add animation keyframes
    if (!document.querySelector('#notification-styles')) {
        const style = document.createElement('style');
        style.id = 'notification-styles';
        style.textContent = `
            @keyframes slideInRight {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
            @keyframes slideOutRight {
                from { transform: translateX(0); opacity: 1; }
                to { transform: translateX(100%); opacity: 0; }
            }
        `;
        document.head.appendChild(style);
    }
    
    document.body.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease-in';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 3000);
}

// Smooth scrolling for better UX
function smoothScrollToTop() {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
}

// Add some interactive animations
document.addEventListener('DOMContentLoaded', function() {
    // Add hover effects to cards
    const cards = document.querySelectorAll('.card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
            this.style.transition = 'transform 0.3s ease';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
    
    // Add ripple effect to buttons
    const buttons = document.querySelectorAll('.primary-btn, .secondary-btn');
    buttons.forEach(button => {
        button.addEventListener('click', function(e) {
            const ripple = document.createElement('span');
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;
            
            ripple.style.cssText = `
                position: absolute;
                width: ${size}px;
                height: ${size}px;
                left: ${x}px;
                top: ${y}px;
                background: rgba(255, 255, 255, 0.3);
                border-radius: 50%;
                transform: scale(0);
                animation: ripple 0.6s linear;
                pointer-events: none;
            `;
            
            if (!document.querySelector('#ripple-styles')) {
                const style = document.createElement('style');
                style.id = 'ripple-styles';
                style.textContent = `
                    @keyframes ripple {
                        to {
                            transform: scale(4);
                            opacity: 0;
                        }
                    }
                `;
                document.head.appendChild(style);
            }
            
            this.style.position = 'relative';
            this.style.overflow = 'hidden';
            this.appendChild(ripple);
            
            setTimeout(() => {
                if (ripple.parentNode) {
                    ripple.parentNode.removeChild(ripple);
                }
            }, 600);
        });
    });
});

// Add some easter eggs and delightful interactions
let clickCount = 0;
document.querySelector('.logo').addEventListener('click', function() {
    clickCount++;
    if (clickCount === 5) {
        showNotification('🎉 You found the secret! Thanks for exploring WanderLust AI!');
        clickCount = 0;
        
        // Add some confetti effect
        for (let i = 0; i < 20; i++) {
            setTimeout(() => {
                createConfetti();
            }, i * 100);
        }
    }
});

function createConfetti() {
    const confetti = document.createElement('div');
    confetti.style.cssText = `
        position: fixed;
        width: 10px;
        height: 10px;
        background: ${['#ffd700', '#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4'][Math.floor(Math.random() * 5)]};
        left: ${Math.random() * 100}vw;
        top: -10px;
        z-index: 10000;
        border-radius: 50%;
        animation: confettiFall 3s linear forwards;
    `;
    
    if (!document.querySelector('#confetti-styles')) {
        const style = document.createElement('style');
        style.id = 'confetti-styles';
        style.textContent = `
            @keyframes confettiFall {
                to {
                    transform: translateY(100vh) rotate(720deg);
                    opacity: 0;
                }
            }
        `;
        document.head.appendChild(style);
    }
    
    document.body.appendChild(confetti);
    
    setTimeout(() => {
        if (confetti.parentNode) {
            confetti.parentNode.removeChild(confetti);
        }
    }, 3000);
}