import React, { useState, useRef } from 'react';
import Webcam from 'react-webcam';
import './app.css';
import logo from './assets/Acera.svg'; // Import logo

const App = () => {
    const [error, setError] = useState(null);
    const webcamRef = useRef(null); // Create a ref for Webcam component

    const handleButtonClick = (buttonName) => {
        if (buttonName === 'Activate AI') {
            fetch('/activate-acera-ai')
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Failed to activate Acera AI');
                    }
                    return response.json();
                })
                .then(data => {
                    console.log('Acera AI activated:', data);
                    setError(null); // Clear any previous errors
                })
                .catch(error => {
                    console.error('Error activating Acera AI:', error);
                    setError('Failed to activate Acera AI');
                });
        } else if (buttonName === 'Gesture Control') {
            fetch('/activate-gesture-control')
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Failed to activate gesture control');
                    }
                    return response.json();
                })
                .then(data => {
                    console.log('Gesture control activated:', data);
                    setError(null); // Clear any previous errors
                })
                .catch(error => {
                    console.error('Error activating gesture control:', error);
                    setError('Failed to activate gesture control');
                });
        }
        // Handle other button clicks as needed
    };

    return (
        <div className="app">
            <div className="sidebar">
                <img src={logo} alt="Acera AI Logo" className="logo" />
                <button onClick={() => handleButtonClick('Dashboard')}>Dashboard</button>
                <button onClick={() => handleButtonClick('Profile')}>Profile</button>
                <button onClick={() => handleButtonClick('Gesture Control')}>
                    <img src={logo} alt="Acera AI Logo" className="button-icon" /> Gesture Control
                </button>
                <button onClick={() => handleButtonClick('Acera AI')}>
                    <img src={logo} alt="Acera AI Logo" className="button-icon" /> Acera AI
                </button>
                <button onClick={() => handleButtonClick('Devices')}>Devices</button>
                <button onClick={() => handleButtonClick('Apps')}>Apps</button>
                <button onClick={() => handleButtonClick('Settings')}>Settings</button>
                <button onClick={() => handleButtonClick('Close')}>Close</button>
            </div>
            <div className="main-content">
                <div className="webcam-container">
                    <Webcam
                        audio={false}
                        ref={webcamRef}
                        screenshotFormat="image/jpeg"
                        width="100%"
                        height="100%"
                        style={{ borderRadius: '10px' }}
                    />
                </div>
                <button className="activate-button" onClick={() => handleButtonClick('Activate AI')}>
                    Activate AI
                </button>
            </div>
            {error && <div className="error-message">{error}</div>}
        </div>
    );
};

export default App;


